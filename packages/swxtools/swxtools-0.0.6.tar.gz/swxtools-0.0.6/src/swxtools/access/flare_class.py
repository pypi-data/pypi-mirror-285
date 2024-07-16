import os
import requests
import pandas as pd
import xarray as xr
from swxtools.config import config
from swxtools import download_tools


def get_latest_flare_class_swpc():
    # Get latest data
    url_latest = ('https://services.swpc.noaa.gov/json/goes/primary/' +
                  'xray-flares-7-day.json')
    df_latest = pd.read_json(url_latest)
    df_latest.index = pd.to_datetime(df_latest['max_time'], utc=True)
    df_latest = df_latest.rename({'max_class': 'flare_class',
                                  'max_xrlong': 'xrsb_flux'}, axis=1)
    df_latest = df_latest[['flare_class', 'xrsb_flux']]
    return df_latest


def get_archived_flare_class_ngdc():
    base_path = config['local_source_data_path']

    # Get archived data
    # GOES 13-18 flare summary
    goes13_15_url_prefix = ('https://www.ncei.noaa.gov/data/' +
                            'goes-space-environment-monitor/' +
                            'access/science/xrs')
    goes16_18_url_prefix = ('https://data.ngdc.noaa.gov/platforms/' +
                            'solar-space-observing-satellites/goes')
    urls = [
        f'{goes13_15_url_prefix}/goes13/xrsf-l2-flsum_science/' +
        'sci_xrsf-l2-flsum_g13_s20130601_e20171214_v1-0-0.nc',
        f'{goes13_15_url_prefix}/goes14/xrsf-l2-flsum_science/' +
        'sci_xrsf-l2-flsum_g14_s20090901_e20200304_v1-0-0.nc',
        f'{goes13_15_url_prefix}/goes15/xrsf-l2-flsum_science/' +
        'sci_xrsf-l2-flsum_g15_s20100331_e20200304_v1-0-0.nc',
        f'{goes16_18_url_prefix}/goes16/l2/data/xrsf-l2-flsum_science/' +
        'sci_xrsf-l2-flsum_g16_s20170209_e20240511_v2-2-0.nc',
        f'{goes16_18_url_prefix}/goes17/l2/data/xrsf-l2-flsum_science/' +
        'sci_xrsf-l2-flsum_g17_s20180601_e20230110_v2-2-0.nc',
        f'{goes16_18_url_prefix}/goes18/l2/data/xrsf-l2-flsum_science/' +
        'sci_xrsf-l2-flsum_g18_s20220905_e20240511_v2-2-0.nc',
    ]

    dfs = []
    for url in urls:
        local_path = f"{base_path}/xrsf_l2_flsum/"
        download_tools.ensure_data_dir(local_path)
        filename = f"{local_path}/{os.path.basename(url)}"
        if not os.path.isfile(filename):
            r = requests.get(url)
            if r.ok:
                with open(filename, 'wb') as fh:
                    fh.write(r.content)
            else:
                print("Problem downloading file: ", filename)
        xrdata = xr.open_dataset(filename)
        df = xrdata.to_dataframe()
        df.index = df.index.tz_localize('utc')
        dfs.append(df)

    df = pd.concat(dfs)
    df = df[df['status'] == 'EVENT_PEAK']
    return df


def get_combined_flare_class():
    df_latest = get_latest_flare_class_swpc()
    df_archived = get_archived_flare_class_ngdc()
    df = pd.concat([df_archived, df_latest])
    df = df[~df.index.duplicated(keep='first')].sort_index()
    return df
