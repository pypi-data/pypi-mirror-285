#!/usr/bin/env python3
import numpy as np
import pandas as pd

# Processing of IMAGE mission data, to add geolocation information.
# Currently tested with FUV WIC data from:
# https://cdaweb.gsfc.nasa.gov/pub/data/image/fuv/wic_k0/
#
# Based on IDL code shared by Steve Milan, Univ. of Leicester,
# ported to Python by Eelco Doornbos, KNMI.
#
# TODO:
# 1. Add further code to be able to align/stabilise images and overlay
# coastlines, graticules and other datasets for use in the KNMI space weather
# timeline viewer.
# 2. Replace transform matrices using Astropy and/or
# scipy.spatial.transform.Rotation


def gei2geo(datetime):
    # Convert from Python datetime to Pandas timestamp
    dt = pd.to_datetime(datetime, utc=True)
    # Julian date
    jd = dt.to_julian_date()
    # Modified julian date
    mjd = jd-2400000.5
    # Time in centuries from 12 UT on 1 Jan. 2000
    t0 = (mjd - 51544.5) / 36525.0
    # UT time of day in seconds
    ut = (dt - dt.floor('D')) / pd.to_timedelta(1, 'sec')
    # Greenwhich mean sidereal time
    theta = 100.461 + 36000.770 * t0 + 15.04107 * ut

    cos_theta = np.cos(np.radians(theta))
    sin_theta = np.sin(np.radians(theta))

    # Define transformation from Geocentric Equatorial Inertial (GEI)
    #   to Geographic (GEO) Cartesian coordinates
    gei2geo = [[cos_theta,  sin_theta, 0, 0],
               [-sin_theta, cos_theta, 0, 0],
               [0,          0,         1, 0],
               [0,          0,         0, 1]]

    return gei2geo


def gei2gse(datetime):
    # Convert from Python datetime to Pandas timestamp
    dt = pd.to_datetime(datetime, utc=True)
    # Julian date
    jd = dt.to_julian_date()
    # Modified julian date
    mjd = jd-2400000.5
    # Time in centuries from 12 UT on 1 Jan. 2000
    t0 = (mjd - 51544.5) / 36525.0
    # UT time of day in seconds
    ut = (dt - dt.floor('D')) / pd.to_timedelta(1, 'sec')

    # Obliquity of the ecliptic (rad)
    epsilon = 23.439-0.013*t0
    # Mean anomaly of the Sun
    mean_anomaly_sun = 357.528 + 35999.050 * t0 + 0.04107 * ut
    # Mean longitude of the Sun
    mean_longitude_sun = 280.460 + 36000.772 * t0 + 0.04107 * ut
    # Ecliptic longitude of the Sun (deg)
    lambda_sun = (mean_longitude_sun + (1.915 - 0.0048 * t0) *
                  np.sin(np.radians(mean_anomaly_sun)) +
                  0.020 * np.sin(np.degrees(2*mean_anomaly_sun)))

    # cos and sin of the angles
    cos_lambda = np.cos(np.radians(lambda_sun))
    sin_lambda = np.sin(np.radians(lambda_sun))
    cos_eps = np.cos(np.radians(epsilon))
    sin_eps = np.sin(np.radians(epsilon))

    # Define transformation maxtrix from GEI to Geocentric Solar Ecliptic (GSE)
    # Rotate around X from equatorial to ecliptic
    gei2gse_1 = [[1, 0,        0,       0],
                 [0, cos_eps,  sin_eps, 0],
                 [0, -sin_eps, cos_eps, 0],
                 [0, 0,        0,       1]]

    # Rotate around Z, towards the longitude of the Sun
    gei2gse_2 = [[cos_lambda,  sin_lambda, 0, 0],
                 [-sin_lambda, cos_lambda, 0, 0],
                 [0,           0,          1, 0],
                 [0,           0,          0, 1]]

    gei2gse = np.matmul(gei2gse_2, gei2gse_1)
    return gei2gse

    # Define transformation maxtrix from GEO to GSE
    # geo2gse = np.matmul(gei2gse, np.linalg.inv(gei2geo))
    # return geo2gse


