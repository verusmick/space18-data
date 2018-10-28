import pickle

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
    return ice_dataframes, iceshelfl_files

def read_temp_csv(sample_size='all'):
    iceshelfl_files = fileutils.find_all_files(settings.TEMP_HOME, ".csv")
    if not sample_size == 'all':
        iceshelfl_files = iceshelfl_files[0:sample_size]
    temp_dataframes = []
    print('Casting temp csv in to dataframes.')
    read_files = []
    for icefile in tqdm(iceshelfl_files):
        date = icefile[-14:-7]
        if str(date).startswith('2015') | str(date).startswith('2016')| str(date).startswith('2017'):
            icedf = pd.read_csv(icefile)
            temp_dataframes.append(icedf)
            read_files.append(icefile)
    return temp_dataframes, read_files


def cast_line_to_values(line):
    tokens = line[:-1].replace('_','0').replace(';','').split(',')[:-1]
    try:
        values = [ float(x) for x in tokens]
        return values
    except:
        print('ERROR!')
        print(tokens)
        return None
def read_icespeed_cld_creation(pckl_filename):
    cld_file = fileutils.correct_path(settings.ICE_SPEED_CDL_FILE)
    data = [[], [], [], []]

    with open(cld_file) as fp:
        pointer = -1
        stop = True
        print('processing...' + cld_file)
        print('reading file')
        content = fp.readlines()
        print('parsing content')
        # pbar = tqdm(total= 108894074 + 1)
        pbar = tqdm(total=len(content) + 1)

        for line in content:
            if 'lat =' in line:
                print('lat found')
                pointer = 0
            elif 'lon =' in line:
                print('lon found')
                pointer = 1
            elif 'VX =' in line:
                print('Vx found')
                pointer = 2
            elif 'VY =' in line:
                print('Vy found')
                pointer = 3
            if pointer > -1:
                values = cast_line_to_values(line)
                if values:
                    [data[pointer].append(v) for v in values]
            pbar.update(1)
        pbar.close()

        # print('done processing. Creating pickle file...')
        # with open(pckl_filename, 'wb') as f:
        #     pickle.dump(data, f)

    return data
def read_icespeed_cdl():
    header = ['lat', 'lon', 'VX', 'VY']
    filename_pkcl = fileutils.correct_path(settings.ICE_SPEED_CDL_FILE[:-4] + '.pckl')
    # if os.path.exists(filename_pkcl):
    #     print("!!! pickle rick file exist. Reading..")
    #     f = open(filename_pkcl, 'rb')
    #     data = pickle.load(f)
    #     f.close()
    # else:
    #     print('Damm morty! I am going to turn my selft inot pickle. Creating ...')
    #     #     data = read_icespeed_cld_creation(filename_pkcl)
    print('Damm morty! I am going to turn my selft inot pickle. Creating ...')
    data = read_icespeed_cld_creation(filename_pkcl)
    print('done. data has benn retrieved. creating the df...')
    table = {}
    minlenght = min([len(d) for d in data])
    for i in range(0,4):
        table[header[i]] = data[i][0:minlenght]
    df = pd.DataFrame(table, columns=header)
    print('ice speep map has been read. DONE! Alles klar!')
    return df


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
        lon.append(ma.getdata(mask_lon[pos[0],pos[1]]))
        vel_x.append(ma.getdata(mask_vel_x[pos[0],pos[1]]))
        vel_y.append(ma.getdata(mask_vel_y[pos[0],pos[1]]))

    table = {headers[0]: lat, headers[1]: lon, headers[2]: vel_x, headers[3]: vel_y}

    df = pd.DataFrame(table, columns=headers)
    if store:
        print('storing in a csv')
        df.to_csv(settings.OUTPUT_ICESPEED_CSV, sep=',', encoding='utf-8')
    print('DONE')
    return df

def read_temp_h5(store=False):
    datafield_name_sur = 'HDFEOS/GRIDS/SpPolarGrid06km/Data Fields/SI_06km_SH_89V_DAY'
    datafield_name_nor = 'HDFEOS/GRIDS/NpPolarGrid06km/Data Fields/SI_06km_NH_89V_DAY'
    # 'HDFEOS/GRIDS/SpPolarGrid06km/Data Fields/SI_06km_SH_89H_DAY'
    icetemp_files = fileutils.find_all_files(settings.TEMP_HOME, ".he5")
    print('reading soiuth..')
    for file in (icetemp_files):
        print('processing: ' + file + ' ...')
        outfilename = file[:-4] +"_S.csv"
        if not os.path.exists(outfilename):
            read_one_temp_h5(file, datafield_name_sur, outfilename, 'south', store=store)
        else:
            print('skipping the file ' + outfilename)
    print('reading norht...')
    for file in (icetemp_files):
        outfilename = file[:-4]+"_N.csv"
        if not os.path.exists(outfilename):
            read_one_temp_h5(file, datafield_name_nor, outfilename, 'north', store=store)
        else:
            print('skipping the file ' + outfilename)

def read_one_temp_h5(filename, datafield_name,outfilename,pole, store=False):
    # filename = fileutils.correct_path(settings.ICE_TEMP_H5_FILE)
    filename = fileutils.correct_path(filename)
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
        if pole == 'south':
            xx = np.linspace(0, 7900000, dimensions[1])
            yy = np.linspace(0, 8300000, dimensions[0])
            m = Basemap(width=7900000, height=8300000, projection='stere', lat_ts=-70, lat_0=-90, lon_0=0,resolution='l')
        elif pole == 'north':
            xx = np.linspace(0, 7600000, dimensions[1])
            yy = np.linspace(0, 11200000, dimensions[0])
            m = Basemap(width=7600000, height=11200000, projection='stere', lat_ts=70, lat_0=90, lon_0=-45, resolution='l')
        else:
            print('ERROR NOTHINGOT DO pole is not corerdt')
            return
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
    # read_icespeed_nc(store=True)
    # read_icespeed_cdl()
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