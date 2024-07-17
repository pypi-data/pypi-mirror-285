import csv
import commentjson
import numpy as np
import math
import time
from scipy.signal import medfilt
import os


# This function is to get header position from the given array
def get_index(search_input, array_in):
    idx_found = False
    return_idx = None
    for idx, val in enumerate(array_in):
        if val == search_input:
            idx_found = True
            return_idx = idx
            break

    if not idx_found:
        print(f"{search_input} can not be found!")

    return return_idx


def load_commented_json(config_input):
    with open(config_input, 'r') as handle:
        protocol = commentjson.load(handle)
    return protocol


def read_table(input_file_dir):
    file = open(input_file_dir)
    csv_reader = csv.reader(file)
    header_array = []
    rows = []
    data_table_dict = {}
    count = 0

    for row in csv_reader:
        if count <= 0:
            header_array = row
            count += 1
        else:
            rows.append(row)

    for header in header_array:
        header_position = get_index(header, header_array)
        value_array = []
        for row in rows:
            # print(header)
            try:
                input_value = float(row[header_position])
            except ValueError:
                input_value = float("NaN")
            value_array.append(input_value)
        data_table_dict[header] = value_array

    return data_table_dict


# dispatch function

def dispatch_function(filter_info_input, data_dict_input, extra=None):
    if extra is not None:
        pass
    match_item = filter_info_input["function"]
    # print(f"Dispatched function name: {match_item}")
    if match_item == "cdp_direction":

        # t = data_dict_input[filter_info_input["input"]]
        # # need to be fixed ********
        # keyname = "need to be fixed"
        # f = cdp_direction(extra.log, keyname, t)
        # data_dict_input[filter_info_input["output"]] = f
        pass

    elif match_item == "reduce":

        t = data_dict_input[filter_info_input["input"]]
        data_dict_input[filter_info_input["output"]] = t[1::2]

    elif match_item == "dwnsample":

        t = data_dict_input[filter_info_input["input"]]
        n = filter_info_input["target_samplerate"]
        dt = np.nanmean(np.diff(t))
        T = 1 / dt
        try:
            r = math.log(math.floor(T / n), 2)
        except ValueError:
            r = 0

        print('Target samplerate       = ', n)
        print('Estimated samplerate    = ', T)
        print('Approximated reductions = ', r)

        if r == 0:
            return data_dict_input

        p = dwnsample(data_dict_input, r)
        data_dict_input = p
        return data_dict_input

    elif match_item == "detectblinkv":

        x1 = data_dict_input[filter_info_input["input"][0]]
        x2 = data_dict_input[filter_info_input["input"][1]]
        x1 = medfilt(x1, 3)
        x2 = medfilt(x2, 3)

        # need to be continued
        print(x1)
        print(x2)
        pass

    elif match_item == "deblinker2":

        x0 = data_dict_input[filter_info_input["input"][0]]
        y0 = data_dict_input[filter_info_input["input"][1]]
        th = filter_info_input["threshold"]

        i = deblinker2(x0, y0, th)
        data_dict_input[filter_info_input["output"]] = i

    elif match_item == 'passthrough':

        f = data_dict_input[filter_info_input["input"]]
        output_column = filter_info_input["output"]
        data_dict_input[output_column] = f
        # print(f"{output_column} column has been added to csv data.")

    elif match_item == 'dshift':

        f = data_dict_input[filter_info_input["input"][0]]
        data_dict_input[filter_info_input["output"]] = dshift(f)

    elif match_item == 'tidy':

        f = data_dict_input[filter_info_input["input"][0]]
        n = filter_info_input["value"]
        thicken = filter_info_input["thicken"]

        is_tracking = data_dict_input[filter_info_input["input"][1]]
        data_dict_input[filter_info_input["output"]] = tidy(f, n, thicken, np.logical_not(is_tracking))

    elif match_item == 'wavelet':
        print(f"Dispatch function:({match_item}) is not available in python updater.")

    elif match_item == 'spikeRemover':
        print(f"Dispatch function:({match_item}) is not available in python updater.")

    elif match_item == 'deblinker':
        print(f"Dispatch function:({match_item}) is not available in python updater.")

    elif match_item == 'shiftSignal':
        print(f"Dispatch function:({match_item}) is not available in python updater.")

    elif match_item == 'medianFilter':

        input_column = filter_info_input["input"][0]
        f = data_dict_input[input_column]
        n = filter_info_input["npoint"]
        data_dict_input[filter_info_input["output"]] = medfilt(f, n)
        # print(f"{input_column} column has been median filtered with n point {n}.")

    elif match_item == 'replaceNanBy':

        input_column = filter_info_input["input"][0]
        input_array = data_dict_input[input_column]
        pointer = filter_info_input["pointer"]
        data_dict_input[filter_info_input["output"]] = replace_nan_by(data_dict_input, input_array, pointer)

    elif match_item == 'applymask':
        print(f"Dispatch function:({match_item}) is not available in python updater.")

    elif match_item == 'detrender':
        print(f"Dispatch function:({match_item}) is not available in python updater.")

    elif match_item == 'detectblinkV':
        print(f"Dispatch function:({match_item}) is not available in python updater.")

    elif match_item == 'gradient':

        related_column_name_array = filter_info_input["input"]
        f = data_dict_input[related_column_name_array[1]]
        t = data_dict_input[related_column_name_array[0]]
        output_column = filter_info_input["output"]
        data_dict_input[output_column] = grad(f, t)
        # print(f"{output_column} column is added to the csv data by using gradient.")

    elif match_item == "live_gradient":

        related_column_name_array = filter_info_input["input"]
        f = data_dict_input[related_column_name_array[1]]
        t = data_dict_input[related_column_name_array[0]]
        output_column = filter_info_input["output"]
        data_dict_input[output_column] = live_grad(f, t)

    else:
        print(f"Dispatch function:({match_item}) is not found.")
    return data_dict_input


