
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
    print('Reading speeds from file....')
    mask_lat = dataset.variables[headers[0]][:]
    print('done with: ' + headers[0])
    mask_lon = dataset.variables[headers[1]][:]
    print('done with: ' + headers[1])
    mask_vel_x = dataset.variables[headers[2]][:]
    print('done with: ' + headers[2])
    mask_vel_y = dataset.variables[headers[3]][:]
    print('done with: ' + headers[3])
    print('reading the nonzero...')
    nonzeroposition_x = ma.nonzero(mask_vel_x)
    nonzeroposition_y = ma.nonzero(mask_vel_y)
    print('zip...')
    nonzeroposition_zip = zip(nonzeroposition_x[0], nonzeroposition_x[1], nonzeroposition_y[0], nonzeroposition_y[1])
    print('filtering and casting cooridnates....')
    nonzeroposition = []
    for x in tqdm(nonzeroposition_zip):
        if x[0]==x[2] & x[1]==x[3]:
            nonzeroposition.append((x[0],x[1]))
    lat = []
    lon = []
    vel_x = []
    vel_y = []
    print('creatating the dataframe...')
    for pos in tqdm(nonzeroposition):
        lat.append(ma.getdata(mask_lat[pos[0],pos[1]]))
        lon.append(ma.getdata(mask_lat[pos[0],pos[1]]))
        vel_x.append(ma.getdata(mask_vel_x[pos[0],pos[1]]))
        vel_y.append(ma.getdata(mask_vel_y[pos[0],pos[1]]))

    table = {headers[0]: lat, headers[1]: lon, headers[2]: vel_x, headers[3]: vel_y}

    # for varname in headers:
    #     table[varname] =
        # print('reading values for variable ' + varname + '...')
        # values = dataset.variables[varname][:]
        # varshape = values.shape[0]
        # # resamplespace = range(0,varshape,sample_step)
        # nonzeroposition = ma.nonzero(values)
        # values = values[::sample_step,::sample_step]
        # array = np.asarray(values,dtype=np.float64)
        # print(array.dtype)
        # aaa = np.ndarray.flatten(array)
        # # values3 = np.empty((1,varshape))
        # # for i in resamplespace:
        # #     piece = aaa[i:i+sample_step]
        # #     piecemean = piece.mean()
        # #     np.append(values3,piecemean)
        # table[varname] = aaa.tolist()
        # print(aaa[100000:1000000].mean())
        # print(aaa[-1])
        # print ('append to table :_)')
    df = pd.DataFrame(table, columns=headers)
    print('storing in a csv')
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

def main():
    print('this is main at the sice shldet')
    pass


if __name__ == '__main__':
    main()