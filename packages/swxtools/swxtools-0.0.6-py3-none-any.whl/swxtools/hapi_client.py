import requests
import json
import logging
import sys
import pandas as pd
import numpy as np
from swxtools.dataframe_tools import mark_gaps_in_dataframe
from swxtools.config import ISO_TIMEFMT


ISO_TIMEFMT = '%Y-%m-%dT%H:%M:%S.%fZ'


class APIError(Exception):
    pass


def ensure_dataset_info(hapi_server, hapi_server_key, metadata):
    # Get the id, parameters and cadences from the definition
    db_id = metadata['id']

    # Info
    info_request = get_info(hapi_server, db_id)

    # TODO: Compare info and input metadata here, to check consistency
    # Otherwise give error message

    # Create if the dataset does not exist
    if info_request['status']['code'] == 1406:
        logging.info(f"Dataset {db_id} did not yet exist, adding now...")
        create_dataset(hapi_server, hapi_server_key, metadata)
        # Repeat info
        info_request = get_info(hapi_server, db_id)

    return info_request


def create_dataset(server, key, dataset_metadata):
    url = f'{server}/api/datasets?key={key}'
    logging.info(f"Adding new dataset using POST to url: {url}")
    r = requests.post(url=url, json=dataset_metadata)
    if not r.ok:
        try:
            message = json.loads(r.content)
        except json.decoder.JSONDecodeError:
            message = r.content
        raise APIError(message)


def delete_dataset(server, key, dataset_id):
    print("This does not work right now, "
          "check again after knmi-hapi-server updates")
    r = requests.delete(url=f'{server}/api/dataset?key={key}&id={dataset_id}')
    if not r.ok:
        try:
            message = json.loads(r.content)
        except json.decoder.JSONDecodeError:
            message = r.content
        raise APIError(message)


def add_data(server, key, dataset_id, dataframe):
    N_ROWS = 20000  # number of rows in chunk
    list_dataframes = [dataframe.iloc[i:i+N_ROWS]
                       for i in range(0, dataframe.shape[0], N_ROWS)]
    url = f'{server}/api/dataset?key={key}'
    for i_df, df in enumerate(list_dataframes):
        data_obj = {'id': dataset_id,
                    'parameters': list(df.columns),
                    'data': df.values.tolist()}
        data_obj['id'] = dataset_id
        logging.info(f"Sending {sys.getsizeof(json.dumps(data_obj))} "
                     f"bytes of JSON data for block "
                     f"{i_df+1}/{len(list_dataframes)} "
                     f"using PUT to url: {url} for table {dataset_id}.")
        r = requests.put(url, json=data_obj)
        if r.ok:
            logging.info(f"Successful response received on PUT request to {url}.")
        else:
            logging.error(f"Error in add_data PUT request to {url}.")
            try:
                message = json.loads(r.content)
            except json.decoder.JSONDecodeError:
                message = r.content
            raise APIError(message)


def get_catalog(server):
    r = requests.get(url=f'{server}/hapi/catalog')
    if not r.ok:
        try:
            message = json.loads(r.content)
        except json.decoder.JSONDecodeError:
            message = r.content
        raise APIError(message)
    else:
        return json.loads(r.content)


def get_info(server, dataset_id):
    r = requests.get(url=f'{server}/hapi/info?id={dataset_id}')
    # if not r.ok:
    #    raise APIError(json.loads(r.content))
    return json.loads(r.content)


def get_info_values(metadata):
    # Get the id, parameters and cadences from the definition
    output = {}
    output['id'] = metadata['id']
    output['cadence'] = metadata['cadence']
    output['parameters'] = [param['name'] for param in metadata['parameters']]
    output['replace_nan_fill'] = {}
    output['replace_fill_nan'] = {}
    for param in metadata['parameters']:
        if param['type'] == 'double':
            output['replace_nan_fill'][param['name']] = {
                np.nan: float(param['fill']),
                np.inf: float(param['fill']),
                -np.inf: float(param['fill'])
            }
            output['replace_fill_nan'][param['name']] = {
                float(param['fill']): np.nan
            }
        elif param['type'] == 'integer':
            output['replace_nan_fill'][param['name']] = {
                np.nan: int(param['fill'])
            }
            output['replace_fill_nan'][param['name']] = {
                int(param['fill']): np.nan
            }

    if 'x_relations' in metadata:
        output['cadences'] = [relation['cadence']
                              for relation in metadata['x_relations']]
    return output


