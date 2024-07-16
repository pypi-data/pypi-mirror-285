import pandas as pd
import requests
import gzip
import tempfile
import netCDF4
import logging
from swxtools import download_tools
from swxtools.config import config

base_url = 'https://www.ngdc.noaa.gov/dscovr/data/'
catalog_url = 'https://www.ngdc.noaa.gov/next-catalogs/rest/dscovr/catalog/'


def download_data(t0, t1, datatype='m1m'):
    """
    Ensure that DSCOVR magnetometer (m1m) or Faraday Cup (f1m) data is
    stored locally. Otherwise the download the data.

    Args:
        t0 (int, float, str, datetime): Start time of data to download
        t1 (int, float, str, datetime): End time of data to download
        datatype ('m1m' or 'f1m'): DSCOVR data product abbreviation.

    Returns:
        List of the filenames stored locally.
    """
    if datatype not in ['m1m', 'f1m']:
        logging.error(f"Unknown DSCOVR datatype: {datatype}.")
        return []

    # Parse and format the date/time
    t0 = pd.to_datetime(t0)
    t1 = pd.to_datetime(t1)
    t0str = t0.strftime('%Y-%m-%dT%H:%MZ')
    t1str = t1.strftime('%Y-%m-%dT%H:%MZ')

    # Inquire about the available data files
    url = (catalog_url + f'filename?processEnvs=oe&dataTypes={datatype}&'
                       + f'dataStartTime={t0str}&dataEndTime={t1str}')
    r = requests.get(url)
    if not r.ok:
        logging.error(f'Error accessing DSCOVR files from {url}. '
                      f'Response was: {r}.')
        return []
    files = r.json()['items']
    files.sort()

    # Construct the list of files to download and where to put them
    files_to_download = []
    for file in files:
        year = file[15:19]
        month = file[19:21]
        url = base_url + f'{year}/{month}/{file}'
        local_data_dir = (f'{config["local_source_data_path"]}/'
                          f'dscovr/{datatype}/{year}/{month}')
        download_tools.ensure_data_dir(local_data_dir)
        local_filename = f'{local_data_dir}/{file}'
        files_to_download.append({'url': url, 'local_path': local_filename})

    # Download the files if they are not yet available locally
    filenames = download_tools.download_files(files_to_download)

    return filenames


def nc_to_dataframe(ncfile):
    """
    Read the contents of a DSCOVR NetCDF data file into a Pandas DataFrame.

    Args:
        ncfile (string): Name of the NetCDF file (can be gzipped)

    Returns:
        Pandas dataframe containing the timeseries data
    """
    zipped = (ncfile[-3:] == '.gz')
    if zipped:
        with gzip.open(ncfile, 'rb') as gzip_fh:
            file_content = gzip_fh.read()
        netcdf_fh = tempfile.NamedTemporaryFile()
        logging.debug('uncompressing to {}'.format(netcdf_fh.name))
        netcdf_fh.write(file_content)
        netcdf_fh.flush()
        file = netcdf_fh.name
    else:
        file = ncfile

    nc = netCDF4.Dataset(file)
    time_index = pd.to_datetime(nc.variables['time'][:]*1e6, utc=True)
    data = {}
    for variable in nc.variables.keys():
        if (variable != 'time' and
                nc.variables[variable].dimensions == ('time', )):
            data[variable] = nc.variables[variable][:]
    nc.close()
    df = pd.DataFrame(data=data, index=time_index)
    return df


def to_dataframe(t0, t1, datatype='m1m'):
    filenames = download_data(t0, t1, datatype)
    dfs = []
    for file in filenames:
        dfs.append(nc_to_dataframe(file))
    df = pd.concat(dfs, axis=0).sort_index()
    return df

