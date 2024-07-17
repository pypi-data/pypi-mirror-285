import csv
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import os

logmar_level_array = [1.0, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0, -0.1, -0.2,
                      "no logMAR", "right_down", "right_up", "left_down", "left_up"]


def get_logmar_level_array():
    return logmar_level_array


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


# This function is to translate disk condition string to logmar value
def disk_to_logmar(disk_string_input):
    disk_logmar_equivalent = {"disk-condition-1-1": 1.0, "disk-condition-1-2": 1.0, "disk-condition-2-1": 0.9,
                              "disk-condition-2-2": 0.9, "disk-condition-3-1": 0.8, "disk-condition-3-2": 0.8,
                              "disk-condition-4-1": 0.7, "disk-condition-4-2": 0.7, "disk-condition-5-1": 0.6,
                              "disk-condition-5-2": 0.6, "disk-condition-6-1": 0.5, "disk-condition-6-2": 0.5,
                              "disk-condition-7-1": 0.4, "disk-condition-7-2": 0.4, "disk-condition-8-1": 0.3,
                              "disk-condition-8-2": 0.3, "disk-condition-9-1": 0.2, "disk-condition-9-2": 0.2,
                              "disk-condition-10-1": 0.1, "disk-condition-10-2": 0.1, "disk-condition-11-1": 0.0,
                              "disk-condition-11-2": 0.0, "disk-condition-12-1": -0.1, "disk-condition-12-2": -0.1,
                              "disk-condition-13-1": -0.2, "disk-condition-13-2": -0.2,
                              "no-disk-condition": "no logMAR",
                              "right_down": "right_down", "right_up": "right_up",
                              "left_down": "left_down", "left_up": "left_up"}

    try:
        out_string = disk_logmar_equivalent[disk_string_input]
    except KeyError:
        out_string = disk_string_input
    if out_string not in logmar_level_array:
        logmar_level_array.append(out_string)

    return out_string


# This function is to draw a graph with slow phase and quick phase overlay from the given config info


def trial_plot(trial_plot_info_input, signal_dir_input, output_dir_input=None, image_name_input=None, gaze_csv_dir=None,
               trial_name=None):
    title = trial_plot_info_input["title"]
    x_label = trial_plot_info_input["x_label"]
    y_label = trial_plot_info_input["y_label"]
    x_data_column_name = trial_plot_info_input["x_data_column_name"]
    y_data_column_name = trial_plot_info_input["y_data_column_name"]
    graph_line_color = trial_plot_info_input["graph_line_color"]
    graph_line_thickness = trial_plot_info_input["graph_line_thickness"]
    # image_scale = trial_plot_info_input["image_scale"]
    sp_column_name = trial_plot_info_input["sp_column_name"]
    qp_column_name = trial_plot_info_input["qp_column_name"]
    sp_line_color = trial_plot_info_input["sp_line_color"]
    sp_line_thickness = trial_plot_info_input["sp_line_thickness"]
    qp_line_color = trial_plot_info_input["qp_line_color"]
    qp_line_thickness = trial_plot_info_input["qp_line_thickness"]
    output_image_name = trial_plot_info_input["output_image_name"]
    if output_dir_input:
        output_dir = output_dir_input
        if image_name_input is not None:
            image_name_input = str(image_name_input)
            if image_name_input.lower().endswith(".png"):
                output_image_name = str(image_name_input)
            else:
                output_image_name = f"{image_name_input}.png"
    else:
        result_folder_dir = os.path.abspath(os.path.join(signal_dir_input, os.pardir))
        trial_folder_dir = os.path.abspath(os.path.join(result_folder_dir, os.pardir))
        output_dir = trial_folder_dir

    display_output_dir = os.path.join(output_dir, output_image_name)

    try:
        file_to_open = open(signal_dir_input)
        csv_reader = csv.reader(file_to_open)
        header_array = []
        rows = []
        count_one = 0

        for row in csv_reader:
            if count_one <= 0:
                header_array = row
                count_one += 1
            else:
                rows.append(row)

        x_header_position = get_index(x_data_column_name, header_array)
        y_header_position = get_index(y_data_column_name, header_array)
    except FileNotFoundError:
        print(f"{signal_dir_input} could not be found.")
        rows = []
        x_header_position = None
        y_header_position = None

    x_array = []
    y_array = []
    first_value_recorded = False
    first_value = 0

    if len(rows) > 0:
        for row in rows:
            raw_value = float(row[x_header_position])
            if not first_value_recorded:
                first_value = raw_value
                first_value_recorded = True
            value_input = raw_value - first_value
            x_array.append(value_input)

            y_array.append(float(row[y_header_position]))

        x_limits, y_limits, x_array, y_array = get_draw_info_for_trial_plot(trial_plot_info_input, x_array, y_array)

        x_lower_limit = x_limits["lower_limit"]
        x_upper_limit = x_limits["upper_limit"]
        y_lower_limit = y_limits["lower_limit"]
        y_upper_limit = y_limits["upper_limit"]
    else:
        x_lower_limit = None
        x_upper_limit = None
        y_lower_limit = None
        y_upper_limit = None

    try:
        file_to_open = open(signal_dir_input)
        csv_reader2 = csv.reader(file_to_open)
        header_array2 = []
        rows2 = []
        count_one2 = 0

        for row in csv_reader2:
            if count_one2 <= 0:
                header_array2 = row
                count_one2 += 1
            else:
                rows2.append(row)

        # print(header_array2)
        slow_phase_position = get_index(sp_column_name, header_array2)
        quick_phase_position = get_index(qp_column_name, header_array2)
    except FileNotFoundError:
        print(f"{signal_dir_input} could not be found.")
        rows2 = []
        slow_phase_position = None
        quick_phase_position = None

    sp_array = []
    qp_array = []

    if len(rows2) > 0:
        for row in rows2:
            sp_value = row[slow_phase_position]
            qp_value = row[quick_phase_position]
            sp_array.append(str(sp_value).lower())
            qp_array.append(str(qp_value).lower())

        # for ind in range(len(sp_array)):
        #     print(sp_array[ind], qp_array[ind])
        #     if sp_array[ind] == "false" and qp_array[ind] == "false":
        #         print("both false")

        for ind in range(len(sp_array)):
            if sp_array[ind] == "true":
                sp_array[ind] = y_array[ind]
            else:
                sp_array[ind] = np.nan

        for ind in range(len(qp_array)):
            if qp_array[ind] == "true":
                qp_array[ind] = y_array[ind]
                previous_ind = ind - 1
                if previous_ind >= 0:
                    qp_array[ind - 1] = y_array[ind - 1]

            else:
                qp_array[ind] = np.nan

        # Check maximum of x_array to decide whether it needs to be expended or not
        x_array_max = math.ceil(max(x_array))
        # default figsize 6.4 and 4.8
        if x_array_max >= 10:
            plt.figure(figsize=(x_array_max, 4.8))
        plt.plot(x_array, y_array, color=graph_line_color, linewidth=graph_line_thickness)
        plt.plot(x_array, sp_array, color=sp_line_color, linewidth=sp_line_thickness)
        plt.plot(x_array, qp_array, color=qp_line_color, linewidth=qp_line_thickness)

        plt.title(title)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.xlim(x_lower_limit, x_upper_limit)
        plt.ylim(y_lower_limit, y_upper_limit)
        x_axis_array = np.arange(start=min(x_array), stop=max(x_array), step=1)
        plt.xticks(x_axis_array)
        if gaze_csv_dir:
            event_marker_exist = string_exist("event_marker", gaze_csv_dir, "event_string")
            if trial_name is None:
                folder_name = os.path.basename(output_dir)
                trial_id, condition = str(folder_name).split("_", 1)
            else:
                trial_id, condition = str(trial_name).split("_", 1)
            if event_marker_exist:
                event_marker_info = get_event_marker_info(gaze_csv_dir, trial_id)
                for marker_time in event_marker_info:
                    plt.axvline(x=float(marker_time), color=graph_line_color,
                                linestyle=":",
                                linewidth=graph_line_thickness, label=f"{marker_time}")
        os.chdir(output_dir)
        plt.savefig(output_image_name)
        plt.close()

        print(f"Trial plot has been saved at:{display_output_dir}")
    else:
        print(f"There is no data in {signal_dir_input} or it does not exist.")


# This function is to produce a plan as an array from the given folder to be used in drawing combined summary plot
def get_plot_info(data_dir, plot_info_input, summary_csv_dir_input=None):
    x_label = plot_info_input["x_label"]
    y_label = plot_info_input["y_label"]
    x_data_column_name = plot_info_input["x_data_column_name"]
    y_data_column_name = plot_info_input["y_data_column_name"]
    x_axis_limit = plot_info_input["x_axis_limit"]
    y_axis_limit = plot_info_input["y_axis_limit"]
    mean_offset = plot_info_input["mean_offset"]
    axis_adjustment_types = plot_info_input["axis_adjustment_types"]
    axis_adjustment_type_number = plot_info_input["axis_adjustment_type_number"]
    signal_csv_folder_name = plot_info_input["signal_csv_folder_name"]
    signal_csv_name = plot_info_input["signal_csv_name"]
    sp_column_name = plot_info_input["sp_column_name"]
    qp_column_name = plot_info_input["qp_column_name"]
    sp_line_color = plot_info_input["sp_line_color"]
    sp_line_thickness = plot_info_input["sp_line_thickness"]
    qp_line_color = plot_info_input["qp_line_color"]
    qp_line_thickness = plot_info_input["qp_line_thickness"]
    summary_csv_name = plot_info_input["summary_csv_name"]
    if summary_csv_dir_input is None:
        summary_csv_dir_input = os.path.join(data_dir, summary_csv_name)
    folder_array = get_folder_name_from_dir(summary_csv_dir_input)

    adjustment_type = axis_adjustment_types[str(axis_adjustment_type_number)]
    if adjustment_type == "mean_offset":
        plot_info_array = []
        x_adjust_limit, y_adjust_limit, ignore_folder_array = get_adjust_limit(data_dir, None,
                                                                               x_data_column_name, y_data_column_name,
                                                                               folder_array, x_axis_limit,
                                                                               y_axis_limit, mean_offset,
                                                                               axis_adjustment_types,
                                                                               axis_adjustment_type_number,
                                                                               signal_csv_folder_name, signal_csv_name)
        adjust_limit_dict = {"x_adjust_limit": x_adjust_limit, "y_adjust_limit": y_adjust_limit}
        # If there is folder to be ignored, take out that folder name from the folder array
        if ignore_folder_array:
            folder_array = [folder for folder in folder_array if folder not in ignore_folder_array]
        for folder_name in folder_array:
            trial_id, disk_condition = str(folder_name).split("_", 1)
            signal_csv_dir = os.path.join(data_dir, folder_name, signal_csv_folder_name, signal_csv_name)
            x_array = get_data_array(signal_csv_dir, x_data_column_name)
            y_array = get_data_array(signal_csv_dir, y_data_column_name)
            y_mean = np.nanmean(y_array)
            y_array = [value - y_mean for value in y_array]
            sp_array, qp_array = get_sp_and_qp_array(signal_csv_dir, sp_column_name, qp_column_name,
                                                     y_array)
            plot_info = {"trial_id": trial_id, "disk_condition": disk_condition,
                         "x_label": x_label, "y_label": y_label,
                         "x_array": x_array, "y_array": y_array,
                         "sp_array": sp_array, "qp_array": qp_array,
                         "sp_line_color": sp_line_color, "sp_line_thickness": sp_line_thickness,
                         "qp_line_color": qp_line_color, "qp_line_thickness": qp_line_thickness,
                         "logmar": disk_to_logmar(disk_condition)}
            plot_info_array.append(plot_info)
    else:
        plot_info_array = []
        x_adjust_limit, y_adjust_limit, ignore_folder_array = get_adjust_limit(data_dir, None,
                                                                               x_data_column_name, y_data_column_name,
                                                                               folder_array, x_axis_limit,
                                                                               y_axis_limit, mean_offset,
                                                                               axis_adjustment_types,
                                                                               axis_adjustment_type_number,
                                                                               signal_csv_folder_name, signal_csv_name)
        adjust_limit_dict = {"x_adjust_limit": x_adjust_limit, "y_adjust_limit": y_adjust_limit}
        # If there is folder to be ignored, take out that folder name from the folder array
        if ignore_folder_array:
            folder_array = [folder for folder in folder_array if folder not in ignore_folder_array]
        for folder_name in folder_array:
            trial_id, disk_condition = str(folder_name).split("_", 1)
            signal_csv_dir = os.path.join(data_dir, folder_name, signal_csv_folder_name, signal_csv_name)
            x_array = get_data_array(signal_csv_dir, x_data_column_name)
            y_array = get_data_array(signal_csv_dir, y_data_column_name)
            sp_array, qp_array = get_sp_and_qp_array(signal_csv_dir, sp_column_name, qp_column_name,
                                                     y_array)
            plot_info = {"trial_id": trial_id, "disk_condition": disk_condition,
                         "x_label": x_label, "y_label": y_label,
                         "x_array": x_array, "y_array": y_array,
                         "sp_array": sp_array, "qp_array": qp_array,
                         "sp_line_color": sp_line_color, "sp_line_thickness": sp_line_thickness,
                         "qp_line_color": qp_line_color, "qp_line_thickness": qp_line_thickness,
                         "logmar": disk_to_logmar(disk_condition)}
            plot_info_array.append(plot_info)

    return plot_info_array, adjust_limit_dict


