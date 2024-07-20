import os
import copy
import json
import struct
import socket
import logging
import datetime
import itertools
import collections.abc
import urllib.parse

import yaml
import numexpr
import numpy as np
import scipy.ndimage


logger = logging.getLogger(__name__)


TABLE_WR_REQUEST = 13
TABLE_WR_RESPONSE = 14
TABLE_RD_REQUEST = 15
TABLE_RD_RESPONSE = 16
ERROR_RESPONSE = 23
ERROR_UNIMPLEMENTED = 1


def template_str(s, variables):
    """
    If `s` is a string wrapped by '{}', evaluate the contents using `variables`
    and return the result. Otherwise, returns `s` unchanged.
    """
    if isinstance(s, str) and s.startswith("{") and s.endswith("}"):
        return numexpr.evaluate(s[1:-1], local_dict=variables, global_dict={})
    else:
        return s


def template_value(v, variables):
    """
    Recursively template `v`, replacing any strings wrapped in '{}' by
    their templated values.

    Mutates lists and dictionaries in-place; copy first if you need to
    preserve the original.
    """
    if isinstance(v, collections.abc.MutableSequence):
        for i in range(len(v)):
            v[i] = template_value(v[i], variables)
    elif isinstance(v, collections.abc.MutableMapping):
        for k in v:
            v[k] = template_value(v[k], variables)
    else:
        v = template_str(v, variables)
        if isinstance(v, np.ndarray):
            v = float(v)
    return v


def get_value(block, key, variables=None, default=None):
    """
    Look up `key` in `block`, replacing with `default` if not found,
    evaluating using `variables` if a string wrapped by "{}".
    """
    if variables is None:
        variables = {}
    v = block.get(key, default)
    return template_str(v, variables)


def get_float(block, key, variables=None, default=None):
    """
    Look up `key` in `block`, replacing with `default` if not found,
    evaluating using `variables` if a string wrapped by "{}",
    and return as a float.
    """
    return float(get_value(block, key, variables, default))


def get_int(block, key, variables=None, default=None):
    """
    Look up `key` in `block`, replacing with `default` if not found,
    evaluating using `variables` if a string wrapped by "{}",
    and return as an int.
    """
    return int(get_value(block, key, variables, default))


def block_corner(block, prev_corner, variables=None):
    """
    Insert a single new corner at time block['duration'] from previous time,
    to new value block['target'].

    Block keys:
    * 'duration': Delta time from previous corner, in seconds.
                  Specify either 'duration' or 'time'.
                  Default: 0.0
                  Templated: Yes, float
    * 'time':     Absolute time of corner, in seconds.
                  Specify either 'duration' or 'time'.
                  Default: Uses 'duration' if unspecified.
                  Templated: Yes, float
    * 'target':   New value to move to.
                  Default: previous value
                  Templated: Yes, float
    """
    prev_t, prev_v = prev_corner
    if 'time' in block:
        assert 'duration' not in block, \
            "Cannot specify both 'time' and 'duration'"
        time = get_float(block, 'time', variables)
        assert time >= prev_t, "'time' must be after previous corner time"
        duration = time - prev_t
    else:
        duration = get_float(block, 'duration', variables, 0.0)
    target = get_float(block, 'target', variables, prev_v)
    return [[prev_t + duration, target]]


def block_hold(block, prev_corner, variables=None):
    """
    Hold previous value for an additional block['duration'] seconds.

    Block keys:
    * 'duration': Duration of hold, in seconds.
                  Specify either 'duration' or 'until'.
                  Default: 0.0
                  Templated: Yes, float
    * 'until':    Hold until an absolute time in seconds.
                  Specify either 'duration' or 'until'.
                  Default: Uses 'duration' if unspecified.
                  Templated: Yes, float
    """
    prev_t, prev_v = prev_corner
    if 'until' in block:
        assert 'duration' not in block, \
            "Cannot specify both 'until' and 'duration'"
        until = get_float(block, 'until', variables)
        assert until >= prev_t, "'until' must be after previous corner time"
        duration = until - prev_t
    else:
        duration = get_float(block, 'duration', variables, 0.0)
    return [[prev_t + duration, prev_v]]


