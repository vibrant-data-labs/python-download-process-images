import os
import sys


def get_user_input():
    process = {
        'is_resize': False,
        'width': 0,
        'height': 0,
        'is_padding': False,
        'f_width': 0,
        'f_height': 0,
        'pad_color': None,
        'is_greyscale': False,
    }

    def get_size(question):
        reply = input(question).strip()
        if not reply == "1":
            return None

        if reply == "1":
            width = input("Width: ")
            height = input("Height: ")

        if reply== "1" and question.startswith("Pad"):
            is_dom = input("Padding based on dominant color? (1: Yes 0: No): ")
            if is_dom.strip() == "1":
                process['is_padding'] = True
                process['f_width'] = width
                process['f_height'] = height

                return None
            else:
                return f"{width} {height}"

        process['is_resize'] = True
        process['width'] = width
        process['height'] = height

    get_size("Do we need to resize? (Press (1: Yes 0: No): ")
    pd = get_size("Padding? (1: Yes 0: No): ")
    if pd:
        width, height = pd.split(" ")
        color_value = input("    >> Ok. Then what color? (ex. '#ffffff' or white): ")
        if color_value:
            process['pad_color'] = color_value.lower()
        else:
            process['pad_color'] = 'white'

        process['is_padding'] = True
        process['f_width'] = width
        process['f_height'] = height

    is_black_white = input("Black and White? (1: Yes 0: No) : ")
    if is_black_white.strip() == "1":
        process['is_greyscale'] = True

    return process

if __name__ == '__main__':
    filename = sys.argv[1]
    i = get_user_input()

    cmd = [f'python3 image_processor.py {filename} ']

    if i['is_resize']:
        cmd.append(f'--resize --height {i["height"]} --width {i["width"]} ')

    if i['is_padding']:
        cmd.append(f'--padding --f_height {i["f_height"]} --f_width {i["f_width"]} ')

    if i['pad_color']:
        cmd.append(f'--pad_color {i["pad_color"]} ')

    if i['is_greyscale']:
        cmd.append(f'--greyscale ')
    
    os.system("".join(cmd))
