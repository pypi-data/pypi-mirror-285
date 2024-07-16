import os
import io
import re
import requests
import time
import numpy as np
import pandas as pd
import netCDF4
import logging
from bs4 import BeautifulSoup
from swxtools import download_tools
from swxtools.config import config


def get_urls_from_ngdc_page(base_url, match):
    expr = re.compile(match)
    hrefs = []
    retries = 3
    for retry in range(retries):
        r = requests.get(base_url)
        print(f"Access of {base_url}, status code: {r.status_code}")
        if r.status_code == 200:
            break  # break out of the loop
        elif r.status_code == 404:
            return []
        elif r.status_code == 429:
            time.sleep(3)
        else:
            return []
    soup = BeautifulSoup(r.text, 'html.parser')
    table_rows = soup.find_all('table')[1].find_all('tr')
    for row in table_rows:
        link = row.find('a')
        if link is None:
            continue
        href = link.get('href')
        if expr.match(href):
            hrefs.append(f'{base_url}{href}')
    return hrefs


def update_list_of_goes_avg_nc_files(filename):
    base_url = 'https://www.ncei.noaa.gov/data/goes-space-environment-monitor/access/avg/'
    with open(filename, 'w') as fh:
        for year in range(1974, 2022):
            for month in range(1, 13):
                url = f"{base_url}{year:04d}/{month:02d}/"
                new_urls = get_urls_from_ngdc_page(url, 'goes\d\d')
                for new_url in new_urls:
                    nc_urls = get_urls_from_ngdc_page(
                        f'{new_url}netcdf/', '.*\.nc'
                    )
                    for nc_url in nc_urls:
                        fh.write(f'{nc_url}\n')


def goes_xrs_urls():
    goes_urls = {}
    # GOES 3-12
    goes_xrs_url_list_file = (f"{config['local_source_data_path']}/" +
                              "goes_avg_nc_files.txt")
    if not os.path.isfile(goes_xrs_url_list_file):
        update_list_of_goes_avg_nc_files(goes_xrs_url_list_file)
    with open(goes_xrs_url_list_file,  'r') as fh:
        urls = fh.readlines()
    for goesnum in range(3, 13):
        goesnumstr = f"g{goesnum:02d}"
        goes_urls[goesnum] = [url.strip() for url in urls
                              if goesnumstr in url and
                              'xrs_1m_' in url and
                              'xrs_1m_3s' not in url]

    # GOES 13-17 science data files
    xrs_url = ("https://www.ncei.noaa.gov/"
               "data/goes-space-environment-monitor/access/science/xrs")
    new_xrs_url = ("https://data.ngdc.noaa.gov/"
                   "platforms/solar-space-observing-satellites/goes/")
    goes_urls[13] = [f"{xrs_url}/goes13/xrsf-l2-avg1m_science/"
                     "sci_xrsf-l2-avg1m_g13_s20130601_e20171214_v1-0-0.nc"]
    goes_urls[14] = [f"{xrs_url}/goes14/xrsf-l2-avg1m_science/"
                     "sci_xrsf-l2-avg1m_g14_s20090901_e20200304_v1-0-0.nc"]
    goes_urls[15] = [f"{xrs_url}/goes15/xrsf-l2-avg1m_science/"
                     "sci_xrsf-l2-avg1m_g15_s20100331_e20200304_v1-0-0.nc"]
    goes_urls[16] = []
    goes_urls[17] = [f"{new_xrs_url}"
                     "goes17/l2/data/xrsf-l2-avg1m_science/"
                     "sci_xrsf-l2-avg1m_g17_s20180601_e20230110_v2-2-0.nc"]
    goes_urls[18] = []
    # Active satellites
    goes16_years = [2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024]
    goes18_years = [2022, 2023, 2024]
    for year in goes16_years:
        goes_urls[16].append((f"{new_xrs_url}"
                              "goes16/l2/data/xrsf-l2-avg1m_science/"
                              f"sci_xrsf-l2-avg1m_g16_y{year}_v2-1-0.nc"))
    for year in goes18_years:
        goes_urls[18].append((f"{new_xrs_url}"
                              "goes18/l2/data/xrsf-l2-avg1m_science/"
                              f"sci_xrsf-l2-avg1m_g18_y{year}_v2-1-0.nc"))
    return goes_urls