def block_ramp(block, prev_corner, variables=None):
    """
    Ramp from previous value to block['target'],
    either over block['duration'] seconds or
    at a rate of block['rate'] per second.

    Block keys:
    * 'duration': Duration of ramp, in seconds.
                  Specify either 'duration' or 'rate'.
                  Default: 0.0
                  Templated: Yes, float
    * 'rate':     Ramp rate in value-units per second.
                  Specify either 'duration' or 'rate'.
                  Default: Uses 'duration' if unspecified.
                  Templated: Yes, float
    * 'target':   Target value to ramp to.
                  Default: previous value
                  Templated: Yes, float
    """
    prev_t, prev_v = prev_corner
    target = get_float(block, 'target', variables, prev_v)
    if 'rate' in block:
        rate = get_float(block, 'rate', variables)
        duration = abs(prev_v - target) / rate
    else:
        duration = get_float(block, 'duration', variables, 0.0)
    return [[prev_t + duration, target]]


def block_staircase(block, prev_corner, variables=None):
    """
    Generates a staircase profile. Step values are either given in
    block['steps'], or computed from block['nsteps'] and block['target'].

    Each step is dwelled on for block['step_duration'] seconds, ramping between
    steps either over block['ramp_duration'] seconds or at a rate of
    block['ramp_rate'].

    Block keys:
    * 'steps':         List of values to hold at.
                       Specify either 'steps' OR ('nsteps' and 'target').
                       Default: Uses 'nsteps' if unspecified.
                       Templated: Yes, see below.
    * 'nsteps':        Number of steps to generate, instead of using 'steps'.
                       Specify either 'steps' OR ('nsteps' and 'target').
                       Default: 1
                       Templated: Yes, integer
    * 'target':        Final value to hold at, instead of using 'steps'.
                       Specify either 'steps' OR ('nsteps' and 'target').
                       Default: previous value
                       Templated: Yes, float
    * 'step_duration': Duration to hold each step.
                       Default: 0.0
                       Templated: Yes, float
    * 'ramp_rate':     Ramp rate between steps in value-units per second
                       Specify either 'ramp_rate' OR 'ramp_duration'.
                       Default: uses 'ramp_duration' if unspecified.
                       Templated: Yes, float
    * 'ramp_duration': Duration to ramp between each step.
                       Specify either 'ramp_rate' OR 'ramp_duration'.
                       Default: 0.0
                       Templated: Yes, float

    Note on templating 'steps':
    If 'steps' is a single variable name enclosed by "{" and "}", it is
    replaced entirely by the template value, which must be either a list of
    floats or a string representing a list of floats in YAML format.
    If 'steps' is a list or a string representing a list, each entry in the
    list is optionally templated as a float.
    """
    prev_t, prev_v = prev_corner
    if variables is None:
        variables = {}
    if 'steps' in block:
        # If steps is specified, it may be a simple list of floats,
        # or a list of strings representing templated floats,
        # or a string representing a variable containing a list.
        s = block['steps']
        if isinstance(s, str) and s.startswith("{") and s.endswith("}"):
            # In this case s is like '{variable}',
            # and variable is either a list already or a string for a list.
            s_var = s[1:-1]
            if s_var not in variables:
                raise KeyError(f"{s_var} not found in variables")
            steps = variables[s_var]
            if isinstance(steps, str):
                steps = list(yaml.safe_load(steps))
            else:
                steps = list(steps)
        else:
            steps = []
            # Otherwise s is a list of either floats or strings to template
            for step in list(s):
                steps.append(get_float({'step': step}, 'step', variables))

    else:
        # If steps is not specified, use 'nsteps' and 'target' instead,
        # both of which can take default values.
        nsteps = int(get_float(block, 'nsteps', variables, 1))
        target = get_float(block, 'target', variables, prev_v)
        if nsteps <= 1:
            step_size = (target - prev_v)
        else:
            step_size = (target - prev_v) / (nsteps - 1)
        steps = [prev_v + step_size * i for i in range(nsteps)]

    step_duration = get_float(block, 'step_duration', variables, 0.0)
    ramp = {}
    if 'ramp_rate' in block:
        ramp['rate'] = get_float(block, 'ramp_rate', variables)
    else:
        ramp['duration'] = get_float(block, 'ramp_duration', variables, 0.0)

    # Start with the previous corner, then remove it at the end.
    corners = [prev_corner]

    def ramp_to(target):
        b = {'target': target}
        b.update(ramp)
        return block_ramp(b, corners[-1])

    if steps[0] != prev_v:
        corners += ramp_to(steps[0])
    for step in steps[1:]:
        corners += block_hold({'duration': step_duration}, corners[-1])
        corners += ramp_to(step)
    corners += block_hold({'duration': step_duration}, corners[-1])

    return corners[1:]


