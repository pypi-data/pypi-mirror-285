import numpy as np
import pandas as pd
import apexpy
from astropy.time import Time
import astropy.coordinates as coord
from astropy.coordinates import CartesianRepresentation
from astropy import units as u
from scipy.interpolate import lagrange, interp1d

'''
This module provides routines for converting between various representations
of orbit ephemeris. The routines take pandas dataframes as input and return
an expanded dataframe as output. A naming convention is used for the columns.
'''


def itrf_to_geodetic_func(position_vectors):
    '''
    Helper function for conversion of ITRF dataframe to geodetic coordinates.
    To be used in a pd.DataFrame.apply call.
    '''

    if np.any(np.isnan(position_vectors)):
        return {'lon': np.nan,
                'lat': np.nan,
                'height': np.nan}
    astro_position = coord.ITRS(CartesianRepresentation(position_vectors,
                                unit=u.km))
    geodetic_position = astro_position.earth_location.to_geodetic('WGS84')
    return {'lon': geodetic_position.lon.value,
            'lat': geodetic_position.lat.value,
            'height': geodetic_position.height.to(u.m).value}


def itrf_to_geodetic(df_itrf):
    df_out = pd.concat([df_itrf,
                        df_itrf[['x_itrf',
                                 'y_itrf',
                                 'z_itrf']].apply(itrf_to_geodetic_func,
                                                  axis=1,
                                                  result_type='expand')
                        ], axis=1)
    return df_out


def geodetic_to_qd(df_geod):
    A = apexpy.Apex(df_geod.index[0])
    lat_qd, lon_qd = A.geo2qd(glat=df_geod['lat'],
                              glon=df_geod['lon'],
                              height=df_geod['height']/1e3)
    mlt = A.mlon2mlt(lon_qd, df_geod.index.values)
    df_new = df_geod.copy()
    df_new['lon_qd'] = lon_qd
    df_new['lat_qd'] = lat_qd
    df_new['mlt'] = mlt
    return df_new


def itrs_to_igrs(df_itrs):
    t = Time(df_itrs.index)
    df_out = df_itrs.copy()
    itrs = coord.ITRS(x=df_itrs['x_itrf'].values*u.km,
                      y=df_itrs['y_itrf'].values*u.km,
                      z=df_itrs['z_itrf'].values*u.km,
                      v_x=df_itrs['vx_itrf'].values*u.km/u.second,
                      v_y=df_itrs['vy_itrf'].values*u.km/u.second,
                      v_z=df_itrs['vz_itrf'].values*u.km/u.second,
                      obstime=df_itrs.index)
    gcrs_instance = coord.GCRS(obstime=t)
    gcrs = itrs.transform_to(gcrs_instance)
    df_out['x_gcrs'] = gcrs.cartesian.x.to_value()
    df_out['y_gcrs'] = gcrs.cartesian.y.to_value()
    df_out['z_gcrs'] = gcrs.cartesian.z.to_value()
    df_out['vx_gcrs'] = gcrs.velocity.d_x.to_value()
    df_out['vy_gcrs'] = gcrs.velocity.d_y.to_value()
    df_out['vz_gcrs'] = gcrs.velocity.d_z.to_value()
    return df_out


def igrs_to_itrs(df_igrs):
    t = Time(df_igrs.index)
    df_out = df_igrs.copy()
    igrs = coord.GCRS(representation_type='cartesian',
                      differential_type='cartesian',
                      x=df_igrs['x_gcrs'].values*u.km,
                      y=df_igrs['y_gcrs'].values*u.km,
                      z=df_igrs['z_gcrs'].values*u.km,
                      v_x=df_igrs['vx_gcrs'].values*u.km/u.second,
                      v_y=df_igrs['vy_gcrs'].values*u.km/u.second,
                      v_z=df_igrs['vz_gcrs'].values*u.km/u.second,
                      obstime=df_igrs.index)
    itrs_instance = coord.ITRS(obstime=t)
    itrs = igrs.transform_to(itrs_instance)
    df_out['x_itrf'] = itrs.cartesian.x.to_value()
    df_out['y_itrf'] = itrs.cartesian.y.to_value()
    df_out['z_itrf'] = itrs.cartesian.z.to_value()
    df_out['vx_itrf'] = itrs.velocity.d_x.to_value()
    df_out['vy_itrf'] = itrs.velocity.d_y.to_value()
    df_out['vz_itrf'] = itrs.velocity.d_z.to_value()
    return df_out


