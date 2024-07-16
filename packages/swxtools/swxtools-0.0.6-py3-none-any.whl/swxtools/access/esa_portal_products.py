import os
import requests
import logging
import pandas as pd
import xarray as xr
import numpy as np
from swxtools.access.esa_session_cookies import get_auth_cookie


def download_enlil_file(username, password, filename, local_filename):
    session_established, auth_cookie = get_auth_cookie(
        username,
        password
    )
    base_url = ('https://esa.spaceweather.api.metoffice.gov.uk/' +
                'models/enlil/files/')
    if session_established:
        url = base_url + filename
        logging.info(f"Session with ESA portal established, accessing {url}")
        response = requests.get(
            url,
            cookies={'iPlanetDirectoryPro': auth_cookie}
        )
        if response.ok:
            data = response.content
            with open(local_filename, 'wb') as fh:
                fh.write(data)
            logging.info(f"{filename} was retrieved from ESA portal")
            return local_filename
        else:
            logging.error("Request failed. "
                          f"{response.status_code}, {response.reason}")
    else:
        logging.error("Unable to establish session with ESA portal")
    return None


def download_enlil_files_timerange(username, password, local_path, t0, t1):
    files_downloaded = []
    date_range = pd.date_range(t0, t1, freq='2H')

    for date in date_range:
        date_str = date.strftime("%Y-%m-%dT%HZ")
        filename = f"{date_str}.evo.Earth.nc"
        local_filename = f'{local_path}{filename}'
        if os.path.isfile(local_filename):
            print(f"file {filename} already exists locally")
        else:
            new_file = download_enlil_file(
                username,
                password,
                filename,
                local_filename
            )
            if new_file:
                files_downloaded.append(new_file)
    return files_downloaded


def enlilfile_to_dataframe(enlilfile, reftime):
    timefmt = "%Y-%m-%dT%H:%M:%SZ"
    ds = xr.open_dataset(enlilfile)
    df = ds.to_dataframe()
    df.index = reftime + pd.to_timedelta(df['TIME'], 's')
    df = df.resample('30min').mean()
    df.index = df.index + pd.to_timedelta('15min')
    df['density'] = 1e-6 * df['D'] / (1.67262e-27)  # kg/m3 to protons/cm3
    df['speed'] = 1e-3 * np.sqrt(df['V1']**2 + df['V2']**2 + df['V3']**2)
    df['pressure'] = 1.6726e-6 * df['density'] * df['speed']**2
    df['bt'] = 1e9 * np.sqrt(df['B1']**2 + df['B2']**2 + df['B3']**2)
    df.rename({'T': 'temperature'}, axis=1, inplace=True)
    df['time'] = df.index.strftime(timefmt)
    df['timetag_issue'] = reftime.strftime(timefmt)
    return df
