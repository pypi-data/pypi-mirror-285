# Module for obtaining Cartesian coordinates along a Keplerian orbit, or for an orbit which 
# includes secular J2-perturbation effects on the argument of perigee and right ascension of 
# the ascending node.
#
# First version by Eelco Doornbos, KNMI, April 4, 2020

import numpy as np

def kepler_to_cartesian(kepler, trueanomaly):
    '''Calcuates the inertial cartesian coordinates along a Keplerian orbit, based on the
    Keplerian elements.

    Keyword arguments:
    kepler (dict) -- A dict of floats containing values for:
         mu                -- the central body's gravitational parameter in km^{3}/s^{-2}
         semimajoraxis     -- the orbit's semi-major axis in km
         eccentricity      -- the orbit's eccentricity
         inclination       -- the orbit's inclination
         argumentofperigee -- the orbit's argument of perigee in radians
         raan              -- the orbit's right-ascension of the ascending node in radians
    trueanomaly (float) -- the true anomaly in radians

    Returns:
    cartesian (array) -- 6-element numpy array containing the Cartesian position and velocity vector components
    '''    
    costheta = np.cos(trueanomaly)
    sintheta = np.sin(trueanomaly)
    cosargper = np.cos(kepler["argumentofperigee"])
    sinargper = np.sin(kepler["argumentofperigee"])
    cosraan = np.cos(kepler["raan"])
    sinraan = np.sin(kepler["raan"])
    cosi = np.cos(kepler["inclination"])
    sini = np.sin(kepler["inclination"])
    eccentricity = kepler["eccentricity"]
    semimajoraxis = kepler["semimajoraxis"]
    mu = kepler["mu"]

    l1 = cosargper * cosraan - sinargper * sinraan * cosi
    m1 = cosargper * sinraan + sinargper * cosraan * cosi
    n1 = sinargper * sini
    l2 = -sinargper * cosraan - cosargper * sinraan * cosi
    m2 = -sinargper * sinraan + cosargper * cosraan * cosi
    n2 = cosargper * sini

    r = semimajoraxis * (1 - eccentricity**2) / (1 + eccentricity * costheta)
    x = r * (l1 * costheta + l2 * sintheta)
    y = r * (m1 * costheta + m2 * sintheta)
    z = r * (n1 * costheta + n2 * sintheta)

    angularmomentum = np.sqrt(mu * semimajoraxis * (1 - eccentricity**2))
    muoverh = mu / angularmomentum
    xdot = muoverh * (-l1 * sintheta + l2 * (eccentricity + costheta))
    ydot = muoverh * (-m1 * sintheta + m2 * (eccentricity + costheta))
    zdot = muoverh * (-n1 * sintheta + n2 * (eccentricity + costheta))
    return np.array((x, y, z, xdot, ydot, zdot))


def true_anomaly_from_mean_anomaly(mean_anomaly, eccentricity):
    '''For an elliptical Keplerian orbit, calculate the true anomaly from the mean anomaly 
    and eccentricity, by solving Kepler's equation.

    Keyword arguments: 
    mean_anomaly (float) -- the mean anomaly in radians
    eccentricity (float) -- the eccentricity, which should have a value larger or equal to zero and smaller than one
    
    Returns:
    true_anomaly (float) -- the true anomaly in radians'''
    # Written by Eelco Doornbos, based on Karel Wakker, Fundamentals of astrodynamics, section 6.5
    convergence = 999.99;
    if eccentricity < 0.95:
        eccentric_anomaly_old = mean_anomaly
        iterations = 0
        while convergence > 1e-6:
            iterations = iterations + 1
            eccentric_anomaly_new = mean_anomaly + eccentricity * np.sin(eccentric_anomaly_old)
            convergence = np.abs(eccentric_anomaly_old - eccentric_anomaly_new)
            if iterations > 100:
                print("Too many iterations!") # TODO: error handling
                break
            eccentric_anomaly_old = eccentric_anomaly_new
    else:
        print("True anomaly can only be calculated for elliptical orbits.") # TODO: error handling
    true_anomaly = 2.0*np.arctan(np.sqrt((1+eccentricity)/(1.0-eccentricity))*np.tan(0.5 * eccentric_anomaly_new));        
    return true_anomaly


def unperturbed_mean_motion(kepler):
    '''Calcuates the unperturbed mean motion of a Keplerian orbit, based on the gravitational parameter
    and semi-major axis of the orbit.

    Keyword arguments:
    kepler (dict) -- A dict of floats containing values for:
         mu            -- the central body's gravitational parameter in km^{3}/s^{-2}
         semimajoraxis -- the orbit's semi-major axis in km

    Returns:
    unperturbed_mean_motion (float) -- the mean motion in radians/s
    '''
    # Written by Eelco Doornbos, based on Karel Wakker, Fundamentals of astrodynamics, equation (6.27)
    return np.sqrt(kepler["mu"] / np.power(kepler["semimajoraxis"], 3))


