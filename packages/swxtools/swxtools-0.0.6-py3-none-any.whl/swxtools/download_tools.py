import os
import re
import requests
import logging
import pandas as pd
from bs4 import BeautifulSoup
import urllib
import shutil
import ftplib
import tempfile
from urllib.parse import urlparse

def ensure_data_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory


def download_file_http(url, filename):
    r = requests.get(url)
    if r.ok:
        with open(filename, 'wb') as fh:
            fh.write(r.content)
        logging.info(
            f"Downloaded file stored locally at {filename}")
        return True
    else:
        error = f"{r.status_code} {r.reason}"
        logging.error(f"A problem occurred when downloading {url}: {error}")
        return False


def download_file_ftp(url, filename, ftp_conn):
    url_parts = urlparse(url)
    try:
        # print(f'URL {url}')
        # print(f'To {filename}')
        with tempfile.TemporaryFile() as fp:
            ftp_conn.retrbinary(f'RETR {url_parts.path}', fp.write)
            if os.stat(tempfile.name).st_size > 0:
                os.rename(tempfile.name, filename)
            else:
                logging.error(f"Error downloading {url} via FTP.")
                return False
        logging.info(
            f"Downloaded file stored locally at {filename}")
        return True
    except ftplib.all_errors as reason:
        logging.error(f"There was a problem with downloading from URL: {url}, to filename: {filename}. Reason: {reason}")
        return False


def download_files(files_to_download, progress=False, ftp_conn=None):
    filenames = []
    total_count = len(files_to_download)
    for count, item in enumerate(files_to_download):
        download = True
        url = item['url']
        filename = item['local_path']
        if 'max_age' in item:
            max_age = pd.to_timedelta(item['max_age'])
        else:
            max_age = pd.to_timedelta(200*365, 'D')
        if os.path.isfile(filename):
            t_now = pd.Timestamp.now()
            t_file = pd.to_datetime(os.path.getmtime(filename), unit='s')
            file_age = t_now - t_file
            if file_age < max_age:
                logging.debug(f"Local file {filename} is up-to-date.")
                download = False
                filenames.append(filename)
        if download:
            if progress:
                logging.info(f"{count+1}/{total_count}: {item['local_path']}")
            if url.startswith('http'):
                logging.info(f"Attempting download over http of {url}")
                if download_file_http(url, filename):
                    filenames.append(filename)
            elif url.startswith('ftp'):
                logging.info(f"Attempting download over ftp of {url}")
                if download_file_ftp(url, filename, ftp_conn):
                    filenames.append(filename)
            else:
                logging.error(f"Do not know how to handle url: {url}")
    return filenames


def crawl_http(base_url, recursive=False):
    '''Crawl a website hosting data files, such as NASA SPDF, and retrieve a
    list of available (sub)directories and files. With the recursive option,
    the contents of subdirectories will be added to the lists as well.'''

    r = requests.get(base_url)
    dirs = []
    files = []
    if r.ok:
        soup = BeautifulSoup(r.text, 'html.parser')
        match_date = re.compile(r'\d\d\d\d-\d\d-\d\d \d\d:\d\d')
        for row in soup.table.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) == 3:
                href = cols[0].find('a').get('href')
                date_string = cols[1].text
                size = cols[2].text
            elif len(cols) == 5:  # For new NASA GSFC SDO website special case
                href = cols[1].find('a').get('href')
                date_string = cols[2].text
                if match_date.match(date_string):
                    date = pd.to_datetime(date_string)
                size = cols[3].text
            else:
                continue  # no file or dir here, so skip rest of the loop
            url = f"{base_url}{href}"
            if match_date.match(date_string):
                date = pd.to_datetime(date_string)
            else:
                date = None
            if not href.startswith('/'):  # Skip the /. and /.. dirs
                if href.endswith('/'):
                    dirs.append({'url': url, 'date': date})
                else:
                    files.append({'url': url, 'date': date, 'size': size})
    if recursive:
        for subdir in [d['url'] for d in dirs]:
            newdirs, newfiles = crawl_http(subdir, recursive=True)
            dirs.extend(newdirs)
            files.extend(newfiles)
    return dirs, files


def setup_ftp_conn(base_url, username, password):
    url_parts = urlparse(base_url)
    if url_parts.scheme == 'ftp':
        ftp_conn = ftplib.FTP(url_parts.netloc, username, password)
    elif url_parts.scheme == 'ftp+tls':
        ftp_conn = ftplib.FTP_TLS(url_parts.netloc, username, password)
        #ftp_conn.set_debuglevel(2)
    else:
        logging.error("Unkown scheme: ", url_parts.scheme)
        return None
    return ftp_conn