# This function is to retrieve folder names from the given csv
def get_folder_name_from_dir(summary_csv_input,
                             trial_id_header_input="trial_id",
                             disk_condition_header_input="disk_condition"):
    csv_dir = summary_csv_input
    if not os.path.isfile(csv_dir):
        print(f"Invalid summary csv file location: {csv_dir}.")
    output_array = []

    try:
        file_to_open = open(csv_dir)
        csv_reader = csv.reader(file_to_open)
        header_array = []
        rows = []
        count_one = 0

        for row in csv_reader:
            if count_one <= 0:
                header_array = row
                count_one += 1
            else:
                rows.append(row)

        trial_id_header_position = get_index(trial_id_header_input, header_array)
        disk_condition_header_position = get_index(disk_condition_header_input, header_array)
    except FileNotFoundError:
        print(f"{csv_dir} could not be found.")
        rows = []
        trial_id_header_position = None
        disk_condition_header_position = None

    if len(rows) > 0:
        for row in rows:
            trial_string_raw = row[trial_id_header_position]
            disk_string_raw = row[disk_condition_header_position]
            folder_name_input = f"{trial_string_raw}_{disk_string_raw}"
            output_array.append(folder_name_input)
    else:
        print(f"There is no data in {csv_dir} or it does not exist.")

    return output_array


def get_folder_info_from_summary_csv(summary_csv):
    output_array = []

    try:
        file_to_open = open(summary_csv)
        csv_reader = csv.reader(file_to_open)
        header_array = []
        rows = []
        count_one = 0

        for row in csv_reader:
            if count_one <= 0:
                header_array = row
                count_one += 1
            else:
                rows.append(row)
    except FileNotFoundError:
        print(f"{summary_csv} could not be found.")
        return []

    if len(rows) > 0:
        for row in rows:
            temp_dict = {}
            for ind, header in enumerate(header_array):
                temp_dict[header] = row[ind]
            output_array.append(temp_dict)
    else:
        print(f"There is no data in {summary_csv} or it does not exist.")

    return output_array


# This function is to retrieve the data array from the given csv and header name
def get_data_array(data_dir, header_name_input):
    output_array = []
    try:
        file_to_open = open(data_dir)
        csv_reader = csv.reader(file_to_open)
        header_array = []
        rows = []
        count_one = 0

        for row in csv_reader:
            if count_one <= 0:
                header_array = row
                count_one += 1
            else:
                rows.append(row)

        header_position = get_index(header_name_input, header_array)
    except FileNotFoundError:
        print(f"{data_dir} could not be found.")
        rows = []
        header_position = None

    first_value_recorded = False
    first_value = 0

    if len(rows) > 0:
        if "timestamp" in str(header_name_input) or str(header_name_input) == "t":
            for row in rows:
                raw_value = float(row[header_position])
                if not first_value_recorded:
                    first_value = raw_value
                    first_value_recorded = True
                value_input = raw_value - first_value
                output_array.append(value_input)
        else:
            for row in rows:
                output_array.append(float(row[header_position]))
    else:
        print(f"There is no data in {data_dir} or it does not exist.")

    return output_array


# This function is to retrieve the slow phase and quick phase data arrays from the given signal csv
def get_sp_and_qp_array(signal_dir_input, sp_column_name_input, qp_column_name_input, y_data_array_input):
    sp_array = []
    qp_array = []
    try:
        file_to_open = open(signal_dir_input)
        csv_reader = csv.reader(file_to_open)
        header_array = []
        rows = []
        count = 0

        for row in csv_reader:
            if count <= 0:
                header_array = row
                count += 1
            else:
                rows.append(row)

        slow_phase_position = get_index(sp_column_name_input, header_array)
        quick_phase_position = get_index(qp_column_name_input, header_array)
    except FileNotFoundError:
        print(f"{signal_dir_input} could not be found.")
        rows = []
        slow_phase_position = None
        quick_phase_position = None

    if len(rows) > 0:
        for row in rows:
            sp_value = row[slow_phase_position]
            qp_value = row[quick_phase_position]
            sp_array.append(str(sp_value).lower())
            qp_array.append(str(qp_value).lower())

        for ind in range(len(sp_array)):
            if sp_array[ind] == "true":
                sp_array[ind] = y_data_array_input[ind]
            else:
                sp_array[ind] = np.nan

        for ind in range(len(qp_array)):
            if qp_array[ind] == "true":
                qp_array[ind] = y_data_array_input[ind]
                previous_ind = ind - 1
                if previous_ind >= 0:
                    qp_array[ind - 1] = y_data_array_input[ind - 1]
            else:
                qp_array[ind] = np.nan
    else:
        print(f"There is no data in {signal_dir_input} or it does not exist.")

    return sp_array, qp_array


