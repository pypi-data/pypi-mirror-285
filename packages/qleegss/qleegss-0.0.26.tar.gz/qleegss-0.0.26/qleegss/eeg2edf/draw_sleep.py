import matplotlib.pyplot as plt
import re
from datetime import datetime, timedelta
file = r'C:\Users\fengxinan\Desktop\13547951033_20231017_00_06_17_20231017_08_02_08\sti.log'
with open(file, 'r') as f:
        lines = f.readlines()
real_res = []
start_time = datetime.strptime('20240303 23:29:01', '%Y%m%d %H:%M:%S')
for l in lines:
    rr = {}
    res = re.search(r'NoSti,Stage:([-\d]+),point count: (\d+)', l)
    if res is None:
        res = re.search(r'point count: (\d+)\s+(\w[\w :\(\)]+)', l)
        if res is not None:
            rr['point_count'] = int(res.group(1))
            rr['stage'] = 0
    else:
        rr['point_count'] = int(res.group(2))
        rr['stage'] = int(res.group(1))

    if len(rr) > 0 and rr['stage'] >= 0:
        rr['time'] = start_time + timedelta(seconds=rr['point_count']/503)
        real_res.append(rr)
real_res.sort(key=lambda x: x['point_count'])
x = [i['time'] for i in real_res]
y = [i['stage'] for i in real_res]
start_i = 0
while start_i < len(x) - 1:
    for i in range(start_i, len(x) - 1):
         if x[i] + timedelta(seconds=300) < x[i + 1]:
              x.insert(i + 1, x[i] + timedelta(seconds=150))
              y.insert(i + 1, 5)
              break
    start_i = i + 2
     
plt.plot(x, y, marker='o')
plt.show()
# print()
