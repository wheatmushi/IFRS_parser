"""
Functions for processing companies data by using linear regression methods.
"""

import pandas as pd
import numpy as np

def add_linear_regression(arr, outliers, linear_source, forecast):
    # get 1D pandas DF (array) and add linear forecast column with optional removal of outliers
    old_data = arr.iloc[0: arr.shape[0]+linear_source[0]]  # data excluded from linearization
    source = arr.iloc[arr.shape[0]+linear_source[0]: arr.shape[0]+linear_source[1]]  # source for linear regression
    new_data = arr.iloc[arr.shape[0]+linear_source[1]:]  # in case if linearization counted not on latest data

    t1 = np.arange(old_data.shape[0])
    t2 = np.arange(old_data.shape[0], old_data.shape[0] + source.shape[0])  # X-axis for linear regression
    t3 = np.arange(old_data.shape[0] + source.shape[0], old_data.shape[0] + source.shape[0] + new_data.shape[0])
    t4 = np.arange(old_data.shape[0] + source.shape[0] + new_data.shape[0],
                   old_data.shape[0] + source.shape[0] + new_data.shape[0] + forecast)

    line = np.polyfit(t2, source.values, 1)
    last_index = new_data.index[-1] if not new_data.empty else source.index[-1]
    last_index = last_index + pd.Timedelta(90, 'D')
    forecasted_data = pd.DataFrame(data=t4, columns=['t'], index=pd.date_range(last_index, periods=forecast, freq='3M'))
    old_data['t'], source['t'], new_data['t'] = t1, t2, t3

    arr_res = pd.concat((old_data, source, new_data, forecasted_data), axis=0)
    arr_res['linear_regression'] = line[0] * arr_res['t'] + line[1]
    return arr_res, line[0]

