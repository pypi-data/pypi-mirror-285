import pandas as pd
import numpy as np
from swxtools.config import config
from swxtools.download_tools import ensure_data_dir, download_file_http

dataset_filenames = [
    'orbit-density-ds01-objects-used.txt',
    'orbit-density-ds02-density-ratios.txt',
    'orbit-density-ds03-density-values.txt',
    'orbit-density-ds04-binave-ratio-plots.pdf',
    'orbit-density-ds05-ratio-plots.pdf',
    'orbit-density-ds06-density-plots.pdf',
]


def download():
    local_source_data_path = (
        config['local_source_data_path'] +
        "/emmert2021_tle_density/"
    )
    ensure_data_dir(local_source_data_path)

    files = [
        '2021JA029455-sup-0002-Data+Set+SI-S01.txt',
        '2021JA029455-sup-0003-Data+Set+SI-S02.txt',
        '2021JA029455-sup-0004-Data+Set+SI-S03.txt'
    ]

    base_url = ('https://agupubs.onlinelibrary.wiley.com/' +
                'action/downloadSupplement?doi=10.1029%2F2021JA029455')

    for file in files:
        url = f'{base_url}&file={file}'
        local_filename = local_source_data_path + file
        download_file_http(url, local_filename)


def to_dataframe(sigma=True, log10=True, ratios=False):
    if ratios:
        filename = (
            config['local_source_data_path'] +
            '/emmert2021_tle_density/orbit-density-ds02-density-ratios.txt'
        )
    else:
        filename = (
            config['local_source_data_path'] +
            '/emmert2021_tle_density/orbit-density-ds03-density-values.txt'
        )
    df = pd.read_table(
        filename,
        sep=r'\s+',
        na_values=['-9999.000000'])
    df['date'] = (
        pd.to_datetime(df['year'], format='%Y', utc=True) +
        pd.to_timedelta(df['day']-1, 'D')
    )
    df.replace(-999.0, np.nan, inplace=True)
    df.index = df['date']
    df.drop(['year', 'day', 'date'], axis=1, inplace=True)
    if sigma:
        pass
    else:
        # Get rid of sigma columns
        df.drop([column for column in df.columns if 'sigma' in column],
                axis=1, inplace=True)
    if log10 or ratios:
        return df
    else:
        # Convert log10 data to linear scaled data
        df = 10**df
        df.rename(
            {column: column.replace("log10", "") for column in df.columns},
            axis=1,
            inplace=True
        )
    return df
