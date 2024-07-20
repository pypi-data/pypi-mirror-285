import logging

import numpy as np

from .sequencing import generate_profile, generate_sequence
from .dataset import Dataset

logger = logging.getLogger(__name__)


class ProfileDataset(Dataset):
    """
    Store a dataset generated from a templated profile.
    """
    def __init__(self, template, variables):
        channels = {}
        groups = [{"id": "profiles", "name": "Profiles"},
                  {"id": "run_seq", "name": "Run Sequences"},
                  {"id": "stop_seq", "name": "Stop Sequences"}]
        self.channel_time = {}
        self.channel_data = {}
        self.template = template
        self.variables = variables

        for dau in self.template.get('daus', []):
            if dau.get('type', '').startswith("profile_"):
                dau_id = dau.get('dau')
                t, p, _ = generate_profile(dau, self.variables)
                ch = {"id": dau_id, "name": dau['name'], "format": "%.03f",
                      "groups": ["profiles"], "units": dau['units']}
                channels[dau_id] = ch
                self.channel_time[dau_id] = np.asarray(t)
                self.channel_data[dau_id] = np.asarray(p)
            elif dau.get('type') == "sequence":
                dau_id = dau.get('dau')
                names = {c['channel']: c['name'] for c in dau['sequence']}
                run, stop, _ = generate_sequence(dau, self.variables)

                def add_ch(channel, t, d, group):
                    ch_id = f"{dau_id}-{channel:02d}-{group}"
                    ch = {"id": ch_id, "name": names[channel],
                          "format": "%.1f", "groups": [f"{group}_seq"],
                          "units": ""}
                    channels[ch_id] = ch
                    self.channel_time[ch_id] = np.asarray(t)
                    self.channel_data[ch_id] = np.asarray(d) * 0.5 + channel

                for (channel, t, d) in run:
                    add_ch(channel, t, d, 'run')
                for (channel, t, d) in stop:
                    add_ch(channel, t, d, 'stop')

        super().__init__(list(channels.values()), groups)

    def name(self):
        return self.template.get('name', "Profile Data")

    def get_channel_data(self, channel_id):
        time = self.channel_time[channel_id]
        data = self.channel_data[channel_id]
        idx = min(time.size, data.size)
        return time[:idx], data[:idx]
