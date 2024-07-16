import numpy as np
import pandas as pd
import scipy.interpolate
import pymsis.msis
from swxtools.access import penticton_f10
from swxtools.access import gfz_kp_hp_indices


msis_column_names = ['dens_msis2',
                     'N2',
                     'O2',
                     'O',
                     'He',
                     'H',
                     'Ar',
                     'N',
                     'O+',
                     'NO',
                     'T']

# Read in the space weather proxies and indices
df_f10 = penticton_f10.to_dataframe()
df_kpap = gfz_kp_hp_indices.to_dataframe(index_type='Kp')
df_Ap = gfz_kp_hp_indices.to_dataframe(index_type='Ap')

# Compute the 81-day rolling average F10.7
rolling = df_f10['f10_7'].rolling(window=pd.to_timedelta('81D'),
                                  closed='neither', center=True)
df_f107a = pd.DataFrame({'f10_7a': rolling.mean()})

# Set up the interpolators
f10_7_interpolator = scipy.interpolate.interp1d(
    x=df_f10.index.values.astype(float),
    y=df_f10['f10_7'].values,
    kind='previous')

f10_7a_interpolator = scipy.interpolate.interp1d(
    x=df_f10.index.values.astype(float),
    y=df_f107a['f10_7a'].values,
    kind='previous')

Ap_interpolator = scipy.interpolate.interp1d(
    x=df_Ap.index.values.astype(float),
    y=df_Ap['Ap'].values,
    kind='previous')

ap3h_interpolator = scipy.interpolate.interp1d(
    x=df_kpap.index.values.astype(float),
    y=df_kpap['ap'].values, kind='previous')


def ap3h_avg(dt_index, ap3h_interpolator, time_hours=[0]):
    apsum = 0
    for hours in time_hours:
        apsum = apsum + ap3h_interpolator(
            (dt_index - pd.to_timedelta(hours, 'h')).values.astype(float)
        )
    return apsum/len(time_hours)


def to_dataframe(dt_index, lon, lat, height, include_proxies=True, override_f107=None):
    floattime = dt_index.values.astype(float)
    prevday_index = dt_index - pd.to_timedelta(1, 'D')
    floattime_prevday = prevday_index.values.astype(float)
    data = pd.DataFrame(index=dt_index)
    data['lon'] = lon
    data['lat'] = lat
    data['height'] = height
    if override_f107 is None:
        data['f10_7'] = f10_7_interpolator(floattime_prevday)
        data['f10_7a'] = f10_7a_interpolator(floattime)
    else:
        data['f10_7'] = np.array(override_f107).item()
        data['f10_7a'] = np.array(override_f107).item()
    data['Ap'] = Ap_interpolator(floattime)
    data['ap1'] = ap3h_avg(dt_index, ap3h_interpolator, [0])
    data['ap2'] = ap3h_avg(dt_index, ap3h_interpolator, [3])
    data['ap3'] = ap3h_avg(dt_index, ap3h_interpolator, [6])
    data['ap4'] = ap3h_avg(dt_index, ap3h_interpolator, [9])
    data['ap5'] = ap3h_avg(dt_index, ap3h_interpolator,
                           [12, 15, 18, 21, 24, 27, 30, 33])
    data['ap6'] = ap3h_avg(dt_index, ap3h_interpolator,
                           [36, 39, 42, 45, 48, 51, 54, 57])
    apvalues = data[['Ap', 'ap1', 'ap2', 'ap3', 'ap4', 'ap5', 'ap6']].values
    msisoptions = pymsis.msis.create_options(geomagnetic_activity=-1)
    msisout = pymsis.msis.run(dates=dt_index.values,
                              lons=data['lon'].values,
                              lats=data['lat'].values,
                              alts=data['height'].values,
                              f107s=data['f10_7'].values,
                              f107as=data['f10_7a'].values,
                              aps=apvalues, options=msisoptions, version=2)

    df_msis = pd.DataFrame(data=msisout,
                           index=dt_index,
                           columns=msis_column_names)
    if include_proxies:
        df_proxies = pd.DataFrame(data=data, index=dt_index)
        df_msis = pd.concat([df_msis, df_proxies], axis=1)

    return df_msis
