import numpy as np
import re


def load_sti(sti_path):
    index_list = []
    with open(sti_path, 'r') as f:
        content = f.read()
        zero_counts = len(re.findall(r'\(0\)', content))
        one_counts = len(re.findall(r'\(1\)', content))
    with open(sti_path, 'r') as f:
        for line in f:
            if line.startswith("point count: "):
                index = line.split("\t")[0][13:]
                index_list.append(int(index) // 5)
    index_list = np.array(index_list, dtype=np.int32) if len(index_list) >= 2 else None
    return index_list, one_counts, zero_counts


if __name__ == '__main__':
    sti_path_ = r'D:\pythonProject\sleep_stage\dev_test_data\13592029172_0321-22_16_05_0322-08_04_45_2\sti.log'
    sti_data = load_sti(sti_path_)