def resample_lower_cadences(server,
                            key,
                            dataset_id,
                            dataframe=None,
                            t_first_data=None,
                            t_last_data=None,
                            resample_method='mean'):

    # Get the necessary info from metadata
    metadata = get_info(server, dataset_id)
    metadata_values = get_info_values(metadata)
    db_id = metadata_values['id']
    cadences = metadata_values['cadences']
    parameters = metadata_values['parameters']
    replace_nan_fill = metadata_values['replace_nan_fill']
    replace_fill_nan = metadata_values['replace_fill_nan']
    parameters_no_time = parameters.copy()
    parameters_no_time.remove("time")

    # Set date/time bounds for resampling based on dataframe, if necessary
    if t_first_data is None:
        t_first_data = dataframe.index[0]
    if t_last_data is None:
        t_last_data = dataframe.index[-1]

    # Compute time interval for processing lower cadences
    lowest_cadence = pd.to_timedelta(cadences[-1])
    t_start = t_first_data.floor(freq=lowest_cadence)
    t_stop = t_last_data.ceil(freq=lowest_cadence)
    logging.info(
        f"Resampling {dataset_id} for the time interval: {t_start} - {t_stop}"
    )

    if callable(dataframe):
        dataframe_loaded = dataframe(t_first_data, t_last_data)
        if len(dataframe_loaded) == 0:
            logging.error("Empty dataframe encountered while resampling to lower cadence")
            return
    elif type(dataframe) == pd.DataFrame:
        dataframe_loaded = dataframe

    lowest_cadence_factor = 4*24
    freq = lowest_cadence_factor * lowest_cadence
    for t in pd.date_range(t_start, t_stop, freq=freq, tz='utc'):
        t0 = t
        t1 = t + freq
        url = (f"{server}/hapi/data?id={db_id}"
               f"&time.min={t0.strftime(ISO_TIMEFMT)}"
               f"&time.max={t1.strftime(ISO_TIMEFMT)}")
        if dataframe is None:
            logging.info(f"Reading data from HAPI server for: {t0} - {t1}")
            df = pd.read_csv(url, header=None, names=parameters)
            if len(df) == 0:
                continue
            df.replace(replace_fill_nan, inplace=True)
            df.index = pd.to_datetime(df['time'], utc=True)
        else:
            logging.info(f"Input data for resampling from dataframe for: {t0} - {t1}")
            df = dataframe_loaded[t0:t1]

        if len(df) == 0:
            logging.error(f"Encountered empty dataframe for {t0} - {t1}. Cannot downsample to lower cadences")
            continue
        for dataset in metadata['x_relations']:
            db_id_resampled = dataset['id']
            cadence = dataset['cadence']

            # Resample
            if resample_method == 'lttb':
                logging.error("LTTB not yet implemented")
            else:
                # User Pandas for resampling
                resampler = df[parameters_no_time].resample(pd.to_timedelta(cadence), origin='epoch')
                if resample_method == 'mean':
                    df_resampled = resampler.mean()
                elif resample_method == 'max':
                    df_resampled = resampler.max()
                elif resample_method == 'min':
                    df_resampled = resampler.min()
                elif resample_method == 'median':
                    df_resampled = resampler.median()

            df_resampled = mark_gaps_in_dataframe(
                df_resampled,
                nominal_timedelta=pd.to_timedelta(cadence),
                nominal_start_time=df.index[0],
                nominal_end_time=df.index[-1]
            )
            df_resampled['time'] = df_resampled.index.strftime(ISO_TIMEFMT)
            df_resampled = df_resampled[parameters].replace(replace_nan_fill)
            logging.info(f"--Writing data for {df_resampled.index[0]} "
                         f"- {df_resampled.index[-1]} to HAPI dataset "
                         f"{db_id_resampled}, {len(df_resampled)}")
            add_data(server,
                     key,
                     db_id_resampled,
                     df_resampled)
        logging.info(f"Finished resampling data for {dataset_id}")


def ingest_lower_cadence_aggregates(
            hapi_server,
            hapi_server_key,
            metadata,
            dataframe_func,
            t0="2023-01-01",
            t1="2023-01-10",
            high_cadence='PT0.5S',
            min_completeness=0.9):

    # Info
    info_values = get_info_values(metadata)
    replace_nan_fill = info_values['replace_nan_fill']
    parameters = info_values['parameters']

    # Look for original variable names by removing "_min", "_max", etc.
    variables = list(set(
        p.replace("_min", "").replace("_max", "").replace("_mean", "")
        for p in parameters
        if any(suffix in p for suffix in ['_min', '_max', '_mean'])))

    # Cadences
    cadences = [metadata['cadence'], *[x['cadence']
                for x in metadata['x_relations']]]
    cadence_ids = {metadata['cadence']: metadata['id'],
                   **{x['cadence']: x['id']
                   for x in metadata['x_relations']}}

    # Round start and stop time to include lowest cadence
    lowest_cadence = pd.to_timedelta(cadences[-1])
    t_start = t0.floor(freq=lowest_cadence)
    t_stop = t1.ceil(freq=lowest_cadence)

    # Set up the aggregate statistics
    aggstats = ['min', 'max', 'mean', 'count']

    # Load the data
    df_in = dataframe_func(t_start, t_stop)

    if len(df_in) == 0:
        logging.error(f"Encountered empty dataframe for {t0} - {t1}. Cannot downsample to lower cadence aggregate")
        return
    for cadence in cadences:
        # Compute statistics
        df_agg = df_in[variables].resample(
            pd.to_timedelta(cadence), label='left', origin='epoch'
        ).agg(aggstats)

        # Adjust index to middle of cadence
        df_agg.index = df_agg.index + 0.5 * pd.to_timedelta(cadence)

        # Set overall count
        maxcount = pd.to_timedelta(cadence) / pd.to_timedelta(high_cadence)
        coverage = df_agg[[(v, 'count')
                           for v in variables]].apply(max, axis=1) / maxcount

        # Set data to NaN if statistics are based on limited
        # observations in the interval
        for par in variables:
            for aggstat in ['min', 'max', 'mean']:
                df_agg.loc[:, (par, aggstat)] = (
                    df_agg.loc[:, (par, aggstat)].where(
                        df_agg.loc[:, (par, 'count')] >
                        min_completeness*maxcount
                    )
                )

        # Get rid of the counts
        for par in variables:
            df_agg.drop((par, "count"), axis=1, inplace=True)

        # Change the multi-index to single index
        #  ("density_min", "density_max", etc.)
        df_agg.columns = ["_".join(col_name)
                          for col_name in df_agg.columns.to_flat_index()]

        # Add time and completeness columns
        df_agg['coverage'] = coverage
        df_agg.replace(replace_nan_fill, inplace=True)
        df_agg['time'] = df_agg.index.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        add_data(hapi_server,
                 hapi_server_key,
                 cadence_ids[cadence],
                 df_agg)
