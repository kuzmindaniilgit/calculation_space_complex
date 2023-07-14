from tkinter import *
from tkinter import ttk
from PIL import Image, ImageTk
from math import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import webbrowser

class Trajectory():
    def __init__(self, start, end, step):
        
        self.start = start
        self.end = end
        self.step = step
        self.fi = []
        self.X = []
        self.Y = []
        self.r = []
        self.Vx = []
        self.Vy = []
        self.v = []
        self.q = []
    
    def _spacecraft_param(self, mass, mass_fuel, dm, abs_w):
        
        self.mass = mass
        self.mass_fuel = mass_fuel
        self.dm = dm*self.step
        self.abs_w = abs_w*self.step

    def trajectory(self, x_0, y_0, vx_0, vy_0, engine_start, engine_dt):
        
        grad = 180/pi
        M = 5.9722e24 #масса Земли [кг] /  Earth's mass [kg]
        G = 6.674e-20 #гравитационная постоянная [км^3/ кг*c^2] / gravitational constant [km^3 / kg*s^2]
        MU = G*M #гравитационный параметр для Земли [км^3*c^-2] / the gravitational parameter of the Earth [km^3*s^-2]
        
        self.X.append(x_0)
        self.Y.append(y_0)
        self.r.append([self.X[0], self.Y[0]])
        self.fi.append(atan(self.Y[0]/self.X[0])*grad)
        self.Vx.append(vx_0)
        self.Vy.append(vy_0)
        self.v.append([self.Vx[0],self.Vy[0]])
        self.q.append([self.fi[0], 
                       self.X[0],
                       self.Y[0], 
                       sqrt(self.X[0]**2+self.Y[0]**2),
                       self.Vx[0],
                       self.Vy[0],
                       sqrt(self.Vx[0]**2+self.Vy[0]**2), 
                       0, 
                       self.mass])
        
        self.engine_start = engine_start
        
        flag = False
        engine_start = engine_start
        count_run = 0
        engine_dt = [0] + engine_dt
        engine_t = 0
        Wx = 0
        Wy = 0
        for t, i in zip(np.arange(self.start, self.end, self.step), range(int(self.end/self.step))) :
                self.X.append(self.X[i]+self.Vx[i]*t)
                self.Y.append(self.Y[i]+self.Vy[i]*t)
                self.fi.append(atan(self.Y[i]/self.X[i])*grad)
                self.r.append([self.X[i],self.Y[i]])
                abs_r = sqrt(self.X[i+1]**2+self.Y[i+1]**2)
                if t in engine_start and self.mass_fuel > 0 and flag==False: 
                    count_run += 1
                    flag = True
                    
                if flag == True:
                    Wx = self.abs_w * self.Vx[i]/sqrt(self.Vx[i]**2+self.Vy[i]**2)
                    Wy = self.abs_w * self.Vy[i]/sqrt(self.Vx[i]**2+self.Vy[i]**2)
                    
                self.Vx.append(self.Vx[i]-MU*(self.X[i+1]/(abs_r**3))*t+((self.dm*Wx)/self.mass)*t)
                self.Vy.append(self.Vy[i]-MU*(self.Y[i+1]/abs_r**3)*t+((self.dm*Wy)/self.mass)*t)

                self.v.append([self.Vx[i],self.Vy[i]])

                if flag == True:
                    engine_t += self.step
                    self.mass -= self.dm
                    self.mass_fuel -= self.dm

                self.q.append([self.fi[i+1], 
                               self.X[i+1], 
                               self.Y[i+1], 
                               abs_r, 
                               self.Vx[i+1],
                               self.Vy[i+1], 
                               sqrt(self.Vx[i+1]**2+self.Vy[i+1]**2), 
                               t+self.step, 
                               self.mass])

                if engine_t == engine_dt[count_run]: 
                    flag = False
                    Wx = 0
                    Wy = 0
                    engine_t = 0
                                    
    def data(self):
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)
        return pd.DataFrame(self.q, columns=['fi','X', 'Y', '|r|' ,'Vx', 'Vy', '|V|', 't','mass'])
                    
    def plot(self, radius_vect=False, dot_engine_start=False):
        
        data = self.data()
        max_val = int(data[data['|r|']==max(data['|r|'])]['|r|']) + 5000
        
        d = {3:50, 4:500, 5:5000, 6:50000, 7:500000}
        step = d[len(str(max_val))]
        
        color = 'blue'
        fig, ax = plt.subplots(figsize=(20,20))
        ax.spines['left'].set_position('center')
        ax.spines['bottom'].set_position('center')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        ax.scatter(self.X, self.Y, c=color, alpha = 0.5)
        ax.set(xlim=(-max_val, max_val), xticks=np.arange(-max_val, max_val,step),
               ylim=(-max_val, max_val), yticks=np.arange(-max_val, max_val,step))
        ax.plot(self.X, self.Y, "r--", alpha=0.2)
        
        if radius_vect == True:
            x_0 = np.zeros(len(self.X))
            y_0 = np.zeros(len(self.Y))
            X_array = np.array(self.X)
            Y_array = np.array(self.Y)
            ax.quiver(x_0, y_0, X_array, Y_array, units='xy' ,scale=1, color='red', width=5, headwidth=100, headlength=50)
        
        
        if dot_engine_start == True:
            for i in range(len(self.engine_start)):
                x = data.loc[data['t'] == self.engine_start[i], 'X']
                y = data.loc[data['t'] == self.engine_start[i], 'Y']
                ax.scatter(x, y, color='red', linewidths=3, marker='*',s=150)
            
        plt.grid()
        plt.show()