def crawl_ftp(base_url,
              recursive=False,
              ftp_conn=None):
    '''Crawl an FTP site hosting data files and retrieve a list of available
    (sub)directories and files. With the recursive option, the contents of
    subdirectories will be added to the lists as well.'''

    url_parts = urlparse(base_url)

    # Change to the specified directory, and request the file list using MLSD
    ftp_conn.cwd(url_parts.path)
    listing = list(ftp_conn.mlsd())
    df_listing = pd.DataFrame(data=[item[1] for item in listing])
    df_listing['filename'] = [item[0] for item in listing]
    df_listing['modify'] = pd.to_datetime(df_listing['modify'])
    for col in ['sizd', 'size']:
        # Set size of directory (sizd) or size of file (size) to numeric
        if col in df_listing:
            df_listing[col] = pd.to_numeric(df_listing[col])

    # Now build the list of directories and files
    dirs = []
    files = []
    for row in df_listing.to_dict(orient='records'):
        if row['type'] == 'dir':
            url = base_url + row['filename'] + "/"
            dirs.append({'url': url,
                         'date': row['modify']})
        elif row['type'] == 'file':
            url = base_url + row['filename']
            files.append({'url': url,
                          'date': row['modify'],
                          'size': row['size']})
    if recursive:
        for subdir in [d['url'] for d in dirs]:
            newdirs, newfiles = crawl_ftp(subdir, recursive=True)
            dirs.extend(newdirs)
            files.extend(newfiles)

    return dirs, files


def mirror(base_url, sub_url, local_dir,
           include_strings=None, exclude_strings=None,
           esa_eo_timespan=None, ftp_conn=None):
    '''Mirror files from a website or FTP site such as NASA SPDF.
    Example arguments to download all L1C GOLD files except limb and
    occultation files, and store these under
    /Volumes/datasets/gold/level1c/2021/...etc:

    local_dir = '/Volumes/datasets/gold/'
    base_url = 'https://spdf.gsfc.nasa.gov/pub/data/gold/'
    sub_url = 'level1c/2021/'
    exclude_strings = ['LIM', 'OCC']'''

    traverse_url = f'{base_url}{sub_url}'
    if traverse_url.startswith('http'):
        dirs, files = crawl_http(traverse_url, recursive=True)
    elif traverse_url.startswith('ftp'):
        # Set up the FTP connection
        dirs, files = crawl_ftp(
            traverse_url,
            recursive=True,
            ftp_conn=ftp_conn
        )
    else:
        raise ValueError(f"Unknown URL type: {traverse_url}. " +
                         "URLs should start with http or ftp")

    # Create root directories if necessary
    if not os.path.exists(local_dir):
        os.makedirs(local_dir)
    if not os.path.exists(local_dir + sub_url):
        os.makedirs(local_dir + sub_url)

    # Create subdirectories if necessary
    for mydir in dirs:
        local_sub_dir = local_dir + mydir['url'].replace(base_url, '')
        if not os.path.exists(local_sub_dir):
            os.makedirs(local_sub_dir)

    files_to_download = []
    for file in files:
        include = True
        if isinstance(include_strings, (list, tuple)):
            if not any([term in file['url'] for term in include_strings]):
                include = False
        if isinstance(exclude_strings, (list, tuple)):
            if any([term in file['url'] for term in exclude_strings]):
                include = False
        if isinstance(esa_eo_timespan, (list, tuple)):
            # Get the start/end timestamps from the filename
            file_sections = file['url'].split("/")[-1].split("_")
            [t0str, t1str] = [s for s in file_sections if s[8:9] == 'T']
            # In case of double underscores, remove empty sections
            # if '' in file_sections:
            #     file_sections.remove('')
            # Timestamps should be in section -2 and -3
            #   (with -1 being the baseline/version and extension)
            t0file = pd.to_datetime(t0str, utc=True)
            t1file = pd.to_datetime(t1str, utc=True)
            # Get the desired start/end time from the argument
            t0arg = pd.to_datetime(esa_eo_timespan[0], utc=True)
            t1arg = pd.to_datetime(esa_eo_timespan[1], utc=True)
            # Check if the file is in the desired start/end time
            if ((t0file > pd.to_datetime(t1arg, utc=True)) or
               (t1file < pd.to_datetime(t0arg, utc=True))):
                include = False
        if include:
            file['local_path'] = local_dir + file['url'].replace(base_url, '')
            files_to_download.append(file)

    downloaded_files = download_files(
        files_to_download,
        progress=True,
        ftp_conn=ftp_conn
    )

    return downloaded_files
