import pytz
import datetime

# # 获得当前时间时间戳
# ts = 1635796646
# ts = 1635804773
# ts = 1635968399

# #转换为其他日期格式,如:"%Y-%m-%d %H:%M:%S"
# tz = pytz.timezone('US/Eastern')
# dt = datetime.datetime.fromtimestamp(ts, tz)
# print(dt.strftime('%Y-%m-%d %H:%M:%S'))

import numpy as np
x = [1, 2, 3]
y = [1.2, 2.3, 2.8]
pccs = np.corrcoef(x, y)
print(pccs[0][1])