BGCOLOR = 'lightblue'
TXTCOLOR = '#00567B'

def start_app():
    intro_frame.pack_forget()
    label_steps.pack(pady=[35,0])
    init_param_frame.pack()

def send_init_param():
    global tj
    tj = Trajectory(float(start.get()), float(stop.get()), float(step.get()))
    init_param_frame.pack_forget()
    img = Image.open("img/title_step_2.png")
    step2 = ImageTk.PhotoImage(img)
    label_steps.configure(image=step2)
    label_steps.image = step2
    spacecraft_param_frame.pack(anchor=CENTER, padx=10, pady=10)

def send_spacecraft_param():
    global tj
    tj._spacecraft_param(
        mass = float(mass.get()),
        mass_fuel = float(mass_fuel.get()),
        dm = float(dm.get()),
        abs_w = float(abs_w.get())
    )
    spacecraft_param_frame.pack_forget()
    img = Image.open("img/title_step_3.png")
    step3 = ImageTk.PhotoImage(img)
    label_steps.configure(image=step3)
    label_steps.image = step3
    start_param_frame.pack(anchor=CENTER, padx=10, pady=10)

def send_start_param():
    start_param_frame.pack_forget()
    img = Image.open("img/title_step_4.png")
    step4 = ImageTk.PhotoImage(img)
    label_steps.configure(image=step4)
    label_steps.image = step4
    engine_param_frame.pack(anchor=CENTER, padx=10, pady=10)

def add_engine_time():
    engine_start.append(float(eng_start.get()))
    engine_dt.append(float(eng_dt.get()))
    eng_dt.delete(0, END)
    eng_start.delete(0, END)
        
def send_all():
    global tj
    tj.trajectory(
        x_0=float(x.get()), 
        y_0=float(y.get()), 
        vx_0=float(vx.get()), 
        vy_0=float(vy.get()), 
        engine_start=engine_start, 
        engine_dt = engine_dt
    )
    engine_param_frame.pack_forget()
    final_frame.pack(anchor=CENTER, padx=10, pady=10)
    img = Image.open("img/title_step_5.png")
    step5 = ImageTk.PhotoImage(img)
    label_steps.configure(image=step5)
    label_steps.image = step5
    label_end.pack(side=BOTTOM)

def visual_plot():
    global tj
    tj.plot(radius_vect=radius_vect, dot_engine_start=dot_engine_start)

def selected(event):
    global selection
    selection = combobox.get()

def get_data():
    path = str(namepath.get())
    global tj
    if selection == 'Excel (.xlsx)':
        tj.data().to_excel(path+'matrix.xlsx')
    else:
        data = str(tj.data())
        f = open(path+'matrix.txt', 'w')
        f.write(data)
        f.close()
    
    window = Tk()
    window.title('Сохранение данных')
    window.geometry('400x100')
    window.configure(bg=BGCOLOR)

    label = Label(window, text='Сохранение выполнено успешно!', bg=BGCOLOR, font=('Arial', 16, 'bold'), fg=TXTCOLOR)
    label.pack(anchor=CENTER, pady=35)

