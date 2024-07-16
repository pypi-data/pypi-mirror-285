import os
import pandas as pd
import numpy as np
from swxtools import download_tools
from swxtools.config import config

local_data_dir = (f'{config["local_source_data_path"]}/penticton')

base_url = ('ftp://ftp.seismo.nrcan.gc.ca/spaceweather/'
            'solar_flux/daily_flux_values')
username = "anonymous"
password = "eelco.doornbos@knmi.nl"

urls_max_ages = {
    f'{base_url}/fluxtable.txt': pd.to_timedelta(1, 'D'),
    f'{base_url}/F107_1947_1996.txt': pd.to_timedelta(1000, 'D'),
    f'{base_url}/F107_1996_2007.txt': pd.to_timedelta(1000, 'D')
}


def correct_flux_file(path):
    # replace space with comma on line 17860 of the flux archive file,
    # otherwise parsing will run into problems
    with open(f'{path}/F107_1947_1996.txt', 'r') as fh:
        lines = fh.readlines()
    lines[17860] = lines[17860][0:55] + ',' + lines[17860][56:]
    with open(f'{path}/F107_1947_1996.txt', 'w') as fh:
        fh.writelines(lines)


def download():
    download_tools.ensure_data_dir(local_data_dir)
    files_to_download = []
    for url in urls_max_ages.keys():
        filename = os.path.basename(url)
        local_filename = f'{local_data_dir}/{filename}'
        files_to_download.append({
            'url': url,
            'local_path': local_filename,
            'max_age': urls_max_ages[url]
        })

    # Download the files if they are not yet available locally
    ftp_conn = download_tools.setup_ftp_conn(base_url, username, password)
    try:
        filenames = download_tools.download_files(files_to_download, ftp_conn=ftp_conn)
    except Exception as e:
        logging.info(f"Error downloading files: {e}")
    ftp_conn.quit()
    correct_flux_file(local_data_dir)
    return filenames


def list_outliers(df_in, field='f10_7', multiplier=3, threshold=20):
    '''Provide list of dates of outliers that differ from the median over a
    5-day window by a threshold, as well as a multiplier times the standard
    deviation over an 81-day window'''
    df = df_in.copy()
    df['5d_median'] = df[field].rolling('5D').median()
    df['81d_std'] = df[field].rolling('81D').std()
    df['5d_diff'] = df[field] - df['5d_median']
    outlier_dates = df.index[(df['5d_diff'] > threshold) &
                             (df['5d_diff'] > multiplier*df['81d_std'])]
    return outlier_dates


def to_dataframe(noontime=True, drop_outliers=True,
                 merge=True, timestamp='start'):
    columns = {
        'F107_1947_1996.txt':
            ['jd', 'cr', 'year', 'month', 'day',
             'fluxobs', 'fluxadj', 'fluxursi'],
        'F107_1996_2007.txt':
            ['jd', 'cr', 'year', 'month', 'day', 'ut',
             'fluxobs', 'fluxadj', 'fluxursi'],
        'fluxtable.txt':
            ["fluxdate", "ut", "jd", "cr",
             "fluxobs", "fluxadj", "fluxursi"],
    }

    skiprows = {
        'F107_1947_1996.txt': 3,
        'F107_1996_2007.txt': 3,
        'fluxtable.txt': 2,
    }
    delimeter = {
        'F107_1947_1996.txt': ',',
        'F107_1996_2007.txt': r'\s+',
        'fluxtable.txt': r'\s+',
    }
    sep = {
        'F107_1947_1996.txt': ',',
        'F107_1996_2007.txt': None,
        'fluxtable.txt': None,
    }
    usecols = {
        'F107_1996_2007.txt': list(range(0, 9)),
        'fluxtable.txt': list(range(0, 7)),
    }
    dfs = []
    for filename in columns.keys():
        print(filename)
        if sep[filename] is not None:
            df = pd.read_table(f'{local_data_dir}/{filename}',
                               sep=sep[filename],
                               skiprows=skiprows[filename],
                               names=columns[filename])
        else:
            df = pd.read_table(f'{local_data_dir}/{filename}',
                               sep=delimeter[filename],
                               skiprows=skiprows[filename],
                               names=columns[filename],
                               usecols=usecols[filename])

        # Set the index to the date
        dates = pd.to_datetime(df['jd'], unit='D', origin='julian')
        df['time'] = dates.dt.strftime("%Y-%m-%d")
        df.index = pd.to_datetime(df['time'], utc=True)
        if timestamp == 'start':
            pass
        elif timestamp == 'mid':
            df.index = df.index + pd.to_timedelta(12, 'H')

        df.sort_index(inplace=True)

        # Set the observed flux to the same name
        df.rename({'fluxobs': 'f10_7'}, axis=1, inplace=True)

        # Set zeros to NaN
        df['f10_7'] = df['f10_7'].replace(0.0, np.nan)

        # Drop outliers
        if drop_outliers:
            outlier_dates = list_outliers(df)
            df.drop(outlier_dates, inplace=True)

        if noontime:
            # Noontime is 20 local time
            if 'ut' in df.columns:
                df = df[(df['ut'].astype(str).str[:2] == '20') |
                        (df['ut'].astype(str).str[:2] == '19')]

        df['f10_7'] = df['f10_7'].replace(0.0, np.nan)
        df['fluxadj'] = df['fluxadj'].replace(0.0, np.nan)
        df['filename'] = filename
        dfs.append(df)

    if merge:
        # Concatenate, sort and drop duplicate entries from mulitple files
        df = pd.concat(dfs).sort_index()
        # Also drop multiple measurements (even from the same file)
        df = df[~df.index.duplicated(keep='last')]
        return df
    else:
        return dfs
