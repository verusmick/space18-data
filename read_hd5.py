import h5py
# filename = '/media/ari/E25AB5BC5AB58DB3/spaceapps2018/AMSR_36V_PM_FT_2010_day360_v04.h5' #'file.hdf5'
filename = 'AMSR_36V_PM_FT_2010_day360_v04.h5' #'file.hdf5'
f = h5py.File(filename, 'r')
# List all groups
print("Keys: %s" % f.keys())
keys = list(f.keys())
for k in keys:
    print('=====Keys')
    print(k)
a_group_key = list(f.keys())[3]

# Get the data
data = list(f[a_group_key])
print('one data field ' + str(a_group_key))
print(data)