def add_radius():
    global radius_vect
    if radius_vect:
        radius_vect = False
    else:
        radius_vect = True

def add_engine_start_dot():
    global dot_engine_start
    if dot_engine_start:
        dot_engine_start = False
    else:
        dot_engine_start = True
    
def callback(url):
    webbrowser.open_new(url)

#init root
root = Tk()
root.title('Coplanar Orbits') 
root.geometry('600x550')
root.resizable(False, False)
root.iconbitmap('img/Icon.ico')
root.configure(bg=BGCOLOR)

intro_frame = Frame(bg=BGCOLOR)

#title and subtitle
img = Image.open("img/Logo.png")
logo = ImageTk.PhotoImage(img)
label_title = Label(intro_frame,image=logo, bg=BGCOLOR)
label_title.pack()

img = Image.open("img/Info.png")
info = ImageTk.PhotoImage(img)
label_subtitle = Label(intro_frame, image=info, bg=BGCOLOR)
label_subtitle.pack()

img = Image.open("img/btn_start.png")
btn_start = ImageTk.PhotoImage(img)
btn = Button(intro_frame, text='', image=btn_start, bg=BGCOLOR, borderwidth=0, highlightthickness=0, command=start_app)
btn.pack(side=BOTTOM, pady=35)

intro_frame.pack()

#title steps
img = Image.open("img/title_step_1.png")
step1 = ImageTk.PhotoImage(img)
label_steps = Label(image=step1, bg=BGCOLOR)
label_steps.pack_forget()

#first frame
init_param_frame = Frame(height=250, width=350, padx=10, pady=10, bg=BGCOLOR)

label = Label(init_param_frame, 
              text='Введите начальный момент времени:', 
              foreground=TXTCOLOR, 
              bg=BGCOLOR, 
              font=('Arial', 16, 'bold'))
label.pack(anchor=NW)

frame_entry = Frame(init_param_frame, bg=BGCOLOR)
img = Image.open("img/Entry.png")
entry_start = ImageTk.PhotoImage(img)
label_entry = Label(frame_entry, image=entry_start, bg=BGCOLOR, borderwidth=0, highlightthickness=0)
label_entry.pack()
start = Entry(frame_entry, bg='white', highlightthickness=0, borderwidth=0, width=25, font=('Arial', 16))
start.place(x=15, y=12)
frame_entry.pack(pady=[0,15])

label = Label(init_param_frame, 
              text='Введите конечный момент времени:',
              foreground=TXTCOLOR, 
              bg=BGCOLOR, 
              font=('Arial', 16, 'bold'))
label.pack(anchor=NW)
frame_entry = Frame(init_param_frame, bg=BGCOLOR)
img = Image.open("img/Entry.png")
entry_end = ImageTk.PhotoImage(img)
label_entry = Label(frame_entry, image=entry_end, bg=BGCOLOR, borderwidth=0, highlightthickness=0)
label_entry.pack()
stop = Entry(frame_entry, bg='white', highlightthickness=0, borderwidth=0, width=25, font=('Arial', 16))
stop.place(x=15, y=12)
frame_entry.pack(pady=[0,15])

label = Label(init_param_frame, 
              text='Введите шаг интегрирования:',
              foreground=TXTCOLOR, 
              bg=BGCOLOR, 
              font=('Arial', 16, 'bold'))
label.pack(anchor=NW)

frame_entry = Frame(init_param_frame, bg=BGCOLOR)
img = Image.open("img/Entry.png")
entry_step = ImageTk.PhotoImage(img)
label_entry = Label(frame_entry, image=entry_step, bg=BGCOLOR, borderwidth=0, highlightthickness=0)
label_entry.pack()
step = Entry(frame_entry, bg='white', highlightthickness=0, borderwidth=0, width=25, font=('Arial', 16))
step.place(x=15, y=12)
frame_entry.pack()

