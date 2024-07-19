import scipy.io as scio
import numpy as np
from decode_data import DataloaderX7 as oriDataloaderX7, eegIsX8, DataloaderX8, get_box_mac
from scipy import signal
from transdata2edf import repair_err_data

def data_translate_mat(filepath):

    def no_path_warning():
        return "请选择导出路径"
    try:
        filepath
    except NameError:
        A = no_path_warning()
        return
    # else:
    #     if path_of_data:
    #         data_p = filepath
    #     elif path_of_data_batch:
    #         data_p = filepath
    #     print(data_p[-3::])
    filepath = repair_err_data(filepath)
    EEG_p = filepath
    DataloaderX7 = DataloaderX8 if eegIsX8(filepath) else oriDataloaderX7
    A =EEG_p[-3::]
    tail = EEG_p[-3::]

    if tail == 'eeg':
        EEG, PackageIDs, SampleRate, ST, ET, package_loss = DataloaderX7(EEG_p, signed=False)

        b_hp, a_hp = signal.butter(3, 1 / (SampleRate/ 2), 'highpass')
        for i in range(len(EEG)):
            EEG[i] = signal.lfilter(b_hp, a_hp, EEG[i])
        mat_map = {'PackageIDs': PackageIDs, 'SampleRate': SampleRate, 'BoxMac':get_box_mac(),
                            'StartTime': ST, 'EndTime': ET, 'package_loss': package_loss}
        mat_map['EEG'] = EEG
        scio.savemat(EEG_p[:-3] + "mat", mat_map)
    elif tail == 'lay':
        Delay, PackageIDs, SampleRate, ST, ET, package_loss = DataloaderX7(EEG_p, signed=False)
        scio.savemat(EEG_p[:-5] + "mat", {'Delay': Delay, 'PackageIDs': PackageIDs, 'SampleRate': SampleRate,
                                            'StartTime': ST, 'EndTime': ET, 'package_loss': package_loss})

    elif tail == 'emg':
        EMG_p = EEG_p
        EMG, PackageIDs, SampleRate, ST, ET, package_loss = DataloaderX7(EMG_p, signed=False)
        scio.savemat(EEG_p[:-3] + "mat", {'EMG': EMG, 'PackageIDs': PackageIDs, 'SampleRate': SampleRate,
                                            'StartTime': ST, 'EndTime': ET, 'package_loss': package_loss})

    elif tail == 'sti':
        Sti_p = EEG_p
        Sti_T, PackageIDs, SampleRate, ST, ET, package_loss = DataloaderX7(Sti_p, signed=False)
        scio.savemat(EEG_p[:-3] + "mat", {'StiIdx': Sti_T})

    elif tail == 'acc':
        ACC_p = EEG_p
        ACC_T, PackageIDs, SampleRate, ST, ET, package_loss = DataloaderX7(ACC_p, signed=False)
        # plt.plot(ACC_T)
        ACC_T = ACC_T
        ACCx_raw = ACC_T[0]- 32768
        ACCy_raw = ACC_T[1]- 32768
        ACCz_raw = ACC_T[2]- 32768

        ACCx = ACC_T[0][1:-2] - ACC_T[0][2:-1]
        ACCy = ACC_T[1][1:-2] - ACC_T[1][2:-1]
        ACCz = ACC_T[2][1:-2] - ACC_T[2][2:-1]
        ACC = np.abs(ACCx) + np.abs(ACCy) + np.abs(ACCz)
        scio.savemat(EEG_p[:-3] + "mat",
                        {'ACC': ACC, 'ACCT': ACC_T, 'ACCx_raw': ACCx_raw, 'ACCy_raw': ACCy_raw, 'ACCz_raw': ACCz_raw, 'BoxMac':get_box_mac(),
                        'ACCx': ACCx, 'ACCy': ACCy, 'ACCz': ACCz, 'PackageIDs': PackageIDs, 'SampleRate': SampleRate,
                        'StartTime': ST, 'EndTime': ET, 'package_loss': package_loss})
    else:
        return "%s 不是可转换的文件" % EEG_p
    
if __name__ == '__main__':
    data_translate_mat(r'C:\Users\fengxinan\Downloads\14222_1705232999217.eeg.eeg')