# The main function to plot the combined graph with plan array/plot info
# If max graph in a row is "none", there is no limitation of graph number in a row
def summary_plot(folder_dir_input, summary_plot_info_input, output_dir_input=None, image_name_input=None,
                 gaze_csv_dir=None, max_graph_in_a_row_input=None, summary_csv_input=None, is_sweep=False,
                 is_trial_order=True):
    title_font_size = int(summary_plot_info_input["title_font_size"])
    label_font_size = int(summary_plot_info_input["label_font_size"])
    graph_line_color = summary_plot_info_input["graph_line_color"]
    graph_line_thickness = summary_plot_info_input["graph_line_thickness"]
    max_graph_in_a_row = summary_plot_info_input["max_graph_in_a_row"]
    image_scale = summary_plot_info_input["image_scale"]
    image_width_scale = image_scale
    try:
        extra_width_scale_for_sweep = summary_plot_info_input["extra_width_scale_for_sweep"]
    except IndexError:
        extra_width_scale_for_sweep = None
    if extra_width_scale_for_sweep is not None and is_sweep:
        try:
            extra_width_scale_for_sweep = int(extra_width_scale_for_sweep)
        except ValueError:
            extra_width_scale_for_sweep = 1
        image_width_scale = image_width_scale * extra_width_scale_for_sweep

    if summary_csv_input is not None:
        plot_data_array, auto_adjust_info = get_plot_info(folder_dir_input, summary_plot_info_input, summary_csv_input)
    else:
        plot_data_array, auto_adjust_info = get_plot_info(folder_dir_input, summary_plot_info_input)

    x_adjust_limit = auto_adjust_info["x_adjust_limit"]
    x_lower_limit = x_adjust_limit["lower_limit"]
    x_upper_limit = x_adjust_limit["upper_limit"]
    y_adjust_limit = auto_adjust_info["y_adjust_limit"]
    y_lower_limit = y_adjust_limit["lower_limit"]
    y_upper_limit = y_adjust_limit["upper_limit"]

    output_image_name = summary_plot_info_input["output_image_name"]
    if output_dir_input:
        output_dir = output_dir_input
        if image_name_input is not None:
            output_image_name = image_name_input
    else:
        output_dir = folder_dir_input

    display_output_dir = os.path.join(output_dir, output_image_name)

    if image_name_input is not None:
        image_name_input = str(image_name_input)
        if image_name_input.lower().endswith(".png"):
            output_image_name = str(image_name_input)
        else:
            output_image_name = f"{image_name_input}.png"

    if gaze_csv_dir is None:
        gaze_csv_dir = str(folder_dir_input).replace(os.path.basename(folder_dir_input), "gaze.csv")
    gaze_file_exist = os.path.isfile(gaze_csv_dir)

    if max_graph_in_a_row_input is not None:
        try:
            max_graph_in_a_row = int(max_graph_in_a_row_input)
        except ValueError:
            print(f"max_graph_in_a_row_input {max_graph_in_a_row_input} could not be changed to integer.")
            print(f"Therefore, default info from config: \"{max_graph_in_a_row}\":{max_graph_in_a_row} will be used.")
    else:
        if max_graph_in_a_row != "none":
            try:
                max_graph_in_a_row = int(max_graph_in_a_row)
            except ValueError:
                print(f"max_graph_in_a_row {max_graph_in_a_row} could not be changed to integer.")
                print("Therefore, there will be no max graph limit.")

    max_graph_limit = True if type(max_graph_in_a_row) is int and max_graph_in_a_row >= 1 else False

    if not max_graph_limit:
        final_plot_array = []
        for logmar_level in logmar_level_array:
            temp_logmar_info_array = []

            for info in plot_data_array:
                if info["logmar"] == logmar_level:
                    temp_logmar_info_array.append(info)

            if len(temp_logmar_info_array) > 0:
                temp_dict = {"logmar_level": logmar_level, "info_array": temp_logmar_info_array}
                final_plot_array.append(temp_dict)

        if len(final_plot_array) > 0:
            final_row_length = len(final_plot_array)
            final_column_length = 0
            for plot_info in final_plot_array:
                info_array = plot_info["info_array"]
                if len(info_array) > final_column_length:
                    final_column_length = len(info_array)

            # print(final_row_length)
            # print(final_column_length)
            if final_row_length <= 1:
                plot_info_len = len(final_plot_array)
                if plot_info_len <= 1:
                    if len(final_plot_array[0]["info_array"]) <= 1:
                        plot_info = final_plot_array[0]
                        logmar_level = plot_info["logmar_level"]
                        info_array = plot_info["info_array"]
                        info = info_array[0]
                        x_array = info["x_array"]
                        y_array = info["y_array"]
                        x_label = info["x_label"]
                        y_label = info["y_label"]
                        sp_array = info["sp_array"]
                        sp_line_color = info["sp_line_color"]
                        sp_line_thickness = info["sp_line_thickness"]
                        qp_array = info["qp_array"]
                        qp_line_color = info["qp_line_color"]
                        qp_line_thickness = info["qp_line_thickness"]
                        trial_id = info["trial_id"]
                        if type(logmar_level) is float:
                            axs_title = f"{trial_id}(logMAR {logmar_level})"
                        else:
                            axs_title = f"{trial_id}({logmar_level})"
                        plt.plot(x_array, y_array, color=graph_line_color, linewidth=graph_line_thickness)
                        plt.plot(x_array, sp_array, color=sp_line_color, linewidth=sp_line_thickness)
                        plt.plot(x_array, qp_array, color=qp_line_color, linewidth=qp_line_thickness)
                        plt.title(axs_title)
                        plt.xlabel(x_label)
                        plt.ylabel(y_label)
                        if gaze_csv_dir:
                            event_marker_exist = string_exist("event_marker", gaze_csv_dir, "event_string")
                            if event_marker_exist:
                                event_marker_info = get_event_marker_info(gaze_csv_dir, trial_id)
                                for marker_time in event_marker_info:
                                    plt.axvline(x=float(marker_time), color=graph_line_color,
                                                linestyle=":",
                                                linewidth=graph_line_thickness, label=f"{marker_time}")
                        os.chdir(output_dir)
                        plt.savefig(output_image_name)
                        plt.close()
                    else:
                        fig, axs = plt.subplots(final_row_length, final_column_length,
                                                figsize=(final_column_length * image_width_scale,
                                                         final_row_length * image_scale))
                        for row_index, plot_info in enumerate(final_plot_array):
                            # print(row_index)
                            logmar_level = plot_info["logmar_level"]
                            info_array = plot_info["info_array"]
                            info_array_length = len(info_array)
                            num_plot_to_be_deleted = 0
                            if info_array_length < int(final_column_length):
                                num_plot_to_be_deleted = final_column_length - info_array_length
                            for column_index, info in enumerate(info_array):
                                # print(column_index)
                                x_array = info["x_array"]
                                y_array = info["y_array"]
                                x_label = info["x_label"]
                                y_label = info["y_label"]
                                sp_array = info["sp_array"]
                                sp_line_color = info["sp_line_color"]
                                sp_line_thickness = info["sp_line_thickness"]
                                qp_array = info["qp_array"]
                                qp_line_color = info["qp_line_color"]
                                qp_line_thickness = info["qp_line_thickness"]
                                trial_id = info["trial_id"]
                                if type(logmar_level) is float:
                                    axs_title = f"{trial_id}(logMAR {logmar_level})"
                                else:
                                    axs_title = f"{trial_id}({logmar_level})"
                                axs[column_index].plot(x_array, y_array, color=graph_line_color,
                                                       linewidth=graph_line_thickness)
                                axs[column_index].plot(x_array, sp_array, color=sp_line_color,
                                                       linewidth=sp_line_thickness)
                                axs[column_index].plot(x_array, qp_array, color=qp_line_color,
                                                       linewidth=qp_line_thickness)
                                axs[column_index].set_title(axs_title, fontsize=title_font_size)
                                axs[column_index].set_xlim([x_lower_limit, x_upper_limit])
                                axs[column_index].set_ylim([y_lower_limit, y_upper_limit])
                                x_axis_array = np.arange(start=x_lower_limit, stop=x_upper_limit, step=1)
                                axs[column_index].set_xticks(x_axis_array)
                                if gaze_file_exist:
                                    event_marker_exist = string_exist("event_marker", gaze_csv_dir, "event_string")
                                    if event_marker_exist:
                                        event_marker_info = get_event_marker_info(gaze_csv_dir, trial_id)
                                        for marker_time in event_marker_info:
                                            axs[column_index].axvline(x=float(marker_time),
                                                                      color=graph_line_color,
                                                                      linestyle=":",
                                                                      linewidth=graph_line_thickness)
                                # # Hide the right and top spines
                                # axs.spines.right.set_visible(False)
                                # axs.spines.top.set_visible(False)
                                for ax in axs.flat:
                                    ax.set(xlabel=x_label, ylabel=y_label)
                                    ax.xaxis.label.set(fontsize=label_font_size)
                                    ax.yaxis.label.set(fontsize=label_font_size)

                            if num_plot_to_be_deleted > 0:
                                for index in range(num_plot_to_be_deleted):
                                    # print(int(final_column_length) - index)
                                    column_index_to_be_deleted = int(final_column_length) - (index + 1)
                                    axs[row_index, column_index_to_be_deleted].set_axis_off()

                            # Hide x labels and tick labels for top plots and y ticks for right plots.
                            for ax in axs.flat:
                                ax.label_outer()

                        plt.tight_layout()
                        os.chdir(output_dir)
                        fig.savefig(output_image_name)
                        plt.close()
                else:
                    fig, axs = plt.subplots(final_row_length, final_column_length,
                                            figsize=(final_column_length * image_width_scale,
                                                     final_row_length * image_scale))
                    for row_index, plot_info in enumerate(final_plot_array):
                        # print(row_index)
                        logmar_level = plot_info["logmar_level"]
                        info_array = plot_info["info_array"]
                        info_array_length = len(info_array)
                        num_plot_to_be_deleted = 0
                        if info_array_length < int(final_column_length):
                            num_plot_to_be_deleted = final_column_length - info_array_length
                        for column_index, info in enumerate(info_array):
                            # print(column_index)
                            x_array = info["x_array"]
                            y_array = info["y_array"]
                            x_label = info["x_label"]
                            y_label = info["y_label"]
                            sp_array = info["sp_array"]
                            sp_line_color = info["sp_line_color"]
                            sp_line_thickness = info["sp_line_thickness"]
                            qp_array = info["qp_array"]
                            qp_line_color = info["qp_line_color"]
                            qp_line_thickness = info["qp_line_thickness"]
                            trial_id = info["trial_id"]
                            if type(logmar_level) is float:
                                axs_title = f"{trial_id}(logMAR {logmar_level})"
                            else:
                                axs_title = f"{trial_id}({logmar_level})"
                            axs[column_index].plot(x_array, y_array, color=graph_line_color,
                                                   linewidth=graph_line_thickness)
                            axs[column_index].plot(x_array, sp_array, color=sp_line_color, linewidth=sp_line_thickness)
                            axs[column_index].plot(x_array, qp_array, color=qp_line_color, linewidth=qp_line_thickness)
                            axs[column_index].set_title(axs_title, fontsize=title_font_size)
                            axs[column_index].set_xlim([x_lower_limit, x_upper_limit])
                            axs[column_index].set_ylim([y_lower_limit, y_upper_limit])
                            x_axis_array = np.arange(start=x_lower_limit, stop=x_upper_limit, step=1)
                            axs[column_index].set_xticks(x_axis_array)
                            if gaze_file_exist:
                                event_marker_exist = string_exist("event_marker", gaze_csv_dir, "event_string")
                                if event_marker_exist:
                                    event_marker_info = get_event_marker_info(gaze_csv_dir, trial_id)
                                    for marker_time in event_marker_info:
                                        axs[column_index].axvline(x=float(marker_time),
                                                                  color=graph_line_color,
                                                                  linestyle=":",
                                                                  linewidth=graph_line_thickness)
                            # # Hide the right and top spines
                            # axs.spines.right.set_visible(False)
                            # axs.spines.top.set_visible(False)
                            for ax in axs.flat:
                                ax.set(xlabel=x_label, ylabel=y_label)
                                ax.xaxis.label.set(fontsize=label_font_size)
                                ax.yaxis.label.set(fontsize=label_font_size)

                        if num_plot_to_be_deleted > 0:
                            for index in range(num_plot_to_be_deleted):
                                # print(int(final_column_length) - index)
                                column_index_to_be_deleted = int(final_column_length) - (index + 1)
                                axs[row_index, column_index_to_be_deleted].set_axis_off()

                        # Hide x labels and tick labels for top plots and y ticks for right plots.
                        for ax in axs.flat:
                            ax.label_outer()

                    plt.tight_layout()
                    os.chdir(output_dir)
                    fig.savefig(output_image_name)
                    plt.close()
            else:
                if final_column_length <= 1:
                    fig, axs = plt.subplots(final_row_length, final_column_length,
                                            figsize=(final_column_length * image_width_scale,
                                                     final_row_length * image_scale))

                    for row_index, plot_info in enumerate(final_plot_array):
                        logmar_level = plot_info["logmar_level"]
                        info_array = plot_info["info_array"]
                        info_array_length = len(info_array)
                        num_plot_to_be_deleted = 0
                        if info_array_length < int(final_column_length):
                            num_plot_to_be_deleted = final_column_length - info_array_length
                        for column_index, info in enumerate(info_array):
                            x_array = info["x_array"]
                            y_array = info["y_array"]
                            x_label = info["x_label"]
                            y_label = info["y_label"]
                            sp_array = info["sp_array"]
                            sp_line_color = info["sp_line_color"]
                            sp_line_thickness = info["sp_line_thickness"]
                            qp_array = info["qp_array"]
                            qp_line_color = info["qp_line_color"]
                            qp_line_thickness = info["qp_line_thickness"]
                            trial_id = info["trial_id"]
                            if type(logmar_level) is float:
                                axs_title = f"{trial_id}(logMAR {logmar_level})"
                            else:
                                axs_title = f"{trial_id}({logmar_level})"
                            # Check maximum of x_array to decide whether it needs to be expended or not
                            x_array_max = math.ceil(max(x_array))
                            # default figsize 6.4 and 4.8
                            if x_array_max >= 10:
                                # axs[row_index].figure(figsize=(x_array_max, 4.8))
                                fig.set_figwidth((x_array_max * image_scale) / 8)
                                fig.set_figheight((final_row_length * image_scale) / 2)
                            axs[row_index].plot(x_array, y_array, color=graph_line_color,
                                                linewidth=graph_line_thickness)
                            axs[row_index].plot(x_array, sp_array, color=sp_line_color,
                                                linewidth=sp_line_thickness)
                            axs[row_index].plot(x_array, qp_array, color=qp_line_color,
                                                linewidth=qp_line_thickness)
                            axs[row_index].set_title(axs_title, fontsize=title_font_size)
                            axs[row_index].set_xlim([x_lower_limit, x_upper_limit])
                            axs[row_index].set_ylim([y_lower_limit, y_upper_limit])
                            x_axis_array = np.arange(start=x_lower_limit, stop=x_upper_limit, step=1)
                            axs[row_index].set_xticks(x_axis_array)
                            if gaze_file_exist:
                                event_marker_exist = string_exist("event_marker", gaze_csv_dir, "event_string")
                                if event_marker_exist:
                                    event_marker_info = get_event_marker_info(gaze_csv_dir, trial_id)
                                    for marker_time in event_marker_info:
                                        axs[row_index].axvline(x=float(marker_time),
                                                               color=graph_line_color,
                                                               linestyle=":",
                                                               linewidth=graph_line_thickness)

                            for ax in axs.flat:
                                ax.set(xlabel=x_label, ylabel=y_label)
                                ax.xaxis.label.set(fontsize=label_font_size)
                                ax.yaxis.label.set(fontsize=label_font_size)

                        if num_plot_to_be_deleted > 0:
                            for index in range(num_plot_to_be_deleted):
                                # print(int(final_column_length) - index)
                                column_index_to_be_deleted = int(final_column_length) - (index + 1)
                                axs[row_index, column_index_to_be_deleted].set_axis_off()

                        # Hide x labels and tick labels for top plots and y ticks for right plots.
                        for ax in axs.flat:
                            ax.label_outer()

                    plt.tight_layout()
                    os.chdir(output_dir)
                    fig.savefig(output_image_name)
                    plt.close()
                else:
                    fig, axs = plt.subplots(final_row_length, final_column_length,
                                            figsize=(final_column_length * image_width_scale,
                                                     final_row_length * image_scale))
                    for row_index, plot_info in enumerate(final_plot_array):
                        logmar_level = plot_info["logmar_level"]
                        info_array = plot_info["info_array"]
                        info_array_length = len(info_array)
                        num_plot_to_be_deleted = 0
                        if info_array_length < int(final_column_length):
                            num_plot_to_be_deleted = final_column_length - info_array_length
                        for column_index, info in enumerate(info_array):
                            x_array = info["x_array"]
                            y_array = info["y_array"]
                            x_label = info["x_label"]
                            y_label = info["y_label"]
                            sp_array = info["sp_array"]
                            sp_line_color = info["sp_line_color"]
                            sp_line_thickness = info["sp_line_thickness"]
                            qp_array = info["qp_array"]
                            qp_line_color = info["qp_line_color"]
                            qp_line_thickness = info["qp_line_thickness"]
                            trial_id = info["trial_id"]
                            if type(logmar_level) is float:
                                axs_title = f"{trial_id}(logMAR {logmar_level})"
                            else:
                                axs_title = f"{trial_id}({logmar_level})"
                            axs[row_index, column_index].plot(x_array, y_array, color=graph_line_color,
                                                              linewidth=graph_line_thickness)
                            axs[row_index, column_index].plot(x_array, sp_array, color=sp_line_color,
                                                              linewidth=sp_line_thickness)
                            axs[row_index, column_index].plot(x_array, qp_array, color=qp_line_color,
                                                              linewidth=qp_line_thickness)
                            axs[row_index, column_index].set_title(axs_title, fontsize=title_font_size)
                            axs[row_index, column_index].set_xlim([x_lower_limit, x_upper_limit])
                            axs[row_index, column_index].set_ylim([y_lower_limit, y_upper_limit])
                            x_axis_array = np.arange(start=x_lower_limit, stop=x_upper_limit, step=1)
                            axs[row_index, column_index].set_xticks(x_axis_array)
                            if gaze_file_exist:
                                event_marker_exist = string_exist("event_marker", gaze_csv_dir, "event_string")
                                if event_marker_exist:
                                    event_marker_info = get_event_marker_info(gaze_csv_dir, trial_id)
                                    for marker_time in event_marker_info:
                                        axs[row_index, column_index].axvline(x=float(marker_time),
                                                                             color=graph_line_color,
                                                                             linestyle=":",
                                                                             linewidth=graph_line_thickness)

                            for ax in axs.flat:
                                ax.set(xlabel=x_label, ylabel=y_label)
                                ax.xaxis.label.set(fontsize=label_font_size)
                                ax.yaxis.label.set(fontsize=label_font_size)

                        if num_plot_to_be_deleted > 0:
                            for index in range(num_plot_to_be_deleted):
                                # print(int(final_column_length) - index)
                                column_index_to_be_deleted = int(final_column_length) - (index + 1)
                                axs[row_index, column_index_to_be_deleted].set_axis_off()

                        # Hide x labels and tick labels for top plots and y ticks for right plots.
                        for ax in axs.flat:
                            ax.label_outer()

                    plt.tight_layout()
                    os.chdir(output_dir)
                    fig.savefig(output_image_name)
                    plt.close()
            print(f"Summary plot has been saved at:{display_output_dir}")
        else:
            print("There is nothing to plot")
    else:
        if int(max_graph_in_a_row) <= 1:
            if int(max_graph_in_a_row) <= 0:
                print(f"Max graph in a row must be greater than zero but the input is {int(max_graph_in_a_row)}")
            else:
                final_plot_array = []
                for info in plot_data_array:
                    info_logmar = info["logmar"]
                    temp_dict = {"logmar_level": info_logmar, "info_array": [info]}
                    final_plot_array.append(temp_dict)
                if len(final_plot_array) > 0:
                    final_row_length = len(final_plot_array)
                    final_column_length = 0
                    for plot_info in final_plot_array:
                        info_array = plot_info["info_array"]
                        if len(info_array) > final_column_length:
                            final_column_length = len(info_array)
                    fig, axs = plt.subplots(final_row_length, final_column_length,
                                            figsize=(final_column_length * image_width_scale,
                                                     final_row_length * image_scale))
                    for row_index, plot_info in enumerate(final_plot_array):
                        logmar_level = plot_info["logmar_level"]
                        info_array = plot_info["info_array"]
                        info_array_length = len(info_array)
                        num_plot_to_be_deleted = 0
                        if info_array_length < int(final_column_length):
                            num_plot_to_be_deleted = final_column_length - info_array_length
                        for column_index, info in enumerate(info_array):
                            x_array = info["x_array"]
                            y_array = info["y_array"]
                            x_label = info["x_label"]
                            y_label = info["y_label"]
                            sp_array = info["sp_array"]
                            sp_line_color = info["sp_line_color"]
                            sp_line_thickness = info["sp_line_thickness"]
                            qp_array = info["qp_array"]
                            qp_line_color = info["qp_line_color"]
                            qp_line_thickness = info["qp_line_thickness"]
                            trial_id = info["trial_id"]
                            if type(logmar_level) is float:
                                axs_title = f"{trial_id}(logMAR {logmar_level})"
                            else:
                                axs_title = f"{trial_id}({logmar_level})"
                            axs[row_index].plot(x_array, y_array, color=graph_line_color,
                                                linewidth=graph_line_thickness)
                            axs[row_index].plot(x_array, sp_array, color=sp_line_color,
                                                linewidth=sp_line_thickness)
                            axs[row_index].plot(x_array, qp_array, color=qp_line_color,
                                                linewidth=qp_line_thickness)
                            axs[row_index].set_title(axs_title, fontsize=title_font_size)
                            axs[row_index].set_xlim([x_lower_limit, x_upper_limit])
                            axs[row_index].set_ylim([y_lower_limit, y_upper_limit])
                            x_axis_array = np.arange(start=x_lower_limit, stop=x_upper_limit, step=1)
                            axs[row_index].set_xticks(x_axis_array)
                            if gaze_file_exist:
                                event_marker_exist = string_exist("event_marker", gaze_csv_dir, "event_string")
                                if event_marker_exist:
                                    event_marker_info = get_event_marker_info(gaze_csv_dir, trial_id)
                                    for marker_time in event_marker_info:
                                        axs[row_index].axvline(x=float(marker_time),
                                                               color=graph_line_color,
                                                               linestyle=":",
                                                               linewidth=graph_line_thickness)

                            for ax in axs.flat:
                                ax.set(xlabel=x_label, ylabel=y_label)
                                ax.xaxis.label.set(fontsize=label_font_size)
                                ax.yaxis.label.set(fontsize=label_font_size)

                        if num_plot_to_be_deleted > 0:
                            for index in range(num_plot_to_be_deleted):
                                # print(int(final_column_length) - index)
                                column_index_to_be_deleted = int(final_column_length) - (index + 1)
                                axs[row_index, column_index_to_be_deleted].set_axis_off()

                        # Hide x labels and tick labels for top plots and y ticks for right plots.
                        for ax in axs.flat:
                            ax.label_outer()

                    plt.tight_layout()
                    os.chdir(output_dir)
                    fig.savefig(output_image_name)
                    plt.close()
                else:
                    print("There is nothing to plot")
        else:
            final_plot_array = []
            if is_trial_order:
                temp_logmar_info_array = []
                graph_limit = int(max_graph_in_a_row)
                graph_count = 0
                for info in plot_data_array:
                    graph_count += 1
                    if graph_count < graph_limit:
                        temp_logmar_info_array.append(info)
                    else:
                        temp_logmar_info_array.append(info)
                        temp_dict = {"logmar_level": "order_by_trial", "info_array": temp_logmar_info_array}
                        final_plot_array.append(temp_dict)
                        temp_logmar_info_array = []
                        graph_count = 0
            else:
                temp_logmar_level_array = []
                for info in plot_data_array:
                    new_logmar_level = info["logmar"]
                    if new_logmar_level not in temp_logmar_level_array:
                        temp_logmar_level_array.append(new_logmar_level)
                if not temp_logmar_level_array:
                    print("There is nothing to plot in summary plot.")
                    return
                else:
                    for temp_logmar in temp_logmar_level_array:
                        temp_logmar_info_array = []
                        for info in plot_data_array:
                            info_logmar = info["logmar"]
                            if temp_logmar == info_logmar:
                                temp_logmar_info_array.append(info)
                        temp_dict = {"logmar_level": temp_logmar, "info_array": temp_logmar_info_array}
                        final_plot_array.append(temp_dict)

            info_array_length_to_check = 0
            for info in final_plot_array:
                info_array = info["info_array"]
                if len(info_array) >= info_array_length_to_check:
                    info_array_length_to_check = len(info_array)

            # for info in final_plot_array:
            #     print("start")
            #     for name in info["info_array"]:
            #         t_id = name["trial_id"]
            #         print(f"**{t_id}**")
            #     print("end")
            # return
            if info_array_length_to_check == 0:
                print("There is nothing to plot in summary plot.")
            elif info_array_length_to_check == 1:
                if len(final_plot_array) > 0:
                    final_row_length = len(final_plot_array)
                    final_column_length = 0
                    for plot_info in final_plot_array:
                        info_array = plot_info["info_array"]
                        if len(info_array) > final_column_length:
                            final_column_length = len(info_array)
                    fig, axs = plt.subplots(final_row_length, final_column_length,
                                            figsize=(final_column_length * image_width_scale,
                                                     final_row_length * image_scale))
                    for row_index, plot_info in enumerate(final_plot_array):
                        logmar_level = plot_info["logmar_level"]
                        info_array = plot_info["info_array"]
                        info_array_length = len(info_array)
                        num_plot_to_be_deleted = 0
                        if info_array_length < int(final_column_length):
                            num_plot_to_be_deleted = final_column_length - info_array_length
                        for column_index, info in enumerate(info_array):
                            x_array = info["x_array"]
                            y_array = info["y_array"]
                            x_label = info["x_label"]
                            y_label = info["y_label"]
                            sp_array = info["sp_array"]
                            sp_line_color = info["sp_line_color"]
                            sp_line_thickness = info["sp_line_thickness"]
                            qp_array = info["qp_array"]
                            qp_line_color = info["qp_line_color"]
                            qp_line_thickness = info["qp_line_thickness"]
                            trial_id = info["trial_id"]
                            if type(logmar_level) is float:
                                axs_title = f"{trial_id}(logMAR {logmar_level})"
                            else:
                                if logmar_level == "order_by_trial":
                                    disk_condition_string = info["disk_condition"]
                                    axs_title = f"{trial_id}({disk_condition_string})"
                                else:
                                    axs_title = f"{trial_id}({logmar_level})"
                            axs[row_index].plot(x_array, y_array, color=graph_line_color,
                                                linewidth=graph_line_thickness)
                            axs[row_index].plot(x_array, sp_array, color=sp_line_color,
                                                linewidth=sp_line_thickness)
                            axs[row_index].plot(x_array, qp_array, color=qp_line_color,
                                                linewidth=qp_line_thickness)
                            axs[row_index].set_title(axs_title, fontsize=title_font_size)
                            axs[row_index].set_xlim([x_lower_limit, x_upper_limit])
                            axs[row_index].set_ylim([y_lower_limit, y_upper_limit])
                            x_axis_array = np.arange(start=x_lower_limit, stop=x_upper_limit, step=1)
                            axs[row_index].set_xticks(x_axis_array)
                            if gaze_file_exist:
                                event_marker_exist = string_exist("event_marker", gaze_csv_dir, "event_string")
                                if event_marker_exist:
                                    event_marker_info = get_event_marker_info(gaze_csv_dir, trial_id)
                                    for marker_time in event_marker_info:
                                        axs[row_index].axvline(x=float(marker_time),
                                                               color=graph_line_color,
                                                               linestyle=":",
                                                               linewidth=graph_line_thickness)

                            for ax in axs.flat:
                                ax.set(xlabel=x_label, ylabel=y_label)
                                ax.xaxis.label.set(fontsize=label_font_size)
                                ax.yaxis.label.set(fontsize=label_font_size)

                        if num_plot_to_be_deleted > 0:
                            for index in range(num_plot_to_be_deleted):
                                # print(int(final_column_length) - index)
                                column_index_to_be_deleted = int(final_column_length) - (index + 1)
                                axs[row_index, column_index_to_be_deleted].set_axis_off()

                        # Hide x labels and tick labels for top plots and y ticks for right plots.
                        for ax in axs.flat:
                            ax.label_outer()

                    plt.tight_layout()
                    os.chdir(output_dir)
                    fig.savefig(output_image_name)
                    plt.close()
                else:
                    print("There is nothing to plot")
            else:
                if len(final_plot_array) > 0:
                    final_row_length = len(final_plot_array)
                    final_column_length = 0
                    for plot_info in final_plot_array:
                        info_array = plot_info["info_array"]
                        if len(info_array) > final_column_length:
                            final_column_length = len(info_array)
                    fig, axs = plt.subplots(final_row_length, final_column_length,
                                            figsize=(final_column_length * image_width_scale,
                                                     final_row_length * image_scale))
                    for row_index, plot_info in enumerate(final_plot_array):
                        logmar_level = plot_info["logmar_level"]
                        info_array = plot_info["info_array"]
                        info_array_length = len(info_array)
                        num_plot_to_be_deleted = 0
                        if info_array_length < int(final_column_length):
                            num_plot_to_be_deleted = final_column_length - info_array_length
                        for column_index, info in enumerate(info_array):
                            x_array = info["x_array"]
                            y_array = info["y_array"]
                            x_label = info["x_label"]
                            y_label = info["y_label"]
                            sp_array = info["sp_array"]
                            sp_line_color = info["sp_line_color"]
                            sp_line_thickness = info["sp_line_thickness"]
                            qp_array = info["qp_array"]
                            qp_line_color = info["qp_line_color"]
                            qp_line_thickness = info["qp_line_thickness"]
                            trial_id = info["trial_id"]
                            if type(logmar_level) is float:
                                axs_title = f"{trial_id}(logMAR {logmar_level})"
                            else:
                                if logmar_level == "order_by_trial":
                                    disk_condition_string = info["disk_condition"]
                                    axs_title = f"{trial_id}({disk_condition_string})"
                                else:
                                    axs_title = f"{trial_id}({logmar_level})"
                            axs[row_index, column_index].plot(x_array, y_array, color=graph_line_color,
                                                              linewidth=graph_line_thickness)
                            axs[row_index, column_index].plot(x_array, sp_array, color=sp_line_color,
                                                              linewidth=sp_line_thickness)
                            axs[row_index, column_index].plot(x_array, qp_array, color=qp_line_color,
                                                              linewidth=qp_line_thickness)
                            axs[row_index, column_index].set_title(axs_title, fontsize=title_font_size)
                            axs[row_index, column_index].set_xlim([x_lower_limit, x_upper_limit])
                            axs[row_index, column_index].set_ylim([y_lower_limit, y_upper_limit])
                            x_axis_array = np.arange(start=x_lower_limit, stop=x_upper_limit, step=1)
                            axs[row_index, column_index].set_xticks(x_axis_array)
                            if gaze_file_exist:
                                event_marker_exist = string_exist("event_marker", gaze_csv_dir, "event_string")
                                if event_marker_exist:
                                    event_marker_info = get_event_marker_info(gaze_csv_dir, trial_id)
                                    for marker_time in event_marker_info:
                                        axs[row_index, column_index].axvline(x=float(marker_time),
                                                                             color=graph_line_color,
                                                                             linestyle=":",
                                                                             linewidth=graph_line_thickness)

                            for ax in axs.flat:
                                ax.set(xlabel=x_label, ylabel=y_label)
                                ax.xaxis.label.set(fontsize=label_font_size)
                                ax.yaxis.label.set(fontsize=label_font_size)

                        if num_plot_to_be_deleted > 0:
                            for index in range(num_plot_to_be_deleted):
                                # print(int(final_column_length) - index)
                                column_index_to_be_deleted = int(final_column_length) - (index + 1)
                                axs[row_index, column_index_to_be_deleted].set_axis_off()

                        # Hide x labels and tick labels for top plots and y ticks for right plots.
                        for ax in axs.flat:
                            ax.label_outer()

                    plt.tight_layout()
                    os.chdir(output_dir)
                    fig.savefig(output_image_name)
                    plt.close()
                else:
                    print("There is nothing to plot")
            print(f"Summary plot has been saved at:{display_output_dir}")


