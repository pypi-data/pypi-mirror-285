import os
import tarfile
import numpy as np
import pandas as pd
import xarray as xr
import logging
from scipy.integrate import cumulative_trapezoid
from scipy.interpolate import interp1d


var_attributes_ipe = {
    'O_plus_density': {'long_name': 'Number density of O+', 'unit': 'm-3'},
    'H_plus_density': {'long_name': 'Number density of H+', 'unit': 'm-3'},
    'He_plus_density': {'long_name': 'Number density of He+', 'unit': 'm-3'},
    'N_plus_density': {'long_name': 'Number density of N+', 'unit': 'm-3'},
    'NO_plus_density': {'long_name': 'Number density of NO+', 'unit': 'm-3'},
    'O2_plus_density': {'long_name': 'Number density of O2+', 'unit': 'm-3'},
    'N2_plus_density': {'long_name': 'Number density of N2+', 'unit': 'm-3'},
    'ion_temperature': {'long_name': 'Ion temperature', 'unit': 'K'},
    'electron_temperature': {'long_name': 'Electron temperature', 'unit': 'K'},
    'eastward_exb_velocity': {'long_name': 'Eastward ExB velocity', 'unit': 'm/s'},
    'northward_exb_velocity': {'long_name': 'Northward ExB velocity', 'unit': 'm/s'},
    'upward_exb_velocity': {'long_name': 'Upward ExB velocity', 'unit': 'm/s'},
    'electron_density': {'long_name': 'Electron density', 'unit': 'cm-3'},
    'VTEC_below': {'long_name': 'Vertical total electron content below the location', 'unit': '10+16 m-2'},
    'VTEC_above': {'long_name': 'Vertical total electron content above the location', 'unit': '10+16 m-2'},
    'latitude': {'long_name': 'Geodetic latitude', 'unit': 'degrees_north'},
    'longitude': {'long_name': 'Longitude', 'unit': 'degrees_east'},
    'altitude': {'long_name': 'Altitude', 'unit': 'km'},
}

var_attributes_wam = {
    'latitude': {'long_name': 'Geodetic latitude', 'unit': 'degrees north'},
    'longitude': {'long_name': 'Geographic longitude', 'unit': 'degrees east'},
    'altitude': {'long_name': 'Altitude', 'unit': 'km'},
    'log10_O_Density': {'long_name': 'Log10 of O number density', 'unit': 'lg m-3'},
    'log10_O2_Density': {'long_name': 'Log10 of O2 number density', 'unit': 'lg m-3'},
    'log10_N2_Density': {'long_name': 'Log10 of N2 number density', 'unit': 'lg m-3'},
    'temp_neutral': {'long_name': 'Temperature', 'unit': 'K'},
    'u_neutral': {'long_name': 'Eastward wind velocity', 'unit': 'm/s'},
    'v_neutral': {'long_name': 'Northward wind velocity', 'unit': 'm/s'},
    'w_neutral': {'long_name': 'Upward wind velocity', 'unit': 'm/s'},
    'mass_density': {'long_name': 'Neutral mass density', 'unit': 'kg m-3'},
}

def nc_file_name_extract_date(nc_file_name):
    return pd.to_datetime(nc_file_name.split('.')[-2].replace('_', 'T'), utc=True).to_numpy()


def time_to_t_run(time):
    run_freq = pd.to_timedelta('6H')
    run_offset = pd.to_timedelta('3H')-pd.to_timedelta('5min')
    return (time+run_offset).floor('6H')


def _nc_file_obj_to_xr(nc_file_obj, timestamp):
    xrdata_in = xr.open_dataset(nc_file_obj)
    var_arrays = {}
    variable_names = [key for key in xrdata_in.variables.keys() if key not in ['lon', 'lat', 'alt']]
    for var in variable_names:
        if len(xrdata_in[var].dims) == 2:
            var_array = xr.DataArray(data=xrdata_in[var].data[np.newaxis, ...],
                                     coords={'time': np.array([timestamp]),
                                             'longitude': xrdata_in['lon'].data,
                                             'latitude': xrdata_in['lat'].data},
                                     dims=('time', 'latitude', 'longitude'))
        else:
            if 'alt' in xrdata_in.variables.keys():
                var_array = xr.DataArray(data=xrdata_in[var].data[np.newaxis, ...],
                                        coords={'time': np.array([timestamp]),
                                                'altitude': xrdata_in['alt'].data,
                                                'longitude': xrdata_in['lon'].data,
                                                'latitude': xrdata_in['lat'].data},
                                        dims=('time', 'altitude', 'latitude', 'longitude'))
            elif 'height' in xrdata_in.variables.keys():
                var_array = xr.DataArray(data=xrdata_in[var].data[np.newaxis, ...],
                                        coords={'time': np.array([timestamp]),
                                                'level': xrdata_in['x03'].data,
                                                'longitude': xrdata_in['lon'].data,
                                                'latitude': xrdata_in['lat'].data},
                                        dims=('time', 'level', 'latitude', 'longitude'))
            else:
                raise ValueError("Unknown structure of WAM-IPE NetCDF file")
        var_arrays[var] = var_array
    return xr.Dataset(var_arrays)

