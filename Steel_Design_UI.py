import tkinter as tk
from tkinter import ttk

import numpy as np
import pandas as pd

# Importing the backend
from Updated_Steel_Design import UB, UDL, PointLoad, Analyze

# Data dictionary
list_of_udl = []
list_of_pl = []

win = tk.Tk()  # Creating a window
win.title('Stability of Steel Structures')

win.resizable(True, True)  # making the win non-resizable
win.geometry("200x200")  # setting the geometry or size of the window
win.state("zoomed")  # making it a fullscreen

win.configure(bg="violet")

main_frame = tk.Frame(win)
main_frame.pack(fill="both", expand=1)

def FrameWidth(event):
    canvas_width = event.width
    my_canvas.itemconfig(canvas_frame, width=canvas_width)

def OnFrameConfigure(event):
    my_canvas.configure(scrollregion=my_canvas.bbox("all"))

# Create a Canvas
my_canvas = tk.Canvas(main_frame, bg="cyan")
my_canvas.pack(side="left", fill="both", expand=1)

# Add a Scrollbar To the Canvas
my_scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=my_canvas.yview)
my_scrollbar.pack(side="right", fill="y")

# Configure the Canvas
my_canvas.configure(yscrollcommand=my_scrollbar.set)

my_canvas.bind('<Configure>', FrameWidth)
# Create Another Frame INSIDE the Canvas
second_frame = tk.Frame(my_canvas, bg="cyan")
second_frame.pack(fill="both", expand=1)

second_frame.bind("<Configure>", OnFrameConfigure)
# Add that new frame to a Window In the Canvas
canvas_frame = my_canvas.create_window((0, 0), window=second_frame, anchor="nw" )

# Create another frame for the radiobutton
third_frame = tk.Frame(second_frame)
third_frame.grid(row=1, column=0, columnspan=2)

# Create a Label Frame for the loadings(UDL)
UDL_frame = ttk.LabelFrame(second_frame, text="UDL (in kN/m)")
UDL_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ns")

PL_frame = ttk.LabelFrame(second_frame, text="PointLoad (in kN) and its distance from left support\nEg:\nPointLoad = 20 (in kN)\nDistance From the left = 3 (in metres)")
PL_frame.grid(row=3, column=0, padx=5, pady=5, sticky="w")

# Store the variables
beam_var = tk.StringVar()
length_var = tk.StringVar()
Py_var = tk.StringVar()
E_var = tk.StringVar()
dead_var = tk.StringVar()
live_var = tk.StringVar()
P_LL_var = tk.StringVar()
P_DL_var = tk.StringVar()
a_ll_var = tk.StringVar()
a_dl_var = tk.StringVar()

# Creating a Frame for length, Py, and E
Frame_1 = ttk.LabelFrame(second_frame)
Frame_1.grid(row = 0, column=0, sticky="w", padx=5, pady=5)

length_label = ttk.Label(Frame_1, text="Length of beam(in m): ", font=("Corbel", 12))
length_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

Py_label = ttk.Label(Frame_1, text=f"Py(in N/mm\N{SUPERSCRIPT TWO}): ", font=("Corbel", 12))
Py_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)

E_label = ttk.Label(Frame_1, text="Young's Modulus E (in kN/mm\N{SUPERSCRIPT TWO})", font=("Corbel", 12))
E_label.grid(row=2, column=0, sticky="w", padx=5, pady=5)

dead_label = tk.Label(UDL_frame, text="Dead load", font=("Corbel", 12))
dead_label.grid(row=0, column=0, sticky="w", padx=5, pady=5)

live_label = tk.Label(UDL_frame, text="Live load", font=("Corbel", 12))
live_label.grid(row=1, column=0, sticky="w", padx=5, pady=5)

dead_pl_label = tk.Label(PL_frame, text="Dead load :", font=("Corbel", 12))
dead_pl_label.grid(row=0, column=0, sticky="w", padx=2, pady=2)