# The main function to plot the combined tidy graph with plan array/plot info
def tidy_plot(folder_dir_input, tidy_plot_info_input, output_dir_input=None, image_name=None):
    graph_line_color = tidy_plot_info_input["graph_line_color"]
    graph_line_thickness = tidy_plot_info_input["graph_line_thickness"]
    x_label = tidy_plot_info_input["x_label"]
    x_label_x_position = tidy_plot_info_input["x_label_x_position"]
    x_label_y_position = tidy_plot_info_input["x_label_y_position"]
    x_label_alignment = tidy_plot_info_input["x_label_alignment"]
    x_label_rotation = tidy_plot_info_input["x_label_rotation"]
    x_label_weight = tidy_plot_info_input["x_label_weight"]
    x_label_font_size = tidy_plot_info_input["x_label_font_size"]
    y_label = tidy_plot_info_input["y_label"]
    y_label_x_position = tidy_plot_info_input["y_label_x_position"]
    y_label_y_position = tidy_plot_info_input["y_label_y_position"]
    y_label_alignment = tidy_plot_info_input["y_label_alignment"]
    y_label_rotation = tidy_plot_info_input["y_label_rotation"]
    y_label_weight = tidy_plot_info_input["y_label_weight"]
    y_label_font_size = tidy_plot_info_input["y_label_font_size"]
    main_boundary_position = tidy_plot_info_input["main_boundary_position"]
    main_boundary_width = tidy_plot_info_input["main_boundary_width"]
    main_boundary_height = tidy_plot_info_input["main_boundary_height"]
    main_boundary_color = tidy_plot_info_input["main_boundary_color"]
    main_boundary_line_thickness = tidy_plot_info_input["main_boundary_line_thickness"]
    image_scale = tidy_plot_info_input["image_scale"]
    axis_y_label_rotation = tidy_plot_info_input["axis_y_label_rotation"]
    axis_y_label_weight = tidy_plot_info_input["axis_y_label_weight"]
    axis_y_label_font_size = tidy_plot_info_input["axis_y_label_font_size"]
    axis_y_label_pad = tidy_plot_info_input["axis_y_label_pad"]
    mid_line = tidy_plot_info_input["mid_line"]
    mid_line_level = tidy_plot_info_input["mid_line_level"]
    mid_line_color = tidy_plot_info_input["mid_line_color"]
    mid_line_style = tidy_plot_info_input["mid_line_style"]
    mid_line_thickness = tidy_plot_info_input["mid_line_thickness"]
    axis_right_top_left_bottom_borders = tidy_plot_info_input["axis_right_top_left_bottom_borders"]
    subplots_space_adjustment = tidy_plot_info_input["subplots_space_adjustment"]
    subplots_width_space = tidy_plot_info_input["subplots_width_space"]
    subplots_height_space = tidy_plot_info_input["subplots_height_space"]
    time_notation = tidy_plot_info_input["time_notation"]
    time_notation_text_position = tidy_plot_info_input["time_notation_text_position"]
    time_notation_text_weight = tidy_plot_info_input["time_notation_text_weight"]
    time_notation_text_font_size = tidy_plot_info_input["time_notation_text_font_size"]
    time_line_x_position_start_end = tidy_plot_info_input["time_line_x_position_start_end"]
    time_line_y_position_start_end = tidy_plot_info_input["time_line_y_position_start_end"]
    time_line_style = tidy_plot_info_input["time_line_style"]
    time_line_color = tidy_plot_info_input["time_line_color"]
    time_line_thickness = tidy_plot_info_input["time_line_thickness"]
    time_boundary_position = tidy_plot_info_input["time_boundary_position"]
    time_boundary_width = tidy_plot_info_input["time_boundary_width"]
    time_boundary_height = tidy_plot_info_input["time_boundary_height"]
    time_boundary_color = tidy_plot_info_input["time_boundary_color"]
    time_boundary_line_thickness = tidy_plot_info_input["time_boundary_line_thickness"]

    plot_info, adjust_limit_info = get_plot_info(folder_dir_input, tidy_plot_info_input)

    x_adjust_limit = adjust_limit_info["x_adjust_limit"]
    x_lower_limit = x_adjust_limit["lower_limit"]
    x_upper_limit = x_adjust_limit["upper_limit"]
    y_adjust_limit = adjust_limit_info["y_adjust_limit"]
    y_lower_limit = y_adjust_limit["lower_limit"]
    y_upper_limit = y_adjust_limit["upper_limit"]

    output_image_name = tidy_plot_info_input["output_image_name"]
    if output_dir_input:
        output_dir = output_dir_input
        if image_name is not None:
            output_image_name = image_name
    else:
        output_dir = folder_dir_input

    display_output_dir = os.path.join(output_dir, output_image_name)

    final_plot_array = []
    for logmar_level in logmar_level_array:
        temp_logmar_info_array = []

        for info in plot_info:
            if info["logmar"] == logmar_level:
                temp_logmar_info_array.append(info)

        if len(temp_logmar_info_array) > 0:
            temp_dict = {"logmar_level": logmar_level, "info_array": temp_logmar_info_array}
            final_plot_array.append(temp_dict)

    if len(final_plot_array) > 0:
        final_row_length = len(final_plot_array)
        final_column_length = 0
        for plot_info in final_plot_array:
            info_array = plot_info["info_array"]
            if len(info_array) > final_column_length:
                final_column_length = len(info_array)

        if final_row_length > 1:
            plot_info_len = len(final_plot_array)
            if plot_info_len <= 1:
                print("There is only 1 logmar level in the given data.")
                print("Therefore, we cannot draw tidy graph. It needs at least 2 logmar level.")
            else:
                fig, axs = plt.subplots(final_row_length, final_column_length,
                                        figsize=(final_column_length * image_scale,
                                                 final_row_length * image_scale * 0.4))

                for row_index, plot_info in enumerate(final_plot_array):
                    logmar_level = plot_info["logmar_level"]
                    info_array = plot_info["info_array"]
                    info_array_length = len(info_array)
                    num_plot_to_be_deleted = 0
                    if info_array_length < int(final_column_length):
                        num_plot_to_be_deleted = final_column_length - info_array_length
                    for column_index, info in enumerate(info_array):
                        x_array = info["x_array"]
                        y_array = info["y_array"]
                        sp_array = info["sp_array"]
                        sp_line_color = info["sp_line_color"]
                        sp_line_thickness = info["sp_line_thickness"]
                        qp_array = info["qp_array"]
                        qp_line_color = info["qp_line_color"]
                        qp_line_thickness = info["qp_line_thickness"]
                        axs[row_index, column_index].plot(x_array, y_array, color=graph_line_color,
                                                          linewidth=graph_line_thickness)
                        axs[row_index, column_index].plot(x_array, sp_array, color=sp_line_color,
                                                          linewidth=sp_line_thickness)
                        axs[row_index, column_index].plot(x_array, qp_array, color=qp_line_color,
                                                          linewidth=qp_line_thickness)
                        axs[row_index, column_index].set_xlim([x_lower_limit, x_upper_limit])
                        axs[row_index, column_index].set_ylim([y_lower_limit, y_upper_limit])
                        if type(logmar_level) is int or type(logmar_level) is float:
                            axs[row_index, column_index].set_ylabel(str(logmar_level),
                                                                    rotation=axis_y_label_rotation,
                                                                    weight=axis_y_label_weight,
                                                                    fontsize=axis_y_label_font_size,
                                                                    labelpad=axis_y_label_pad)
                        else:
                            axs[row_index, column_index].set_ylabel(str("None  "),
                                                                    rotation=axis_y_label_rotation,
                                                                    weight=axis_y_label_weight,
                                                                    fontsize=axis_y_label_font_size,
                                                                    labelpad=axis_y_label_pad)
                        axs[row_index, column_index].set_xticks([])
                        axs[row_index, column_index].set_yticks([])
                        if mid_line:
                            axs[row_index, column_index].axhline(y=mid_line_level, color=mid_line_color,
                                                                 linestyle=mid_line_style,
                                                                 linewidth=mid_line_thickness)

                        # Hide/Show the borders/spines
                        for axx in axs.flat:
                            axx.spines['right'].set_visible(axis_right_top_left_bottom_borders[0])
                            axx.spines['top'].set_visible(axis_right_top_left_bottom_borders[1])
                            axx.spines['left'].set_visible(axis_right_top_left_bottom_borders[2])
                            axx.spines['bottom'].set_visible(axis_right_top_left_bottom_borders[3])

                    if num_plot_to_be_deleted > 0:
                        for index in range(num_plot_to_be_deleted):
                            column_index_to_be_deleted = int(final_column_length) - (index + 1)
                            axs[row_index, column_index_to_be_deleted].set_axis_off()

                    # Hide all x-axis labels inside the combined graph and show left and outside.
                    for ax in axs.flat:
                        ax.label_outer()

                plt.tick_params(
                    axis='x',  # changes apply to the x-axis
                    which='both',
                    left=False,
                    right=False,  # both major and minor ticks are affected
                    bottom=False,  # ticks along the bottom edge are off
                    top=False,  # ticks along the top edge are off
                    labelbottom=False)  # labels along the bottom edge are off
                plt.tick_params(
                    axis='y',  # changes apply to the y-axis
                    which='both',
                    left=False,
                    right=False,  # both major and minor ticks are affected
                    bottom=False,  # ticks along the bottom edge are off
                    top=False,  # ticks along the top edge are off
                    labelbottom=False)  # labels along the bottom edge are off
                plt.xticks([]), plt.yticks([])

                if subplots_space_adjustment:
                    plt.subplots_adjust(wspace=subplots_width_space, hspace=subplots_height_space)

                fig.text(x_label_x_position, x_label_y_position, x_label,
                         ha=x_label_alignment, rotation=x_label_rotation,
                         weight=x_label_weight, fontsize=x_label_font_size)
                fig.text(y_label_x_position, y_label_y_position, y_label,
                         va=y_label_alignment, rotation=y_label_rotation,
                         weight=y_label_weight, fontsize=y_label_font_size)
                main_boundary = plt.Rectangle(
                    # (x,y at lower-left corner), width, height
                    (main_boundary_position[0], main_boundary_position[1]),
                    main_boundary_width, main_boundary_height,
                    fill=False, color=main_boundary_color,
                    lw=main_boundary_line_thickness,
                    zorder=1000, transform=fig.transFigure,
                    figure=fig
                )
                if time_notation and time_notation != "none":
                    fig.text(time_notation_text_position[0],
                             time_notation_text_position[1],
                             time_notation,
                             weight=time_notation_text_weight,
                             fontsize=time_notation_text_font_size)
                    fig.add_artist(Line2D(time_line_x_position_start_end, time_line_y_position_start_end,
                                          linestyle=time_line_style, color=time_line_color,
                                          linewidth=time_line_thickness))
                    time_notation_boundary = plt.Rectangle(
                        # (x,y at lower-left corner), width, height
                        (time_boundary_position[0], time_boundary_position[1]),
                        time_boundary_width, time_boundary_height,
                        fill=False, color=time_boundary_color,
                        lw=time_boundary_line_thickness,
                        zorder=1000, transform=fig.transFigure,
                        figure=fig
                    )
                    fig.patches.extend([main_boundary, time_notation_boundary])
                else:
                    fig.patches.extend([main_boundary])
                os.chdir(output_dir)
                fig.savefig(output_image_name)
                plt.close()
            print(f"Tidy plot has been saved at:{display_output_dir}")
        else:
            print("There is only 1 logmar level in the given data.")
            print("Therefore, we cannot draw tidy graph. It needs at least 2 logmar level.")
    else:
        print("There is nothing to plot")


