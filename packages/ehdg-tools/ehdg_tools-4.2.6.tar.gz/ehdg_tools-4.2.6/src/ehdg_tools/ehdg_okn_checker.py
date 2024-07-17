import os
import csv
import time


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


def read_signal_csv(input_file_dir1):
    file1 = open(input_file_dir1)
    csv_reader = csv.reader(file1)
    header_array = []
    rows = []
    data_table_dict = {}
    count_one = 0

    for row in csv_reader:
        if count_one <= 0:
            header_array = row
            count_one += 1
        else:
            rows.append(row)

    for header in header_array:
        header_position = get_index(header, header_array)
        value_array = []
        for row in rows:
            value_array.append(row[header_position])
        data_table_dict[header] = value_array

    return data_table_dict


# This function is to read the signal.csv and retrieve max chain length and unchained okn total
def signal_checker(dir_input, signal_csv_name="signal.csv"):
    print(f"Sending the following directory: {dir_input} to signal checker!")
    start_time = time.time()
    # Add signal.csv to directory
    csv_input = os.path.join(dir_input, signal_csv_name)
    data_table = read_signal_csv(csv_input)
    result_id_array = data_table["result_id"]
    result_chain_id_array = data_table["result_chain_id"]
    signal_data = {}
    result_data = []
    temp_max_chain_length = 0
    temp_unchained_okn_total = 0

    # Looking for result id and result chain id.
    # When they are found, they are added into result data array
    for r_id, r_c_id in zip(result_id_array, result_chain_id_array):
        if int(r_id) != -1 and int(r_c_id) != -1:
            result_data.append((int(r_c_id), int(r_id)))

    # remove duplicate number from result data array
    unique_result_data = list(dict.fromkeys(result_data))
    # print(unique_result_data)

    # taking only result id
    raw_unique_result_id_array = []
    for ri in unique_result_data:
        raw_unique_result_id_array.append(ri[0])

    # remove duplicate result id from raw unique result id array
    unique_result_id_array = list(dict.fromkeys(raw_unique_result_id_array))

    final_data_array = []

    # looping unique result id array to get all result chain id which are
    # related to their individual result id into temp array
    # after that, add result id and its related result chain id into final data array as a tuple
    for rid in unique_result_id_array:
        temp_array = []
        for data in unique_result_data:
            if rid == data[0]:
                temp_array.append(data[1])
        final_data_array.append((rid, temp_array))

    # determine the max chain length and unchained okn total from final data array
    if len(final_data_array) > 0:
        print(f"Raw result: {final_data_array}")
        for tuple_item in final_data_array:
            chain_length = len(tuple_item[1])
            if chain_length > temp_max_chain_length:
                temp_max_chain_length = chain_length
            if chain_length == 1:
                temp_unchained_okn_total += 1
        signal_data["max_chain_length"] = temp_max_chain_length
        signal_data["unchained_okn_total"] = temp_unchained_okn_total
    else:
        print("There is no chain or okn")
        signal_data["max_chain_length"] = 0
        signal_data["unchained_okn_total"] = 0

    print(f"Signal data: {signal_data} is collected and it took {time.time() - start_time} sec.")
    print("--------------------------------------------------------------------------------------")

    return signal_data


# This function is to decide whether there is okn or not by the given rules
def apply_okn_detection_rule(data, min_chain_length_input, min_unchained_okn_input):
    print(f"Start applying the okn detection rule.")
    print(f"Minimum chain length must be greater than equal {min_chain_length_input}.")
    print(f"Minimum unchained okn must be greater than equal {min_unchained_okn_input}.")
    start_time = time.time()
    # Rule 1
    is_chained = (data["max_chain_length"] >= min_chain_length_input)

    # Rule 2
    is_unchained = (data["unchained_okn_total"] >= min_unchained_okn_input)
    i = is_chained | is_unchained
    print(f"Data:{data} has been measured by okn detection rules!")
    if i:
        print("There is an okn!")
    else:
        print("There is no okn!")
    print(f"The process took {time.time() - start_time} sec.")
    print("--------------------------------------------------------------------------------------")

    return i


# This function is to detect okn from the given preprocessed csv and produce result folder which includes signal.csv
def detect_with_okn_detector(csv_to_b_detected, odc):
    start_time = time.time()
    print(f"Sending the following directory to okn detector: {csv_to_b_detected}!")
    updated_filename = os.path.basename(csv_to_b_detected)
    out_put_dir = csv_to_b_detected.replace(updated_filename, "result")

    if not os.path.isfile(odc):
        raise FileNotFoundError("OKN detector config file cannot be found.")

    commandline = f"okndetector -c \"{odc}\" -i \"{csv_to_b_detected}\" -o \"{out_put_dir}\""
    os.system(commandline)
    print(f"The result has been produced in the directory {out_put_dir}.")
    print(f"The process took {time.time() - start_time} sec.")
    print("--------------------------------------------------------------------------------------")

    return out_put_dir