def fuv2gei(cdfdata, i):
    inst_roll = cdfdata['INST_ROLL'][...]
    inst_azimuth = cdfdata['INST_AZIMUTH'][...]
    inst_co_elevation = cdfdata['INST_CO_ELEVATION'][...]
    scsv_x = cdfdata['SCSV_X'][i]
    scsv_y = cdfdata['SCSV_Y'][i]
    scsv_z = cdfdata['SCSV_Z'][i]
    spin_axis_x = cdfdata['SV_X'][i]
    spin_axis_y = cdfdata['SV_Y'][i]
    spin_axis_z = cdfdata['SV_Z'][i]
    spin_phase = cdfdata['SPINPHASE'][i]

    sin_roll = np.sin(np.radians(inst_roll))
    cos_roll = np.cos(np.radians(inst_roll))
    sin_azim = np.sin(np.radians(inst_azimuth))
    cos_azim = np.cos(np.radians(inst_azimuth))
    sin_coel = np.sin(np.radians(inst_co_elevation))
    cos_coel = np.cos(np.radians(inst_co_elevation))
    cos_psi = np.cos(np.radians(spin_phase))
    sin_psi = np.sin(np.radians(spin_phase))

    sin_beta = scsv_x
    cos_beta = np.sqrt(1-scsv_x**2)
    sin_alpha = scsv_y/cos_beta
    cos_alpha = scsv_z/cos_beta

    cos_eta = spin_axis_z / cos_beta
    sin_eta = np.sqrt(1-scsv_x**2 - spin_axis_z**2) / cos_beta
    cos_delta = ((scsv_x * spin_axis_x +
                  spin_axis_y * np.sqrt(1-scsv_x**2 - spin_axis_z**2)) /
                 (1-spin_axis_z**2))
    sin_delta = ((scsv_x * spin_axis_y -
                  spin_axis_x * np.sqrt(1-scsv_x**2 - spin_axis_z**2)) /
                 (1-spin_axis_z**2))

    t1a = [[cos_roll, -sin_roll, 0, 0],
           [sin_roll, cos_roll,  0, 0],
           [0,        0,         1, 0],
           [0,        0,         0, 1]]

    t1b = [[1, 0,         0,         0],
           [0, -sin_coel, -cos_coel, 0],
           [0, cos_coel,  -sin_coel, 0],
           [0, 0,         0,         1]]

    t1c = [[sin_azim,   cos_azim, 0, 0],
           [-cos_azim,  sin_azim, 0, 0],
           [0,          0,        1, 0],
           [0,          0,        0, 1]]

    t2a = [[1, 0,         0,          0],
           [0, cos_alpha, -sin_alpha, 0],
           [0, sin_alpha, cos_alpha,  0],
           [0, 0,         0,          1]]

    t2b = [[cos_beta, 0, -sin_beta, 0],
           [0,        1, 0,         0],
           [sin_beta, 0, cos_beta,  0],
           [0,        0, 0,         1]]

    t3a = [[cos_psi, -sin_psi, 0, 0],
           [sin_psi, cos_psi,  0, 0],
           [0,       0,        1, 0],
           [0,       0,        0, 1]]

    t3b = [[cos_beta,  0, sin_beta,  0],
           [0,         1, 0,         0],
           [-sin_beta, 0, cos_beta,  0],
           [0,         0, 0,         1]]

    t3c = [[1, 0,        0,       0],
           [0, cos_eta,  sin_eta, 0],
           [0, -sin_eta, cos_eta, 0],
           [0, 0,        0,       1]]

    t3d = [[cos_delta, -sin_delta, 0, 0],
           [sin_delta, cos_delta,  0, 0],
           [0,         0,          1, 0],
           [0,         0,          0, 1]]

    t1 = np.matmul(t1c, np.matmul(t1b, t1a))
    t2 = np.matmul(t2b, t2a)  # This seems to be always the unit matrix!
    t3 = np.matmul(t3d, np.matmul(t3c, np.matmul(t3b, t3a)))
    fuv_gei = np.matmul(t3, np.matmul(t2, t1))

    return fuv_gei


