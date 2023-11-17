import tkinter as tk
from numpy.random import normal as npRand

# import keyboard
from pynput import mouse
from pynput import keyboard as kb

import multiprocessing

from AppKit import NSWorkspace
from os import system
from time import sleep


def validateInt(inStr, acttyp):
    if acttyp == "1":
        if not inStr.isdigit():
            return False
    return True


def newCoordinate(coordinates_list_frame):
    newCoordFrame = tk.Frame(master=coordinates_list_frame)

    tk.Label(
        master=newCoordFrame,
        text="X: ",
    ).grid(row=0, column=0)

    XCoord = tk.Entry(master=newCoordFrame, validate="key", width=7)
    XCoord["validatecommand"] = (XCoord.register(validateInt), "%P", "%d")
    XCoord.grid(row=0, column=1)

    tk.Label(
        master=newCoordFrame,
        text="Y: ",
    ).grid(row=0, column=2)

    YCoord = tk.Entry(master=newCoordFrame, validate="key", width=7)
    YCoord["validatecommand"] = (YCoord.register(validateInt), "%P", "%d")
    YCoord.grid(row=0, column=3)

    tk.Button(
        master=newCoordFrame,
        text="Locate",
        command=lambda: locate_btn_press(newCoordFrame),
    ).grid(row=0, column=4)

    return newCoordFrame


def recheck_target_window():
    target_window_name = target_window.get()
    opened_windows = ["(None)"] + [
        apps["NSApplicationName"]
        for apps in NSWorkspace.sharedWorkspace().launchedApplications()
    ]
    if not target_window_name in opened_windows:
        target_window.set("(None)")

    window_list["menu"].delete(0, "end")
    for window in opened_windows:
        window_list["menu"].add_command(
            label=window, command=tk._setit(target_window, window)
        )


def target_window_into_focus(target_window):
    if not target_window == "(None)":
        try:
            recheck_target_window()
        except:
            pass
    if not target_window == "(None)":
        system(
            '/usr/bin/osascript -e \'tell app "Finder" to set frontmost of process "'
            + target_window
            + "\" to true'"
        )


def click_listener(x, y, button, pressed, CoordFrameList):
    if button == mouse.Button.left and pressed:
        CoordFrameList[1].configure(
            highlightbackground="systemWindowBackgroundColor",
            highlightcolor="systemTextColor",
        )
        CoordFrameList[3].configure(
            highlightbackground="systemWindowBackgroundColor",
            highlightcolor="systemTextColor",
        )
        target_window_into_focus("Python")
        return False


def tk_set_text(e, text):
    e.delete(0, tk.END)
    e.insert(0, text)


def move_listener(x, y, x_entry, y_entry):
    tk_set_text(x_entry, round(x))
    tk_set_text(y_entry, round(y))


def locate_btn_press(CoordFrame):
    CoordFrameList = CoordFrame.winfo_children()

    CoordFrameList[1].configure(highlightbackground="red", highlightcolor="red")
    CoordFrameList[3].configure(highlightbackground="red", highlightcolor="red")

    target_window_into_focus(target_window.get())
    listener = mouse.Listener(
        on_click=lambda x, y, button, pressed: click_listener(
            x, y, button, pressed, CoordFrameList
        ),
        on_move=lambda x, y: move_listener(x, y, CoordFrameList[1], CoordFrameList[3]),
    )
    listener.start()


# def hotkey_press_listener(key):
#     try:
#         print("alphanumeric key {0} pressed".format(key.char))
#     except AttributeError:
#         print("special key {0} pressed".format(key))


# def hotkey_select_btn_press():
#     orig_color = hotkey.cget("background")
#     hotkey.configure(background="red")

#     with kb.Listener(on_press=hotkey_press_listener) as hotkey_listener:
#         hotkey_listener.join()

#     # new_hotkey = keyboard.read_key()
#     # if new_hotkey == "ƒ":
#     #     new_hotkey = keyboard.read_key()

