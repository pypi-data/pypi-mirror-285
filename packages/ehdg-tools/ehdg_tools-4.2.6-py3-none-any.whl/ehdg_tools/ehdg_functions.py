import subprocess

color_dictionary = {
    'olive': (128, 128, 0),
    'crimson': (220, 20, 60),
    'mauve': (203, 78, 97),
    'indigo': (75, 0, 130),
    'snow': (255, 250, 250),
    'ghost white': (248, 248, 255),
    'white smoke': (245, 245, 245),
    'gainsboro': (220, 220, 220),
    'floral white': (255, 250, 240),
    'old lace': (253, 245, 230),
    'linen': (250, 240, 230),
    'antique white': (250, 235, 215),
    'papaya whip': (255, 239, 213),
    'blanched almond': (255, 235, 205),
    'bisque': (255, 228, 196),
    'peach puff': (255, 218, 185),
    'peachpuff': (255, 218, 185),
    'navajo white': (255, 222, 173),
    'moccasin': (255, 228, 181),
    'cornsilk': (255, 248, 220),
    'ivory': (255, 255, 240),
    'lemon chiffon': (255, 250, 205),
    'seashell': (255, 245, 238),
    'honeydew': (240, 255, 240),
    'mint cream': (245, 255, 250),
    'azure': (240, 255, 255),
    'alice blue': (240, 248, 255),
    'lavender': (230, 230, 250),
    'lavender blush': (255, 240, 245),
    'misty rose': (255, 228, 225),
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'dark slate grey': (47, 79, 79),
    'dim grey': (105, 105, 105),
    'slate grey': (112, 128, 144),
    'light slate grey': (119, 136, 153),
    'grey': (190, 190, 190),
    'light grey': (211, 211, 211),
    'midnight blue': (25, 25, 112),
    'navy': (0, 0, 128),
    'navy blue': (0, 0, 128),
    'cornflower blue': (100, 149, 237),
    'dark slate blue': (72, 61, 139),
    'slate blue': (106, 90, 205),
    'medium slate blue': (123, 104, 238),
    'light slate blue': (132, 112, 255),
    'medium blue': (0, 0, 205),
    'royal blue': (65, 105, 225),
    'blue': (0, 0, 255),
    'dodger blue': (30, 144, 255),
    'deep sky blue': (0, 191, 255),
    'sky blue': (135, 206, 235),
    'light sky blue': (135, 206, 250),
    'steel blue': (70, 130, 180),
    'light steel blue': (176, 196, 222),
    'light blue': (173, 216, 230),
    'powder blue': (176, 224, 230),
    'pale turquoise': (175, 238, 238),
    'dark turquoise': (0, 206, 209),
    'medium turquoise': (72, 209, 204),
    'turquoise': (64, 224, 208),
    'cyan': (0, 255, 255),
    'light cyan': (224, 255, 255),
    'cadet blue': (95, 158, 160),
    'medium aquamarine': (102, 205, 170),
    'aquamarine': (127, 255, 212),
    'dark green': (0, 100, 0),
    'dark olive green': (85, 107, 47),
    'dark sea green': (143, 188, 143),
    'sea green': (46, 139, 87),
    'medium sea green': (60, 179, 113),
    'light sea green': (32, 178, 170),
    'pale green': (152, 251, 152),
    'spring green': (0, 255, 127),
    'lawn green': (124, 252, 0),
    'green': (0, 255, 0),
    'chartreuse': (127, 255, 0),
    'medium spring green': (0, 250, 154),
    'green yellow': (173, 255, 47),
    'lime green': (50, 205, 50),
    'yellow green': (154, 205, 50),
    'forest green': (34, 139, 34),
    'olive drab': (107, 142, 35),
    'dark khaki': (189, 183, 107),
    'khaki': (240, 230, 140),
    'pale goldenrod': (238, 232, 170),
    'light goldenrod yellow': (250, 250, 210),
    'light yellow': (255, 255, 224),
    'yellow': (255, 255, 0),
    'gold': (255, 215, 0),
    'light goldenrod': (238, 221, 130),
    'goldenrod': (218, 165, 32),
    'dark goldenrod': (184, 134, 11),
    'rosy brown': (188, 143, 143),
    'indian red': (205, 92, 92),
    'saddle brown': (139, 69, 19),
    'sienna': (160, 82, 45),
    'peru': (205, 133, 63),
    'burlywood': (222, 184, 135),
    'beige': (245, 245, 220),
    'wheat': (245, 222, 179),
    'sandy brown': (244, 164, 96),
    'tan': (210, 180, 140),
    'chocolate': (210, 105, 30),
    'fire brick': (178, 34, 34),
    'brown': (165, 42, 42),
    'dark salmon': (233, 150, 122),
    'salmon': (250, 128, 114),
    'light salmon': (255, 160, 122),
    'orange': (255, 165, 0),
    'dark orange': (255, 140, 0),
    'coral': (255, 127, 80),
    'light coral': (240, 128, 128),
    'tomato': (255, 99, 71),
    'orange red': (255, 69, 0),
    'red': (255, 0, 0),
    'hot pink': (255, 105, 180),
    'deep pink': (255, 20, 147),
    'pink': (255, 192, 203),
    'light pink': (255, 182, 193),
    'pale violet red': (219, 112, 147),
    'maroon': (176, 48, 96),
    'medium violet red': (199, 21, 133),
    'violet red': (208, 32, 144),
    'magenta': (255, 0, 255),
    'violet': (238, 130, 238),
    'plum': (221, 160, 221),
    'orchid': (218, 112, 214),
    'medium orchid': (186, 85, 211),
    'dark orchid': (153, 50, 204),
    'dark violet': (148, 0, 211),
    'blue violet': (138, 43, 226),
    'purple': (160, 32, 240),
    'medium purple': (147, 112, 219),
    'thistle': (216, 191, 216),
    'dark grey': (169, 169, 169),
    'dark blue': (0, 0, 139),
    'dark cyan': (0, 139, 139),
    'dark magenta': (139, 0, 139),
    'dark red': (139, 0, 0),
    'light green': (144, 238, 144),
}


