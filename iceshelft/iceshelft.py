
from sputils import fileutils
import settings.settings as settings
from tqdm import tqdm
from netCDF4 import Dataset
import pandas as pd
import csv
import numpy.ma as ma
import numpy as np
import h5py
import matplotlib.pyplot as plt
import os
import conda

conda_file_dir = conda.__file__
conda_dir = conda_file_dir.split('lib')[0]
proj_lib = os.path.join(os.path.join(conda_dir, 'share'), 'proj')
os.environ["PROJ_LIB"] = proj_lib

from mpl_toolkits.basemap import Basemap

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

def read_temp_csv(sample_size='all'):
    iceshelfl_files = fileutils.find_all_files(settings.TEMP_HOME, ".csv")
    if not sample_size == 'all':
        iceshelfl_files = iceshelfl_files[0:sample_size]
    temp_dataframes = []
    print('Casting temp csv in to dataframes.')
    for icefile in tqdm(iceshelfl_files):
        icedf = read_as_df(icefile)
        temp_dataframes.append(icedf)
    return temp_dataframes


def read_icespeed_nc(sample_step=10, store = True):
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
    if store:
        print('storing in a csv')
        df.to_csv(settings.OUTPUT_ICESPEED_CSV, sep=',', encoding='utf-8')
    print('DONE')
    return  df

def read_temp_h5(store=False):
    datafield_name_sur = 'HDFEOS/GRIDS/NpPolarGrid06km/Data Fields/SI_06km_NH_89V_DAY'
    datafield_name_nor = 'HDFEOS/GRIDS/SpPolarGrid06km/Data Fields/SI_06km_NH_89V_DAY'
    icetemp_files = fileutils.find_all_files(settings.TEMP_HOME, ".he5")
    print('reading soiuth..')
    for file in icetemp_files:
        print('processing: ' + file + ' ...')
        outfilename = file[:-3]+"csv"
        if not os.path.exists(outfilename):
            read_one_temp_h5(datafield_name_sur,outfilename,store=store)
        else:
            print('skipping the file ' + outfilename)
    print('reading norht...')
    for file in tqdm(icetemp_files):
        outfilename = file[:-3]+".csv"
        if not os.path.exists(outfilename):
            read_one_temp_h5(datafield_name_nor,outfilename,store=store)
        else:
            print('skipping the file ' + outfilename)

def read_one_temp_h5(datafield_name,outfilename, store=False):
    filename = fileutils.correct_path(settings.ICE_TEMP_H5_FILE)
    with h5py.File(filename, mode='r') as f:
        # List available datasets.
        # Read dataset.
        dset = f[datafield_name]
        data = dset[:]

        # Handle fill value.
        data[data == dset.fillvalue] = 0
        data = np.ma.masked_where(np.isnan(data), data)
        data1 = np.ma.getdata(data)
        dimensions = data1.shape
        xx = np.linspace(0, 7600000, dimensions[1])
        yy = np.linspace(0, 11200000, dimensions[0])
        m = Basemap(width=7600000, height=11200000, projection='stere', lat_ts=70, lat_0=90, lon_0=-45, resolution='l')
        lat = []
        lon = []
        print('transforming to lat and long')
        for y in tqdm(yy[::-1]):
            for x in xx:
                lon_item, lat_item = m(x, y, inverse=True)
                lat.append(lat_item)
                lon.append(lon_item)
        print('generating the data into a csv file')
        data_list = data1.flatten().tolist()
        table = {'lat': lat, 'lon': lon, 'temp': data_list}
        df = pd.DataFrame(table, columns=['lat','lon','temp'])
        if store:
            print('storing in a csv')
            cc = fileutils.correct_path(outfilename)
            print('at.. ' + cc)
            df.to_csv(cc, sep=',', encoding='utf-8')
        else:
            print('dont store')
        print('DONE')

        # plt.imshow(data)
        # plt.colorbar()
        # plt.show()

        # Get attributes needed for the plot.
        # String attributes actually come in as the bytes type and should
        # be decoded to UTF-8 (python3).
        # title = dset.attrs['Title'].decode()
        # units = dset.attrs['Units'].decode()


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
    read_temp_h5(store=True)


if __name__ == '__main__':
    main()
    # m = Basemap(width=7600000,height=11200000,projection='stere', lat_ts=70, lat_0=90, lon_0=-45, resolution='l')
    # print(m.proj4string)
    # m.drawcoastlines()
    # m.fillcontinents(color='coral', lake_color='aqua')
    # # draw parallels and meridians.
    # m.drawparallels(np.arange(-80., 81., 20.))
    # m.drawmeridians(np.arange(-180., 181., 20.))
    # m.drawmapboundary(fill_color='aqua')
    # # draw tissot's indicatrix to show distortion.
    # ax = plt.gca()
    # print(m.ymax)
    # print(m.xmax)
    # print(m.ymin)
    # print(m.xmin)
    # # for x in np.linspace(0, 3750/20, 10): #np.linspace(m.ymax / 20, 19 * m.ymax / 20, 10):
    # #     for y in np.linspace(0, 5850/20,10):
    # #         lon, lat = m(x, y, inverse=True)
    # #         poly = m.tissot(lon, lat, 2.5, 100, \
    # #                         facecolor='green', zorder=10, alpha=0.5)
    # xpt = m.xmax
    # ypt = m.ymax
    # lon, lat = m(xpt, ypt, inverse=True)
    # m.plot(xpt, ypt, 'bo')  # plot a blue dot there
    # plt.text(xpt + 100000, ypt + 100000, 'Boulder (%5.1fW,%3.1fN)' % (lon, lat))
    #
    # plt.title("North Polar Stereographic Projection")
    # plt.show()