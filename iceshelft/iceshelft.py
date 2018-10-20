
from sputils import fileutils
import settings.settings as settings
import pandas as pd

def read_as_df(file):
    df = pd.read_csv(file, skiprows=9)
    return df

def read_all_ice_csv(sample_size):
    iceshelfl_files = fileutils.find_all_files(settings.ICE_HOME, ".csv")
    if not sample_size == 'all':
        iceshelfl_files = iceshelfl_files[0:sample_size]
    ice_dataframes = []
    for icefile in iceshelfl_files:
        icedf = read_as_df(icefile)
        ice_dataframes.append(icedf)

    return ice_dataframes

if __name__ == '__main__':
    read_all_ice_csv(100)