live_pl_label = tk.Label(PL_frame, text="Live load :", font=("Corbel", 12))
live_pl_label.grid(row=1, column=0, sticky="w", padx=2, pady=2)

dist_dead_pl = tk.Label(PL_frame, text="distance(in m)", font=("Corbel", 12))
dist_dead_pl.grid(row=0, column=2, sticky="w", padx=2, pady=2)

dist_live_pl = tk.Label(PL_frame, text="distance(in m)", font=("Corbel", 12))
dist_live_pl.grid(row=1, column=2, sticky="w", padx=2, pady=2)

length_entry = ttk.Entry(Frame_1, width=12, textvariable=length_var)
length_entry.grid(row=0, column=1, padx=5, pady=5, ipady=4)

Py_entry = ttk.Entry(Frame_1, width=12, textvariable=Py_var)
Py_entry.grid(row=1, column=1, padx=5, pady=5, ipady=4)
Py_entry.insert(0, 275)

E_entry = ttk.Entry(Frame_1, width=12, textvariable=E_var)
E_entry.grid(row=2, column=1, padx=5, pady=5, ipady=4)
E_entry.insert(0, 205)

dead_entry = ttk.Entry(UDL_frame, width=12, textvariable=dead_var)
dead_entry.grid(row=0, column=1, padx=5, pady=5, ipady=4)

live_entry = ttk.Entry(UDL_frame, width=12, textvariable=live_var)
live_entry.grid(row=1, column=1, padx=5, pady=5, ipady=4)

dead_pl_entry = ttk.Entry(PL_frame, width=8, textvariable=P_DL_var)
dead_pl_entry.grid(row=0, column=1, padx=2, pady=2, ipady=4)

live_pl_entry = ttk.Entry(PL_frame, width=8, textvariable=P_LL_var)
live_pl_entry.grid(row=1, column=1, padx=2, pady=2, ipady=4)

dist_dl_pl = ttk.Entry(PL_frame, width=8, textvariable=a_dl_var)
dist_dl_pl.grid(row=0, column=3, padx=2, pady=2, ipady=4)

dist_ll_pl = ttk.Entry(PL_frame, width=8, textvariable=a_ll_var)
dist_ll_pl.grid(row=1, column=3, padx=2, pady=2, ipady=4)

beam_types = {'simply-supported' : 0,
              'cantilever':1}


tk.Label(third_frame, text= "Select beam type", justify=tk.LEFT, padx=20,  font=("Arial, 12")).pack()

def show_result():
    var = beam_var.get()

for beam, value in beam_types.items():
    tk.Radiobutton(third_frame, text=beam, padx=20, font=("Helvetica", 11),
                   indicator=0, bg="light blue",
                   variable=beam_var, command=show_result, value=beam).pack(anchor=tk.W)



sec_frame = ttk.LabelFrame(second_frame)
sec_frame.grid(row=0, column=2, padx=5, pady=5, sticky="w")