def map_fuv_pixel(epoch, x, y, res_x, res_y, image_pos_gei, h, fuv_gei):
    # Find look direction in FUV system
    look = [np.tan(np.radians((x-127.5)*res_x)),
            np.tan(np.radians((y-127.5)*res_y)),
            -1,
            1]
    look = np.matmul(fuv_gei, look)
    # Test to see if look direction intersects planet
    a = look[0]**2 + look[1]**2 + look[2]**2
    b = 2 * (image_pos_gei[0] * look[0] +
             image_pos_gei[1] * look[1] +
             image_pos_gei[2] * look[2])
    c = (image_pos_gei[0]**2 +
         image_pos_gei[1]**2 +
         image_pos_gei[2]**2 -
         (1+h)**2)

    if (b**2-4*a*c) >= 0:
        mu = (-b-np.sqrt(b**2-4*a*c))/(2*a)
        # Find GEI position of intersection
        gei_pos = [image_pos_gei[0] + mu * look[0],
                   image_pos_gei[1] + mu * look[1],
                   image_pos_gei[2] + mu * look[2],
                   1]
        # Convert to GEO position
        geo_pos = np.matmul(gei2geo(epoch), gei_pos)
        # Convert to geographic lat and lon
        geo_lat = np.degrees(np.arctan2(geo_pos[2],
                             np.sqrt(geo_pos[0]**2 + geo_pos[1]**2)))
        geo_lon = np.degrees(np.arctan2(geo_pos[1], geo_pos[0]))
        return {'on_disc': 1,
                'geo_lat': geo_lat,
                'geo_lon': geo_lon}
    else:
        return {'on_disc': 0,
                'geo_lat': np.nan,
                'geo_lon': np.nan}


def map_fuv(cdfdata, i, h_emis=None):
    on_disc = np.full((256, 256), 0)
    geo_lats = np.full((256, 256), np.nan)
    geo_lons = np.full((256, 256), np.nan)

    res_x = cdfdata['VFOV'][...] / 256.0
    res_y = cdfdata['VFOV'][...] / 256.0

    if h_emis is not None:
        h = h_emis / 6371.0
    else:
        h = 0.0

    fuv_gei = fuv2gei(cdfdata, i)
    image_pos_gei = np.array([cdfdata['ORB_X'][i],
                              cdfdata['ORB_Y'][i],
                              cdfdata['ORB_Z'][i]])/6371.0
    epoch = cdfdata['EPOCH'][i]
    for x in range(256):
        for y in range(256):
            pixel_info = map_fuv_pixel(epoch, x, y,
                                       res_x, res_y,
                                       image_pos_gei,
                                       h, fuv_gei)
            on_disc[x, y] = pixel_info['on_disc']
            geo_lats[x, y] = pixel_info['geo_lat']
            geo_lons[x, y] = pixel_info['geo_lon']

    return {'on_disc': on_disc,
            'geo_lats': geo_lats,
            'geo_lons': geo_lons}


def gei2fuv_pixel(cdfdata, i, gei_pos):
    fuv_gei = fuv2gei(cdfdata, i)
    gei_fuv = np.linalg.inv(fuv_gei)

    image_pos_gei = np.array([cdfdata['ORB_X'][i],
                              cdfdata['ORB_Y'][i],
                              cdfdata['ORB_Z'][i]])/6371.0

    gei_diff = image_pos_gei - gei_pos
    fuv_pos = np.matmul(gei_fuv, [gei_diff[0], gei_diff[1], gei_diff[2], 1])

    angle_x = np.degrees(np.arctan2(fuv_pos[0], fuv_pos[2]))
    angle_y = np.degrees(np.arctan2(fuv_pos[1], fuv_pos[2]))

    res_x = cdfdata['VFOV'][...] / 256.0
    res_y = cdfdata['VFOV'][...] / 256.0

    fuv_x = -angle_x / res_x + 127
    fuv_y = -angle_y / res_y + 127

    return np.array([fuv_x, fuv_y, fuv_pos[2]])


# FUNCTION gse2fuv_pixel,gse_pos,image_pos,res_x,res_y
#
#             ; Find FUV pixel position given gse coordinates
#             ; Need - position of IMAGE s/c in GEI and angular resolutions of pixels in x and y directions
#
#             COMMON transformations,gei2geo,gei2gse,geo2gse,fuv2gei
#
#             gei_pos=INVERT(gei2gse)##gse_pos
#             fuv_pos=INVERT(fuv2gei)##[image_pos(0:2)-gei_pos(0:2),1]
#
#             angle_x=ATAN(fuv_pos(0),fuv_pos(2))*!radeg
#             angle_y=ATAN(fuv_pos(1),fuv_pos(2))*!radeg
#
#             fuv_x=-angle_x/res_x+127
#             fuv_y=-angle_y/res_y+127
#
#             RETURN,[fuv_x,fuv_y,fuv_pos(2)]
#             END