def filename_from_url(url):
    return url[url.rfind("/")+1:len(url)]


def download(goesnum):
    local_data_dir = (f"{config['local_source_data_path']}/"
                      f"goes_xrs/g{goesnum:02d}")
    download_tools.ensure_data_dir(local_data_dir)
    goes_urls = goes_xrs_urls()
    urls = goes_urls[goesnum]
    files_to_download = []
    for url in urls:
        if goesnum >= 16 and f'y{pd.Timestamp.utcnow().year}' in url:
            max_age = pd.to_timedelta(1, 'D')
        else:
            max_age = pd.to_timedelta(200*365, 'D')
        filename = f"{local_data_dir}/{filename_from_url(url)}"
        files_to_download.append(
            {'url': url,
             'local_path': filename,
             'max_age': max_age}
         )
    filenames = download_tools.download_files(files_to_download)
    # TODO: Force download/overwrite of this year's file for GOES-16 and 17
    return filenames


def nc_to_dataframe(file, apply_flags=False, convert_column_names=False):
    ncdata = netCDF4.Dataset(file)
    ncvariables = ncdata.variables.keys()

    # Old and new data formats have different time variables and conventions
    if 'time' in ncvariables:
        index_var = 'time'
        time_var = ncdata.variables['time']
        time_units = ncdata.variables['time'].units
    elif 'time_tag' in ncvariables:
        index_var = 'time_tag'
        time_var = ncdata.variables['time_tag']
        time_units = ncdata.variables['time_tag'].units
    else:
        print("Error finding time stamp variable")
        return pd.DataFrame()
    (units, time_base_str) = time_units.split(" since ")
    time_index = (pd.to_datetime(time_base_str, utc=True) +
                  pd.to_timedelta(time_var[:], units))

    # Collect the data
    framedata = {}
    for key in ncdata.variables.keys():
        if (key == index_var):  # Col is time-tag. Already used as index.
            continue
        var = ncdata.variables[key]

        #  Collect from columns that match the time-tag's dimension
        if var.dimensions == time_var.dimensions:
            values = var[:].astype(float)

            # Set missing values to NaN (old format data only)
            if 'missing_value' in var.ncattrs():
                missing_value = float(var.getncattr('missing_value'))
                mask = values == missing_value
                framedata[key] = np.where(mask, np.nan, values)
            else:
                framedata[key] = values

    ncdata.close()
    df = pd.DataFrame(data=framedata, index=time_index)

    # Apply flags (available for GOES15 and later science data only)
    if apply_flags and 'xrsa_flag' in df.columns:
        mask_a = (df['xrsa_flag'] == 0) | (df['xrsa_flag'] == 16)
        mask_b = (df['xrsb_flag'] == 0) | (df['xrsb_flag'] == 16)
        df['xrsa_flux'][~mask_a] = np.nan
        df['xrsb_flux'][~mask_b] = np.nan

    # Harmonize column names (needed for combining old and new data formats)
    if convert_column_names:
        if 'xrsa_flux' in df.columns:
            df.rename({'xrsa_flux': 'xray_flux_short',
                       'xrsb_flux': 'xray_flux_long'}, axis=1, inplace=True)
        elif 'xs' in df.columns:
            df.rename({'xs': 'xray_flux_short',
                       'xl': 'xray_flux_long'}, axis=1, inplace=True)
    return df


def flag_to_string_list(flag):
    flag_meanings = {
        1: 'eclipse',
        2: 'bad_data',
        4: 'e_contam_significant',
        8: 'e_correction_invalid',
        16: 'e_correction_interp',
        32: 'e_correction_decay'}
    flag_string_list = []
    for flag_value in flag_meanings.keys():
        if flag_value & flag == flag_value:
            flag_string_list.append(flag_meanings[flag_value])
    return flag_string_list