def choose_sec():

        dl = float(dead_var.get())
        ll = float(live_var.get())
        udl_dl = UDL("dead_load", dl)
        udl_ll = UDL("live_load", ll)
        list_of_udl.append(udl_dl)
        list_of_udl.append(udl_ll)

        L = float(length_var.get())
        beam_type = beam_var.get()
        Py = float(Py_var.get())
        E = float(E_var.get())
        ub = UB(L, beam_type, Py, E)
        solve = Analyze(ub, list_of_udl, list_of_pl)
        section = solve.choose_a_section()
        tk.Label(sec_frame, text=f" The selected section is \n{section}").grid(row=0, column=1)

        list_of_pl.clear()
        list_of_udl.clear()

        def classify_sec():
            sec = solve.classify_the_section()
            text = f"The flange is {sec['flange']}\nThe web is {sec['web']}"
            tk.Label(classify_frame, text=text).grid(row=0, column=1)

            def max_Shear():
                shear = solve.max_Shear_Moment()["Maximum Shear Force"]
                tk.Label(max_Shear_frame, text=str(round(shear, 3)) + "kN").grid(row=0, column=1)

            def max_Moment():
                moment = solve.max_Shear_Moment()["Maximum Moment"]
                tk.Label(max_Moment_frame, text=str(round(moment, 3)) + "kN").grid(row=0, column=1)

                def check_shear():
                    chk_shear = solve.shear_check()[0]
                    Fv = round(solve.shear_check()[1], 3)
                    Pv = round(solve.shear_check()[2], 3)
                    if chk_shear == "Shear is okay":
                        tk.Label(shear_check_frame, text="Shear is Okay").grid(row=0, column=1)
                    else:
                        tk.Label(shear_check_frame, text="There is Shear Failure\nThe applied shear({} kN)\n is greater than\n the shear capacity({} kN)".format(Fv, Pv)).grid(row=0, column=1)
                        tk.Button(shear_check_frame, text="Change Section", bg="red").grid(row=1, column=1)
                sh_check_btn = tk.Button(shear_check_frame, text="Check for Shear", bg="violet", height=2,
                                       command=check_shear)
                sh_check_btn.grid(row=0, column=0, sticky="w", padx=10, pady=10)

            text_shear = 'Calculate Maximum \nShear Force(in KN)'
            shear_btn = tk.Button(max_Shear_frame, text=text_shear, bg="violet", height=2,
                          command=max_Shear)
            shear_btn.grid(row=0, column=0, sticky="w", padx=10, pady=10)

            text_moment = 'Calculate Maximum \nMoment(in KNm)'
            moment_btn = tk.Button(max_Moment_frame, text=text_moment, bg="violet", height=2,
                          command=max_Moment)
            moment_btn.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        # Create a frame to classify section
        classify_sect = tk.Button(classify_frame, text="Classify the Section", bg="violet", height=3,
                          command=classify_sec)
        classify_sect.grid(row=0, column=0, sticky="w", padx=10, pady=10)
# Creating the add buttons


def add_1():

    p_dl = float(P_DL_var.get())
    a_dl = float(a_dl_var.get())
    pl = PointLoad("dead_load", p_dl, a_dl)
    list_of_pl.append(pl)
    dead_pl_entry.delete(0, "end")
    dist_dl_pl.delete(0, "end")
    print(list_of_udl)

def add_2():
    p_ll = float(P_LL_var.get())
    a_ll = float(a_ll_var.get())
    pl = PointLoad("live_load", p_ll, a_ll)
    list_of_pl.append(pl)
    live_pl_entry.delete(0, "end")
    dist_ll_pl.delete(0, "end")
    print(list_of_pl)

# Create a button to choose a section
add_button_1 = tk.Button(PL_frame, text="Add", bg="brown", command=add_1, width=5)
add_button_1.grid(row=0, column=4, padx=5, pady=5)

add_button_2 = tk.Button(PL_frame, text="Add", bg="brown", command=add_2, width=5)
add_button_2.grid(row=1, column=4, padx=5, pady=5)

ch_section = tk.Button(sec_frame, text="Choose a Section", bg="violet", height=3, command=choose_sec)
ch_section.grid(row=0, column=0, sticky="w", padx=10, pady=10)

classify_frame = ttk.LabelFrame(second_frame)
classify_frame.grid(row=1, column=2, padx=5, pady=5, sticky="w")

max_Shear_frame = ttk.LabelFrame(second_frame)
max_Shear_frame.grid(row=2, column=2, padx=5, pady=5, sticky="w")

max_Moment_frame = ttk.LabelFrame(second_frame)
max_Moment_frame.grid(row=3, column=2, padx=5, pady=5, sticky="w")

shear_check_frame = ttk.LabelFrame(second_frame)
shear_check_frame.grid(row=4, column=2, padx=5, pady=5, sticky="w")

win.mainloop()