def interpolate_orbit_to_freq(df_orbit, index, order=7, freq='10ms'):
    nlagrange = int((order-1)/2)
    if (index-nlagrange) < 0 or index+nlagrange > len(df_orbit):
        raise IndexError("Trying to interpolate out of bounds of input orbit")
    new_index = pd.date_range(df_orbit.index[index-nlagrange],
                              df_orbit.index[index+nlagrange], freq=freq)
    x = (df_orbit.index[index-nlagrange:index+nlagrange] -
         df_orbit.index[index])/pd.to_timedelta('1s')
    newx = (new_index - df_orbit.index[index])/pd.to_timedelta('1s')
    data = {}
    for column in [col for col in df_orbit.columns
                   if df_orbit.dtypes[col] == float]:
        w = df_orbit[index-nlagrange:index+nlagrange][column].values
        f = lagrange(x, w)
        data[column] = f(newx)
    return pd.DataFrame(data=data, index=new_index)


def interpolate_orbit_to_timestamp(df_orbit, timestamp, order=7):
    nlagrange = int((order-1)/2)
    [index] = df_orbit.index.get_indexer([timestamp], method='nearest')
    newx = (timestamp - df_orbit.index[index])/pd.to_timedelta('1s')
    x = (df_orbit.index[index-nlagrange:index + nlagrange] -
         df_orbit.index[index]) / pd.to_timedelta('1s')
    data = {}
    for column in [col for col in df_orbit.columns
                   if df_orbit.dtypes[col] == float]:
        w = df_orbit[index-nlagrange:index+nlagrange][column].values
        f = lagrange(x, w)
        data[column] = f(newx)
    return pd.DataFrame(data=data, index=[timestamp])


def interpolate_orbit_to_datetimeindex(df_orbit, datetimeindex, kind='cubic'):
    if not np.all(df_orbit.dtypes == float):
        raise ValueError("Can only interpolate orbit if all columns are float")
    t0 = df_orbit.index[0]
    newx = (datetimeindex - t0) / pd.to_timedelta('1s')
    x = (df_orbit.index - t0) / pd.to_timedelta('1s')
    w = df_orbit.values
    f = interp1d(x,
                 w,
                 bounds_error=False,
                 fill_value=np.nan,
                 axis=0,
                 kind=kind)
    return pd.DataFrame(data=f(newx),
                        index=datetimeindex,
                        columns=df_orbit.columns)


def find_zero_crossings(df, column, resolution='10s'):
    before_zero_indices = np.where(np.diff(np.signbit(df[column])))[0]
    zero_crossings_datetimes = []
    for index in before_zero_indices:
        try:
            highfreq_df = interpolate_orbit_to_freq(df, index, freq=resolution)
            before_zero_indices2 = np.where(np.diff(np.signbit(
                                            highfreq_df[column])))[0]
            for index2 in before_zero_indices2:
                if (highfreq_df.iloc[index2][column]
                        < highfreq_df.iloc[index2+1][column]):
                    zero_crossings_datetimes.append(highfreq_df.iloc[index2])
                else:
                    zero_crossings_datetimes.append(highfreq_df.iloc[index2+1])
        except IndexError:
            print("Zero crossing too close to edge of input orbit.")
    return pd.DataFrame(zero_crossings_datetimes)


