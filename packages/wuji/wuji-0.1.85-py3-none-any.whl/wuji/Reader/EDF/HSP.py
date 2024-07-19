#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@File        :   HSP 
@Time        :   2023/12/13 16:42
@Author      :   Xuesong Chen
@Description :   
"""

import numpy as np
from datetime import datetime
import h5py
from wuji.Reader.EDF.Base import Base


class HSPEDFReader(Base):
    def __init__(self, file_path):
        super().__init__(file_path)

    def _parse_file(self, file_path):
        self.data = h5py.File(file_path, 'r')
        self.reader = self.data
        self.signal_labels = self.get_signal_labels()
        self._assign_signal_types()

    def get_signal_labels(self):
        label = self.data['hdr']['signal_labels'][:]
        signal_labels = []
        for i in range(label.shape[0]):
            channel_info = ''.join(chr(j[0]) for j in self.data[label[i][0]])
            signal_labels.append(channel_info)

        signal_labels = np.array(signal_labels)
        return signal_labels

    def _get_header_property(self, property_name):
        if property_name not in self.data['hdr']:
            return None
        property_data = self.data['hdr'][property_name]
        res = {}
        for sig_name, p in zip(self.signal_labels, property_data):
            res[sig_name] = np.squeeze(self.data[p[0]]).item()
        return res

    def get_signal_header(self):
        res = {}
        for _property in ['physical_min', 'physical_max', 'digital_min', 'digital_max']:
            _property_data = self._get_header_property(_property)
            res.update({_property: _property_data})
        return res

    def get_number_of_signals(self, type='ecg'):
        return np.sum(self.signal_type == type)

    def get_signal(self, ch_name=None, type='ecg', tmin=None, tmax=None, order=0):
        sampling_freq = self.get_sample_frequency()
        if ch_name:
            idx = np.argwhere(self.signal_labels == ch_name).flatten()
        else:
            if type not in self.signal_type:
                return None
            idx = np.argwhere(self.signal_type == type).flatten()[order]
        if tmin is None or tmax is None:
            return self.data['s'][:, idx]
        start_samp_idx = sampling_freq * tmin
        end_samp_idx = sampling_freq * tmax
        return self.data['s'][:, idx][start_samp_idx:end_samp_idx]

    def get_sample_frequency(self, type=None, order=0):
        return int(np.squeeze(self.data['recording']['samplingrate']))

    def get_start_recording_time(self):
        year, month, day = self.data['recording']['year'], self.data['recording']['month'], self.data['recording'][
            'day']
        hour, minute = self.data['recording']['hour'], self.data['recording']['minute']
        second, millisecond = self.data['recording']['second'], self.data['recording']['millisecond']
        get_single_value = lambda x: np.squeeze(x).astype(int).item()
        start_time = datetime(
            get_single_value(year),
            get_single_value(month),
            get_single_value(day),
            get_single_value(hour),
            get_single_value(minute),
            get_single_value(second),
            get_single_value(millisecond) * 1000,
        )
        return start_time

    def get_durations(self):
        sampling_freq = self.get_sample_frequency()
        return np.squeeze(self.data['samplesCount']) / sampling_freq


if __name__ == '__main__':
    from pprint import pprint as print

    # fp = r'E:\WJ\Shifted_Signal_20230723_212727268.mat'
    fp = r'/Shifted_Signal_000103d6a6d58c79552c49394b3adec2d300352b798aa764bde981b189b2e12e_20200412_205639268.mat'
    # fp = r'E:\WJ\HSP_data\Shifted_Signal_20110417_215226000.mat'
    file_name = '0010ee03836d2d4a4bac885d2f6fcb55c1c437e0ba5b6cf874f15d9d52d29ba7_20110417_215226000'
    hsp = HSPEDFReader(
        f'/Users/cxs/Downloads/hsp/Shifted_Signal_{file_name}.mat')
    # print(hsp.get_signal(type='nasal_pressure'))
    print(hsp.get_signal(type='ecg'))
    print(hsp.get_signal_labels())
    print(hsp.get_sample_frequency())
    print(hsp.get_start_recording_time())
    print(hsp.get_durations())
    print(hsp.get_number_of_signals(type='flow'))
    print(hsp.get_signal_header())