#     hotkey.configure(background=orig_color)


def redraw_coordinates():
    for widget in coordinates_list_frame.winfo_children():
        widget.pack_forget()
    for coordinate in coordinates_list:
        coordinate.pack()
    for widget in coordinates_list_frame.winfo_children():
        if not bool(widget.winfo_manager()):
            widget.destroy()


def redraw_add_minus_buttons():
    add_coordinate.configure(state="active")
    del_coordinate.configure(state="active")
    if len(coordinates_list) >= max_coordinates:
        add_coordinate.configure(state="disabled")
    if len(coordinates_list) <= 1:
        del_coordinate.configure(state="disabled")


def redraw_mode():
    if len(coordinates_list) == 1:
        click_mode.configure(text="Mode: single point")
    elif len(coordinates_list) == 2:
        click_mode.configure(text="Mode: corner")
    elif len(coordinates_list) > 2:
        click_mode.configure(text="Mode: polygon")
    else:
        click_mode.configure(text="Mode: ERROR")


def plus_btn_press():
    if len(coordinates_list) < max_coordinates:
        coordinates_list.append(newCoordinate(coordinates_list_frame))

        redraw_coordinates()
        redraw_mode()
        redraw_add_minus_buttons()


def minus_btn_press():
    if len(coordinates_list) > 1:
        coordinates_list.pop()

        redraw_coordinates()
        redraw_mode()
        redraw_add_minus_buttons()


def random(bound, mean=None, sd=None, toInt=True):
    if len(bound) == 1:
        return bound[0]
    elif len(bound) == 2:
        if bound[0] == bound[1]:
            return bound[0]

        if not mean:
            mean = (bound[0] + bound[1]) / 2
        if not sd:
            sd = (bound[1] - bound[0]) / 6

        result = npRand(loc=mean, scale=sd, size=1)[0]
        if toInt:
            result = round(result)
        result = max(min(result, bound[1]), bound[0])

        return result
    else:
        raise IndexError("Random range size larger than 2")


def pyn_click(pos):
    while not mouse_control.position == (pos[0], pos[1]):
        mouse_control.position = (pos[0], pos[1])
    mouse_control.press(mouse.Button.left)
    sleep(min(max(npRand(loc=0.09, scale=0.013, size=1)[0], 0), 0.15))
    mouse_control.release(mouse.Button.left)


def click(coordinates_numbers, mean=[None, None], sd=[None, None]):
    target_window_into_focus(target_window_name)

    pos1 = coordinates_numbers[0]
    try:
        pos2 = coordinates_numbers[1]
    except:
        pos2 = None

    if not pos2:
        pyn_click(pos1)
    else:
        pyn_click(
            (
                random([pos1[0], pos2[0]], mean=mean[0], sd=sd[0]),
                random([pos1[1], pos2[1]], mean=mean[1], sd=sd[1]),
            )
        )


def disable_all_inputs():
    start_button.configure(state="disabled")
    stop_button.configure(state="active")
    add_coordinate.configure(state="disabled")
    del_coordinate.configure(state="disabled")

    for coordinate_frame in coordinates_list_frame.winfo_children():
        coordinate_list = coordinate_frame.winfo_children()
        coordinate_list[1].configure(state="readonly")
        coordinate_list[3].configure(state="readonly")
        coordinate_list[4].configure(state="disabled")

    time_min.configure(state="readonly")
    time_max.configure(state="readonly")

    window_list.configure(state="disabled")


def reenable_all_inputs():
    stop_button.configure(state="disabled")
    start_button.configure(state="active")
    redraw_add_minus_buttons()

    for coordinate_frame in coordinates_list_frame.winfo_children():
        coordinate_list = coordinate_frame.winfo_children()
        coordinate_list[1].configure(state="normal")
        coordinate_list[3].configure(state="normal")
        coordinate_list[4].configure(state="active")

    time_min.configure(state="normal")
    time_max.configure(state="normal")

    window_list.configure(state="normal")