def itrf_find_poles_and_nodes(df):
    columns = ['x_itrf', 'y_itrf', 'z_itrf', 'vx_itrf', 'vy_itrf', 'vz_itrf']
    df_poles = find_zero_crossings(df[columns], column='vz_itrf', resolution='10ms')
    if len(df_poles) == 0:
        return pd.DataFrame()
    df_poles['type'] = df_poles.apply(lambda row: 'N'
                                      if row['z_itrf'] > 0
                                      else 'S', axis=1)
    df_equator = find_zero_crossings(df[columns], column='z_itrf', resolution='10ms')
    df_equator['type'] = df_equator.apply(lambda row: 'A'
                                          if row['vz_itrf'] > 0
                                          else 'D', axis=1)
    df_out = pd.concat([df_poles, df_equator], axis=0).sort_index()
    df_out = itrf_to_geodetic(df_out)[['type', 'lon', 'lat', 'height']]
    astropy_times = Time(pd.to_datetime(df_out.index, utc=True))
    sunlons = coord.get_sun(astropy_times).itrs.spherical.lon.value
    df_out['lst'] = (12 + ((df_out['lon'] - sunlons) / 15)) % 24
    return df_out


def itrf_orbit_arcs(df_itrf):
    df_poles_and_nodes = itrf_find_poles_and_nodes(df_itrf)
    lastn = None
    lasts = None
    lastan = None
    lastdn = None
    lastan_lon = None
    lastdn_lon = None
    lastn_lon = None
    lasts_lon = None
    lastan_lst = None
    lastdn_lst = None
    lastn_lst = None
    lasts_lst = None
    lastan_h = None
    lastdn_h = None
    lastn_h = None
    lasts_h = None
    orbital_period = pd.to_timedelta(60*100, 'min')
    arcs = []
    for t, row in df_poles_and_nodes.iterrows():
        if row['type'] == 'S':
            lasts = t
            lasts_lon = row['lon']
            lasts_lst = row['lst']
            lasts_h = row['height']
            if lastn is not None and abs(lasts - lastn) < orbital_period:
                arcs.append({'type': 'D',
                             't0': lastn,
                             'tmid': lastdn,
                             'lonmid': lastdn_lon,
                             'lstmid': lastdn_lst,
                             'hmid': lastdn_h,
                             't1': lasts,
                             'duration': lasts - lastn})
        elif row['type'] == 'N':
            lastn = t
            lastn_lon = row['lon']
            lastn_lst = row['lst']
            lastn_h = row['height']
            if lasts is not None and abs(lasts - lastn) < orbital_period:
                arcs.append({'type': 'A',
                             't0': lasts,
                             'tmid': lastan,
                             'lonmid': lastan_lon,
                             'lstmid': lastan_lst,
                             'hmid': lastan_h,
                             't1': lastn,
                             'duration': lastn - lasts})
        elif row['type'] == 'A':
            lastan = t
            lastan_lon = row['lon']
            lastan_lst = row['lst']
            lastan_h = row['height']
            if lastdn is not None and abs(lastdn - lastan) < orbital_period:
                arcs.append({'type': 'SH',
                             't0': lastdn,
                             'tmid': lasts,
                             'lonmid': lasts_lon,
                             'lstmid': lasts_lst,
                             'hmid': lasts_h,
                             't1': lastan,
                             'duration': lastan - lastdn})
        elif row['type'] == 'D':
            lastdn = t
            lastdn_lon = row['lon']
            lastdn_lst = row['lst']
            lastdn_h = row['height']
            if lastan is not None and abs(lastdn - lastan) < orbital_period:
                arcs.append({'type': 'NH',
                             't0': lastan,
                             'tmid': lastn,
                             'lonmid': lastn_lon,
                             'lstmid': lastn_lst,
                             'hmid': lastn_h,
                             't1': lastdn,
                             'duration': lastdn - lastan})
    return pd.DataFrame(arcs)