def block_to_corners(block, prev_corner, variables=None):
    """
    Process block based on block['type'].

    If 'type' is unspecified it defaults to 'corner'.
    """
    blocks = {
        "corner": block_corner,
        "hold": block_hold,
        "ramp": block_ramp,
        "staircase": block_staircase,
    }
    return blocks[block.get('type', 'corner')](block, prev_corner, variables)


def blocks_to_corners(blocks, variables=None, tzero_offset=0.0):
    """
    Process entire list of blocks.

    Starting corner is [tzero_offset, 0].

    Returns final list of corners.
    """
    corners = [[tzero_offset, 0]]
    for block in blocks:
        corners += block_to_corners(block, corners[-1], variables)
    return corners


def interpolate_corners(corners, dt_ms, scale_max, cutoff=3.0):
    """
    Creates a regularly sampled profile based on an array of (t, val) corners.
    The output type is np.uint16, scaled such that `scale_max` in the input
    corresponds to 65535 in the output.

    * `profile`: Corners in (t, value) pairs, ordered by time in seconds
    * `dt_ms`: Output timestep in milliseconds
    * `scale_max`: Value at input to correspond to 65535 at output
    * `cutoff`: Cutoff frequency in Hz

    Returns filtered and resampled profile timesteps and data array.
    """

    corners = np.asarray(corners)

    # Check arguments
    assert np.all(np.diff(corners[:, 0]) >= 0), \
        "Profile times must be monotonically non-decreasing"
    assert not np.any(corners[:, 1] > scale_max), "Profile exceeds scale_max"
    assert type(dt_ms) is int, "dt_ms must be an integer"
    assert 1 <= dt_ms <= 1000, "dt_ms must be between 1 and 1000"

    # Resample to internal dt of 1ms
    dt_filter = 1e-3
    t = np.arange(corners[0, 0], corners[-1, 0]+dt_filter, dt_filter)
    p = np.interp(t, corners[:, 0], corners[:, 1])

    # Filter
    f = (1.0/dt_filter)/(2.0*np.pi*cutoff)
    p_filt = scipy.ndimage.gaussian_filter1d(p, f)

    # Resample to output dt
    t_out = np.arange(corners[0, 0], corners[-1, 0]+dt_ms*1e-3, dt_ms*1e-3)
    p_out = np.interp(t_out, t, p_filt)

    # Rescale
    p_out *= 65535.0 / scale_max

    # Check output
    assert np.all(p_out >= 0.0), "Generated profile not non-negative"
    assert np.all(p_out <= 65535.0), "Generated profile exceeds 65535"

    return t_out, p_out.astype(np.uint16)


