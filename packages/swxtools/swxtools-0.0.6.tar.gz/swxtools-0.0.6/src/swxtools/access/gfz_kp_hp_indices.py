import os
import requests
import pandas as pd
from swxtools.config import config
from swxtools import download_tools

def dataframe_from_gfz_api(start, stop, index_type):
    valid_indices = {'Kp',
                     'ap',
                     'Ap',
                     'Cp',
                     'C9',
                     'Hp30',
                     'Hp60',
                     'ap30',
                     'ap60',
                     'SN',
                     'Fobs',
                     'Fadj'}

    if not index_type in valid_indices:
        raise ValueError(f'Provided index {index_type} is not in set of valid indices: {", ".join(valid_indices)}')

    tstartstr = pd.to_datetime(start).strftime("%Y-%m-%dT%H:%M:%SZ")
    tstopstr = pd.to_datetime(stop).strftime("%Y-%m-%dT%H:%M:%SZ")
    url = f"https://kp.gfz-potsdam.de/app/json/?start={tstartstr}&end={tstopstr}&index={index_type}"
    r = requests.get(url)
    if not r.ok:
        raise ValueError(f"Error when accessing {url}")

    data = r.json()
    del data['meta']
    df = pd.DataFrame(data)
    df.index = pd.to_datetime(df['datetime'], utc=True)
    df = df.drop('datetime', axis=1)
    return df


def download_data(index_type='Kp'):
    """
    Download Kp and Hpo data
    """
    # Setup local dir
    base_path = config['local_source_data_path']
    local_data_dir = f"{base_path}/gfz_potsdam/{index_type}"
    download_tools.ensure_data_dir(local_data_dir)

    # Construct the list of files to download and where to put them
    baseurl = 'http://www-app3.gfz-potsdam.de/kp_index'
    if index_type == 'Hp30':
        urls = [f'{baseurl}/Hp30_ap30_since_1995.txt',
                f'{baseurl}/Hp30_ap30_nowcast.txt']
    elif index_type == 'Hp60':
        urls = [f'{baseurl}/Hp60_ap60_since_1995.txt',
                f'{baseurl}/Hp60_ap60_nowcast.txt']
    elif index_type == 'Kp':
        urls = [f'{baseurl}/Kp_ap_since_1932.txt',
                f'{baseurl}/Kp_ap_nowcast.txt']
    elif index_type == 'Ap':
        urls = [f'{baseurl}/Kp_ap_Ap_SN_F107_since_1932.txt',
                f'{baseurl}/Kp_ap_Ap_SN_F107_nowcast.txt']

    files_to_download = []
    for url in urls:
        filename = os.path.basename(url)
        local_filename = f"{local_data_dir}/{filename}"
        url = f"{baseurl}/{filename}"

        # Determine max download frequency:
        if 'nowcast' in url:
            max_age = pd.to_timedelta(5, 'min')
        else:
            max_age = pd.to_timedelta(1, 'day')

        files_to_download.append({'url': url,
                                  'local_path': local_filename,
                                  'max_age': max_age})

    filenames = download_tools.download_files(files_to_download)
    return filenames


def txt_to_dataframe(filename):
    column_names_base = ['year', 'month', 'day', 'hour', 'hour_mid',
                         'days_since_1932', 'days_since_1932_mid']
    column_names = column_names_base
    if "Hp30_ap30" in filename:
        column_names.extend(['Hp30', 'ap30', 'D'])
    elif "Hp60_ap60" in filename:
        column_names.extend(['Hp60', 'ap60', 'D'])
    elif "Kp_ap_Ap_SN_F107" in filename:
        column_names = ['year', 'month', 'day',
                        'days_since_1932', 'days_since_1932_mid',
                        'Bsr', 'dB',
                        'Kp1', 'Kp2', 'Kp3', 'Kp4', 'Kp5', 'Kp6', 'Kp7', 'Kp8',
                        'ap1', 'ap2', 'ap3', 'ap4', 'ap5', 'ap6', 'ap7', 'ap8',
                        'Ap',
                        'SN', 'F10.7obs', 'F10.7adj', 'D']
    elif "Kp_ap" in filename:
        column_names.extend(['Kp', 'ap', 'D'])

    df = pd.read_table(filename, sep=r'\s+', comment='#',
                       names=column_names, index_col=False, na_values=-1)

    if 'hour' not in df.columns:
        df['hour'] = 0.0
    df.index = pd.to_datetime(
        {'year': df['year'],
         'month': df['month'],
         'day': df['day'],
         'hour': df['hour']}
     )
    df['filename'] = os.path.basename(filename)
    return df


def to_dataframe(index_type='Kp', merge=True, timestamp='start'):
    filenames = download_data(index_type)
    dfs = []
    for filename in filenames:
        dfs.append(txt_to_dataframe((filename)))
    if merge:
        df_kpap = pd.concat(dfs, axis=0).sort_index().dropna()
        duplicated = df_kpap.index.duplicated(keep=False)
        nowcast = df_kpap['filename'].str.contains("nowcast")
        df_kpap = df_kpap[~duplicated | (duplicated & ~nowcast)]
        if timestamp == 'start':
            pass
        elif timestamp == 'mid':
            mid_offset = {'Kp': pd.to_timedelta(1.5, 'H'),
                          'Hp30': pd.to_timedelta(15, 'M'),
                          'Hp60': pd.to_timedelta(30, 'M'),
                          'Ap': pd.to_timedelta(12, 'H')}
            df_kpap.index = df_kpap.index + mid_offset[index_type]
        else:
            raise ValueError(f"Timestamp should be 'start' or 'mid', "
                             f"received '{timestamp}'.")
        return df_kpap
    else:
        return dfs
