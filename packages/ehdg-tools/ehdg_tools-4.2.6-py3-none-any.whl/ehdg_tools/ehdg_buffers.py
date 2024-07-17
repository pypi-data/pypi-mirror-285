import collections
import numpy as np


def get_attribute_array_from_dict(dict_input):
    output_array = []
    for key in dict_input:
        output_array.append(str(key))
    return output_array


def is_nan_or_zero(number_input):
    try:
        temp_number = float(number_input)
    except ValueError:
        print(f"could not convert string to float: '{number_input}'")
        return True
    except TypeError:
        return True
    if temp_number == 0.0 or str(temp_number).lower() == "nan" or temp_number is np.nan:
        return True
    else:
        return False


def fill_data(array_input):
    if type(array_input) is not list:
        raise ValueError("Input must be array/list.")
    start_index = False
    gap_found = False
    end_index = False
    for index, num in enumerate(array_input):
        if is_nan_or_zero(num):
            gap_found = True
            if index > 0:
                start_index = index - 1
                temp_end_index = index + 1
                while True:
                    try:
                        next_data = array_input[temp_end_index]
                    except IndexError:
                        break
                    if is_nan_or_zero(next_data):
                        temp_end_index += 1
                    else:
                        end_index = temp_end_index
                        break
                break
            else:
                break
    if gap_found:
        if start_index is not False and end_index is not False:
            start_value = float(array_input[start_index])
            end_value = float(array_input[end_index])
            fill_length = end_index - start_index + 1
            fill_array = list(np.linspace(start_value, end_value, fill_length))
            temp_array = array_input.copy()
            temp_array[start_index:end_index + 1] = fill_array
            return temp_array
        else:
            return array_input
    else:
        return array_input


class TinyFillBuffer:
    def __init__(self, buffer_length=7):

        if type(buffer_length) is not int:
            raise ValueError("Buffer length must be integer.")
        else:
            self.buffer_length = buffer_length

        self.buffer = collections.deque(maxlen=buffer_length)
        self.buffer_max_length = buffer_length
        self.previous_data = None
        self.data_attribute_array = []

    def add(self, data_input):
        if type(data_input) is not dict:
            raise ValueError("Data input must be dictionary type.")
        else:
            if not self.data_attribute_array:
                self.data_attribute_array = get_attribute_array_from_dict(data_input)
                if not self.data_attribute_array:
                    raise ValueError("Could not retrieve header array from data input.")
            if len(self.buffer) >= 1:
                self.previous_data = self.buffer[0]
            self.buffer.append(data_input)
            if len(self.buffer) >= 3:
                buffer_data_dict = {}
                for attribute in self.data_attribute_array:
                    buffer_data_dict[attribute] = []
                for data in self.buffer:
                    for attribute in self.data_attribute_array:
                        try:
                            temp_data = data[attribute]
                            buffer_data_dict[attribute].append(temp_data)
                        except IndexError:
                            print(f"Data attribute {attribute} could not find in the data:{data}")
                for attribute in self.data_attribute_array:
                    temp_array = buffer_data_dict[attribute]
                    buffer_data_dict[attribute] = fill_data(temp_array)

                temp_buffer = collections.deque(maxlen=self.buffer_max_length)
                for i in range(len(self.buffer)):
                    temp_dict = {}
                    for attribute in self.data_attribute_array:
                        temp_dict[attribute] = buffer_data_dict[attribute][i]
                    temp_buffer.append(temp_dict)
                self.buffer = temp_buffer
            if len(self.buffer) >= self.buffer_max_length:
                return self.buffer[0]
            else:
                return None

    def set_buffer_length(self, new_buffer_length):
        if type(new_buffer_length) is not int:
            raise ValueError("The new buffer length input must be integer type.")
        else:
            self.buffer = collections.deque(maxlen=new_buffer_length)
            self.buffer_max_length = new_buffer_length