def generate_profile(box_cfg, variables=None):
    """
    Generate the profile data required by an AMV box,
    based on the specified box configuration and variables.

    Uses the following keys in `box_cfg`:
        * `type`: One of 'profile_dist', 'profile_ol', or 'profile_cl'
        * `scale_max`: Value in input units to correspond to 65535 at output
        * `dt_ms': Output timestep in milliseconds, default 100
        * `cutoff_freq`: Filter cutoff frequency in Hz, default 3.0
        * `profile`: List of dicts of blocks which define the profile shape:
            * `type`: 'corner'/'hold'/'ramp'/'staircase'
            * See block documentation for remaining keys

    Returns (t, d, p):
        (t, d) are the profile time and data in input units,
        p contains the raw profile words to write to the AMV.
    """
    profile_types = {"profile_dist": 1, "profile_ol": 2, "profile_cl": 3}
    assert 'type' in box_cfg, "Config missing 'type'"
    assert 'scale_max' in box_cfg, "Config missing 'scale_max'"
    assert 'profile' in box_cfg, "Config missing 'profile'"
    assert box_cfg['type'] in profile_types, \
        "Unknown profile type {box_cfg['type']}"

    profile_type = profile_types[box_cfg['type']]
    dt_ms = get_int(box_cfg, 'dt_ms', variables, 100)
    scale_max = get_float(box_cfg, 'scale_max', variables)
    cutoff = get_float(box_cfg, 'cutoff_freq', variables, 3.0)
    tzero_offset = box_cfg.get('tzero_offset', 0.0)

    # Generate list of corners and then filter and scale to profile data
    corners = blocks_to_corners(box_cfg['profile'], variables, tzero_offset)
    t_out, p_out = interpolate_corners(corners, dt_ms, scale_max, cutoff)

    # Generate final profile dataset
    prof_data = [dt_ms, len(p_out), profile_type] + list(p_out)
    assert all(0 <= d <= 65535 for d in prof_data), "Profile data out of range"

    # Rescale to input units for display
    p_in = p_out.astype(float) * (scale_max / 65535.0)

    # Return profile as (t, d) for plotting and as raw data for writing
    return t_out, p_in, prof_data


def sequence_to_steps(sequence, run_or_stop='run', variables=None,
                      tzero_offset=0.0):
    """
    Convert a list of channels with on-windows to a sequence of valve commands.

    `tzero_offset` is subtracted from all times in the provided windows, so the
    returned steps always start at time 0.
    """
    assert run_or_stop in ('run', 'stop')
    mask = 0
    step_times = {0: {"on": [], "off": []}}
    for channel in sequence:
        if run_or_stop in channel and channel[run_or_stop]:
            ch = int(channel['channel'])
            mask |= (1 << (ch - 1))
            windows = channel[run_or_stop]
            for start_stop in windows:
                # Process start time first, which must always be present.
                # Template, convert to seconds, remove offset, convert to
                # 1ms step times, and add to overall sequence.
                start = start_stop[0]
                start = float(template_str(start, variables)) - tzero_offset
                start = int(start * 1000)
                if start not in step_times:
                    step_times[start] = {"on": [], "off": []}
                step_times[start]["on"].append(ch)
                # If present, process stop times, otherwise valve will stay
                # on until the next window or indefinitely.
                if len(start_stop) == 2:
                    stop = start_stop[1]
                    stop = float(template_str(stop, variables)) - tzero_offset
                    stop = int(stop * 1000)
                    if stop not in step_times:
                        step_times[stop] = {"on": [], "off": []}
                    step_times[stop]["off"].append(ch)
    steps = []
    state = 0
    for t in sorted(step_times.keys()):
        for ch in step_times[t]["on"]:
            state |= (1 << (ch - 1))
        for ch in step_times[t]["off"]:
            state &= ~(1 << (ch - 1))
        steps.append([t, state])
    return mask, steps


def steps_to_series(mask, steps, tzero_offset=0.0, edge_dt=0.01, max_dt=0.1):
    """
    Convert a mask and list of (time, state) steps to a time series
    per channel, suitable for plotting. The input steps start at time 0,
    while the output series starts at `tzero_offset`.

    Returns a list of (channel_number, time_series, boolean_value_series),
    with transitions in value output over `edge_dt` seconds to ensure sharp
    edges when points are interpolated, and repeat points inserted
    every `max_dt` to ensure minimum output density. `channel_number` is
    1-indexed.

    Only channels set in `mask` are output.
    """
    # Store time series and corresponding values for each channel
    time = [0.0]
    channels = {i: [0.0] for i in range(len(f"{mask:b}"))}

    for (t, state) in steps:
        # Convert t from steps of 10ms to seconds
        t *= 0.001

        # Insert repeat points every max_dt steps
        while t - time[-1] > max_dt:
            time.append(time[-1] + max_dt)
            for d in channels.values():
                d.append(d[-1])
        # Insert current value at current time
        time.append(t)
        for d in channels.values():
            d.append(d[-1])
        # Insert new values at edge_dt time later
        time.append(t + edge_dt)
        for ch in channels:
            bit = (state & (1 << ch)) >> ch
            channels[ch].append(float(bit))

    # Apply tzero offset for display
    time = [t + tzero_offset for t in time]

    return [(ch+1, time, d) for (ch, d) in channels.items()
            if mask & (1 << ch)]


