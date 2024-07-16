import pandas as pd
import requests
from swxtools import download_tools
from swxtools.config import config
import os
import logging
import numpy as np

local_source_data_path = config['local_source_data_path'] + '/solarsoft/ace_swepam_1m'
download_tools.ensure_data_dir(local_source_data_path)

def download(t0, t1):
    t_start = pd.to_datetime("20010811")
    t_end = pd.Timestamp.now().ceil('D')
    dates = pd.date_range(t0, t1, freq='1D')
    for t in dates:
        if t.tz_localize(None) < t_start:
            continue
        if t.tz_localize(None) > t_end:
            continue
        filename = f"{t.strftime('%Y%m%d')}_ace_swepam_1m.txt"
        local_path = local_source_data_path + '/' + filename
        age = t_end.tz_localize(None) - t.tz_localize(None)
        if (not os.path.isfile(local_path)) or age < pd.to_timedelta(5, 'D'):
            url = f'https://sohoftp.nascom.nasa.gov/sdb/goes/ace/daily/{filename}'
            logging.info(f"Downloading {url}")
            r = requests.get(url)
            if r.ok:
                with open(local_path, 'w') as fh:
                    fh.write(r.text)
            else:
                logging.error(f"Error opening {url}: {r.status_code} {r.reason}")
                continue


def filename_to_dataframe(filename):
    columns = [
        'year',
        'month',
        'day',
        'hhmm',
        'mjd',
        'seconds',
        'status',
        'proton_density',
        'bulk_speed',
        'ion_temperature'
    ]

    def parse_dates(row):
        timestr = f"{int(row.year):04d}-{int(row.month):02d}-{int(row.day):02d}T{int(row.hhmm):04d}"
        return pd.to_datetime(timestr, utc=True)

    df = pd.read_table(filename, sep=r'\s+', skiprows=18, names=columns)
    df.index = df.apply(parse_dates, axis=1)
    df.drop(['year', 'month', 'day', 'hhmm', 'mjd', 'seconds'], axis=1, inplace=True)
    df.replace({-9999.9: np.nan, -1.00e+05: np.nan}, inplace=True)
    return df


def to_dataframe(t0, t1):
    download(t0, t1)
    dates = pd.date_range(t0, t1, freq='1D')
    dfs = []
    for t in dates:
        filename = f"{t.strftime('%Y%m%d')}_ace_swepam_1m.txt"
        local_path = local_source_data_path + '/' + filename
        if os.path.isfile(local_path):
            dfs.append(filename_to_dataframe(local_path))
    return pd.concat(dfs, axis=0).sort_index()