# This function is to draw va testing progress graph from the given config info
def progress_plot(folder_dir_input, progress_plot_info_input, output_dir_input=None, image_name=None):
    x_label = progress_plot_info_input["x_label"]
    y_label = progress_plot_info_input["y_label"]
    x_data_column_name = progress_plot_info_input["x_data_column_name"]
    y_data_column_name = progress_plot_info_input["y_data_column_name"]
    okn_column_name = progress_plot_info_input["okn_column_name"]
    phase_column_name = progress_plot_info_input["phase_column_name"]
    final_logmar_column_name = progress_plot_info_input["final_logmar_column_name"]
    graph_line_color = progress_plot_info_input["graph_line_color"]
    graph_line_thickness = progress_plot_info_input["graph_line_thickness"]
    graph_line_style = progress_plot_info_input["graph_line_style"]
    trial_summary_csv_name = progress_plot_info_input["trial_summary_csv_name"]
    output_image_name = progress_plot_info_input["output_image_name"]
    marker_type_equivalent = progress_plot_info_input["marker_type_equivalent"]
    marker_type = progress_plot_info_input["marker_type"]
    marker_size = progress_plot_info_input["marker_size"]
    okn_marker_color = progress_plot_info_input["okn_marker_color"]
    okn_marker_edge_color = progress_plot_info_input["okn_marker_edge_color"]
    okn_legend_label = progress_plot_info_input["okn_legend_label"]
    non_okn_marker_color = progress_plot_info_input["non_okn_marker_color"]
    non_okn_marker_edge_color = progress_plot_info_input["non_okn_marker_edge_color"]
    non_okn_legend_label = progress_plot_info_input["non_okn_legend_label"]
    best_va_line = progress_plot_info_input["best_va_line"]
    best_va_line_color = progress_plot_info_input["best_va_line_color"]
    best_va_line_thickness = progress_plot_info_input["best_va_line_thickness"]
    best_va_line_style = progress_plot_info_input["best_va_line_style"]
    best_va_line_legend_label = progress_plot_info_input["best_va_line_legend_label"]
    final_va_line = progress_plot_info_input["final_va_line"]
    final_va_line_color = progress_plot_info_input["final_va_line_color"]
    final_va_line_thickness = progress_plot_info_input["final_va_line_thickness"]
    final_va_line_style = progress_plot_info_input["final_va_line_style"]
    final_va_line_legend_label = progress_plot_info_input["final_va_line_legend_label"]
    legend_background_color = progress_plot_info_input["legend_background_color"]
    legend_edge_color = progress_plot_info_input["legend_edge_color"]
    legend_location = progress_plot_info_input["legend_location"]
    legend_font_size = progress_plot_info_input["legend_font_size"]
    legend_icon_size = progress_plot_info_input["legend_icon_size"]
    line_style_equivalent = progress_plot_info_input["line_style_equivalent"]

    trial_data_csv_dir = os.path.join(folder_dir_input, trial_summary_csv_name)

    if output_dir_input:
        output_dir = output_dir_input
        if image_name is not None:
            output_image_name = image_name
    else:
        output_dir = folder_dir_input

    display_output_dir = os.path.join(output_dir, output_image_name)

    try:
        file_to_open = open(trial_data_csv_dir)
        csv_reader = csv.reader(file_to_open)
        header_array = []
        rows = []
        count_one = 0

        for row in csv_reader:
            if count_one <= 0:
                header_array = row
                count_one += 1
            else:
                rows.append(row)

        x_header_position = get_index(x_data_column_name, header_array)
        y_header_position = get_index(y_data_column_name, header_array)
        okn_header_position = get_index(okn_column_name, header_array)
    except FileNotFoundError:
        print(f"{trial_data_csv_dir} could not be found.")
        rows = []
        x_header_position = None
        y_header_position = None
        okn_header_position = None

    # print(x_header_position)
    # print(y_header_position)
    x_array = []
    y_array = []
    okn_array = []
    x_index_array = []

    if len(rows) > 0:
        for row in rows:
            okn_result = str(row[okn_header_position])
            if okn_result.lower() != "restart":
                okn_array.append(okn_result.lower())
                x_array.append(row[x_header_position])
                y_array.append(disk_to_logmar(str(row[y_header_position])))

        for ind in range(len(x_array)):
            x_index_array.append(str(ind + 1))

        # print(x_array)
        # print(y_array)
        # print(okn_array)
        overlay_x_array = []
        overlay_y_array = []
        # final_va_line_level = y_array[-1]

        for ind, value in enumerate(okn_array):
            if value.lower() == "true" or value.lower() == "1":
                overlay_x_array.append(x_index_array[ind])
                overlay_y_array.append(y_array[ind])

        bot_limit = min(y_array) - 0.2
        top_limit = max(y_array) + 0.1

        plt.plot(x_index_array, y_array, line_style_equivalent[graph_line_style],
                 marker=marker_type_equivalent[marker_type], markersize=marker_size, fillstyle='full',
                 color=graph_line_color, linewidth=graph_line_thickness,
                 markerfacecolor=non_okn_marker_color, markeredgecolor=non_okn_marker_edge_color)
        plt.plot(overlay_x_array, overlay_y_array, ' ', marker=marker_type_equivalent[marker_type],
                 markersize=marker_size, fillstyle='full', color=graph_line_color,
                 linewidth=graph_line_thickness, markerfacecolor=okn_marker_color,
                 markeredgecolor=okn_marker_edge_color)

        default_va = 1
        if best_va_line:
            best_va_line_level = get_va_by_phase_name(trial_data_csv_dir, phase_column_name,
                                                      final_logmar_column_name, "best")
            if not best_va_line_level:
                best_va_line_level = default_va
                default_va = best_va_line_level
            else:
                default_va = best_va_line_level
            plt.axhline(y=best_va_line_level, color=best_va_line_color,
                        linestyle=line_style_equivalent[best_va_line_style],
                        linewidth=best_va_line_thickness)
        if final_va_line:
            final_va_line_level = get_va_by_phase_name(trial_data_csv_dir, phase_column_name,
                                                       final_logmar_column_name, "final")
            if not final_va_line_level:
                final_va_line_level = default_va
            plt.axhline(y=final_va_line_level, color=final_va_line_color,
                        linestyle=line_style_equivalent[final_va_line_style],
                        linewidth=final_va_line_thickness)
        plt.ylim(bot_limit, top_limit)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        # plt.xticks(rotation=90)
        y_axis_array = np.arange(start=top_limit, stop=bot_limit, step=-0.1)
        plt.yticks(y_axis_array)
        plt.tight_layout()

        legend_array = []
        okn_marker = Line2D([0], [0], marker=marker_type_equivalent[marker_type],
                            color=legend_background_color, label=okn_legend_label,
                            markerfacecolor=okn_marker_color, markeredgecolor=okn_marker_edge_color,
                            markersize=legend_icon_size)
        legend_array.append(okn_marker)
        non_okn_marker = Line2D([0], [0], marker=marker_type_equivalent[marker_type],
                                color=legend_background_color, label=non_okn_legend_label,
                                markerfacecolor=non_okn_marker_color, markeredgecolor=non_okn_marker_edge_color,
                                markersize=legend_icon_size)
        legend_array.append(non_okn_marker)
        if best_va_line:
            best_va_line = Line2D([0], [0], linestyle=line_style_equivalent[best_va_line_style],
                                  color=best_va_line_color, label=best_va_line_legend_label,
                                  linewidth=best_va_line_thickness)
            legend_array.append(best_va_line)
        if final_va_line:
            final_va_line = Line2D([0], [0], linestyle=line_style_equivalent[final_va_line_style],
                                   color=final_va_line_color, label=final_va_line_legend_label,
                                   linewidth=final_va_line_thickness)
            legend_array.append(final_va_line)
        # legend_array = [okn_marker, non_okn_marker, final_va_line]
        legend = plt.legend(handles=legend_array, loc=legend_location, fontsize=legend_font_size, fancybox=True)
        frame = legend.get_frame()
        frame.set_facecolor(legend_background_color)
        frame.set_edgecolor(legend_edge_color)
        frame.set_alpha(1)
        os.chdir(output_dir)
        plt.savefig(output_image_name)
        # plt.show()
        plt.close()
        print(f"Staircase/progress plot has been saved at:{display_output_dir}")
    else:
        print(f"There is no data in {trial_summary_csv_name} or it does not exist.")