def generate_sequence(box_cfg, variables=None):
    """
    Generate sequencing data required by a valve controller box,
    based on the specified box configuration and variables.

    Uses the following keys in `box_cfg`:
        * `type`: Must be 'sequence'
        * `sequence`: List of dicts of channels:
            * `channel`: Channel number on valve controller box
            * `run`: List of [on_time, off_time] windows for run sequence
            * `stop`: List of [on_time, off_time] windows for stop sequence
            * Both run and stop are optional.
              If neither are specified, the channel is excluded from both
              run and stop masks.
              If only a run sequence is specified, the channel is included
              in both run and stop masks, and turned off in the stop sequence.
              If only a stop sequence is specified, the channel is excluded
              from the run mask, but included in the stop mask.

    Returns (run_series, stop_series, data), where:
        * run_series and stop_series are lists of (channel, time, value)
          tuples containing time-series data for each channel in run and stop
        * data contains the list of 32-bit words to program to the DAU
    """
    # Check configuration
    assert 'type' in box_cfg, "Config missing 'type'"
    assert box_cfg['type'] == 'sequence', f"Invalid type {box_cfg['type']}"
    assert 'sequence' in box_cfg, "Config missing 'sequence'"
    sequence = box_cfg['sequence']
    for channel in sequence:
        assert 'channel' in channel, "Channel definition missing 'channel'"
        assert channel['channel'] > 0, "Channel must be > 0"

    tzero_offset = box_cfg.get('tzero_offset', 0.0)

    # Find mask and steps for run and stop sequences
    run_mask, run_steps = sequence_to_steps(
        sequence, 'run', variables, tzero_offset)
    stop_mask, stop_steps = sequence_to_steps(sequence, 'stop', variables)

    # We ensure all valves changed in run are controlled in stop
    stop_mask |= run_mask

    # Generate DAU data format
    run_n = len(run_steps)
    stop_n = len(stop_steps)
    data = [run_mask, run_n, stop_mask, stop_n]
    for t, val in itertools.chain(run_steps, stop_steps):
        data += [t, val]
    assert all(0 <= v < 2**32 for v in data), "Data out of range"

    # Pack data into 16-bit words
    out_data = []
    for word in data:
        out_data.append(word & 0xFFFF)
        out_data.append(word >> 16)

    # Generate time sequence for display as a 'channel'
    run_series = steps_to_series(run_mask, run_steps, tzero_offset)
    stop_series = steps_to_series(stop_mask, stop_steps)

    return run_series, stop_series, out_data


def generate_nop():
    """
    Generates profile data to cause a programmed box to take no action.
    This can be safely written to all DAUs in a configuration not otherwise
    given a profile, to ensure they do not still contain old profile data.
    """
    return [0]*64


def read_box(hostname, port, n, unimpl_ok=False):
    """
    Read table data from an AEL3xxx DAU.

    Returns an `n`-length list of 16-bit integers.
    """
    logger.info("Reading %d bytes from DAU %s", n, hostname)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(True)
    sock.settimeout(0.2)
    offset = 0  # bytes
    max_chunk_size = 256  # bytes
    data = []  # 16-bit words
    while len(data) < n:
        bytes_left = (n - len(data)) * 2
        chunk_size = min(bytes_left, max_chunk_size)
        cmd = struct.pack("<HHHH", TABLE_RD_REQUEST, 4, offset, chunk_size)
        sock.sendto(cmd, (hostname, port))
        rx = sock.recv(1024)
        logger.debug("Received %d bytes from DAU %s", len(rx), hostname)
        hdr_type, hdr_len = struct.unpack("<HH", rx[:4])
        if hdr_type == ERROR_RESPONSE and rx[4] == ERROR_UNIMPLEMENTED and unimpl_ok:
            logger.debug("Table read unimplemented, ignoring")
            return
        elif hdr_type != TABLE_RD_RESPONSE:
            raise RuntimeError(f"Unexpected packet {hdr_type} from DAU")
        data += struct.unpack(f"<{hdr_len//2}H", rx[4:4+hdr_len])
        offset += hdr_len
    return data