# check whether there is input commandline program or not
def check_commandline_program(program_name):
    check_cmd = f"{program_name} --version"
    try:
        check_output = subprocess.check_output(check_cmd, shell=True)
        check_output = check_output.decode('utf-8')
        print(check_output)
        is_there_program = True
        print(f"{program_name} is found.")
    except Exception as error:
        print(error)
        is_there_program = False
    return is_there_program


# This function is to change color string to color bgr tuple value
def string_to_bgr_tuple(input_string):
    input_string = str(input_string).lower()
    try:
        rgb_tuple = color_dictionary[input_string]
        red_index = rgb_tuple[0]
        green_index = rgb_tuple[1]
        blue_index = rgb_tuple[2]
        return blue_index, green_index, red_index
    except IndexError:
        print(f"Input string {input_string} is not a valid color string input.")
        print("It can be red, green, blue, black, white or magenta.")
        print("It also can be hex color code.")
        raise ValueError(f"Input string {input_string} is not a valid color string input.")


# This function is to change hex color string to color bgr tuple value
def hex_string_to_bgr_tuple(input_string):
    input_string = str(input_string).lower()
    if "#" in input_string:
        value = input_string.lstrip('#')
        lv = len(value)
        if lv == 6:
            try:
                tem_arr = tuple(int(value[xx:xx + lv // 3], 16) for xx in range(0, lv, lv // 3))
                return tem_arr[::-1]
            except ValueError as e:
                print(e)
                raise
        else:
            print(f"The length of input hex string must be 6 character. But it is {lv}.")
            raise ValueError(f"Input string {input_string} is not a valid hex string.")
    else:
        raise ValueError(f"Input string {input_string} must contain #.")


# This function is to translate disk condition string to logmar value
def convert_disk_to_logmar(disk_string_input):
    disk_logmar_equivalent = {"disk-condition-1-1": 1.0, "disk-condition-1-2": 1.0, "disk-condition-2-1": 0.9,
                              "disk-condition-2-2": 0.9, "disk-condition-3-1": 0.8, "disk-condition-3-2": 0.8,
                              "disk-condition-4-1": 0.7, "disk-condition-4-2": 0.7, "disk-condition-5-1": 0.6,
                              "disk-condition-5-2": 0.6, "disk-condition-6-1": 0.5, "disk-condition-6-2": 0.5,
                              "disk-condition-7-1": 0.4, "disk-condition-7-2": 0.4, "disk-condition-8-1": 0.3,
                              "disk-condition-8-2": 0.3, "disk-condition-9-1": 0.2, "disk-condition-9-2": 0.2,
                              "disk-condition-10-1": 0.1, "disk-condition-10-2": 0.1, "disk-condition-11-1": 0.0,
                              "disk-condition-11-2": 0.0, "disk-condition-12-1": -0.1, "disk-condition-12-2": -0.1,
                              "disk-condition-13-1": -0.2, "disk-condition-13-2": -0.2}

    try:
        out_string = disk_logmar_equivalent[disk_string_input]
        convertable = True
    except KeyError:
        out_string = disk_string_input
        convertable = False

    return convertable, out_string