def _tar_file_to_xr(tar_file_name):
    with tarfile.open(tar_file_name) as t:
        nc_file_list = t.getnames()
        nc_file_list.sort()
        xarrays = []
        nc_files_opened = []
        for nc_file_name in nc_file_list:
            try:
                nc_file_obj = t.extractfile(nc_file_name)
                timestamp = nc_file_name_extract_date(nc_file_name)
                xarrays.append(_nc_file_obj_to_xr(nc_file_obj, timestamp))
                nc_files_opened.append(nc_file_name)
            except ValueError as e:
                logging.error(f"There was an error reading {nc_file_name}: {e}")
        if len(xarrays) > 0:
            # print(xarrays)
            output = xr.concat(xarrays, dim='time')
            output.assign_attrs({'nc_files_opened': ','.join(nc_files_opened)})
            return output
        else:
            return None


class wam_ipe_archive():

    def __init__(self,
                 forecast_nowcast="nowcast",
                 output_type="ipe05",
                 archive_root = '/Volumes/datasets/wam-ipe/archive/',
                 archive_subdir = lambda t: f"{t.year:04d}/{t.month:02d}/{t.day:02d}/" ):
        self.forecast_nowcast = forecast_nowcast
        self.output_type = output_type
        self.archive_subdir = archive_subdir
        if os.path.isdir(archive_root):
            self.archive_root = archive_root
        else:
            raise ValueError(f"Archive root path <{archive_root}> does not exist")


    def _tar_file_name(self, t_run):
        t = pd.to_datetime(t_run).round('6H')
        archive_dir = self.archive_root + self.archive_subdir(t)
        return archive_dir + f"wam-ipe_{t.strftime('%Y-%m-%dT%H')}_{self.forecast_nowcast}_{self.output_type}.tar"


    def _time_to_file_names(self, time):
        if self.output_type == 'wam' and (time.tz_localize('utc') <
                                          pd.to_datetime("2023-10-01T")):
            output_type = 'gsm'
        else:
            output_type = self.output_type
        t_run = time_to_t_run(time)
        tar_file_name_out = self._tar_file_name(t_run)
        nc_file_name_out = f"wam-ipe_{t_run.strftime('%Y-%m-%dT%H')}_{self.forecast_nowcast}_{self.output_type}/wfs.t{t_run.hour:02d}z.{output_type}.{time.strftime('%Y%m%d_%H%M%S')}.nc"
        return tar_file_name_out, nc_file_name_out

    def to_xr_at_model_time(self, time):
        time_rounded = time.round('5min')
        (tar_file_name, nc_file_name) = self._time_to_file_names(time_rounded)
        with tarfile.open(tar_file_name) as t:
            nc_file_obj = t.extractfile(nc_file_name)
            timestamp = nc_file_name_extract_date(nc_file_name)
            output = _nc_file_obj_to_xr(nc_file_obj, timestamp)
        return output

    def set_time_interval(self, t0, t1):
        self.t0 = pd.to_datetime(t0, utc=True)
        self.t1 = pd.to_datetime(t1, utc=True)

    def to_xrdata(self):
        time_range = pd.date_range(self.t0.floor('6H'), self.t1.ceil('6H'), freq='6H')
        xarrays = []
        for time in time_range:
            tar_file_name = self._tar_file_name(time)
            if os.path.isfile(tar_file_name):
                logging.info(f"Reading {tar_file_name}")
                xarrays.append(_tar_file_to_xr(tar_file_name))
            else:
                logging.info(f"{tar_file_name} does not exist.")
        if len(xarrays) > 0:
            output = xr.concat(xarrays, dim='time')
            self.xrdata = output
            self._compute_derived_fields()
            return output
        else:
            return None

    def _compute_derived_fields(self):
        if self.output_type == 'ipe10':
            # Compute the total electron density, equal to the sum of the ion densities
            self.xrdata['electron_density'] = (
                self.xrdata['O_plus_density'] +
                self.xrdata['H_plus_density'] +
                self.xrdata['He_plus_density'] +
                self.xrdata['N_plus_density'] +
                self.xrdata['NO_plus_density'] +
                self.xrdata['O2_plus_density'] +
                self.xrdata['N2_plus_density'])

            # Compute the TEC above each height level (to be interpolated to
            # satellite height.

            # First step is  computing the cumulative TEC as a function of altitude
            # divide by 1e13, because 1 TECU is 1e16 el/m2, and electron density is
            # per cm2.
            vtec_below = cumulative_trapezoid(
                y=self.xrdata['electron_density']/1e13,
                x=self.xrdata['altitude'],
                axis=1,
                initial=0
            )
            dims = ('time', 'altitude', 'latitude', 'longitude')
            self.xrdata['VTEC_below'] = (dims, vtec_below)

            # The total TEC is the cumulative TEC at the highest altitude
            vtec_max = vtec_below[:,-1,:,:]

            # The TEC above each altitude is the total TEC minus the TEC below
            self.xrdata['VTEC_above'] = (dims, vtec_max[:,np.newaxis,:,:] - vtec_below)

        elif self.output_type == 'wam10' or self.output_type == 'gsm10':
            # Compute the log10 for more accurate linear interpolation
            for var in ['O_Density', 'O2_Density', 'N2_Density']:
                self.xrdata[f'log10_{var}'] = np.log10(self.xrdata[var])
        return self.xrdata

    def along_orbit(self, df_orbit):
        self.set_time_interval(df_orbit.index[0], df_orbit.index[-1])
        if self.output_type == 'ipe10':
            return self.along_orbit_ipe(df_orbit)
        elif self.output_type == 'wam10' or self.output_type == 'gsm10':
            return self.along_orbit_wam(df_orbit)
        else:
            logging.error("Please select output_type='ipe10' or 'wam10' for IPE interpolation along orbit")
            return

    def along_orbit_ipe(self, df_orbit):
        '''Interpolate the WAM-IPE ionospheric output along the orbit of a satellite.
        '''
        # Get the WAM-IPE data for the time period of the orbit
        xrdata = self.to_xrdata()
        if not xrdata:
            logging.info("No WAM-IPE data found")
            return

        logging.info("Starting interpolation")
        interp_output = xrdata.interp(time=pd.Series(index=df_orbit.index,
                                                     data=df_orbit.index).to_xarray(),
                                      latitude=df_orbit['lat'].to_xarray(),
                                      longitude=(df_orbit['lon']%360.0).to_xarray(),
                                      altitude=(df_orbit['height']/1e3).to_xarray())
        interp_output = interp_output.reset_coords().drop('time').rename({'index': 'time'})

        for var in list(interp_output.keys()):
            if var in var_attributes_ipe:
                interp_output[var] = interp_output[var].assign_attrs(var_attributes_ipe[var])

        interp_output.assign_attrs(xrdata.attrs)
        return interp_output

    def along_orbit_wam(self, df_orbit):
        '''Interpolate the WAM-IPE neutral output along the orbit of a satellite.'''
        # Get the WAM-IPE data for that time period
        xrdata = self.to_xrdata()
        if not xrdata:
            logging.info("No WAM-IPE data found")
            return

        logging.info("Starting interpolation")
        # First interpolate for the right time, lat and lon.
        # The interpolation returns the data in the form of height columns
        interp_height_columns = xrdata.interp(
                                    time=pd.Series(index=df_orbit.index,
                                                   data=df_orbit.index).to_xarray(),
                                    latitude=df_orbit['lat'].to_xarray(),
                                    longitude=(df_orbit['lon']%360.0).to_xarray()
                                             )
        interp_height_columns = interp_height_columns.reset_coords().drop('time').rename({'index': 'time'})

        # Set up output dataset
        interp_output = xr.Dataset(coords={'time': df_orbit.index.values})
        interp_output['latitude'] = ('time', df_orbit['lat'].values)
        interp_output['longitude'] = ('time', df_orbit['lon'].values)
        interp_output['altitude'] = ('time', df_orbit['height'].values*1e-3)

        # Interpolate with height for each of the relevant variables
        vars_to_interp_with_h = ['log10_O_Density', 'log10_O2_Density', 'log10_N2_Density', 'temp_neutral', 'u_neutral', 'v_neutral', 'w_neutral']
        data_dict = {key: [] for key in vars_to_interp_with_h}
        for t in interp_output['time'].data:
            h_profile = interp_height_columns.sel(time=t)
            # Check if satellite height is below max model height:
            if df_orbit['height'][t] > h_profile['height'][-1]:
                for var in vars_to_interp_with_h:
                    data_dict[var].append(np.nan)
            else:
                f = interp1d(x=h_profile['height'], y=h_profile[vars_to_interp_with_h].to_array(), axis=-1)
                var_values = f(df_orbit['height'][t])
                current_data = dict(zip(vars_to_interp_with_h, var_values))
                for var in vars_to_interp_with_h:
                    data_dict[var].append(current_data[var])

        # Assign the interpolated values to the output Dataset
        for var in vars_to_interp_with_h:
            interp_output[var] = ('time', data_dict[var])

        # Calculate mass density
        n_avogadro = 6.02214076e23  # kg/kmol
        m_O = 15.9994
        m_O2 = 31.9988
        m_N2 = 28.0134
        mass_density = ((10**interp_output['log10_O_Density']*m_O +
                         10**interp_output['log10_O2_Density']*m_O2 +
                         10**interp_output['log10_N2_Density']*m_N2) /
                         n_avogadro*1e-3)
        interp_output['mass_density'] = ('time', mass_density.data)

        for var in list(interp_output.keys()):
            if var in var_attributes_wam:
                interp_output[var] = interp_output[var].assign_attrs(var_attributes_wam[var])

        interp_output.assign_attrs(xrdata.attrs)
        return interp_output
