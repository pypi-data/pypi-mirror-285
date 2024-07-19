
import numpy as np
import pyedflib
import math
import csv
from datetime import datetime
import copy

def _debug_parse_header(filename): #pragma: no cover
    """
    A debug function that reads a header and outputs everything that
    is contained in the header
    """
    import json
    from collections import OrderedDict
    header = OrderedDict()
    with open(filename, 'rb') as f:
        f.seek(0)
        header['version'] = f.read(8).decode()
        header['patient_id'] = f.read(80).decode().strip()
        header['recording_id'] = f.read(80).decode().strip()
        header['startdate'] = f.read(8).decode()
        header['starttime'] = f.read(8).decode()
        header['header_n_bytes'] = f.read(8).decode()
        header['reserved'] = f.read(44).decode().strip()
        header['n_records'] = int(f.read(8).decode())
        header['record_duration'] = int(f.read(8).decode())
        header['n_signals'] = int(f.read(4).decode())

    return header



import struct
# signal label/waveform  amplitude    f       sf
# ---------------------------------------------------
#    1    squarewave        100 uV    0.1Hz   200 Hz
#    2    ramp              100 uV    1 Hz    200 Hz
#    3    pulse 1           100 uV    1 Hz    200 Hz
#    4    pulse 2           100 uV    1 Hz    256 Hz
#    5    pulse 3           100 uV    1 Hz    217 Hz
#    6    noise             100 uV    - Hz    200 Hz
#    7    sine 1 Hz         100 uV    1 Hz    200 Hz
#    8    sine 8 Hz         100 uV    8 Hz    200 Hz
#    9    sine 8.1777 Hz    100 uV    8.25 Hz 200 Hz
#    10    sine 8.5 Hz       100 uV    8.5Hz   200 Hz
#    11    sine 15 Hz        100 uV   15 Hz    200 Hz
#    12    sine 17 Hz        100 uV   17 Hz    200 Hz
#    13    sine 50 Hz        100 uV   50 Hz    200 Hz


class DataParser:
    @staticmethod
    def parse_points(in_file, split_char = ','):
        with open(in_file, 'r') as f:
            temp = f.read()
            if '[' in temp:
                temp = temp.replace('][', split_char)
                temp = temp.replace(']', '')
                temp = temp.replace('[', '')
            temp = temp.replace('%s%s' % (split_char,split_char), split_char)
            temp = temp.split(split_char)

            if temp[-1] == '':
                temp.pop(-1)
        temp = [int(v) for v in temp]
        if max(temp) > 15000:
            return [ v/3 for v in temp]
        else:
            return temp

    @staticmethod
    def parse_dat(in_file, byte_len, start_offset, byteorder = 'little', signed = False):
        with open(in_file, 'rb') as f:
            temp = f.read()
            header = temp[:start_offset]
            temp = temp[start_offset:]
        
        data_list = []
        order_map = {'little':'<', 'big':'>'}
        signed_map = {1:'b', 2:'h', 4:'i'}
        unsigned_map = {1:'B', 2:'H', 4:'I'}
        is_sign_map = {True:signed_map, False: unsigned_map}
        cmd = order_map[byteorder] + str(int(len(temp)/2)) + is_sign_map[signed][byte_len]
        data_list = struct.unpack(cmd ,temp)

        return data_list

    @staticmethod
    def parse_rsa32_header(header: bytes, byteorder):
        info = {}
        order_map = {'little':'<', 'big':'>'}
        ch_id, rate, phy_max, phy_min, value_max, value_min, data_len, signed = struct.unpack('%sIIiiiiBB' % order_map[byteorder], header[:26])
        header = header[26:]
        info['channel_id'] = ch_id + 1 
        info['sample_rate'] = rate
        info['phy_max'] = phy_max
        info['phy_min'] = phy_min
        info['value_max'] = value_max
        info['value_min'] = value_min
        info['data_len'] = data_len
        info['signed'] = False if signed == 0 else True
        info['dimension'] = header[:header.index(0)].decode()
        header = header[10:]
        time_str = header[:header.index(0)].decode()
        info['start_time'] = datetime.strptime(time_str, '%Y_%m_%d_%H_%M_%S')
        return info