# This function is to produce x and y adjustment limits according the type of adjustment
# Type comes into the function as int number and is converted into string to be used
# to retrieve the string type from adjustment dictionary
def get_adjust_limit(data_dir_input, csv_name, x_header_input, y_header_input, folder_array_input,
                     x_axis_limit_input, y_axis_limit_input, mean_offset_input,
                     axis_adjustment_types_input, axis_adjustment_type_number_input,
                     signal_folder_name=None, signal_csv_name=None):
    adjustment_type = axis_adjustment_types_input[str(axis_adjustment_type_number_input)]
    ignore_folder_array = []
    print(f"axis_adjustment_type:{adjustment_type}")
    if adjustment_type == "manual":
        x_adjust_limit = {"lower_limit": x_axis_limit_input[0], "upper_limit": x_axis_limit_input[1]}
        y_adjust_limit = {"lower_limit": y_axis_limit_input[0], "upper_limit": y_axis_limit_input[1]}
        print(f"x_adjust_limit:{x_adjust_limit}")
        print(f"y_adjust_limit:{y_adjust_limit}")

    elif adjustment_type == "min_max_mean":
        x_lower_limit_array = []
        x_upper_limit_array = []
        y_lower_limit_array = []
        y_upper_limit_array = []
        for folder in folder_array_input:
            if not csv_name:
                # Default csv name
                updated_csv_name = f"updated_{folder}.csv"
            else:
                updated_csv_name = csv_name
            # Error handling for value error
            # IF there is value error that that folder, its name will be put into the ignore_folder_array
            try:
                if signal_folder_name is not None and signal_csv_name is not None:
                    data_dir_to_be_used = os.path.join(data_dir_input, folder, signal_folder_name, signal_csv_name)
                else:
                    data_dir_to_be_used = os.path.join(data_dir_input, folder, updated_csv_name)
                x_array = get_data_array(data_dir_to_be_used, x_header_input)
                x_lower_limit_array.append(min(x_array))
                x_upper_limit_array.append(max(x_array))
                y_array = get_data_array(data_dir_to_be_used, y_header_input)
                y_lower_limit_array.append(min(y_array))
                y_upper_limit_array.append(max(y_array))
            except ValueError:
                ignore_folder_array.append(folder)

        x_adjust_limit = {"lower_limit": int(min(x_lower_limit_array)),
                          "upper_limit": int(max(x_upper_limit_array))}
        y_adjust_limit = {"lower_limit": round(float(np.nanmean(y_lower_limit_array)), 2),
                          "upper_limit": round(float(np.nanmean(y_upper_limit_array)), 2)}
        print(f"x_adjust_limit:{x_adjust_limit}")
        print(f"y_adjust_limit:{y_adjust_limit}")

    elif adjustment_type == "mean_offset":
        x_lower_limit_array = []
        x_upper_limit_array = []
        for folder in folder_array_input:
            if not csv_name:
                # Default csv name
                updated_csv_name = f"updated_{folder}.csv"
            else:
                updated_csv_name = csv_name
            # Error handling for value error
            # IF there is value error that that folder, its name will be put into the ignore_folder_array
            try:
                if signal_folder_name is not None and signal_csv_name is not None:
                    data_dir_to_be_used = os.path.join(data_dir_input, folder, signal_folder_name, signal_csv_name)
                else:
                    data_dir_to_be_used = os.path.join(data_dir_input, folder, updated_csv_name)
                x_array = get_data_array(data_dir_to_be_used, x_header_input)
                # print(data_dir_to_be_used)
                x_lower_limit_array.append(min(x_array))
                x_upper_limit_array.append(max(x_array))
                # y_array = get_data_array(data_dir_to_be_used, y_header_input)
            except ValueError:
                ignore_folder_array.append(folder)

        x_adjust_limit = {"lower_limit": int(min(x_lower_limit_array)),
                          "upper_limit": int(max(x_upper_limit_array))}
        y_adjust_limit = {"lower_limit": round(float(- mean_offset_input), 2),
                          "upper_limit": round(float(mean_offset_input), 2)}
        print(f"x_adjust_limit:{x_adjust_limit}")
        print(f"y_adjust_limit:{y_adjust_limit}")

    else:
        x_lower_limit_array = []
        x_upper_limit_array = []
        y_lower_limit_array = []
        y_upper_limit_array = []
        for folder in folder_array_input:
            if not csv_name:
                # Default csv name
                updated_csv_name = f"updated_{folder}.csv"
            else:
                updated_csv_name = csv_name
            # Error handling for value error
            # IF there is value error that that folder, its name will be put into the ignore_folder_array
            try:
                if signal_folder_name is not None and signal_csv_name is not None:
                    data_dir_to_be_used = os.path.join(data_dir_input, folder, signal_folder_name, signal_csv_name)
                else:
                    data_dir_to_be_used = os.path.join(data_dir_input, folder, updated_csv_name)
                x_array = get_data_array(data_dir_to_be_used, x_header_input)
                x_lower_limit_array.append(min(x_array))
                x_upper_limit_array.append(max(x_array))
                y_array = get_data_array(data_dir_to_be_used, y_header_input)
                y_lower_limit_array.append(min(y_array))
                y_upper_limit_array.append(max(y_array))
            except ValueError:
                ignore_folder_array.append(folder)

        x_adjust_limit = {"lower_limit": int(min(x_lower_limit_array)),
                          "upper_limit": int(max(x_upper_limit_array))}
        y_adjust_limit = {"lower_limit": round(min(y_lower_limit_array), 2),
                          "upper_limit": round(max(y_upper_limit_array), 2)}
        print(f"x_adjust_limit:{x_adjust_limit}")
        print(f"y_adjust_limit:{y_adjust_limit}")
        if ignore_folder_array:
            num_of_ignore_folder = len(ignore_folder_array)
            if num_of_ignore_folder > 1:
                print(f"{num_of_ignore_folder} folders are ignored because of value error.")
            else:
                print(f"{num_of_ignore_folder} folder is ignored because of value error.")

    return x_adjust_limit, y_adjust_limit, ignore_folder_array


