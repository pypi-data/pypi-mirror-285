import os
import requests
import pandas as pd
import configparser
from sgp4.api import Satrec
from sgp4.api import SGP4_ERRORS
from astropy.time import Time
from astropy.coordinates import CartesianDifferential, CartesianRepresentation
from astropy.coordinates import TEME, ITRS
from astropy import units as u

# Read the username and password from the file
# Contents of ~/.spacetrackorg.txt:
# [default]
# username = xxx
# password = xxx
config = configparser.ConfigParser()
config.read(os.environ["HOME"] + "/.spacetrackorg.txt")
username = config.get("default", "username")
password = config.get("default", "password")
spacetrack_credentials = {'identity': username, 'password': password}

# Basics
base_url = "https://www.space-track.org"
login_request = "/ajaxauth/login"


def satcat_objects_by_name(name):
    satcat_request = ("/basicspacedata/query/class/satcat/OBJECT_NAME/"
                      f"~~{name.upper()}/orderby/NORAD_CAT_ID%20asc")

    with requests.Session() as session:
        resp = session.post(base_url + login_request,
                            data=spacetrack_credentials)
        if resp.status_code != 200:
            print("Logging in to space-track.org failed")
        resp = session.get(base_url + satcat_request)
        if resp.status_code != 200:
            print("Satcat query failed: " + base_url + satcat_request)
            print(resp.status_code)
            print(resp.text)

    df_out = pd.read_json(resp.text, convert_dates=['LAUNCH', 'DECAY'])
    return df_out


def tip_by_noradid(noradid):
    satcat_request = ("/basicspacedata/query/class/tip/NORAD_CAT_ID/"
                      f"{noradid}/WINDOW/1/orderby/MSG_EPOCH%20asc/"
                      "emptyresult/show")

    with requests.Session() as session:
        resp = session.post(base_url + login_request,
                            data=spacetrack_credentials)
        if resp.status_code != 200:
            print("Logging in to space-track.org failed")
        resp = session.get(base_url + satcat_request)
        if resp.status_code != 200:
            print("TIP query failed: " + base_url + satcat_request)
            print(resp.status_code)
            print(resp.text)

    df_out = pd.read_json(resp.text, convert_dates=['MSG_EPOCH',
                                                    'INSERT_EPOCH',
                                                    'DECAY_EPOCH'])
    return df_out


def line1_epoch_timestamp(line1):
    year = int(line1[18:20])
    day = int(line1[20:23])
    secday = float(line1[23:32])*86400
    return (pd.to_datetime(f'{year:02d}{day:03d}', format='%y%j', utc=True) +
            pd.to_timedelta(secday, 'sec'))


def tles_by_id(norad_id, tstart, tend, outfile=None, overwrite=False):
    satcat_request = ("/basicspacedata/query/class/gp_history/"
                      f"NORAD_CAT_ID/{norad_id}/orderby/TLE_LINE1%20ASC/"
                      f"EPOCH/{tstart.strftime('%Y-%m-%d')}"
                      f"--{tend.strftime('%Y-%m-%d')}/format/tle")

    with requests.Session() as session:
        resp = session.post(base_url + login_request,
                            data=spacetrack_credentials)
        if resp.status_code != 200:
            print("Logging in to space-track.org failed")
            return pd.DataFrame()
        resp = session.get(base_url + satcat_request)
        if resp.status_code != 200:
            print("TLE query failed: " + base_url + satcat_request)
            return pd.DataFrame()

    tles = []
    lines = [line.strip() for line in resp.text.split('\n')]
    numtles = int(len(lines)/2)
    for itle in range(numtles):
        tles.append(lines[itle*2:(itle+1)*2])

    df_tle = pd.DataFrame(tles, columns=['line1', 'line2'])

    df_tle['epoch'] = df_tle['line1'].map(line1_epoch_timestamp)
    df_tle['norad_id'] = df_tle['line1'].str[2:7]
    df_tle['intldes'] = df_tle['line1'].str[9:17]
    return df_tle