class EdfHandle:
    class EdfOriChannel:
        def __init__(self, ori_dict):
            self.ch_dict = ori_dict
        def set_data(self, in_data):
            self.__data_list = in_data
        def get_data(self):
            data = self.__data_list
            del self.__data_list
            return data
        
    class ChannelInfo:
        def __init__(self, label:str, dimension:str, sample_rate:int, physical_max:int, physical_min:int, digital_max:int, digital_min:int, transducer :str= '', prefilter:str = '') -> None:
            self.ch_dict = {
                'label': label,
                'dimension': dimension,
                'sample_rate': sample_rate,
                'physical_max': physical_max,
                'physical_min': physical_min,
                'digital_max': digital_max,
                'digital_min': digital_min,
                'transducer': transducer,
                'prefilter': prefilter
                }
            
        def set_data(self, in_data):
            # mut = ( self.ch_dict['physical_max'] - self.ch_dict['physical_min']) / (self.ch_dict['digital_max'] - self.ch_dict['digital_min'])
            # sub = self.ch_dict['digital_min']
            # offset = self.ch_dict['physical_min'] - sub*mut
            # def convert(i):
            #     return i * mut + offset
            # for i in range(len(in_data)):
            #     in_data[i] = convert(in_data[i])
            # if(any( [ i < ]))
            self.__data_list = in_data
        def get_data(self):
            data = self.__data_list
            del self.__data_list
            return data

    def __init__(self, record_duration = None) -> None:
        self.chennel_list = [] #type: list[EdfHandle.ChannelInfo]
        self.annotation = []
        self.__start_time = None
        if record_duration == None:
            record_duration = 1
        self.record_duration = record_duration
        self.anno_csv = []
        pass
    
    def from_reader(self, reader:pyedflib.EdfReader, anno_csv = None):
        len_count = len(reader.getSampleFrequencies())
        for i in range(len_count):
            ch_info = self.EdfOriChannel(reader.getSignalHeader(i))
            self.chennel_list.append(ch_info)
            ch_info.set_data(reader.readSignal(i, digital=True))
        anno = reader.readAnnotations()
        anno_edf = []
        for i in range(len(anno[0])):
            anno_edf.append(['+%.4f000' % anno[0][i], '' + anno[2][i]+ ''])
            self.add_annotation(anno[0][i], anno[1][i], anno[2][i])
        if anno_csv is not None:
            anno_scv_row = []
            with open(anno_csv, 'r') as f:
                c = csv.reader(f)
                next(c)
                for row in c:
                    anno_scv_row.append(row)
            self.anno_csv += anno_scv_row
        else:
            self.anno_csv += anno_edf

    def append_reader(self, reader:pyedflib.EdfReader, anno_csv = None):
        len_count = len(reader.getSampleFrequencies())
        assert len_count == len(self.chennel_list)
        for i in range(len_count):
            data = self.chennel_list[i].get_data()
            offset = 0
            for ii in range(int(reader.getSampleFrequency(i) * self.record_duration)):
                if data[-ii - 1] == 0:
                    offset -= 1
                else:
                    break
            data = data[0:offset]
            if i == 0:
                data_ori_len = len(data)
            data = np.concatenate((data, reader.readSignal(i, digital=True)), axis=0, out=None, dtype=np.int16, casting="same_kind")
            self.chennel_list[i].set_data(data)
        anno = reader.readAnnotations()
        samp_rate = self.chennel_list[0].ch_dict['sample_rate']
        time_offset = data_ori_len / samp_rate
        anno_edf = []
        for i in range(len(anno[0])):
            anno_edf.append(['+%.4f000' % (anno[0][i]*reader.getSampleFrequency(0)/samp_rate + time_offset), '' + anno[2][i]+ ''])
            self.add_annotation(anno[0][i]*reader.getSampleFrequency(0)/samp_rate + time_offset, anno[1][i], anno[2][i])
        if anno_csv is not None:
            anno_scv_row = []
            with open(anno_csv, 'r') as f:
                c = csv.reader(f)
                next(c)
                for row in c:
                    row = list(row)
                    row[0] = '+%.4f000' % (float(row[0])*reader.getSampleFrequency(0)/samp_rate + time_offset)
                    anno_scv_row.append(row)
            self.anno_csv += anno_scv_row
        else:
            self.anno_csv += anno_edf

    def add_channel(self, label:str, dimension:str, sample_rate:int, physical_max:int, 
                    physical_min:int, digital_max:int, digital_min:int, transducer :str= '', prefilter:str = ''):
        ch_info = self.ChannelInfo(label, dimension, sample_rate, physical_max, physical_min, digital_max, digital_min, transducer, prefilter)
        self.chennel_list.append(ch_info)
        return ch_info

    def _export(self, handle:pyedflib.EdfWriter, start_time = None):
        duraion_r = self.record_duration
        if duraion_r != 1:
            handle.setDatarecordDuration(duraion_r)
        else:
            duraion_r = 1
        channel_info_list = [info.ch_dict for info in self.chennel_list]
        handle.setSignalHeaders(channel_info_list)
        data_list = [info.get_data() for info in self.chennel_list]
        sample_rate = round(channel_info_list[0]['sample_rate']*duraion_r)/duraion_r
        duraion_s = len(data_list[0]) / sample_rate
        max_anno_count = math.ceil(duraion_s/duraion_r)
        if max_anno_count < len(self.annotation):
            # print('warning, too much annotation')
            real_anno = copy.deepcopy(self.annotation)
            self.annotation = self.annotation[:max_anno_count]
            self.annotation[-1] = list(self.annotation[-1])
            self.annotation[-1][2] = 'more annotation: .csv'
        else:
            real_anno = self.annotation
        with open(handle.path + '.csv', 'w', encoding='utf-8', newline='') as f:
            f_csv = csv.writer(f)
            title = ['Onset', 'Annotation']
            f_csv.writerow(title)
            if len(self.anno_csv) == 0:
                z = [['+%.4f000' % v[0], '' + v[2]+ ''] for v in real_anno]
            else:
                z = self.anno_csv
            f_csv.writerows(z)
            del f_csv

        for anno in self.annotation:
            handle.writeAnnotation(*anno)
        if start_time is not None:
            handle.setStartdatetime(start_time)
        handle.writeSamples(data_list, digital=True)

        # print('write anno count %d, all %d' % ( len(self.annotation), len(real_anno)))
        handle.close()

    def get_edf_handle(self, filename) ->pyedflib.EdfWriter:
        handle = pyedflib.EdfWriter('%s.edf' %filename,
                           len(self.chennel_list),
                           file_type=pyedflib.FILETYPE_EDFPLUS)
        return handle
    
    def export_edf(self, filename, start_time = None):
        handle = pyedflib.EdfWriter('%s.edf' %filename,
                           len(self.chennel_list),
                           file_type=pyedflib.FILETYPE_EDFPLUS)
        return self._export(handle, start_time)
    def export(self, filename, start_time = None):
        handle = pyedflib.EdfWriter(filename,
                           len(self.chennel_list),
                           file_type=pyedflib.FILETYPE_EDFPLUS)
        return self._export(handle, start_time)

    def add_annotation(self, onset_in_seconds, duration_in_seconds, description, str_format='utf_8'):
        self.annotation.append([onset_in_seconds, duration_in_seconds, description])

    def export_bdf(self, filename, start_time = None):
        handle = pyedflib.EdfWriter('%s.bdf' %filename,
                           len(self.chennel_list),
                           file_type=pyedflib.FILETYPE_BDFPLUS)
        return self._export(handle, start_time)


if __name__ == '__main__':
    import numpy
    edf = pyedflib.EdfReader(r'C:\Users\loudly\Desktop\20221129201246_part4.bdf')
    a = edf.getSampleFrequencies()
    b = edf.readAnnotations()
    c = edf.getStartdatetime()
    d = edf.getNSamples()
    e = edf.getPhysicalDimension(1)
    f = edf.readSignal(0)
    # print()





