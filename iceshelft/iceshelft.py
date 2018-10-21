
from sputils import fileutils
import settings.settings as settings
import pandas as pd
from tqdm import tqdm
from netCDF4 import Dataset
import matplotlib.pyplot as plt
import pandas as pd
import csv
import numpy as np
import numpy.ma as ma
import scipy.ndimage


def read_as_df(file):
    df = pd.read_csv(file, skiprows=9)
    return df

def read_ice_csv(sample_size='all'):
    iceshelfl_files = fileutils.find_all_files(settings.ICE_HOME, ".csv")
    if not sample_size == 'all':
        iceshelfl_files = iceshelfl_files[0:sample_size]
    ice_dataframes = []
    print('Casting ice csv in to dataframes.')
    for icefile in tqdm(iceshelfl_files):
        icedf = read_as_df(icefile)
        ice_dataframes.append(icedf)
    return ice_dataframes

def read_icespeed_nc(sample_step=10):
    '''
    read nc file
    :return:
    '''
    nc_file = fileutils.correct_path(settings.ICE_SPEED_NC_FILE)
    dataset = Dataset(nc_file , mask_and_scale=False, decode_times=False)
    nc_vars = [var for var in dataset.variables]
    headers = nc_vars[3:7]
    table = {}
    for varname in headers:
        print('reading values for variable ' + varname + '...')
        values = ma.getdata(dataset.variables[varname][:])
        varshape = values.shape[0]
        resamplespace = range(0,varshape-1,sample_step)
        values = values[::sample_step,::sample_step]
        # array = np.asarray(values,dtype='int')
        # print(array.dtype)
        aaa = np.ndarray.flatten(values).tolist()
        table[varname] = aaa
        print(values.min())
        print(aaa[0])
        print ('append to table :_)')
    df = pd.DataFrame(table, columns=headers)
    df.to_csv(settings.OUTPUT_ICESPEED_CSV, sep=',', encoding='utf-8')


def write_csv(filename, rows):
    '''
    write rows into  a csv files
    :param filename:
    :param rows:
    :return:
    '''
    with open(filename, 'wb') as csvfile:
        csvwritecls = csv.writer(csvfile, delimiter=',')
        csvwritecls.writerow()


if __name__ == '__main__':
    read_icespeed_nc()