def dau_crc16(data):
    """
    Computes the CRC16 used by the DAUs to verify written table data integrity.
    """
    table = [
        0x0000, 0xCC01, 0xD801, 0x1400, 0xF001, 0x3C00, 0x2800, 0xE401,
        0xA001, 0x6C00, 0x7800, 0xB401, 0x5000, 0x9C01, 0x8801, 0x4400,
    ]
    crc = 0xFFFF
    for byte in data:
        crc = ((crc >> 4) & 0x0FFF) ^ table[(crc ^ byte) & 0xF]
        crc = ((crc >> 4) & 0x0FFF) ^ table[(crc ^ (byte >> 4)) & 0xF]
    return crc ^ 0xFFFF


def write_box(hostname, port, data, unimpl_ok=False):
    """
    Write 16-bit table data to an AEL3xxx DAU.

    Validates the returned CRC16 and raises an exception if doesn't match.
    """
    logger.info("Writing %d bytes to DAU %s", len(data), hostname)
    assert all(0 <= x <= 65535 for x in data), "Data contains invalid values"
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setblocking(True)
    sock.settimeout(0.2)
    offset = 0  # bytes
    nbytes = len(data) * 2  # bytes
    max_chunk_size = 256  # bytes
    while offset < nbytes:
        bytes_left = nbytes - offset
        chunk_size = min(bytes_left, max_chunk_size)
        tx_data = struct.pack(f"<{chunk_size//2}H",
                              *data[offset//2:(offset+chunk_size)//2])
        tx_crc = dau_crc16(tx_data)
        cmd = struct.pack(f"<HHH{chunk_size}B",
                          TABLE_WR_REQUEST, 2+chunk_size, offset, *tx_data)
        logger.debug("Sending %d bytes to DAU %s", chunk_size, hostname)
        sock.sendto(cmd, (hostname, port))
        rx = sock.recv(1024)
        hdr_type, hdr_len = struct.unpack("<HH", rx[:4])
        if hdr_type == ERROR_RESPONSE and rx[4] == ERROR_UNIMPLEMENTED and unimpl_ok:
            logger.debug("Table write unimplemented, ignoring")
            return
        elif hdr_type != TABLE_WR_RESPONSE:
            raise RuntimeError(f"Unexpected packet {hdr_type} from DAU")
        rx_crc = struct.unpack("<H", rx[4:4+hdr_len])[0]
        assert tx_crc == rx_crc, "Invalid CRC received when writing table"
        offset += chunk_size


def load_box(addr, data, unimpl_ok=False):
    """
    Send table data to an AEL3xxx DAU.

    * `addr` is a URL like 'udp://192.168.19.1:1735'.
    * `data` is a list of 16-bit data words.
    * `unimpl_ok`: if True, ignore ERROR_RESPONSE with value UNIMPLEMENTED.

    As well as checking the returned CRC16, also reads the entire
    table back to confirm successful write.
    """
    logger.info("Loading %d words of data to %s", len(data), addr)
    url = urllib.parse.urlparse(addr)
    assert url.scheme == "udp", f"Unsupported URL scheme {url.scheme}"
    hostname = url.hostname
    port = url.port
    write_box(hostname, port, data, unimpl_ok=unimpl_ok)
    rxdata = read_box(hostname, port, len(data), unimpl_ok=unimpl_ok)
    if unimpl_ok and rxdata is None:
        return
    assert rxdata == data, "Readback unsuccessful"


def load_template(tpl, variables=None):
    """
    Given a template and variables, render all profile data and load all DAUs.
    """
    # Load all unused DAUs with an empty profile
    nop = generate_nop()
    for dau in tpl.get('unused_daus', []):
        logger.info("Rendering NOP sequence for DAU %s", dau.get('dau'))
        addr = dau.get('addr')
        load_box(addr, nop, unimpl_ok=True)

    # Render profile/sequence data for each DAU and load it
    for dau in tpl.get('daus', []):
        dau_dau = dau.get('dau')
        dau_type = dau.get('type', '')
        addr = dau.get('addr')
        if dau_type.startswith("profile_"):
            logger.info("Rendering profile for DAU %s", dau_dau)
            _, _, data = generate_profile(dau, variables)
            load_box(addr, data)
        elif dau_type == "sequence":
            logger.info("Rendering sequence for DAU %s", dau_dau)
            data = generate_sequence(dau, variables)
            load_box(addr, data)


def read_templates_from_config(path):
    """
    Read templates from a configuration file, pulling in DAU and channel names.

    Returns a list of templates. Each template has:

    * `name`: String name for template
    * `description`: String description for template
    * `tzero_offset`: Optional offset applied to profile times, default 0
    * `variables`: List of variable dictionaries, each containing:
        * `variable`: String ID for variable
        * `name`: String name for variable
        * `description`: String description for variable
        * `type`: Variable type. One of: `float`
        * `units`: String units for variable
        * `default`: Default value for variable, type depends on `type`
        * `decimals`: Number of decimal places to adjust to, default 3
        * `step`: Adjustment step size, default 0.01
        * `minimum`: Minimum value, default 0.0
        * `maximum`: Maximum value, default 100.0
    * `daus`: List of DAU dictionaries, each containing:
        * `dau`: String ID for DAU, looked up to `dau_assigs` in config
        * `name`: String name for DAU
        * `addr`: String address for DAU
        * `type`: Profile type. One of `profile_dist`, `profile_ol`,
                  `profile_cl`, or `sequence`.
        When `type` is `profile_*`, also contains:
        * `dt_ms`: Integer dt in milliseconds.
        * `scale_max`: Float maximum scale value.
        * `cutoff_freq`: Float profile shape cutoff frequency.
        * `units`: String units for profile
        * `profile`: List of blocks that form profile shape, see
                     `generate_profile` documentation.
        When `type` is `sequence`, also contains:
        * `sequence`: List of channels with sequence data, see
                      `generate_sequence` documentation.
    * `unused_daus`: List of DAUs that exist in the configuration but are
      not used by the profile, each containing:
        * `dau`: String ID for DAU
        * `name`: String name for DAU
        * `addr`: String address for DAU
    """
    try:
        with open(path) as f:
            config = yaml.safe_load(f)
    except (IOError, OSError) as e:
        logger.warning("Error opening config file: %s", e)
        return []

    templates = config.get('templates')
    if templates is None:
        return []

    cfg_daus = config.get('dau_assig', [])
    cfg_daus = {d['dau']: d for d in cfg_daus}
    cfg_assigs = config.get('assignments', [])
    cfg_channels = {f"{a['dau']}-{a['channel']}": a
                    for a in cfg_assigs if 'channel' in a}
    cfg_roles = {a['role']: a for a in cfg_assigs if 'channel' in a}

    # First pass to process inheritance
    for tpl in templates:
        assert 'name' in tpl, "Template missing 'name'"
        for inherit in tpl.get('inherits', []):
            parent_tpl = [t for t in templates if t['name'] == inherit]
            assert len(parent_tpl) == 1, f"Can't find inheritance template {inherit}"
            parent_tpl = parent_tpl[0]
            logger.info("Template %s inheriting from %s",
                        tpl['name'], parent_tpl['name'])
            if 'tzero_offset' not in tpl and 'tzero_offset' in parent_tpl:
                tpl['tzero_offset'] = parent_tpl['tzero_offset']
            assert tpl['tzero_offset'] == parent_tpl['tzero_offset'], \
                "Inherited tzero_offset doesn't match template"
            tpl_vars = {v['id']: v for v in tpl.get('variables', [])}
            for var in parent_tpl.get('variables', []):
                if 'variables' not in tpl:
                    tpl['variables'] = []
                if var['id'] in tpl_vars:
                    logger.info(f"Skipping inheriting extant variable {var['id']}")
                    continue
                tpl['variables'].append(var)
            for valve in parent_tpl.get('valves', []):
                if 'valves' not in tpl:
                    tpl['valves'] = []
                tpl['valves'].append(valve)
            for dau in parent_tpl.get('daus', []):
                if 'daus' not in tpl:
                    tpl['daus'] = []
                tpl['daus'].append(dau)
        if 'inherits' in tpl:
            del tpl['inherits']

    # Second pass to fill in defaults and move valves into DAUs
    for tpl in templates:
        tpl_tzero_offset = float(tpl.get('tzero_offset', 0.0))
        if 'daus' not in tpl:
            tpl['daus'] = []
        profile_daus = [d.get('dau') for d in tpl['daus']]

        for var in tpl.get('variables', []):
            if 'decimals' not in var:
                var['decimals'] = 3
            if 'step' not in var:
                var['step'] = 0.01
            if 'minimum' not in var:
                var['minimum'] = 0.0
            if 'maximum' not in var:
                var['maximum'] = 100.0

        for valve in tpl.get('valves', []):
            role = valve['role']
            assert role in cfg_roles, f"Could not find {role} in config"
            assig = cfg_roles[role]
            assig_dau = assig['dau']
            if assig_dau not in profile_daus:
                tpl['daus'].append(dict(dau=assig_dau, type='sequence', sequence=[]))
                profile_daus.append(assig_dau)
            tpl_dau = [d for d in tpl['daus'] if d['dau'] == assig_dau][0]
            tpl_dau['sequence'].append({
                "channel": assig['channel'],
                "run": valve.get('run', []),
                "stop": valve.get('stop', []),
            })
        if 'valves' in tpl:
            del tpl['valves']

        for dau in tpl.get('daus', []):
            # Look up name and address
            dau_id = dau.get('dau')
            cfg_dau = cfg_daus.get(dau_id)
            assert cfg_dau is not None, f"Could not find {dau_id} in config"
            dau['name'] = cfg_dau.get('name')
            dau['addr'] = cfg_dau.get('addr')
            dau['tzero_offset'] = tpl_tzero_offset

            # Look up channel names
            if 'sequence' in dau:
                for ch in dau['sequence']:
                    ch_id = f"{dau_id}-{ch['channel']}"
                    cfg_ch = cfg_channels.get(ch_id)
                    assert cfg_ch is not None, f"Could not find {ch_id} in cfg"
                    ch['name'] = cfg_ch.get('name')

            # Fill in default profile settings
            if dau['type'].startswith("profile_"):
                if 'dt_ms' not in dau:
                    dau['dt_ms'] = 100
                if 'cutoff_freq' not in dau:
                    dau['cutoff_freq'] = 3.0

        # Generate list of unused DAUs
        tpl['unused_daus'] = []
        for cfg_dau in cfg_daus.values():
            if cfg_dau.get('dau') not in profile_daus:
                tpl['unused_daus'].append({
                    "dau": cfg_dau.get('dau'),
                    "name": cfg_dau.get('name'),
                    "addr": cfg_dau.get('addr'),
                })

    return templates


def write_json_metadata(data_path, template, variables):
    """
    Write out a JSON metadata file containing information on the template
    in use and its variables.

    If `analysis_metadata` is specified in the template, it is filled in
    using `variables` and also written out.
    """
    metadata = {
        "template": json.dumps(template),
        "template_variables": json.dumps(variables),
        "template_datetime": datetime.datetime.utcnow().isoformat() + "Z",
    }
    if 'analysis_metadata' in template:
        am = copy.deepcopy(template['analysis_metadata'])
        am = template_value(am, variables)
        metadata["analysis_metadata"] = json.dumps(am)

    json_path = os.path.join(data_path, "metadata.json")

    # If the JSON file already exists, open it and overwrite the fields
    # relevant to sequencing.
    if os.path.isfile(json_path):
        with open(json_path) as f:
            logger.info("Loading existing JSON file '%s'", json_path)
            existing_metadata = json.load(f)
            existing_metadata.update(metadata)
            metadata = existing_metadata

    logger.info("Writing JSON data to '%s'", json_path)
    with open(json_path, "w") as f:
        json.dump(metadata, f)


if __name__ == "__main__":
    import sys
    import pprint
    t = read_templates_from_config(sys.argv[1])
    pprint.pprint(t)
