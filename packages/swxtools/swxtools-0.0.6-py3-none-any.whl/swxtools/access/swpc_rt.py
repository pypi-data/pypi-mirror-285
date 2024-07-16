import numpy as np
import pandas as pd
import os
import json
import logging
from swxtools import download_tools
from swxtools.config import config
from swxtools.dataframe_tools import mark_gaps_in_dataframe


valid_durations = {
    '5-minute',
    '2-hour',
    '6-hour',
    '1-day',
    '3-day',
    '7-day'
}


def download_data(datatype='plasma',
                  duration='7-day',
                  primary_secondary='primary'):
    """
    Download real-time data from NOAA/SWPC in JSON format.

    Args:
        datatype ('plasma', 'mag', 'xrays', 'xray-flares', 'integral-protons',
                  'integral-electrons'): Type of data

    Returns:
        List of downloaded file(s).

    Remarks:
        To keep a record of older real-time data, the current date is appended
          to the local file's basename.
    """
    datestr = pd.Timestamp.utcnow().strftime("%Y-%m-%d")
    if datatype == 'plasma':
        baseurl = 'https://services.swpc.noaa.gov/products/solar-wind/'
        remote_file = f'plasma-{duration}.json'
        local_file = f'plasma-{duration}_{datestr}.json'
    elif datatype == 'mag':
        baseurl = 'https://services.swpc.noaa.gov/products/solar-wind/'
        remote_file = f'mag-{duration}.json'
        local_file = f'mag-{duration}_{datestr}.json'
    elif datatype == 'xrays':
        baseurl = f'https://services.swpc.noaa.gov/json/goes/{primary_secondary}/'
        remote_file = f'xrays-{duration}.json'
        local_file = f'xrays-{duration}_{primary_secondary}_{datestr}.json'
    elif datatype == 'xray-flares':
        baseurl = f'https://services.swpc.noaa.gov/json/goes/{primary_secondary}/'
        remote_file = f'xray-flares-{duration}.json'
        local_file = f'xray-flares-{duration}_{primary_secondary}_{datestr}.json'
    elif datatype == 'integral-protons':
        baseurl = f'https://services.swpc.noaa.gov/json/goes/{primary_secondary}/'
        remote_file = f'integral-protons-{duration}.json'
        local_file = f'integral-protons-{duration}_{primary_secondary}_{datestr}.json'
    elif datatype == 'integral-electrons':
        baseurl = f'https://services.swpc.noaa.gov/json/goes/{primary_secondary}/'
        remote_file = f'integral-electrons-{duration}.json'
        local_file = f'integral-electrons-{duration}_{primary_secondary}_{datestr}.json'
    else:
        logging.error(f"Unknown SWPC realtime data type: {datatype}")
        return []

    files_to_download = []
    local_data_dir = f"{config['local_source_data_path']}/swpc/rt/{datatype}"
    download_tools.ensure_data_dir(local_data_dir)
    local_filename = f"{local_data_dir}/{local_file}"
    url = f"{baseurl}/{remote_file}"
    files_to_download.append({'url': url, 'local_path': local_filename,
                              'max_age': pd.to_timedelta(1, 'min')})
    filenames = download_tools.download_files(files_to_download)

    return filenames


def json_to_dataframe(filename, mark_gaps=True):
    """
    Reads the real-time data timeseries into a Pandas DataFrame.

    Args:
        filename (string): Name of the .json file

    Returns:
        Pandas DataFrame containing the timeseries data.
    """
    basename = os.path.basename(filename)
    if 'plasma' in filename or 'mag' in basename:
        with open(filename) as fh:
            jsondata = json.load(fh)
        names = jsondata[0][1:]
        data = np.array(jsondata[1:])[:, 1:].astype(float)
        datetimes = pd.to_datetime(np.array(jsondata[1:])[:, 0])
        df = pd.DataFrame(data=data, columns=names, index=datetimes)
        df.replace(0.0, np.nan, inplace=True)
    elif 'xrays' in basename:
        # Real-time X-ray flux data from GOES XRS
        df = pd.read_json(filename)
        df.index = pd.to_datetime(df['time_tag'], utc=True)
        energies = ['0.05-0.4nm', '0.1-0.8nm']
        df_energies = pd.DataFrame()
        for energy in energies:
            df_energies[f'{energy}'] = df[df['energy'] == energy]['flux']
        df = df_energies
        df.replace(0.0, np.nan, inplace=True)
    elif 'xray-flares' in basename:
        # Real-time X-ray flare classifications based on GOES XRS data
        df = pd.read_json(filename)
        df.index = pd.to_datetime(df['time_tag'], utc=True)
    elif 'integral-protons' in basename:
        # Real-time integral proton flux from primary GOES satellite
        df = pd.read_json(filename)
        df.index = pd.to_datetime(df['time_tag'], utc=True)
    elif 'integral-electrons' in basename:
        # Real-time integral proton flux from primary GOES satellite
        df = pd.read_json(filename)
        df.index = pd.to_datetime(df['time_tag'], utc=True)
    else:
        logging.error("Unknown SWPC realtime data type: {datatype}")
        return None

    if mark_gaps:
        df = mark_gaps_in_dataframe(df)

    return df


if __name__ == '__main__':
    allowed_types = [
        'plasma',
        'mag',
        'xrays',
        'xray-flares',
        'integral-protons',
        'integral-electrons'
    ]

    for data_type in allowed_types:
        download_data(data_type)