def get_draw_info_for_trial_plot(config_info_input, x_array_input, y_array_input):
    x_axis_limit = config_info_input["x_axis_limit"]
    y_axis_limit = config_info_input["y_axis_limit"]
    mean_offset = config_info_input["mean_offset"]
    axis_adjustment_types = config_info_input["axis_adjustment_types"]
    axis_adjustment_type_number = config_info_input["axis_adjustment_type_number"]
    adjustment_type = axis_adjustment_types[str(axis_adjustment_type_number)]
    print(f"axis_adjustment_type:{adjustment_type}")
    if adjustment_type == "manual":
        x_adjust_limit = {"lower_limit": x_axis_limit[0], "upper_limit": x_axis_limit[1]}
        y_adjust_limit = {"lower_limit": y_axis_limit[0], "upper_limit": y_axis_limit[1]}
        print(f"x_adjust_limit:{x_adjust_limit}")
        print(f"y_adjust_limit:{y_adjust_limit}")

    elif adjustment_type == "mean_offset":
        x_adjust_limit = {"lower_limit": int(min(x_array_input)),
                          "upper_limit": int(max(x_array_input))}
        y_adjust_limit = {"lower_limit": round(float(- mean_offset), 2),
                          "upper_limit": round(float(mean_offset), 2)}

        y_mean = np.nanmean(y_array_input)
        temp_array = []
        for num in y_array_input:
            if not np.isnan(num):
                temp_number = num - y_mean
                temp_array.append(temp_number)
            else:
                temp_array.append(num)
        y_array_input = temp_array

        print(f"x_adjust_limit:{x_adjust_limit}")
        print(f"y_adjust_limit:{y_adjust_limit}")

    else:
        x_adjust_limit = {"lower_limit": int(min(x_array_input)),
                          "upper_limit": int(max(x_array_input))}
        y_adjust_limit = {"lower_limit": round(min(y_array_input), 2),
                          "upper_limit": round(max(y_array_input), 2)}
        print(f"x_adjust_limit:{x_adjust_limit}")
        print(f"y_adjust_limit:{y_adjust_limit}")

    return x_adjust_limit, y_adjust_limit, x_array_input, y_array_input


def get_va_by_phase_name(csv_dir_input, phase_header_input, final_logmar_header_input, phase_name_input):
    try:
        file_to_open = open(csv_dir_input)
        csv_reader = csv.reader(file_to_open)
        header_array = []
        rows = []
        count_one = 0

        for row in csv_reader:
            if count_one <= 0:
                header_array = row
                count_one += 1
            else:
                rows.append(row)

        phase_header_position = get_index(phase_header_input, header_array)
        final_logmar_header_position = get_index(final_logmar_header_input, header_array)
    except FileNotFoundError:
        print(f"{csv_dir_input} could not be found.")
        rows = []
        phase_header_position = None
        final_logmar_header_position = None

    va_output = None

    if len(rows) > 0:
        last_row = rows[-1]
        va_output = float(last_row[final_logmar_header_position])
        for row in rows:
            if row[phase_header_position] == phase_name_input:
                va_output = float(row[final_logmar_header_position])
    else:
        print(f"There is no data in {csv_dir_input} or it does not exist.")

    return va_output


def string_exist(string_to_check, csv_to_check, column_to_check):
    try:
        file_to_open = open(csv_to_check)
        csv_reader = csv.reader(file_to_open)
        header_array = []
        rows = []
        count = 0

        for row in csv_reader:
            if count <= 0:
                header_array = row
                count += 1
            else:
                rows.append(row)

        event_marker_position = get_index(column_to_check, header_array)
    except FileNotFoundError:
        print(f"{csv_to_check} could not be found.")
        rows = []
        event_marker_position = None

    if len(rows) > 0:
        for row in rows:
            if str(string_to_check) in row[event_marker_position]:
                return True
    else:
        print(f"There is no data in {csv_to_check} or it does not exist.")
        return False

    return False


def get_event_marker_info(gaze_csv_input, trial_id_input):
    try:
        file_to_open = open(gaze_csv_input)
        csv_reader = csv.reader(file_to_open)
        header_array = []
        rows = []
        count = 0

        for row in csv_reader:
            if count <= 0:
                header_array = row
                count += 1
            else:
                rows.append(row)

        # sts = sensor timestamp
        event_string_position = get_index("event_string", header_array)
        sts_position = get_index("sensor_timestamp", header_array)
    except FileNotFoundError:
        print(f"{gaze_csv_input} could not be found.")
        rows = []
        event_string_position = None
        sts_position = None

    event_marker_array = []
    start_marker = None
    if len(rows) > 0:
        for row in rows:
            event_string = row[event_string_position]
            if start_marker is None:
                if "start_marker" in event_string and str(trial_id_input) in event_string:
                    start_marker = float(row[sts_position])
            else:
                if "event_marker" in event_string and str(trial_id_input) in event_string:
                    event_marker_sts = float(row[sts_position])
                    # event_marker_time_i = int(event_marker_sts - start_marker)
                    # event_marker_time_f = float(event_marker_sts - start_marker)
                    # print(event_marker_time_f - event_marker_time_i)
                    event_marker_array.append(float(event_marker_sts - start_marker))
    else:
        print(f"There is no data in {gaze_csv_input} or it does not exist.")

    return event_marker_array


def simpler_plot(folder_dir_input, config_input, referenced_csv_to_be_used, output_file_dir_input=None):
    graph_line_color = config_input["graph_line_color"]
    graph_line_thickness = config_input["graph_line_thickness"]
    x_label = config_input["x_label"]
    x_label_x_position = config_input["x_label_x_position"]
    x_label_y_position = config_input["x_label_y_position"]
    x_label_alignment = config_input["x_label_alignment"]
    x_label_rotation = config_input["x_label_rotation"]
    x_label_weight = config_input["x_label_weight"]
    x_label_font_size = config_input["x_label_font_size"]
    y_label = config_input["y_label"]
    y_label_x_position = config_input["y_label_x_position"]
    y_label_y_position = config_input["y_label_y_position"]
    y_label_alignment = config_input["y_label_alignment"]
    y_label_rotation = config_input["y_label_rotation"]
    y_label_weight = config_input["y_label_weight"]
    y_label_font_size = config_input["y_label_font_size"]
    main_boundary_position = config_input["main_boundary_position"]
    main_boundary_width = config_input["main_boundary_width"]
    main_boundary_height = config_input["main_boundary_height"]
    main_boundary_color = config_input["main_boundary_color"]
    main_boundary_line_thickness = config_input["main_boundary_line_thickness"]
    image_scale = config_input["image_scale"]
    axis_y_label_rotation = config_input["axis_y_label_rotation"]
    axis_y_label_weight = config_input["axis_y_label_weight"]
    axis_y_label_font_size = config_input["axis_y_label_font_size"]
    axis_y_label_pad = config_input["axis_y_label_pad"]
    mid_line = config_input["mid_line"]
    mid_line_level = config_input["mid_line_level"]
    mid_line_color = config_input["mid_line_color"]
    mid_line_style = config_input["mid_line_style"]
    mid_line_thickness = config_input["mid_line_thickness"]
    axis_right_top_left_bottom_borders = config_input["axis_right_top_left_bottom_borders"]
    subplots_space_adjustment = config_input["subplots_space_adjustment"]
    subplots_width_space = config_input["subplots_width_space"]
    subplots_height_space = config_input["subplots_height_space"]
    time_notation = config_input["time_notation"]
    time_notation_text_position = config_input["time_notation_text_position"]
    time_notation_text_weight = config_input["time_notation_text_weight"]
    time_notation_text_font_size = config_input["time_notation_text_font_size"]
    time_line_x_position_start_end = config_input["time_line_x_position_start_end"]
    time_line_y_position_start_end = config_input["time_line_y_position_start_end"]
    time_line_style = config_input["time_line_style"]
    time_line_color = config_input["time_line_color"]
    time_line_thickness = config_input["time_line_thickness"]
    time_boundary_position = config_input["time_boundary_position"]
    time_boundary_width = config_input["time_boundary_width"]
    time_boundary_height = config_input["time_boundary_height"]
    time_boundary_color = config_input["time_boundary_color"]
    time_boundary_line_thickness = config_input["time_boundary_line_thickness"]

    plot_info, adjust_limit_info = get_plot_info_for_simpler(folder_dir_input, config_input, referenced_csv_to_be_used)

    x_adjust_limit = adjust_limit_info["x_adjust_limit"]
    x_lower_limit = x_adjust_limit["lower_limit"]
    x_upper_limit = x_adjust_limit["upper_limit"]
    y_adjust_limit = adjust_limit_info["y_adjust_limit"]
    y_lower_limit = y_adjust_limit["lower_limit"]
    y_upper_limit = y_adjust_limit["upper_limit"]

    output_image_name = config_input["output_image_name"]
    display_output_dir = os.path.join(folder_dir_input, output_image_name)
    output_dir = folder_dir_input
    if output_file_dir_input:
        display_output_dir = output_file_dir_input
        output_image_name = os.path.basename(output_file_dir_input)
        output_dir = os.path.join(output_file_dir_input, os.pardir)

    final_plot_array = []
    for logmar_level in logmar_level_array:
        temp_logmar_info_array = []

        for info in plot_info:
            if info["logmar"] == logmar_level:
                temp_logmar_info_array.append(info)

        if len(temp_logmar_info_array) > 0:
            temp_dict = {"logmar_level": logmar_level, "info_array": temp_logmar_info_array}
            final_plot_array.append(temp_dict)

    if len(final_plot_array) > 0:
        final_row_length = len(final_plot_array)
        final_column_length = 0
        for plot_info in final_plot_array:
            info_array = plot_info["info_array"]
            if len(info_array) > final_column_length:
                final_column_length = len(info_array)

        if final_row_length > 1:
            plot_info_len = len(final_plot_array)
            if plot_info_len <= 1:
                print("There is only 1 logmar level in the given data.")
                print("Therefore, we cannot draw simpler graph. It needs at least 2 logmar level.")
            else:
                fig, axs = plt.subplots(final_row_length, final_column_length,
                                        figsize=(final_column_length * image_scale * 1,
                                                 final_row_length * image_scale * 1))

                for row_index, plot_info in enumerate(final_plot_array):
                    logmar_level = plot_info["logmar_level"]
                    info_array = plot_info["info_array"]
                    info_array_length = len(info_array)
                    num_plot_to_be_deleted = 0
                    if info_array_length < int(final_column_length):
                        num_plot_to_be_deleted = final_column_length - info_array_length
                    for column_index, info in enumerate(info_array):
                        x_array = info["x_array"]
                        y_array = info["y_array"]
                        sp_array = info["sp_array"]
                        sp_line_color = info["sp_line_color"]
                        sp_line_thickness = info["sp_line_thickness"]
                        qp_array = info["qp_array"]
                        qp_line_color = info["qp_line_color"]
                        qp_line_thickness = info["qp_line_thickness"]
                        axs[row_index, column_index].plot(x_array, y_array, color=graph_line_color,
                                                          linewidth=graph_line_thickness)
                        axs[row_index, column_index].plot(x_array, sp_array, color=sp_line_color,
                                                          linewidth=sp_line_thickness)
                        axs[row_index, column_index].plot(x_array, qp_array, color=qp_line_color,
                                                          linewidth=qp_line_thickness)
                        axs[row_index, column_index].set_xlim([x_lower_limit, x_upper_limit])
                        axs[row_index, column_index].set_ylim([y_lower_limit, y_upper_limit])
                        if type(logmar_level) is int or type(logmar_level) is float:
                            axs[row_index, column_index].set_ylabel(str(logmar_level),
                                                                    rotation=axis_y_label_rotation,
                                                                    weight=axis_y_label_weight,
                                                                    fontsize=axis_y_label_font_size,
                                                                    labelpad=axis_y_label_pad)
                        else:
                            axs[row_index, column_index].set_ylabel(str("None  "),
                                                                    rotation=axis_y_label_rotation,
                                                                    weight=axis_y_label_weight,
                                                                    fontsize=axis_y_label_font_size,
                                                                    labelpad=axis_y_label_pad)
                        axs[row_index, column_index].set_xticks([])
                        axs[row_index, column_index].set_yticks([])
                        if mid_line:
                            axs[row_index, column_index].axhline(y=mid_line_level, color=mid_line_color,
                                                                 linestyle=mid_line_style,
                                                                 linewidth=mid_line_thickness)

                        # Hide/Show the borders/spines
                        for axx in axs.flat:
                            axx.spines['right'].set_visible(axis_right_top_left_bottom_borders[0])
                            axx.spines['top'].set_visible(axis_right_top_left_bottom_borders[1])
                            axx.spines['left'].set_visible(axis_right_top_left_bottom_borders[2])
                            axx.spines['bottom'].set_visible(axis_right_top_left_bottom_borders[3])

                    if num_plot_to_be_deleted > 0:
                        for index in range(num_plot_to_be_deleted):
                            column_index_to_be_deleted = int(final_column_length) - (index + 1)
                            axs[row_index, column_index_to_be_deleted].set_axis_off()

                    # Hide all x-axis labels inside the combined graph and show left and outside.
                    for ax in axs.flat:
                        ax.label_outer()

                plt.tick_params(
                    axis='x',  # changes apply to the x-axis
                    which='both',
                    left=False,
                    right=False,  # both major and minor ticks are affected
                    bottom=False,  # ticks along the bottom edge are off
                    top=False,  # ticks along the top edge are off
                    labelbottom=False)  # labels along the bottom edge are off
                plt.tick_params(
                    axis='y',  # changes apply to the y-axis
                    which='both',
                    left=False,
                    right=False,  # both major and minor ticks are affected
                    bottom=False,  # ticks along the bottom edge are off
                    top=False,  # ticks along the top edge are off
                    labelbottom=False)  # labels along the bottom edge are off
                plt.xticks([]), plt.yticks([])

                if subplots_space_adjustment:
                    plt.subplots_adjust(wspace=subplots_width_space, hspace=subplots_height_space)

                fig.text(x_label_x_position, x_label_y_position, x_label,
                         ha=x_label_alignment, rotation=x_label_rotation,
                         weight=x_label_weight, fontsize=x_label_font_size)
                fig.text(y_label_x_position, y_label_y_position, y_label,
                         va=y_label_alignment, rotation=y_label_rotation,
                         weight=y_label_weight, fontsize=y_label_font_size)
                main_boundary = plt.Rectangle(
                    # (x,y at lower-left corner), width, height
                    (main_boundary_position[0], main_boundary_position[1]),
                    main_boundary_width, main_boundary_height,
                    fill=False, color=main_boundary_color,
                    lw=main_boundary_line_thickness,
                    zorder=1000, transform=fig.transFigure,
                    figure=fig
                )
                if time_notation and time_notation != "none":
                    fig.text(time_notation_text_position[0],
                             time_notation_text_position[1],
                             time_notation,
                             weight=time_notation_text_weight,
                             fontsize=time_notation_text_font_size)
                    fig.add_artist(Line2D(time_line_x_position_start_end, time_line_y_position_start_end,
                                          linestyle=time_line_style, color=time_line_color,
                                          linewidth=time_line_thickness))
                    time_notation_boundary = plt.Rectangle(
                        # (x,y at lower-left corner), width, height
                        (time_boundary_position[0], time_boundary_position[1]),
                        time_boundary_width, time_boundary_height,
                        fill=False, color=time_boundary_color,
                        lw=time_boundary_line_thickness,
                        zorder=1000, transform=fig.transFigure,
                        figure=fig
                    )
                    fig.patches.extend([main_boundary, time_notation_boundary])
                else:
                    fig.patches.extend([main_boundary])
                os.chdir(output_dir)
                fig.savefig(output_image_name)
                plt.close()
            print(f"Simpler plot has been saved at:{display_output_dir}")
        else:
            print("There is only 1 logmar level in the given data.")
            print("Therefore, we cannot draw simpler graph. It needs at least 2 logmar level.")
    else:
        print("There is nothing to plot")