# def spike_remover(f):
#     pass
#
#
# def xdetectblink(x1, V, fps, varargin):
#     pass
#
#
# def detectblinkv(t, V, fps, varargin):
#     pass


def dwnsample(M, N):
    F = len(M[next(iter(M))])
    N = int(N)
    if isinstance(N, int):
        loop_count = 0
        while loop_count < N:
            loop_count += 1
            for key in M:
                temp_array = M[key]
                temp_array = temp_array[0:F:2]
                M[key] = temp_array
    else:
        print("The number of loop input must be number!")

    return M


def replace_nan_by(data_dict_input, input_array, pointer):
    if "<=" in pointer:
        try:
            column_name, value = str(pointer).split("<=")
            pointer_column__array = data_dict_input[column_name]
            array_length = len(input_array)
            for ind in range(array_length):
                if float(pointer_column__array[ind]) <= float(value):
                    input_array[ind] = np.nan
        except KeyError:
            pass
    elif "==" in pointer:
        try:
            column_name, value = str(pointer).split("==")
            pointer_column__array = data_dict_input[column_name]
            array_length = len(input_array)
            for ind in range(array_length):
                if float(pointer_column__array[ind]) == float(value):
                    input_array[ind] = np.nan
        except KeyError:
            pass
    elif ">=" in pointer:
        try:
            column_name, value = str(pointer).split(">=")
            pointer_column__array = data_dict_input[column_name]
            array_length = len(input_array)
            for ind in range(array_length):
                if float(pointer_column__array[ind]) >= float(value):
                    input_array[ind] = np.nan
        except KeyError:
            pass
    else:
        if ">" in pointer:
            try:
                column_name, value = str(pointer).split(">")
                pointer_column__array = data_dict_input[column_name]
                array_length = len(input_array)
                for ind in range(array_length):
                    if float(pointer_column__array[ind]) > float(value):
                        input_array[ind] = np.nan
            except KeyError:
                pass
        elif "<" in pointer:
            try:
                column_name, value = str(pointer).split("<")
                pointer_column__array = data_dict_input[column_name]
                array_length = len(input_array)
                for ind in range(array_length):
                    if float(pointer_column__array[ind]) < float(value):
                        input_array[ind] = np.nan
            except KeyError:
                pass
        else:
            pass

    return input_array


