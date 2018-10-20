import pandas as pd

EXAMPLE_FILE = '../anaice/ILATM2_20110505_143158_smooth_nadir3seg_50pt.csv'

anaice = pd.read_csv(EXAMPLE_FILE,skiprows=9)

print('**********************************')
print('head: ')
print(anaice.head())
print('**********************************')
print('info of the dataframe: ')
print(anaice.info())
print('**********************************')
print('some more stats:  ')
print('**********************************')
max_values = anaice.max()
print('max values per column: ')
print(max_values)
print('**********************************')
min_values = anaice.min()
print('min values per column: ')
print(min_values)
print('**********************************')
mean_values = anaice.mean()
print('mean values per column: ')
print(mean_values)