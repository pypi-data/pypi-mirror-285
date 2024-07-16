import pandas as pd
import os
import numpy as np
import requests
import logging
from swxtools import download_tools
from swxtools.config import config

# See https://www.nasa.gov/solar-cycle-progression-and-forecast/archived-forecast/

# base_url = 'https://www.nasa.gov/sites/default/files/atoms/files/'
local_data_dir = (f'{config["local_source_data_path"]}/msfc_solar_cycle')
download_tools.ensure_data_dir(local_data_dir)

years = np.arange(1999, pd.Timestamp.utcnow().year+1)
months = ['jan', 'feb', 'mar',
          'apr', 'may', 'jun',
          'jul', 'aug', 'sep',
          'oct', 'nov', 'dec']

types = ['f10_prd', 'f10_prd75', 'ssn_prd']


def download():
    for year in years:
        for imonth, month in enumerate(months):
            date = pd.to_datetime(f"{month} {year}")
            for type in types:

                # Special cases for older / newer filenames
                if type == 'f10_prd' and date < pd.to_datetime("May 2019"):
                    filename_ext = f'{month}{year}f10.txt'
                if type == 'f10_prd75' and date < pd.to_datetime("May 2019"):
                    filename_ext = f'{month}{year}table_5.txt'
                if type == 'ssn_prd' and date < pd.to_datetime("May 2019"):
                    filename_ext = f'{month}{year}ssn.txt'
                if year == 2004 and month == 'jul':
                    month = 'july'
                else:
                    filename_ext = f'{month}{year}{type}.txt'

                filename = f'{month}{year}{type}.txt'

                if year <= 2023 and imonth < 6:
                    base_url = 'https://www.nasa.gov/wp-content/uploads/2019/04/'
                elif year == 2023 and imonth >= 6 and imonth <= 10:
                    base_url = f'https://www.nasa.gov/wp-content/uploads/2024/01/'
                    filename_ext = filename_ext.replace('_', '-')
                elif year >= 2023:
                    base_url = f'https://www.nasa.gov/wp-content/uploads/{year}/{imonth+1:02d}/'
                    filename_ext = filename_ext.replace('_', '-')

                url = f'{base_url}{filename_ext}'
                print(url)
                local_filename = f'{local_data_dir}/{filename}'
                if os.path.isfile(local_filename):
                    # logging.info(f"Already exists: {local_filename}")
                    continue
                r = requests.get(url)
                if r.ok:
                    logging.info(f"Writing: {local_filename}")
                    with open(local_filename, 'w') as fh:
                        fh.write(r.text)
                else:
                    logging.info(f"Not found: {url}")


def msfc_f10_dataframe(filename):
    columns = ['year',
               'month',
               'f10_95',
               'f10_50',
               'f10_5',
               'Ap_95',
               'Ap_50',
               'Ap_5']

    df95 = pd.read_table(
        filename,
        sep=r'\s+',
        skiprows=7,
        names=columns
    )

    filename = filename.replace('prd.txt', 'prd75.txt')

    columns = ['year',
               'month',
               'f10_75',
               'f10_50',
               'f10_25',
               'Ap_95',
               'Ap_50',
               'Ap_5']

    if os.path.isfile(filename):
        df75 = pd.read_table(
            filename,
            sep=r'\s+',
            skiprows=7,
            names=columns
        )
        df = pd.concat([df95, df75[['f10_75', 'f10_25']]], axis=1)
    else:
        df = df95
        df['f10_75'] = np.nan
        df['f10_25'] = np.nan
    df.index = pd.to_datetime(
        df['month'] + " " + df['year'].astype(int).astype(str)
    )
    return df


def msfc_ssn_dataframe(filename):
    columns = ['year',
               'month',
               'sunspots_95',
               'sunspots_50',
               'sunspots_5',
               'Ap_95',
               'Ap_50',
               'Ap_5']

    df = pd.read_table(
        filename,
        sep=r'\s+',
        skiprows=7,
        names=columns
    )
    df.index = pd.to_datetime(
        df['month'] + " " + df['year'].astype(int).astype(str),
        format='%b %Y'
    )
    return df


def to_dataframe(type):
    dfs = []
    for year in years:
        for month in months:
            if type == 'ssn':
                filename = f'{local_data_dir}/{month}{year}{type}_prd.txt'
                if os.path.exists(filename):
                    df = msfc_ssn_dataframe(filename)
                    df['time'] = df.index.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    timetag_issue = pd.to_datetime(f'{month} {year}', utc=True)
                    df['timetag_issue'] = timetag_issue.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    # Correct for SILSO v1 vs v2 scale factor difference of 0.6
                    if timetag_issue < pd.to_datetime("Sep 2015", utc=True):
                        df['sunspots_5'] = df['sunspots_5']/0.6
                        df['sunspots_50'] = df['sunspots_50']/0.6
                        df['sunspots_95'] = df['sunspots_95']/0.6
                    dfs.append(df)
            elif type == 'f10':
                filename = f'{local_data_dir}/{month}{year}{type}_prd.txt'
                print(filename)
                if os.path.exists(filename):
                    df = msfc_f10_dataframe(filename)
                    df['time'] = df.index.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    timetag_issue = pd.to_datetime(f'{month} {year}', utc=True)
                    df['timetag_issue'] = timetag_issue.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    dfs.append(df)

    return pd.concat(dfs, axis=0).sort_index()