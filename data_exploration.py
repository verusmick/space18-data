import iceshelft
from tqdm import tqdm
import os.path as path
import pickle # pickle rick!!!
import pandas as pd
import settings.settings as settings


def explore_anaice():
    if not path.isfile('dataframes.pckl'):
        print('crateing the dataframe')
        dfs = iceshelft.read_ice_csv(3000)
        f = open('dataframes.pckl', 'wb')
        pickle.dump(dfs, f)
        f.close()
    else:
        print('pickle found loading....')
        f = open('dataframes.pckl', 'rb')
        dfs = pickle.load(f)
        f.close()
        print('loading done')
    print('numbers fo data frames: ')
    print(len(dfs))

    fields = list(dfs[0])
    lat_field_name = fields[1]
    lon_field_name = fields[2]

    total_number_of_points = 0
    for df in tqdm(dfs):
        # filter latitude
        # df_larsen = df[(df[lat_field_name] < 0)]
        df_larsen = df[(df[lat_field_name] < -62) & ((df[lat_field_name] > -74))
                       & ((df[lon_field_name] > 360-67)) & ((df[lon_field_name] > 360-57)) ]
        if len(df_larsen)>0:
            total_number_of_points = total_number_of_points + len(df_larsen)
    print('the total number of point is: ' + str(total_number_of_points))
    return df_larsen
def explore_icespeed():
    df = pd.read_csv(settings.OUTPUT_ICESPEED_CSV)
    lat_field_name = 'lat'
    lon_field_name = 'lon'
    df_larsen = df[(df[lat_field_name] < -62) & ((df[lat_field_name] > -74))
                   & ((df[lon_field_name] <- 67)) & ((df[lon_field_name] < - 57))]
    print('total number of pirnts in the larsec C: ' + str(len(df_larsen)))
    return df_larsen
def main():
    explore_icespeed()

if __name__ == '__main__':
    main()