import pandas as pd
import requests
import logging
from swxtools.config import config
from swxtools import download_tools

# Sample geomagnetic forecast file below. Note that the file must be parsed
# line-by-line, while the data is provided in three columns representing the
# three days of the forecast timespan.
#
# :Product: Geomagnetic Forecast
# :Issued: 2021 Sep 07 2205 UTC
# # Prepared by the U.S. Dept. of Commerce, NOAA, Space Weather Prediction Center
# #
# NOAA Ap Index Forecast
# Observed Ap 06 Sep 006
# Estimated Ap 07 Sep 007
# Predicted Ap 08 Sep-10 Sep 008-005-005
#
# NOAA Geomagnetic Activity Probabilities 08 Sep-10 Sep
# Active                20/15/15
# Minor storm           01/01/01
# Moderate storm        01/01/01
# Strong-Extreme storm  01/01/01
#
# NOAA Kp index forecast 08 Sep - 10 Sep
#              Sep 08    Sep 09    Sep 10
# 00-03UT        2         2         2
# 03-06UT        3         2         1
# 06-09UT        1         1         1
# 09-12UT        3         1         1
# 12-15UT        2         1         1
# 15-18UT        1         1         1
# 18-21UT        2         2         2
# 21-00UT        2         2         2


def download_current():
    urls = ['https://services.swpc.noaa.gov/text/3-day-geomag-forecast.txt',
            'https://services.swpc.noaa.gov/text/45-day-ap-forecast.txt']
    filenames = []
    for url in urls:
        try:
            r = requests.get(url)
            lines = r.text.splitlines()
        except requests.exceptions.RequestException:
            logging.error(
                f"An exception occurred when trying to download from {url}"
            )
            return
        if lines[0] == ':Product: Geomagnetic Forecast':
            for line in lines:
                if line.startswith(':Issued:'):
                    issuedate = pd.to_datetime(line[9:])
                    break

            local_data_dir = (
                f'{config["local_source_data_path"]}/swpc/forecast/geomag/'
            )
            issuedate_str = issuedate.strftime("%Y-%m-%dT%H:%M:%S")
            filename = (
                f'{local_data_dir}/3-day-geomag-forecast_{issuedate_str}.txt'
            )
            filenames.append(filename)
        elif lines[0] == ':Product: 45 Day AP Forecast  45DF.txt':
            for line in lines:
                if line.startswith(':Issued:'):
                    issuedate = pd.to_datetime(line[9:])
                    break
            local_data_dir = (
                f'{config["local_source_data_path"]}/swpc/forecast/45DF/'
            )
            issuedate_str = issuedate.strftime("%Y-%m-%dT%H:%M:%S")
            filename = (
                f'{local_data_dir}/45-day-ap-forecast_{issuedate_str}.txt'
            )
            # filenames.append(filename)  # Do not yet pass on
        download_tools.ensure_data_dir(local_data_dir)
        with open(filename, 'w') as fh:
            fh.writelines(r.text)

    return filenames


def to_dataframe(filename):
    with open(filename, 'r') as fh:
        lines = fh.read().splitlines()
    datalinenum = 0
    data = []
    for line in lines:
        if line.startswith(':Issued:'):
            issuedate = pd.to_datetime(line[9:])
            issueyear = issuedate.year
        if line.startswith('NOAA Kp index forecast'):
            startdatestring = line[23:29]
            startdate = pd.to_datetime(f"{startdatestring} {issueyear}")
            dtindex = pd.date_range(startdate, freq='3H', periods=3*8)
            data = []
        if line[2:3] == '-' and line[5:7] == 'UT':
            linedata = line[8:].split()
            # Append data from the three columns representing the 3 days
            data.append(
                {'timetag_issue': issuedate,
                 'timetag_forecast': dtindex[datalinenum],
                 'kp_index': linedata[0]}
            )
            data.append(
                {'timetag_issue': issuedate,
                 'timetag_forecast': dtindex[datalinenum+8],
                 'kp_index': linedata[1]}
            )
            data.append(
                {'timetag_issue': issuedate,
                 'timetag_forecast': dtindex[datalinenum+16],
                 'kp_index': linedata[2]}
            )
            datalinenum = datalinenum + 1

    df = pd.DataFrame(data=data)
    df.index = df['timetag_forecast']

    return df.sort_index()