def start_btn_press():
    disable_all_inputs()

    coordinates_numbers = []
    for coordinate_frame in coordinates_list_frame.winfo_children():
        coordinate_list = coordinate_frame.winfo_children()
        coordinates_numbers.append([coordinate_list[1].get(), coordinate_list[3].get()])

    for ix, _ in enumerate(coordinates_numbers):
        for iy, __ in enumerate(coordinates_numbers[ix]):
            if not coordinates_numbers[ix][iy]:
                stop_btn_press()
                return None
            coordinates_numbers[ix][iy] = int(coordinates_numbers[ix][iy])
        coordinates_numbers[ix] = tuple(coordinates_numbers[ix])

    if len(coordinates_numbers) == 2:
        coord_mean = [
            (coordinates_numbers[0][0] + coordinates_numbers[1][0]) / 2,
            (coordinates_numbers[0][1] + coordinates_numbers[1][1]) / 2,
        ]
        coord_sd = [
            (coordinates_numbers[1][0] - coordinates_numbers[0][0]) / 6,
            (coordinates_numbers[1][1] - coordinates_numbers[0][1]) / 6,
        ]
    else:
        coord_mean = None
        coord_sd = None

    time_numbers = [time_min.get(), time_max.get()]
    if not time_numbers[0] and not time_numbers[1]:
        stop_btn_press()
        return None
    if not time_numbers[0]:
        time_numbers[0] = time_numbers[1]
    if not time_numbers[1]:
        time_numbers[1] = time_numbers[0]
    time_numbers = [float(time_numbers[0]) / 1000, float(time_numbers[1]) / 1000]
    time_numbers = tuple(time_numbers)

    if not time_numbers[0] == time_numbers[1]:
        time_mean = (time_numbers[0] + time_numbers[1]) / 2
        time_sd = (time_numbers[1] - time_numbers[0]) / 6
    else:
        time_mean = None
        time_sd = None

    manager = multiprocessing.Manager()
    target_manager_value = manager.Value(str, target_window.get())
    p1 = multiprocessing.Process(
        target=click_loop,
        args=(
            coordinates_numbers,
            coord_mean,
            coord_sd,
            time_numbers,
            time_mean,
            time_sd,
        ),
        kwargs={
            "target_window": target_manager_value,
        },
    )
    p1.start()
    p1.join()
    stop_btn_press()


def click_loop(
    coordinates_numbers,
    coord_mean,
    coord_sd,
    time_numbers,
    time_mean,
    time_sd,
    **kwargs
):
    global mouse_control
    mouse_control = mouse.Controller()

    global stop
    stop = False
    global listener
    listener = kb.Listener(on_press=press_listener)
    listener.start()

    global target_window_name
    target_window_name = kwargs.get("target_window").value

    mouse_control.position = (coordinates_numbers[0][0], coordinates_numbers[0][1])

    while not stop:
        print(stop)
        click(coordinates_numbers, coord_mean, coord_sd)
        if time_numbers[0] == time_numbers[1]:
            sleep(time_numbers[0])
        else:
            s = random(time_numbers, mean=time_mean, sd=time_sd, toInt=False)
            sleep(s)


def stop_btn_press():
    reenable_all_inputs()


