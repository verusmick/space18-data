import iceshelft.iceshelft as iceshelft
from tqdm import tqdm
import os.path as path
import pickle # pickle rick!!!
import pandas as pd
import settings.settings as settings
import numpy as np
import iceplot
def explore_anaice():
    if not path.isfile('dataframes.pckl'):
        print('crateing the dataframe')
        dfs, files = iceshelft.read_ice_csv(3000)
        dfs_within_date = []
        file_within_date = []
        for i, file in enumerate(files):
            date = file[-14:-7]
            if str(date).startswith('2015') | str(date).startswith('2016') | str(date).startswith('2017'):
                dfs_within_date.append(dfs[i])
                file_within_date.append(file)

        f = open('dataframes.pckl', 'wb')
        pickle.dump(dfs_within_date, f)
        f.close()
        f = open('files.pckl', 'wb')
        pickle.dump(file_within_date, f)
        f.close()
    else:
        print('pickle found loading....')
        f = open('dataframes.pckl', 'rb')
        dfs_within_date = pickle.load(f)
        f.close()
        f = open('files.pckl', 'rb')
        files_within_frame = pickle.load(f)
        f.close()
        print('loading done')
    print('numbers fo data frames: ')
    print(len(dfs_within_date))

    fields = list(dfs_within_date[0].columns)
    lat_field_name = fields[1]
    lon_field_name = fields[2]

    total_number_of_points = 0
    df_larsens = []
    for df in tqdm(dfs_within_date):
        # filter latitude
        # df_larsen = df[(df[lat_field_name] < 0)]
        df_larsen = df[(df[lat_field_name] < -62) & ((df[lat_field_name] > -74))
                       & ((df[lon_field_name] > 360-67)) & ((df[lon_field_name] > 360-57)) ]
        if len(df_larsen)>0:
            total_number_of_points = total_number_of_points + len(df_larsen)
            df_larsens.append(df_larsen)
    print('the total number of point is: ' + str(total_number_of_points))
    return df_larsens, file_within_date
def explore_icespeed():
    df = iceshelft.read_icespeed_cdl()
    lat_field_name = 'lat'
    lon_field_name = 'lon'
    print(df.head())
    df_larsen = df[(df[lat_field_name] < -62) & ((df[lat_field_name] > -74))
                   & ((df[lon_field_name] > 360- 67)) & ((df[lon_field_name] < 360 - 57))]
    print('total number of pirnts in the larsec C: ' + str(len(df_larsen)))
    return df_larsen
def plot_ice_speed():
    df_icespeed = explore_icespeed()
    # df_icespeed = pd.read_csv(settings.OUTPUT_ICESPEED_CSV)
    # df_icespeed = iceshelft.read_icespeed_cdl()

    vx = df_icespeed['VX'].values
    vy = df_icespeed['VY'].values
    v = np.sqrt(np.square(vx), np.square(vy))
    lat = df_icespeed['lat'].tolist()
    lon = df_icespeed['lon'].tolist()
    v = v.tolist()
    iceplot.plot_world_flat(lon, lat, v)
def convert_icespeed():
    iceshelft.read_icespeed_nc(10,store=True)


def explore_temp():
    dfs, files = iceshelft.read_temp_csv()
    dfs_within_date = []
    file_within_date = []
    for i, file in enumerate(files):
        date = file[-14:-7]
        if str(date).startswith('2015') | str(date).startswith('2016')| str(date).startswith('2017'):
            dfs_within_date.append(dfs[i])
            file_within_date.append(file)
    ##
    ## here we convert to plots

    # for i, file in enumerate(file_within_date):
    #     df = dfs_within_date[i]
    #     lat = df['lat'].values#[::100]
    #     lon = df['lon'].values#[::100]
    #     temp = df['temp'].values#[::100]
    #     tempdata = np.array([lat,lon,temp]).transpose()
    #     imagefile = file[:-4]+".jpg"
    #     iceplot.plot_world_flat(lat,lon,temp, file = imagefile)
    #     # iceplot.plot_ana(tempdata)

    ##
    lat_field_name = 'lat'
    lon_field_name = 'lon'
    total_number_of_points = 0
    # df_larsen_acc = pd.DataFrame(columns=['lat','lon','temp'])
    df_larsens = []
    for df in tqdm(dfs):
        # filter latitude
        # df_larsen = df[(df[lat_field_name] < 0)]
        df_larsen = df[(df[lat_field_name] < -62) & ((df[lat_field_name] > -74))
                       & ((df[lon_field_name] < -67)) & ((df[lon_field_name] < -57)) ]
        if len(df_larsen)>0:
            # print('found ' + str(len(df_larsen)))
            total_number_of_points = total_number_of_points + len(df_larsen)
            df_larsens.append(df_larsen)
            # df_larsen_acc = df_larsen_acc.append(df_larsen, sort=False)
    print('total number == ' + str(total_number_of_points))

    # we glue together both values
    # for df in df_larsens:
    #     data = df['temp'].values

    # print(df_larsen_acc.describe())
    # lat = dfex['lat'].values
    # lon = dfex['lon'].values
    # data = dfex['temp'].values
    # iceplot.plot_world_flat(lon,lat,data)
    return df_larsens, file_within_date

def main():
    # convert_icespeed()
    # iceshelft.read_temp_h5(store=True)
    # dfs, files = explore_temp()
    # f = open('dataframes.pckl', 'wb')
    # pickle.dump(dfs, f)
    # f.close()
    # f = open('files.pckl', 'wb')
    # pickle.dump(files, f)
    # f.close()

    plot_ice_speed()
    pass
if __name__ == '__main__':
    main()