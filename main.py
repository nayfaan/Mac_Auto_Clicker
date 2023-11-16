import tkinter as tk
import keyboard
from pynput import mouse
from pynput import keyboard as kb

from AppKit import NSWorkspace
from os import system


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

    locate_btn = tk.Button(master=newCoordFrame, text="Locate")
    locate_btn.bind(
        "<Button-1>",
        lambda event: locate_btn_press(target_window, newCoordFrame),
    )
    locate_btn.grid(row=0, column=4)

    return newCoordFrame


def target_window_into_focus(target_window):
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


def locate_btn_press(target_window, CoordFrame):
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
#     # print(key)
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


def redraw_coordinates(coordinates):
    for widget in coordinates_list_frame.winfo_children():
        widget.pack_forget()
    for coordinate in coordinates:
        coordinate.pack()
    for widget in coordinates_list_frame.winfo_children():
        if not bool(widget.winfo_manager()):
            widget.destroy()


def redraw_add_minus_buttons(coordinates):
    add_coordinate.configure(state="active")
    del_coordinate.configure(state="active")
    if len(coordinates) >= max_coordinates:
        add_coordinate.configure(state="disabled")
    if len(coordinates) <= 1:
        del_coordinate.configure(state="disabled")


def redraw_mode(coordinates):
    if len(coordinates) == 1:
        click_mode.configure(text="Mode: single point")
    elif len(coordinates) == 2:
        click_mode.configure(text="Mode: corner")
    elif len(coordinates) > 2:
        click_mode.configure(text="Mode: polygon")
    else:
        click_mode.configure(text="Mode: ERROR")


def plus_btn_press(coordinates):
    if len(coordinates) < max_coordinates:
        coordinates.append(newCoordinate(coordinates_list_frame))

        redraw_coordinates(coordinates)
        redraw_mode(coordinates)
        redraw_add_minus_buttons(coordinates)


def minus_btn_press(coordinates):
    if len(coordinates) > 1:
        coordinates.pop()

        redraw_coordinates(coordinates)
        redraw_mode(coordinates)
        redraw_add_minus_buttons(coordinates)


def start_btn_press():
    pass

def stop_btn_press():
    pass

def init():
    global frame_l
    global frame_r
    frame_l = tk.Frame(master=root)
    frame_r = tk.Frame(master=root)
    frame_l.pack(fill=tk.Y, side=tk.LEFT)
    frame_r.pack(fill=tk.Y, side=tk.LEFT)

    window_select_frame = tk.Frame(master=frame_l, borderwidth=10)

    tk.Label(
        master=window_select_frame,
        text="Target Window: ",
    ).grid(row=0, column=0)

    open_windows = [
        apps["NSApplicationName"]
        for apps in NSWorkspace.sharedWorkspace().launchedApplications()
    ]
    global target_window
    target_window = tk.StringVar(value="(None)")
    window_list = tk.OptionMenu(
        window_select_frame, target_window, *["(None)"] + open_windows
    )
    window_list.grid(row=0, column=1)

    window_select_frame.pack()

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

    coordinates = []
    coordinates.append(newCoordinate(coordinates_list_frame))

    redraw_coordinates(coordinates)

    coordinates_list_frame.grid(row=2, column=0, columnspan=2)

    global del_coordinate
    del_coordinate = tk.Button(master=area_select_frame, text="–", state="disabled")
    del_coordinate.bind(
        "<Button-1>",
        lambda event, coordinates=coordinates: minus_btn_press(coordinates),
    )
    del_coordinate.grid(row=3, column=0, sticky="E")

    global add_coordinate
    add_coordinate = tk.Button(master=area_select_frame, text="+")
    add_coordinate.bind(
        "<Button-1>",
        lambda event, coordinates=coordinates: plus_btn_press(coordinates),
    )
    add_coordinate.grid(row=3, column=1, sticky="W")

    area_select_frame.pack()

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

    # hotkey_select_btn = tk.Button(master=hotkey_select_frame, text="Select")
    # hotkey_select_btn.bind(
    #     "<Button-1>",
    #     lambda event: hotkey_select_btn_press(),
    # )
    # hotkey_select_btn.grid(row=0, column=2)

    # hotkey_select_frame.pack()

    control_frame = tk.Frame(master=frame_l, borderwidth=10)

    start_button = tk.Button(master=control_frame, text="START")
    start_button.bind(
        "<Button-1>",
        lambda event: start_btn_press(),
    )
    start_button.grid(row=0, column=0)
    stop_button = tk.Button(master=control_frame, text="STOP", state="disabled")
    stop_button.bind(
        "<Button-1>",
        lambda event: stop_btn_press(),
    )
    stop_button.grid(row=0, column=1)

    control_frame.pack()


def run():
    global root
    root = tk.Tk()

    global max_coordinates
    max_coordinates = 2

    init()

    # global listener
    # listener = kb.Listener(on_press=press_listener)
    # listener.start()

    tk.mainloop()


if __name__ == "__main__":
    run()