def perturbed_mean_motion(kepler):
    '''Calcuates the perturbed mean motion of a Keplerian orbit, based on the gravitational parameter,
    secular J2-effect, eccentricity, inclination and semi-major axis of the orbit.

    Keyword arguments:
    kepler (dict) -- A dict of floats containing values for:
         mu            -- the central body's gravitational parameter in km^{3}/s^{-2}
         j2            -- the J2 term of the gravity field
         re            -- the central body radius
         semimajoraxis -- the orbit's semi-major axis in km
         eccentricity  -- the orbit's eccentricity
         inclination   -- the orbit's inclination

    Returns:
    perturbed_mean_motion (float) -- the mean motion in radians/s
    '''
    # Written by Eelco Doornbos, based on Karel Wakker, Fundamentals of astrodynamics, equation (23.27)
    return unperturbed_mean_motion(kepler) * (1 + 0.75*kepler["j2"]*(kepler["re"]/kepler["semimajoraxis"])**2 *
         np.power(1-kepler["eccentricity"]**2, -3/2)*(3*np.cos(kepler["inclination"])**2-1))



def unperturbed_orbitalperiod(kepler):
    return 2*np.pi * np.sqrt(np.power(kepler["semimajoraxis"],3)/kepler["mu"])


def d_raan_j2_dM(kepler):
    # Karel Wakker, Fundamentals of astrodynamics, equation (23.37) - divided by 2*pi
    p = kepler["semimajoraxis"] * (1 - kepler["eccentricity"]**2)
    return -3/2 * kepler["j2"] * (kepler["re"] / p)**2 * np.cos(kepler["inclination"])


def d_argper_j2_dM(kepler):
    # Karel Wakker, Fundamentals of astrodynamics, equation (23.37) - divided by 2*pi
    p = kepler["semimajoraxis"] * (1 - kepler["eccentricity"]**2)    
    return 3.0/4.0 * kepler["j2"] * (kepler["re"] / p)**2 * (5 * np.cos(kepler["inclination"])**2 - 1)


def simulate_orbit(kepler, times):
    initial_mean_anomaly = kepler['initial_mean_anomaly']
    initial_argper = kepler['argumentofperigee']
    initial_raan = kepler['raan']
    mean_motion = perturbed_mean_motion(kepler)
    d_raan_j2 = d_raan_j2_dM(kepler)
    d_argper_j2 = d_argper_j2_dM(kepler)
    data = []
    for time in times:
        mean_anomaly = initial_mean_anomaly + time * mean_motion
        kepler['argumentofperigee'] = initial_argper + d_argper_j2 * mean_anomaly
        kepler['raan'] = initial_raan + d_raan_j2 * mean_anomaly
        #if kepler['raan'] > np.pi * 2:
        #    kepler['raan']
        true_anomaly = true_anomaly_from_mean_anomaly(mean_anomaly, kepler["eccentricity"])
        vec = kepler_to_cartesian(kepler, true_anomaly)
        data.append(vec)
        #print(np.degrees(kepler['inclination']), np.degrees(kepler['raan']), np.degrees(kepler['argumentofperigee']))
    return data

if __name__ == "__main__":
    import pandas as pd
    # Set the Keplerian elements and associated parameters in a dict - this example uses and ESA EE10 Daedalus phase 0 orbit as an example
    kepler = {
        "semimajoraxis": 6378.2 + 1075,
        "eccentricity": 0.12,
        "inclination": np.radians(85.0),
        "argumentofperigee": np.radians(90.0),
        "raan": np.radians(0.0),
        "initial_mean_anomaly": 0.0,
        "mu": 398600.4415,
        "re": 6378.1363,
        "j2": 1082.6357e-6
    }
    perigeeradius = 6507.0
    apogeeradius = 8357.0
    kepler["semimajoraxis"] = (perigeeradius + apogeeradius) / 2
    kepler["eccentricity"] = (apogeeradius - perigeeradius) / (apogeeradius + perigeeradius)

    # Example 1, calculate a single orbit
    start_time = pd.to_datetime("2008-01-01T00:00:00")
    times_sec = np.linspace(0, unperturbed_orbitalperiod(kepler), 100)
    time_index = start_time + pd.to_timedelta(times_sec, 's')
    orbit1 = simulate_orbit(kepler, times_sec)
    df_orbit1 = pd.DataFrame(data=orbit1, index=time_index, columns = ['x', 'y', 'z', 'vx', 'vy', 'vz'])

    # Example 2, an orbit with a fixed time step
    time_index = pd.date_range(start=pd.to_datetime("2008-01-01T00:00:00"), end=pd.to_datetime("2011-01-01T00:00:00"), freq='1min')
    times_sec = (time_index - time_index[0])/pd.to_timedelta(1,'s')
    orbit2 = simulate_orbit(kepler, times_sec)
    df_orbit2 = pd.DataFrame(data=orbit2, index=time_index, columns = ['x', 'y', 'z', 'vx', 'vy', 'vz'])    
