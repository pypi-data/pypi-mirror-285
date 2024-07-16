import numpy as np
import pandas as pd
from swxtools.config import config
from swxtools import download_tools

local_dir = config['local_source_data_path'] + "/silso"
locations = {}
locations['daily'] = {
    'total': 'SN_d_tot_V2.0.txt',
    'current': 'EISN/EISN_current.txt',
    'hemispheric': 'SN_d_hem_V2.0.txt'
}
locations['monthly'] = {
    'total': 'SN_m_tot_V2.0.txt',
    'hemispheric': 'SN_m_hem_V2.0.txt'
}
locations['13m_smoothed'] = {
    'total': 'SN_ms_tot_V2.0.txt',
    'hemispheric': 'SN_ms_hem_V2.0.txt'
}


def download(cadence_req='all', type_req='all'):
    local_dir = config['local_source_data_path'] + "/silso"
    local_dir_eisn = config['local_source_data_path'] + "/silso/EISN"
    download_tools.ensure_data_dir(local_dir)
    download_tools.ensure_data_dir(local_dir_eisn)
    files_to_download = []
    for cadence in locations:
        if cadence_req == cadence or cadence_req == 'all':
            for type in locations[cadence]:
                if type_req == type or type_req == 'all':
                    files_to_download.append({
                        'url': f'https://www.sidc.be/silso/DATA/{locations[cadence][type]}',
                        'local_path': f'{local_dir}/{locations[cadence][type]}',
                        'max_age': pd.to_timedelta(1, 'D')
                    })

    downloaded_files = download_tools.download_files(files_to_download)
    return downloaded_files


def to_dataframe(cadence='daily', type='total', convert_column_names=True):
    filename = f'{local_dir}/{locations[cadence][type]}'
    return txt_to_dataframe(filename, convert_column_names=convert_column_names)


def txt_to_dataframe(filename, convert_column_names=True):
    print(filename)
    if 'SN_d_tot_V2.0' in filename:
        columns = [
            "Year",
            "Month",
            "Day",
            "Decimal date",
            "Daily sunspot number",
            "Standard deviation",
            "Number of observations",
            "Star",
        ]
    elif "EISN_current" in filename:
        columns = [
            "Year",
            "Month",
            "Day",
            "Decimal date",
            "Estimated Sunspot Number",
            "Estimated Standard Deviation",
            "Number of Stations calculated",
            "Number of Stations available ",
        ]
    elif "SN_d_hem_V2.0" in filename:
        columns = [
            "Year",
            "Month",
            "Day",
            "Date in fraction of year",
            "Daily total sunspot number",
            "Daily North sunspot number",
            "Daily South sunspot number",
            "Standard deviation of raw daily total sunspot data",
            "Standard deviation of raw daily North sunspot data",
            "Standard deviation of raw daily South sunspot data",
            "Number of observations in daily total sunspot number",
            "Number of observations in daily North sunspot number (not determined yet: -1)",
            "Number of observations in daily South sunspot number (not determined yet: -1)",
            "Definitive/provisional marker"
        ]
    elif "SN_m_tot_V2.0" in filename:
        columns = [
            "Year",
            "Month",
            "Decimal date",
            "Monthly total sunspot number",
            "Standard deviation",
            "Number of observations",
            "Definitive/provisional indicator"
        ]
    elif "SN_m_hem_V2.0" in filename:
        columns = [
            "Year",
            "Month",
            "Decimal date",
            "Monthly total sunspot number",
            "Monthly north sunspot number",
            "Monthly south sunspot number",
            "Standard deviation (Total)",
            "Standard deviation (North)",
            "Standard deviation (South)",
            "Number of observations (Total)",
            "Number of observations (North)",
            "Number of observations (South)",
            "Definitive/provisional indicator"
        ]
    elif 'SN_ms_tot_V2.0' in filename:
        columns = [
            "Year",
            "Month",
            "Decimal date",
            "Smoothed total sunspot number",
            "Standard deviation",
            "Number of observations",
            "Definitive/provisional indicator",
        ]
    elif 'SN_ms_hem_V2.0' in filename:
        columns = [
            "Year",
            "Month",
            "Decimal date",
            "Monthly smoothed total sunspot number",
            "Monthly smoothed North sunspot number",
            "Monthly smoothed South sunspot number",
            "Standard deviation (Total)",
            "Standard deviation (North)",
            "Standard deviation (South)",
            "Number of observations (Total)",
            "Number of observations (North)",
            "Number of observations (South)",
            "Definitive/provisional indicator"
        ]


    if '_d_' in filename or 'EISN_current' in filename:
        df = pd.read_csv(filename, sep=r'\s+', names=columns,
                         parse_dates={'DateTime': ['Year', 'Month', 'Day']},
                         index_col='DateTime').replace(-1, np.nan)
    elif '_m_' in filename or '_ms_' in filename:
        df = pd.read_csv(filename, sep=r'\s+', names=columns,
                         parse_dates={'DateTime': ['Year', 'Month']},
                         index_col='DateTime').replace(-1, np.nan)

    if convert_column_names:
        df.rename({'Daily sunspot number': 'sunspot_number',
                   'Estimated Sunspot Number': 'sunspot_number',
                   'Estimated Standard Deviation': 'standard_deviation',
                   'Standard deviation': 'standard_deviation',
                   'Daily total sunspot number': 'sunspot_number',
                   'Daily North sunspot number': 'sunspot_number_north',
                   'Daily South sunspot number': 'sunspot_number_south',
                   'Monthly north sunspot number': 'sunspot_number_north',
                   'Monthly south sunspot number': 'sunspot_number_south',
                   'Monthly total sunspot number': 'sunspot_number',
                   'Smoothed total sunspot number': 'sunspot_number',
                   'Monthly smoothed total sunspot number': 'sunspot_number',
                   'Monthly smoothed North sunspot number': 'sunspot_number_north',
                   'Monthly smoothed South sunspot number': 'sunspot_number_south',
                   'Standard deviation of raw daily total sunspot data': 'standard_deviation',
                   'Standard deviation (Total)': 'standard_deviation'},
                  axis=1, inplace=True)
    return df
