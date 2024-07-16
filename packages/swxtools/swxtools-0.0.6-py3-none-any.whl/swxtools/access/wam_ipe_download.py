#!/usr/bin/env python3
from bs4 import BeautifulSoup
import os
import sys
import time
import logging
import requests
from urllib3.util import Retry
from requests.adapters import HTTPAdapter


def ensure_data_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
    return directory


def list_wam_ipe_files(root_url, root_dir):
    file_list = []
    r = requests.get(root_url)
    if r.ok:
        soup = BeautifulSoup(r.text, "html.parser")
        # Find the URLs in the table
        for pre in soup.find_all('pre'):
            for link in pre.find_all('a'):
                address = link.get('href')
                if (address[0:1] != '/' and
                        address[-1] == '/' and
                        address[0:2] != 'wrs'):

                    ensure_data_dir(f"{root_dir}{address}")
                    # Call recursively
                    file_list = (file_list +
                                 list_wam_ipe_files(
                                     f"{root_url}{address}",
                                     f"{root_dir}{address}")
                                )

                # Get rid of the sorting options and previous directory links
                if (address[0:1] != '?' and
                        address[0:1] != '/' and
                        address[-1] != '/' and
                        address[0:2] != 'wrs'):
                    url = f"{root_url}{address}"
                    local_filename = f"{root_dir}{os.path.basename(url)}"
                    download = False

                    # Add to download if file does not yet exist
                    if not os.path.isfile(local_filename):
                        download = True
                    if download:
                        file_list.append((url, local_filename))

    return file_list


def download_file(session, url, fname, loginfo=""):
    try:
        # Use the s (Session) mounted at the beginning of this file
        # NOTE the stream=True parameter below

        start = time.perf_counter()

        with session.get(url, stream=True) as r:
            r.raise_for_status()

            # Create directory for new file, if already exists > no problem
            logging.info(f"Downloading {url}")
            os.makedirs(os.path.dirname(fname), exist_ok=True)

            # Set up progress indicator
            total_length = r.headers.get('content-length')
            dl = 0

            with open(fname, 'wb') as f:

                if total_length is None:  # no content length header
                    f.write(r.content)
                else:
                    for chunk in r.iter_content(chunk_size=8192):
                        dl += len(chunk)
                        f.write(chunk)
                        done = int(30 * dl / int(total_length))
                        speed = dl//(time.perf_counter() - start) / 100000
                        sys.stdout.write(
                            f"\r[{'=' * done}{' ' * (30-done)}] {speed} Mbps"
                        )
                    print(f"\n{loginfo} {total_length} = "
                          f"{(time.perf_counter() - start):.2f} seconds")

    except requests.exceptions.HTTPError as e:
        logging.warning(
            f"A HTTP error occurred while downloading from {url}: {e}"
        )
        pass


def download_filelist(filelist, root_url):
    with requests.Session() as session:
        retries = Retry(total=5,
                        backoff_factor=1,
                        status_forcelist=[500, 502, 503, 504])
        session.mount(root_url, HTTPAdapter(max_retries=retries))
        for i_file, (url, filename) in enumerate(filelist):
            if not os.path.isfile(filename):
                download_file(session, url, filename, loginfo=f"{i_file} / {len(filelist)}")
                time.sleep(1)


logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s",
                    level=logging.INFO,
                    datefmt="%Y-%m-%d %H:%M:%S")

root_url = 'https://nomads.ncep.noaa.gov/pub/data/nccf/com/wfs/prod/'
root_dirs = ['/Volumes/datasets/wam-ipe/', '/volume1/datasets/wam-ipe/']
root_dir = None
for dir in root_dirs:
    if os.path.isdir(dir):
        root_dir = dir

if root_dir is not None:
    filelist = list_wam_ipe_files(root_url, root_dir)
    download_filelist(filelist, root_url)
