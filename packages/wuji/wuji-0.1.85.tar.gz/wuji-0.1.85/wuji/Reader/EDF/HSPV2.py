#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@File        :   HSPV2
@Time        :   2023/9/14 15:41
@Author      :   Xuesong Chen
@Description :
"""
import re

import matplotlib.pyplot as plt
import numpy as np

from wuji.Reader.EDF.Base import Base
import mne
from pyedflib.edfreader import EdfReader


class HSPV2EDFReader(Base):
    def __init__(self, file_path):
        super().__init__(file_path)

    def _parse_file(self, file_path):
        n_channels = len(mne.io.read_raw_edf(file_path, verbose='error').ch_names)
        self.reader = mne.io.read_raw_edf(file_path, misc=range(n_channels), verbose='error')
        self.signal_labels = np.array(self.reader.ch_names)
        self.duration = self.reader.n_times / self.reader.info['sfreq']
        self._assign_signal_types()

    def _assign_signal_types(self):
        self.signal_type = []
        for idx, sig in enumerate(self.signal_labels):
            if re.search('E[CK]G', sig, re.IGNORECASE):
                self.signal_type.append('ecg')
            elif re.search('S[pa]O2', sig, re.IGNORECASE):
                self.signal_type.append('spo2')
            elif re.search('ABD', sig, re.IGNORECASE):
                self.signal_type.append('abd')
            elif re.search('CHEST|THO', sig, re.IGNORECASE):
                self.signal_type.append('chest')
            elif re.search('C3-M2|C4-M1|F3-M2|F4-M1|O1-M2|O2-M1', sig, re.IGNORECASE):
                self.signal_type.append('eeg')
            elif re.search('EMG', sig, re.IGNORECASE):
                self.signal_type.append('emg')
            elif re.search('EOG', sig, re.IGNORECASE):
                self.signal_type.append('eog')
            elif re.search('Snore', sig, re.IGNORECASE):
                self.signal_type.append('snore')
            elif re.search('position', sig, re.IGNORECASE):
                self.signal_type.append('position')
            elif re.search('Flow|NEW AIR|AirFlow', sig, re.IGNORECASE):
                self.signal_type.append('flow')
            elif re.search('Numeric Aux', sig, re.IGNORECASE):
                self.signal_type.append('trigger')
            elif re.search('Pressure', sig, re.IGNORECASE):
                self.signal_type.append('nasal_pressure')
            elif re.search('Pleth', sig, re.IGNORECASE):
                self.signal_type.append('ppg')
            else:
                self.signal_type.append('unk')
        self.signal_type = np.array(self.signal_type)

    def get_start_recording_time(self):
        return self.reader.info['meas_date']

    def get_sample_frequency(self, **kwargs):
        return int(self.reader.info['sfreq'])

    def get_signal(self, ch_name=None, type='ecg', tmin=None, tmax=None, order=0):
        '''
        获取所有匹配信号，order代表次序，0代表第一个匹配的信号
        :param ch_name:
        :param type:
        :param tmin:
        :param tmax:
        :param order:
        :return:
        '''
        if ch_name:
            idx = np.argwhere(self.signal_labels == ch_name).flatten()[order]
        else:
            idx = np.argwhere(self.signal_type == type).flatten()[order]
        return self.reader.get_data(picks=idx, tmin=tmin, tmax=tmax).squeeze() * 1e6


if __name__ == '__main__':
    fp = '/Users/cxs/Downloads/sub-S0001111239981_ses-3_task-psg_eeg.edf'
    reader = HSPV2EDFReader(fp)
    import yasa
    eeg_chan_name = reader.get_channel_name(type='eeg')
    for tar_pattern in ['C', 'F']:
        for _ch_name in eeg_chan_name:
            if re.search(tar_pattern, _ch_name, re.IGNORECASE):
                print(_ch_name)
    yasa.SleepStaging(reader.reader, )
    # edf_reader = Base(fp)
    # base_ecg = edf_reader.get_signal(type='eeg', order=2)
    print(reader.get_channel_name(type='eeg'))
    plt.plot(reader.get_signal(type='eeg', order=2), label='mne_ecg')
    # plt.plot(base_ecg+10, label='base_ecg')
    plt.legend()
    plt.show()
    print()