def raw_plot(input_csv_dir, plot_info, output_dir=None):
    x_data_column_name = plot_info["x_data_column_name"]
    y_data_column_name = plot_info["y_data_column_name"]
    graph_line_color = plot_info["graph_line_color"]
    graph_line_thickness = plot_info["graph_line_thickness"]
    mean_offset = plot_info["mean_offset"]

    if output_dir is None:
        csv_file_name = os.path.basename(input_csv_dir)
        plot_image_name = str(csv_file_name).replace(".csv", ".png")
        output_dir = str(input_csv_dir).replace(csv_file_name, plot_image_name)

    x_array = get_data_array(input_csv_dir, x_data_column_name)
    y_array = get_data_array(input_csv_dir, y_data_column_name)

    x_array_max = math.ceil(max(x_array))

    if x_array_max <= 100:
        x_fig_size = int(x_array_max * 2)
    else:
        x_fig_size = int(x_array_max * 0.8)

    figsize = (x_fig_size, 5)
    plt.figure(figsize=figsize)
    plt.margins(x=0.001)
    plt.xlabel(x_data_column_name)
    plt.ylabel(y_data_column_name)
    y_limit_mean = np.mean(y_array)
    y_lower_limit = y_limit_mean - mean_offset
    y_upper_limit = y_limit_mean + mean_offset
    plt.ylim(y_lower_limit, y_upper_limit)
    x_axis_array = np.arange(start=min(x_array), stop=max(x_array), step=1)
    plt.xticks(x_axis_array)
    plt.plot(x_array, y_array, color=graph_line_color, linewidth=graph_line_thickness)
    plt.savefig(output_dir)
    plt.close()

    return output_dir


def get_plot_info_for_simpler(data_dir, plot_info_input, referenced_csv_dir_input):
    x_label = plot_info_input["x_label"]
    y_label = plot_info_input["y_label"]
    x_data_column_name = plot_info_input["x_data_column_name"]
    y_data_column_name = plot_info_input["y_data_column_name"]
    x_axis_limit = plot_info_input["x_axis_limit"]
    y_axis_limit = plot_info_input["y_axis_limit"]
    mean_offset = plot_info_input["mean_offset"]
    axis_adjustment_types = plot_info_input["axis_adjustment_types"]
    axis_adjustment_type_number = plot_info_input["axis_adjustment_type_number"]
    # signal_csv_folder_name = plot_info_input["signal_csv_folder_name"]
    signal_csv_name = plot_info_input["signal_csv_name"]
    sp_column_name = plot_info_input["sp_column_name"]
    qp_column_name = plot_info_input["qp_column_name"]
    sp_line_color = plot_info_input["sp_line_color"]
    sp_line_thickness = plot_info_input["sp_line_thickness"]
    qp_line_color = plot_info_input["qp_line_color"]
    qp_line_thickness = plot_info_input["qp_line_thickness"]
    info_array = get_info_array_for_simpler_plot(referenced_csv_dir_input, "logMAR", "filename")
    # Get the folder away from info dictionary array in which index is 2
    folder_array = [info[2] for info in info_array]
    # print(folder_array)

    adjustment_type = axis_adjustment_types[str(axis_adjustment_type_number)]
    if adjustment_type == "mean_offset":
        plot_info_array = []
        x_adjust_limit, y_adjust_limit, ignore_folder_array = get_adjust_limit(data_dir, signal_csv_name,
                                                                               x_data_column_name, y_data_column_name,
                                                                               folder_array, x_axis_limit,
                                                                               y_axis_limit, mean_offset,
                                                                               axis_adjustment_types,
                                                                               axis_adjustment_type_number)
        adjust_limit_dict = {"x_adjust_limit": x_adjust_limit, "y_adjust_limit": y_adjust_limit}
        # If there is folder to be ignored, take out the info dictionary for that folder from info array
        if ignore_folder_array:
            info_array = [info for info in info_array if info[2] not in ignore_folder_array]
        for trial_id, logmar_level, folder_name in info_array:
            signal_csv_dir = os.path.join(data_dir, folder_name, signal_csv_name)
            x_array = get_data_array(signal_csv_dir, x_data_column_name)
            y_array = get_data_array(signal_csv_dir, y_data_column_name)
            y_mean = np.nanmean(y_array)
            y_array = [value - y_mean for value in y_array]
            sp_array, qp_array = get_sp_and_qp_array(signal_csv_dir, sp_column_name, qp_column_name,
                                                     y_array)
            plot_info = {"trial_id": trial_id, "disk_condition": str(logmar_level),
                         "x_label": x_label, "y_label": y_label,
                         "x_array": x_array, "y_array": y_array,
                         "sp_array": sp_array, "qp_array": qp_array,
                         "sp_line_color": sp_line_color, "sp_line_thickness": sp_line_thickness,
                         "qp_line_color": qp_line_color, "qp_line_thickness": qp_line_thickness,
                         "logmar": disk_to_logmar(logmar_level)}
            plot_info_array.append(plot_info)
    else:
        plot_info_array = []
        x_adjust_limit, y_adjust_limit, ignore_folder_array = get_adjust_limit(data_dir, signal_csv_name,
                                                                               x_data_column_name, y_data_column_name,
                                                                               folder_array, x_axis_limit,
                                                                               y_axis_limit, mean_offset,
                                                                               axis_adjustment_types,
                                                                               axis_adjustment_type_number)
        adjust_limit_dict = {"x_adjust_limit": x_adjust_limit, "y_adjust_limit": y_adjust_limit}
        # If there is folder to be ignored, take out the info dictionary for that folder from info array
        if ignore_folder_array:
            info_array = [info for info in info_array if info[2] not in ignore_folder_array]
        for trial_id, logmar_level, folder_name in info_array:
            signal_csv_dir = os.path.join(data_dir, folder_name, signal_csv_name)
            x_array = get_data_array(signal_csv_dir, x_data_column_name)
            y_array = get_data_array(signal_csv_dir, y_data_column_name)
            sp_array, qp_array = get_sp_and_qp_array(signal_csv_dir, sp_column_name, qp_column_name,
                                                     y_array)
            plot_info = {"trial_id": trial_id, "disk_condition": logmar_level,
                         "x_label": x_label, "y_label": y_label,
                         "x_array": x_array, "y_array": y_array,
                         "sp_array": sp_array, "qp_array": qp_array,
                         "sp_line_color": sp_line_color, "sp_line_thickness": sp_line_thickness,
                         "qp_line_color": qp_line_color, "qp_line_thickness": qp_line_thickness,
                         "logmar": disk_to_logmar(logmar_level)}
            plot_info_array.append(plot_info)

    return plot_info_array, adjust_limit_dict


def get_info_array_for_simpler_plot(referenced_csv_dir, logmar_header_input, file_name_header_input):
    file_to_open = open(referenced_csv_dir)
    csv_reader = csv.reader(file_to_open)
    header_array = []
    rows = []
    count_one = 0
    output_array = []

    for row in csv_reader:
        if count_one <= 0:
            header_array = row
            count_one += 1
        else:
            rows.append(row)

    file_name_header_position = get_index(file_name_header_input, header_array)
    logmar_header_position = get_index(logmar_header_input, header_array)

    for row in rows:
        raw_file_name = str(row[file_name_header_position])
        logmar_level = float(row[logmar_header_position])
        folder_name = raw_file_name[raw_file_name.find("./") + 2:raw_file_name.find(".mp4")]
        trial_id = folder_name[folder_name.find("trial-"):folder_name.find("-disks")]
        output_array.append([trial_id, logmar_level, folder_name])

    return output_array