def goes_xrs_primary_to_dataframe(secondary=False, only=None):
    t_now = pd.Timestamp.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
    # Source doc for definitions of primary vs secondary:
    #   https://www.ngdc.noaa.gov/stp/satellite/goes/doc/GOES_XRS_readme.pdf
    #
    goes_primaries = f'''
    starttime             endtime                primary  secondary
    1986-01-01T00:00:00   1988-01-26T00:00:00          6          5
    1988-01-26T00:00:00   1994-12-11T00:00:00          7          6
    1994-12-11T00:00:00   1995-03-01T00:00:00          7          8
    1995-03-01T00:00:00   1998-07-27T00:00:00          8          7
    1998-07-27T00:00:00   2003-04-08T15:00:00          8         10
    2003-04-08T15:00:00   2003-05-15T15:00:00         10         12
    2003-05-15T15:00:00   2006-06-28T14:00:00         12         10
    2006-06-28T14:00:00   2007-01-01T00:00:00         12         11
    2007-01-01T00:00:00   2007-04-12T00:00:00         10         11
    2007-04-12T00:00:00   2007-11-21T00:00:00         11         10
    2007-11-21T00:00:00   2007-12-05T00:00:00         11       None
    2007-12-05T00:00:00   2007-12-18T00:00:00         11         10
    2007-12-18T00:00:00   2008-02-10T16:30:00         11       None
    2008-02-10T16:30:00   2009-12-01T00:00:00         10       None
    2009-12-01T00:00:00   2010-09-01T00:00:00         14       None
    2010-09-01T00:00:00   2010-10-28T00:00:00         14         15
    2010-10-28T00:00:00   2011-09-01T00:00:00         15       None
    2011-09-01T00:00:00   2012-10-23T16:00:00         15         14
    2012-10-23T16:00:00   2012-11-19T16:31:00         14         15
    2012-11-19T16:31:00   2015-01-26T16:01:00         15       None
    2015-01-26T16:01:00   2015-05-21T18:00:00         15         13
    2015-05-21T18:00:00   2015-06-09T16:25:00         14         13
    2015-06-09T16:25:00   2016-05-03T13:00:00         15         13
    2016-05-03T13:00:00   2016-05-12T17:30:00         13         14
    2016-05-12T17:30:00   2016-05-16T17:00:00         14         13
    2016-05-16T17:00:00   2016-06-09T17:30:00         14         15
    2016-06-09T17:30:00   2017-12-12T16:30:00         15         13
    2017-12-12T16:30:00   2019-12-09T00:00:00         15         14
    2019-12-09T00:00:00   {t_now}                     16         17
    '''

    with io.StringIO(goes_primaries) as f:
        goes_primary_df = pd.read_table(f, sep=r'\s+',
                                        parse_dates=True, na_values='None')
    goes_primary_dict = goes_primary_df.to_dict(orient='records')

    dfs_multisat = []
    for goesnum in range(5, 17):
        if only is not None:
            if goesnum not in only:
                continue
        # First collect all the data for the GOES satellite
        filelist = download(goesnum)
        dfs_multifile = []
        for file in filelist:
            df = nc_to_dataframe(file, convert_column_names=True)
            df['satellite'] = f'goes{goesnum:02d}'
            dfs_multifile.append(df)
        df_total_singlesat = pd.concat(dfs_multifile).sort_index()

        # Now slice the dataframe
        if secondary:
            primary_or_secondary = 'secondary'
        else:
            primary_or_secondary = 'primary'

        spans = [(span['starttime'], span['endtime'])
                 for span in goes_primary_dict
                 if span[primary_or_secondary] == goesnum]

        for span in spans:
            logging.info(f"Appending data from GOES-{goesnum}, " +
                         f"for timespan {span}.")
            dfs_multisat.append(df_total_singlesat[slice(*span)])

    df_total = pd.concat(dfs_multisat)

    return df_total