# def waveleter(x, lfr, wt, level):
#     [x1, i] = fillmissing(x)
#     x11 = x1
#
#     return x11


def deblinker2(x, y, th):
    s = x * y
    i = (s > th)
    return i


# def applymask(f, is_mask):
#     pass
#
#
# def deblinker(f, is_blinking):
#     pass
#
#
# def medianfilter(f, npoint):
#     pass
#

def tidy(f, npoint, n_thicken, is_deleted):
    # need  to be fixed
    print(npoint)
    print(n_thicken)
    print(is_deleted)
    return f


def dshift(f):
    y = np.nanmean(f)
    f1 = f - y
    return f1


def grad(f, t):
    df = np.gradient(f)
    dt = np.gradient(t)
    dfdt = df / dt
    return dfdt


# def cdp_direction(logs, fname, t):
#     print(logs)
#     print(fname)
#     return t


def are_all_elements_nan(input_array):
    for ele in input_array:
        if not np.isnan(ele):
            return False
    return True


# def fillmissing(input_array):
#     input_array = ma.masked_array(input_array, input_array == np.nan)
#     for shift in (-1, 1):
#         for axis in (0, 1):
#             shifted_array = np.roll(input_array, shift=shift, axis=axis)
#             idx = ~shifted_array.mask * input_array.mask
#             input_array[idx] = shifted_array[idx]
#     return input_array

def live_grad(f, t):
    f_len = len(f)
    try:
        df = np.gradient(f)
        dt = np.gradient(t)
        dfdt = df / dt
        # print("dfdt", dfdt)
        for ind, value in enumerate(dfdt):
            if math.isinf(value):
                dfdt[ind] = 0
            if np.isnan(value):
                dfdt[ind] = 0
        return dfdt
    except ValueError:
        return f_len * [0]
    except RuntimeWarning:
        return f_len * [0]


# The main function to preprocess the csv data
# This function is also the translation of matlab run_updater function from the okn_matlab repo
def run_updater(config, inputfile, outputfile, varargin=None):
    start_time = time.time()
    if varargin is not None:
        print("varargin is not none.")
    data_table = None

    if isinstance(config, str):
        config = load_commented_json(config)

    if isinstance(inputfile, str):
        data_table = read_table(inputfile)

    # extra information
    extra = {"inputfile": inputfile, "outputfile": outputfile, "config": config}

    config_filter_info_array = config["filters"]

    for filter_info in config_filter_info_array:
        if filter_info["Enabled"]:
            data_table = dispatch_function(filter_info, data_table, extra)
        else:
            pass

    header_array = []
    for key in data_table:
        header_array.append(key)

    print("Start updating the csv!")
    with open(outputfile, mode='w', newline="") as destination_file:
        csv_writer = csv.DictWriter(destination_file, fieldnames=header_array)
        csv_writer.writeheader()

        row_count = len(data_table[header_array[0]])

        for i in range(row_count):
            temp_dict = {}
            for header in header_array:
                temp_dict[header] = data_table[header][i]
            csv_writer.writerow(temp_dict)
    print(f"csv is updated and it took {time.time() - start_time} sec")
    print("--------------------------------------------------------------------------------------")
    return outputfile


# This function is to preprocess the csv data
# es = extra string for updated csv ("updated_"), uc = updater config
def update_csv(input_csv_file_dir, es, uc):
    csv_file_name = os.path.basename(input_csv_file_dir)

    # add extra string in front of csv name
    # Example: if extra string = "updated_", then
    # trial.csv becomes updated_trial.csv
    updated_file_name = es + csv_file_name

    output_dir = input_csv_file_dir.replace(csv_file_name, updated_file_name)
    output_csv_dir = run_updater(uc, input_csv_file_dir, output_dir)

    return output_csv_dir
