# !/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
@File        :   Base 
@Time        :   2023/8/18 14:34
@Author      :   Xuesong Chen
@Description :   
"""
import re
import numpy as np
from pyedflib.edfreader import EdfReader


class Base:
    def __init__(self, file_path):
        self._parse_file(file_path)

    def _parse_file(self, file_path):
        self.reader = EdfReader(file_path)
        self.signal_labels = np.array(self.reader.getSignalLabels())
        self.duration = self.reader.getFileDuration()
        self._assign_signal_types()

    def close(self):
        if self.reader:
            self.reader.close()
            self.reader = None

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

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
            elif re.search('EEG|C3-M2|C4-M1|F3-M2|F4-M1|O1-M2|O2-M1|F3|F4|C3|C4|O1|O2|A1|A2', sig, re.IGNORECASE):
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
        return self.reader.getStartdatetime()

    def get_number_of_signals(self, type='ecg'):
        return np.sum(self.signal_type == type)

    def get_channel_name(self, type='ecg', order=None):
        if order is None:
            return self.signal_labels[self.signal_type == type]
        else:
            return self.signal_labels[self.signal_type == type][order]

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
        sfreq = int(self.reader.getSampleFrequency(idx))
        if tmin is None or tmax is None:
            return self.reader.readSignal(idx)
        start_samp_idx = sfreq * tmin
        end_samp_idx = sfreq * tmax
        n_samples = end_samp_idx - start_samp_idx
        return self.reader.readSignal(idx, start_samp_idx, n=n_samples)

    def get_sample_frequency(self, ch_name=None, type='ecg', order=0):
        if ch_name:
            idx = np.argwhere(self.signal_labels == ch_name).flatten()[order]
        else:
            idx = np.argwhere(self.signal_type == type).flatten()[order]
        return int(self.reader.getSampleFrequency(idx))

    def get_channel(self, ch_name=None, type=None, tmin=None, tmax=None, order=0):
        """
        获取信号和采样率，order代表次序，0代表第一个匹配的信号
        """
        signal = self.get_signal(ch_name, type, tmin, tmax, order)
        sampling_rate = self.get_sample_frequency(ch_name, type, order)
        return signal, sampling_rate

    def get_duration(self):
        return self.reader.file_duration


if __name__ == '__main__':
    fp = '/Users/cxs/project/OSAPillow/data/SHHS/edfs/shhs1-200001.edf'
    reader = Base(fp)
    sig = reader.get_signal(type='ecg')
    print(reader.signal_labels)