img = Image.open("img/btn_next.png")
btn_next = ImageTk.PhotoImage(img)
btn = Button(init_param_frame, image=btn_next, command=send_init_param, bg=BGCOLOR, borderwidth=0, highlightthickness=0)
btn.pack(pady=25)

init_param_frame.pack_forget()

#second frame
spacecraft_param_frame = Frame(padx=10, pady=10, bg=BGCOLOR)

label = Label(spacecraft_param_frame, 
            text='Введите массу КА:',
            foreground=TXTCOLOR, 
            bg=BGCOLOR, 
            font=('Arial', 16, 'bold'))
label.pack(anchor=NW)

frame_entry = Frame(spacecraft_param_frame, bg=BGCOLOR)
img = Image.open("img/Entry.png")
entry_mass = ImageTk.PhotoImage(img)
label_entry = Label(frame_entry, image=entry_mass, bg=BGCOLOR, borderwidth=0, highlightthickness=0)
label_entry.pack()
mass = Entry(frame_entry, bg='white', highlightthickness=0, borderwidth=0, width=25, font=('Arial', 16))
mass.place(x=15, y=12)
frame_entry.pack(pady=[0,15])

label = Label(spacecraft_param_frame,
            text='Введите массу топлива:',
            foreground=TXTCOLOR, 
            bg=BGCOLOR, 
            font=('Arial', 16, 'bold'))
label.pack(anchor=NW)

frame_entry = Frame(spacecraft_param_frame, bg=BGCOLOR)
img = Image.open("img/Entry.png")
entry_mass_fuel = ImageTk.PhotoImage(img)
label_entry = Label(frame_entry, image=entry_mass_fuel, bg=BGCOLOR, borderwidth=0, highlightthickness=0)
label_entry.pack()
mass_fuel = Entry(frame_entry, bg='white', highlightthickness=0, borderwidth=0, width=25, font=('Arial', 16))
mass_fuel.place(x=15, y=12)
frame_entry.pack(pady=[0,15])

label = Label(spacecraft_param_frame,
            text='Введите массовый расход:',
            foreground=TXTCOLOR, 
            bg=BGCOLOR, 
            font=('Arial', 16, 'bold'))
label.pack(anchor=NW)

frame_entry = Frame(spacecraft_param_frame, bg=BGCOLOR)
img = Image.open("img/Entry.png")
entry_dm = ImageTk.PhotoImage(img)
label_entry = Label(frame_entry, image=entry_dm, bg=BGCOLOR, borderwidth=0, highlightthickness=0, font=('Arial', 16))
label_entry.pack()
dm = Entry(frame_entry, bg='white', highlightthickness=0, borderwidth=0, width=25, font=('Arial', 16))
dm.place(x=15, y=12)
frame_entry.pack(pady=[0,15])

label = Label(spacecraft_param_frame,
            text='Введите модуль скорости истечения газа:',
            foreground=TXTCOLOR, 
            bg=BGCOLOR, 
            font=('Arial', 16, 'bold'))
label.pack(anchor=NW)

frame_entry = Frame(spacecraft_param_frame, bg=BGCOLOR)
img = Image.open("img/Entry.png")
entry_abs_w= ImageTk.PhotoImage(img)
label_entry = Label(frame_entry, image=entry_abs_w, bg=BGCOLOR, borderwidth=0, highlightthickness=0)
label_entry.pack()
abs_w = Entry(frame_entry, bg='white', highlightthickness=0, borderwidth=0, width=25, font=('Arial', 16))
abs_w.place(x=15, y=12)
frame_entry.pack()

img = Image.open("img/btn_next.png")
btn_next_spc = ImageTk.PhotoImage(img)
btn = Button(spacecraft_param_frame, image=btn_next_spc, command=send_spacecraft_param, bg=BGCOLOR, borderwidth=0, highlightthickness=0)
btn.pack(pady=[15,0])

spacecraft_param_frame.pack_forget()

#third frame
start_param_frame = Frame(bg=BGCOLOR, padx=10, pady=10)

label = Label(start_param_frame, 
            text='Введите начальную x компоненту:',
            foreground=TXTCOLOR, 
            bg=BGCOLOR, 
            font=('Arial', 16, 'bold'))
label.pack(anchor=NW)

