import pandas as pd
import random
import numpy as np
import visual_test as v

data1 = [1, 2, 3, 2, 1, 2, 3]
data2 = data1.copy()
random.shuffle(data2)

data1d = pd.DataFrame(data1)
data2d = pd.DataFrame()
data2d['x'] = data1
data2d['y'] = data2
list2d = [[data1[i], data2[i]] for i in range(len(data1))]

from data_filter import filtered_data as fd
mlist = []
fd(mlist, machine = 'FL02', sensor = 'drive_gear_V_eff')

#v.Plot(data = data1d, kind = 'scatter', marker = 'D', color = 'r', s = 3)
#v.Plot(data = data1d, kind = 'scatter', marker = 'D', ccolor = 'b', s = 3, legend = True, name = 'drek')

a = np.array(data2d)

#v.Plot(data = a, kind = 'scatter', marker = 'x', color = 'r', s = 15, figure = 'prasac')
#v.Plot(data = a, kind = 'line', c = 'r', legend = True, name = 'drek', figure = 'prasac')

b = np.arange(1, 100, 0.5)
c = b + np.random.rand(len(b)) * 50
df = pd.DataFrame()
df['x'] = b
df['y'] = c

v.Plot(data = df, kind = 'line', figure = 'konj', name = 'random')
v.Plot(data = df, kind = 'line', figure = 'konj', name = 'mean', feature = 'rol-mean', window = 10)

v.Plot(data = mlist, kind = 'scatter', marker = 'x', s = 0.1, color = 'r', figure = 'mes')
v.Plot(data = mlist, figure = 'mes', kind = 'scatter', marker = 'x', s = 0.1, color = 'b', feature = 'rol-mean', window = '1d')
v.Plot(data = mlist, figure = 'mes', kind = 'line',  color = 'y', feature = 'rol-mean', window = '15d')

v.Merge([['konj', 'mes'], ['t', 't']])