def init():
    # Main frames
    global frame_l
    global frame_r
    frame_l = tk.Frame(master=root)
    frame_r = tk.Frame(master=root)
    frame_l.pack(fill=tk.Y, side=tk.LEFT)
    frame_r.pack(fill=tk.Y, side=tk.LEFT)

    # Windows select frame
    window_select_frame = tk.Frame(master=frame_l, borderwidth=10)

    tk.Label(
        master=window_select_frame,
        text="Target Window: ",
    ).grid(row=0, column=0)

    opened_windows = [
        apps["NSApplicationName"]
        for apps in NSWorkspace.sharedWorkspace().launchedApplications()
    ]
    global target_window
    target_window = tk.StringVar(value="(None)")
    global window_list
    window_list = tk.OptionMenu(
        window_select_frame, target_window, *["(None)"] + opened_windows
    )
    window_list.bind("<Button-1>", lambda event: recheck_target_window())
    window_list.grid(row=0, column=1)

    window_select_frame.pack()

    # Timer frame
    timer_frame = tk.Frame(master=frame_l, borderwidth=10)

    tk.Label(
        master=timer_frame,
        text="Timer (in milliseconds)",
    ).grid(row=0, column=0, columnspan=4)

    tk.Label(
        master=timer_frame,
        text="Min: ",
    ).grid(row=1, column=0)

    global time_min
    time_min = tk.Entry(master=timer_frame, validate="key", width=7)
    time_min["validatecommand"] = (time_min.register(validateInt), "%P", "%d")
    time_min.grid(row=1, column=1)

    tk.Label(
        master=timer_frame,
        text="Max: ",
    ).grid(row=1, column=2)

    global time_max
    time_max = tk.Entry(master=timer_frame, validate="key", width=7)
    time_max["validatecommand"] = (time_max.register(validateInt), "%P", "%d")
    time_max.grid(row=1, column=3)

    timer_frame.pack()

    # Area select frame
    area_select_frame = tk.Frame(master=frame_l, borderwidth=10)

    tk.Label(
        master=area_select_frame,
        text="Click Position",
    ).grid(row=0, column=0, columnspan=2)

    global click_mode
    click_mode = tk.Label(
        master=area_select_frame,
        text="Mode: single point",
    )
    click_mode.grid(row=1, column=0, columnspan=2)

    global coordinates_list_frame
    coordinates_list_frame = tk.Frame(master=area_select_frame)

    global coordinates_list
    coordinates_list = []
    coordinates_list.append(newCoordinate(coordinates_list_frame))

    redraw_coordinates()

    coordinates_list_frame.grid(row=2, column=0, columnspan=2)

    global del_coordinate
    del_coordinate = tk.Button(
        master=area_select_frame, text="–", state="disabled", command=minus_btn_press
    )
    del_coordinate.grid(row=3, column=0, sticky="E")

    global add_coordinate
    add_coordinate = tk.Button(
        master=area_select_frame, text="+", command=plus_btn_press
    )
    add_coordinate.grid(row=3, column=1, sticky="W")

    area_select_frame.pack()

    # # Hotkey select frame
    # hotkey_select_frame = tk.Frame(master=frame_l, borderwidth=10)

    # tk.Label(master=hotkey_select_frame, text="Hotkey: ").grid(row=0, column=0)

    # global hotkey
    # hotkey = tk.Label(
    #     master=hotkey_select_frame,
    #     text="Key.f1",
    #     borderwidth=2,
    #     relief="solid",
    #     padx=7,
    #     pady=3,
    # )
    # hotkey.grid(row=0, column=1)

    # hotkey_select_btn = tk.Button(master=hotkey_select_frame, text="Select", command=hotkey_select_btn_press)
    # hotkey_select_btn.grid(row=0, column=2)

    # hotkey_select_frame.pack()

    # Control frame
    control_frame = tk.Frame(master=frame_l, borderwidth=10)

    global start_button
    start_button = tk.Button(
        master=control_frame, text="START", command=start_btn_press
    )
    start_button.grid(row=0, column=0)

    global stop_button
    stop_button = tk.Button(
        master=control_frame, text="STOP", state="disabled", command=stop_btn_press
    )
    stop_button.grid(row=0, column=1)

    control_frame.pack()


def press_listener(key):
    if key == kb.Key.esc:
        stop = True
        return False


def run():
    global root
    root = tk.Tk()
    root.title("Mac Auto Clicker")

    global mouse_control
    mouse_control = mouse.Controller()

    global max_coordinates
    max_coordinates = 2

    init()

    tk.mainloop()


if __name__ == "__main__":
    run()