frame_entry = Frame(start_param_frame, bg=BGCOLOR)
img = Image.open("img/Entry.png")
entry_x = ImageTk.PhotoImage(img)
label_entry = Label(frame_entry, image=entry_x, bg=BGCOLOR, borderwidth=0, highlightthickness=0)
label_entry.pack()
x = Entry(frame_entry, bg='white', highlightthickness=0, borderwidth=0, width=25, font=('Arial', 16))
x.place(x=15, y=12)
frame_entry.pack(pady=[0,15])

label = Label(start_param_frame,
            text='Введите начальную y компоненту:',
            foreground=TXTCOLOR, 
            bg=BGCOLOR, 
            font=('Arial', 16, 'bold'))
label.pack(anchor=NW)

frame_entry = Frame(start_param_frame, bg=BGCOLOR)
img = Image.open("img/Entry.png")
entry_y = ImageTk.PhotoImage(img)
label_entry = Label(frame_entry, image=entry_y, bg=BGCOLOR, borderwidth=0, highlightthickness=0)
label_entry.pack()
y = Entry(frame_entry, bg='white', highlightthickness=0, borderwidth=0, width=25, font=('Arial', 16))
y.place(x=15, y=12)
frame_entry.pack(pady=[0,15])

label = Label(start_param_frame,
            text='Введите начальную Vx компоненту:',
            foreground=TXTCOLOR, 
            bg=BGCOLOR, 
            font=('Arial', 16, 'bold'))
label.pack(anchor=NW)

frame_entry = Frame(start_param_frame, bg=BGCOLOR)
img = Image.open("img/Entry.png")
entry_vx = ImageTk.PhotoImage(img)
label_entry = Label(frame_entry, image=entry_vx, bg=BGCOLOR, borderwidth=0, highlightthickness=0)
label_entry.pack()
vx = Entry(frame_entry, bg='white', highlightthickness=0, borderwidth=0, width=25, font=('Arial', 16))
vx.place(x=15, y=12)
frame_entry.pack(pady=[0,15])

label = Label(start_param_frame,
            text='Введите начальную Vy компоненту:',
            foreground=TXTCOLOR, 
            bg=BGCOLOR, 
            font=('Arial', 16, 'bold'))
label.pack(anchor=NW)

frame_entry = Frame(start_param_frame, bg=BGCOLOR)
img = Image.open("img/Entry.png")
entry_vy= ImageTk.PhotoImage(img)
label_entry = Label(frame_entry, image=entry_vy, bg=BGCOLOR, borderwidth=0, highlightthickness=0)
label_entry.pack()
vy = Entry(frame_entry, bg='white', highlightthickness=0, borderwidth=0, width=25, font=('Arial', 16))
vy.place(x=15, y=12)
frame_entry.pack()

img = Image.open("img/btn_next.png")
btn_next_stpm = ImageTk.PhotoImage(img)
btn = Button(start_param_frame, image=btn_next_stpm, command=send_start_param, bg=BGCOLOR, borderwidth=0, highlightthickness=0)
btn.pack(pady=[15,0])

start_param_frame.pack_forget()

#du frame
engine_param_frame = Frame(padx=10, bg=BGCOLOR)

label = Label(engine_param_frame, 
            text='Укажите момент времени запуска двигателя \n и далее - время его работы (дельту). \n Далее нажмите кнопку добавить. \n Повторите необходимое кол-во раз.',
            foreground=TXTCOLOR, 
            bg=BGCOLOR, 
            font=('Arial', 18, 'bold'))
label.pack(anchor=NW)

frame_entry = Frame(engine_param_frame, bg=BGCOLOR)
img = Image.open("img/Entry.png")
entry_eng_start = ImageTk.PhotoImage(img)
label_entry = Label(frame_entry, image=entry_eng_start, bg=BGCOLOR, borderwidth=0, highlightthickness=0)
label_entry.pack()
eng_start = Entry(frame_entry, bg='white', highlightthickness=0, borderwidth=0, width=25, font=('Arial', 16))
eng_start.place(x=15, y=12)
frame_entry.pack(pady=[15,15])

