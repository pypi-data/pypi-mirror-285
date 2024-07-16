import pandas as pd
import numpy as np

def mark_gaps_in_dataframe(df,
                           nominal_timedelta=pd.to_timedelta(1, 'min'),
                           nominal_start_time=None,
                           nominal_end_time=None):
    """
    Look for gaps and add np.nan record to enforce breaks in plotted lines

    Args:
        df: Pandas DataFrame object, must have DatetimeIndex as index

    Returns:
        DataFrame with nan-records appended inside gaps.
    """
    deltas = pd.Series(df.index).diff()[1:]
    gaps = deltas[deltas > nominal_timedelta] / nominal_timedelta

    df_gapfilled = df.copy()

    data_nans = {col: np.nan for col in df.columns}

    for i, gap in gaps.items():
        # Add a np.nan record after the start of each gap,
        # to force breaks in plotted lines
        time_gap_start = df.index[i-1] + nominal_timedelta
        df_new_record = pd.DataFrame(data=data_nans, index=[time_gap_start])
        df_gapfilled = pd.concat([df_gapfilled, df_new_record]).sort_index()

        # For gaps longer than 1 record, also add a np.nan record before the
        # end of the gap
        if gap > 2:
            time_gap_end = df.index[i] - nominal_timedelta
            df_new_record = pd.DataFrame(data=data_nans, index=[time_gap_end])
            df_gapfilled = pd.concat([df_gapfilled,
                                      df_new_record]).sort_index()

    # Add gap before start
    if nominal_start_time is not None:
        if df.index[0] > nominal_start_time:
            df_new_record_before = pd.DataFrame(
                data=data_nans,
                index=[df.index[0]-nominal_timedelta]
            )
            df_gapfilled = pd.concat([df_new_record_before, df_gapfilled])
    # Add gap after end
    if nominal_end_time is not None:
        if df.index[-1] < nominal_end_time:
            df_new_record_after = pd.DataFrame(
                data=data_nans,
                index=[df.index[-1]+nominal_timedelta]
            )
            df_gapfilled = pd.concat([df_gapfilled, df_new_record_after])

    return df_gapfilled
