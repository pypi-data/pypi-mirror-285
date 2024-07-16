import numpy as np
import pandas as pd
import logging
import pyhdf.HDF
import pyhdf.V
import pyhdf.VS
import pyhdf.SD
from swxtools.config import config
import swxtools.download


def download_data(t0, t1, datatype='swepam'):
    """
    Ensure that ACE SWEPAM (plasma) or magnetometer (IMF) data is stored
    locally. Otherwise, download the data. The data comes in yearly files.

    Args:
        t0 (int, float, str, datetime): Start time of data to download (>1998)
        t1 (int, float, str, datetime): End time of data to download
        datatype ('mag' or 'swepam'): ACE data product abbreviation

    Returns:
        List of the filenames stored locally.
    """
    # Parse date/time
    t0 = pd.to_datetime(t0)
    t1 = pd.to_datetime(t1)

    # Set the details for product retrieval, based on the data type
    resolutions = {'swepam': '64sec', 'mag': '16sec'}
    try:
        resolution = resolutions[datatype]
        baseurl = f'ftp://mussel.srl.caltech.edu/pub/ace/level2/{datatype}'
    except KeyError:
        logging.error("Unknown ACE data type: {datatype}")
        return []

    # Construct the list of files to download and where to put them
    files_to_download = []
    for year in range(t0.year, t1.year+1):
        local_data_dir = f"{config['local_source_data_path']}/ace/{datatype}"
        swxtools.download.ensure_data_dir(local_data_dir)
        filename = f'{datatype}_data_{resolution}_year{year}.hdf'
        local_filename = f"{local_data_dir}/{filename}"
        url = f"{baseurl}/{filename}"
        files_to_download.append({
            'url': url,
            'local_path': local_filename
        })

    filenames = swxtools.download.download_files(files_to_download)
    return filenames


def hdf_to_dataframe(filename):
    """
    Read the contents of an ACE HDF4 data file into a Pandas DataFrame.

    Args:
        filename (string): Name of the HDF4 file

    Returns:
        Pandas dataframe containing the timeseries data
    """
    # open HDF file in read-only mode
    hdffile = pyhdf.HDF.HDF(filename, pyhdf.HDF.HC.READ)

    # Initiate the HDF interfaces
    vg = hdffile.vgstart()
    vs = hdffile.vstart()

    # Dig down to the data
    vgid = vg.getid(-1)
    vg1 = vg.attach(vgid)
    members = vg1.tagrefs()
    tag, ref = members[0]
    vd = vs.attach(ref, write=0)

    # Get the names of the fields (dataframe columns)
    # and the number of records to read
    nrecs, intmode, fields, size, name = vd.inquire()

    # Read the data into the dataframe
    df = pd.DataFrame(data=vd.read(nRec=nrecs), columns=fields)
    ace_epoch = pd.to_datetime("19960101")
    df.index = (ace_epoch + pd.to_timedelta(df['ACEepoch'], 's'))

    # Set the fill value (-9999.9) to NaN, except for the date/time fields
    replace_fields = set(df.columns) - set(['year', 'day', 'hr', 'min', 'sec',
                                            'fp_year', 'fp_doy', 'ACEepoch'])

    for field in replace_fields:
        if 'swepam_data' in filename:
            df[field].where(df[field] > -9998, other=np.nan, inplace=True)
        elif 'mag_data' in filename:
            df[field].where(df[field] > -998, other=np.nan, inplace=True)

    # Close the interfaces and close the file
    vd.detach()
    vg1.detach()
    vg.end()
    vs.end()
    hdffile.close()

    return df
