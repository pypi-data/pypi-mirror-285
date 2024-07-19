import qleegss.eeg2edf.qlelib as qlelib
import os
from qleegss.eeg2edf.decode_data import eegIsX8
"""
copy from FengXiNan
"""


qldata2edf = qlelib.qldata2edf
qle2edf = qlelib.qle2edf
repair = qlelib.qle_data_check


def find_file(root, func, recursion=True):
    ret = []
    for f in os.listdir(root):
        full_name = root + '/' + f
        if (os.path.isfile(full_name)):
            if func(full_name):
                ret.append(full_name)
        elif recursion:
            ret += find_file(full_name, func)
    return ret


def repair_err_data(data_p):
    if eegIsX8(data_p):
        with open(data_p, 'rb') as f:
            f.seek(41)
            data = f.read(8)
        end_ms = int.from_bytes(data, byteorder='little', signed=True)
        if end_ms == 0:
            dir_ = os.path.dirname(data_p)
            base_name = data_p[len(dir_) + 1:]
            repair_name = dir_ + '/repair_' + base_name
            data, err_list = repair.qle_data_check(data_p, repair_name, force_write=False)
            if len(err_list) > 0:
                data_p = repair_name
    return data_p


def data_translate_edf(data_p):
    data_p = repair_err_data(data_p)
    qldata2edf.convert(data_p)


def edf_join(edf_list: list[str], out_put_name):
    import qlelib.data2edf as data2edf
    from pyedflib import EdfReader

    if len(edf_list) == 0:
        return
    if os.path.exists(out_put_name + '.edf'):
        raise Exception('out name is exists %s' % out_put_name)
    edf_readers: list[EdfReader] = []
    anno_csvs = []
    headers = [data2edf._debug_parse_header(name) for name in edf_list]
    assert all([h['record_duration'] == headers[0]['record_duration'] for h in
                headers]), 'All files must have the same record duration'
    header = headers[0]
    durations = []
    for i in edf_list:
        csv_f = i + '.csv'
        if not os.path.exists(csv_f):
            csv_f = None
        anno_csvs.append(csv_f)
        edf_readers.append(EdfReader(i))
    for i in range(len(edf_readers)):
        sample_rate = edf_readers[i].getSampleFrequency(0)
        ori_duration = edf_readers[i].getFileDuration()
        last_data = edf_readers[i].readSignal(0, start=int((ori_duration - header['record_duration']) * sample_rate),
                                              n=int(sample_rate * header['record_duration']), digital=True)
        offset = 0
        for ii in range(int(sample_rate * header['record_duration'])):
            if last_data[-ii - 1] == 0:
                offset -= 1
            else:
                break
        time_d = offset / sample_rate
        durations.append(ori_duration + time_d)

    edf_writer = data2edf.EdfHandle(header['record_duration'])
    edf_writer.from_reader(edf_readers[0], anno_csvs[0])
    edf_end_time = edf_readers[0].getStartdatetime().timestamp() + durations[0]
    for i in range(1, len(edf_readers)):
        edf_start_time = edf_readers[i].getStartdatetime().timestamp()
        dif = edf_start_time - edf_end_time
        assert abs(dif) < 100, 'edf not conutiue'
        edf_end_time = edf_start_time + durations[i]
        edf_writer.append_reader(edf_readers[i], anno_csvs[0])

    handle = edf_writer.get_edf_handle(out_put_name)
    handle.setEquipment(edf_readers[0].getEquipment().replace(' ', '_'))
    start_time = edf_readers[0].getStartdatetime()
    edf_writer._export(handle, start_time)


def data_translate_edf_path(data_p: str):
    def func(path: str):
        return path.endswith('.eeg') or path.endswith('eeg.qle')

    eeg_p = find_file(data_p, func, recursion=False)
    if len(eeg_p) == 1:
        eeg_p = eeg_p[0]
        if eegIsX8(eeg_p):
            acc_p = find_file(data_p, lambda _: _.endswith('.acc') or _.endswith('acc.qle'), recursion=False)
            tri_p = find_file(data_p, lambda _: _.endswith('tri.tri') or _.endswith('tri.dat'), recursion=False)
            sw_p = find_file(data_p, lambda _: _.endswith('sti.log'), recursion=False)
            dir_info = {'EEG': eeg_p}
            if len(acc_p) == 1:
                dir_info['ACC'] = acc_p[0]
            if len(tri_p) == 1:
                dir_info['TRI'] = tri_p[0]
            if len(sw_p) == 1:
                dir_info['SW'] = sw_p[0]
            qle2edf.convert_dir(dir_info, os.path.join(data_p, os.path.basename(data_p)))
            return

    def func(path: str):
        return path.endswith('.eeg') or path.endswith('.acc') or path.endswith('.qle')

    all_file = find_file(data_p, func, recursion=False)
    for f in all_file:
        qldata2edf.convert(f)


if __name__ == '__main__':
    dir_name = r'D:\pythonProject\sleep_stage\dev_test_data\13592029172_0321-22_16_05_0322-08_04_45_2'
    data_translate_edf_path(dir_name)