def tle_to_itrs(line1, line2, time):
    satellite = Satrec.twoline2rv(line1, line2)

    t = Time(time)
    error_code, teme_p, teme_v = satellite.sgp4(t.jd1, t.jd2)  # in km and km/s
    if error_code != 0:
        raise RuntimeError(SGP4_ERRORS[error_code])

    # Create the state vector in astropy
    teme_p = CartesianRepresentation(teme_p*u.km)
    teme_v = CartesianDifferential(teme_v*u.km/u.s)
    teme = TEME(teme_p.with_differentials(teme_v), obstime=t)

    # Convert to ITRS and geodetic coordinates
    itrs = teme.transform_to(ITRS(obstime=t))
    return itrs


def geodetic_orbit_from_tle(norad_id, times, max_time_difference=86400):
    import collections.abc
    # First get the TLEs for the time interval, with a few days margin
    tle_starttime = times[0] - pd.to_timedelta(2, 'D')
    tle_stoptime = times[-1] + pd.to_timedelta(2, 'D')
    tles = tles_by_id(norad_id, tle_starttime, tle_stoptime, overwrite=True)
    if len(tles) == 0:
        return pd.DataFrame()
    # Loop over the times to evaluate the TLEs
    geodetic_orbit = []
    old_e = None
    for time in times:
        print(time, end='\r')
        # Find the closest TLE epoch
        result_index = tles['epoch'].sub(time).abs().idxmin()
        tle = tles.iloc[result_index]
        time_difference = (tle['epoch'] - time).total_seconds()
        # Check the time difference, first if a tuple is supplied:
        if isinstance(max_time_difference, collections.abc.Sequence):
            if (time_difference < max_time_difference[0] or
                time_difference > max_time_difference[1]):
                continue
        elif (abs(time_difference) > max_time_difference):
            continue
        try:
            itrs = tle_to_itrs(tle['line1'], tle['line2'], time)
            geodetic = itrs.earth_location.to_geodetic()
            geodetic_orbit.append({'time': time,
                                   'height': geodetic.height.value,
                                   'lat': geodetic.lat.value,
                                   'lon': geodetic.lon.value,
                                   'x_itrf': itrs.x.value,
                                   'y_itrf': itrs.y.value,
                                   'z_itrf': itrs.z.value,
                                   'vx_itrf': itrs.v_x.value,
                                   'vy_itrf': itrs.v_y.value,
                                   'vz_itrf': itrs.v_z.value,
                                   'tle_epoch': tle['epoch']})
        except RuntimeError as e:
            if e != old_e:
                print("Error evaluating TLE with epoch "
                      f"{tle['epoch']} for time {time}.")
                print(e)
            old_e = e
            continue
    df = pd.DataFrame(geodetic_orbit)
    if len(df) > 0:
        df.index = df['time']
    return df


def geodetic_orbit_from_tlelines(tleline1,
                                 tleline2,
                                 start_offset='-86400s',
                                 stop_offset='86400s',
                                 freq='1min'):
    import collections.abc
    # First get the TLEs for the time interval, with a few days margin
    geodetic_orbit = []
    old_e = None
    tle_epoch = line1_epoch_timestamp(tleline1)
    tstart = tle_epoch.round('min') + pd.to_timedelta(start_offset)
    tstop  = tle_epoch.round('min') + pd.to_timedelta(stop_offset)
    times = pd.date_range(tstart, tstop, freq=freq)
    for time in times:
        print(time, end='\r')
        try:
            itrs = tle_to_itrs(tleline1, tleline2, time)
            geodetic = itrs.earth_location.to_geodetic()
            geodetic_orbit.append({'time': time,
                                   'height': geodetic.height.value,
                                   'lat': geodetic.lat.value,
                                   'lon': geodetic.lon.value,
                                   'x_itrf': itrs.x.value,
                                   'y_itrf': itrs.y.value,
                                   'z_itrf': itrs.z.value,
                                   'vx_itrf': itrs.v_x.value,
                                   'vy_itrf': itrs.v_x.value,
                                   'vz_itrf': itrs.v_x.value,
                                   'tle_epoch': tle_epoch})
        except RuntimeError as e:
            if e != old_e:
                print("Error evaluating TLE with epoch "
                      f"{tle['epoch']} for time {time}.")
                print(e)
            old_e = e
            continue
    df = pd.DataFrame(geodetic_orbit)
    df.index = df['time']
    return df.drop(['time'], axis=1)