frame_entry = Frame(engine_param_frame, bg=BGCOLOR)
img = Image.open("img/Entry.png")
entry_eng_dt = ImageTk.PhotoImage(img)
label_entry = Label(frame_entry, image=entry_eng_dt, bg=BGCOLOR, borderwidth=0, highlightthickness=0)
label_entry.pack()
eng_dt = Entry(frame_entry, bg='white', highlightthickness=0, borderwidth=0, width=25, font=('Arial', 16))
eng_dt.place(x=15, y=12)
frame_entry.pack(pady=[0,15])

#a place we add the entry
engine_dt = []
engine_start = []

img_btadd = Image.open("img/btn_add.png")
btn_add = ImageTk.PhotoImage(img_btadd)
btn = Button(engine_param_frame, image=btn_add, command=add_engine_time, bg=BGCOLOR, borderwidth=0, highlightthickness=0)
btn.pack(side=LEFT, pady=25)

img = Image.open("img/btn_next.png")
btn_next_eng = ImageTk.PhotoImage(img)
btn = Button(engine_param_frame, image=btn_next_eng, command=send_all, bg=BGCOLOR, borderwidth=0, highlightthickness=0)
btn.pack(side=RIGHT, pady=25)

engine_param_frame.pack_forget()

#final frame
final_frame = Frame(padx=10, bg=BGCOLOR)

label = Label(final_frame, 
            text='Что указать на графике?',
            foreground=TXTCOLOR, 
            bg=BGCOLOR, 
            font=('Arial', 16, 'bold'))
label.pack(anchor=NW) 

radius_vect = False
dot_engine_start = False
btn_add_rv = Checkbutton(final_frame, text='Добавить радиус-вектора', command=add_radius, bg=BGCOLOR, font=('Arial', 14), fg=TXTCOLOR, padx=20)
btn_add_rv.pack(anchor=NW)
btn_add_dot = Checkbutton(final_frame, text='Добавить точки вкл ДУ', command=add_engine_start_dot, bg=BGCOLOR, font=('Arial', 14), fg=TXTCOLOR, padx=20)
btn_add_dot.pack(anchor=NW)

img = Image.open("img/btn_create.png")
btn_create = ImageTk.PhotoImage(img)
btn = Button(final_frame, image=btn_create, command=visual_plot, bg=BGCOLOR, borderwidth=0, highlightthickness=0)
btn.pack(anchor=CENTER, pady=[5,15])

label_wnd = Label(final_frame, bg=BGCOLOR, text = 'Укажите формат и путь, куда сохранить файл. Или оставьте поле пустым. \n В таком случае файл сохранится там, где запущена программа. \n (Пример, MacOS: /Users/daniilkuzmin/Documents/) \n (Пример, Windows: C:\kuzmd\Documents\)', fg=TXTCOLOR, font=('Arial', 12), padx=5)
label_wnd.pack(side=TOP)

frame_btn = Frame(final_frame, bg=BGCOLOR)
format = ["Excel (.xlsx)", "Text (.txt)"]
combobox = ttk.Combobox(frame_btn, values=format, background=BGCOLOR)
combobox.pack(side=LEFT, padx=[0,5])
combobox.bind("<<ComboboxSelected>>", selected)

frame_entry = Frame(frame_btn, bg=BGCOLOR)
img = Image.open("img/entry_path.png")
entry_namepath = ImageTk.PhotoImage(img)
label_entry = Label(frame_entry, image=entry_namepath, bg=BGCOLOR, borderwidth=0, highlightthickness=0)
label_entry.pack()

namepath = Entry(frame_entry, bg='white', highlightthickness=0, borderwidth=0, width=10, font=('Arial', 12))
namepath.place(x=13, y=4)
frame_entry.pack(side=RIGHT)

frame_btn.pack(pady=[0,5])

img = Image.open("img/btn_save.png")
btn_save = ImageTk.PhotoImage(img)
btn = Button(final_frame, image=btn_save, command=get_data, bg=BGCOLOR, borderwidth=0, highlightthickness=0)
btn.pack(anchor=CENTER)
final_frame.pack_forget()

label_end = Label(text='Разработчик: https://github.com/kuzmindaniilgit', background=BGCOLOR, cursor="hand2", font=('Arial', 12), fg=TXTCOLOR)
label_end.pack_forget()
label_end.bind("<Button-1>", lambda e: callback("https://github.com/kuzmindaniilgit"))

#save frame


root.mainloop()