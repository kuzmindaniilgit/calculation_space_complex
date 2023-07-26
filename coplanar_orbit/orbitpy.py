from math import *
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

class IntegrationConstants:
    def __init__(self, x, y, z, vx, vy, vz, t0=None):
        self.x=x
        self.y=y
        self.z=z

        self.r=[x, y, z]

        self.vx=vx 
        self.vy=vy
        self.vz=vz

        self.v=[vx,vy,vz]

        self.R = (x**2+y**2+z**2)**(1/2)
        self.V = (vx**2+vy**2+vz**2)**(1/2)

        self.t0=t0
    
    def find(self):
        MU=398600 # приведенный гравитационный параметр для Земли [км^3*c^-2]

        self.h = self.V**2 - 2*MU/self.R #постоянная энергии
    
        cx = (self.y*self.vz-self.z*self.vy)
        cy = (self.z*self.vx-self.x*self.vz)
        cz = (self.x*self.vy-self.y*self.vx)


        self.c = [cx, cy, cz] #векторная постоянная площадей
        self.C = (cx**2+cy**2+cz**2)**(1/2)

        fx = (self.vy*cz-self.vz*cy-MU*(self.x/self.R))
        fy = (self.vz*cx-self.vx*cz-MU*(self.y/self.R))
        fz = (self.vx*cy-self.vy*cx-MU*(self.z/self.R))

        self.f = [fx,fy,fz] #вектор Лапласа
        self.F = (fx**2+fy**2+fz**2)**(1/2)

        self.p = self.C**2/MU #фокальный параметр
        self.e = self.F/MU #эксцентриситет
        self.i = acos(cz/self.C) #наклонение

        e_N = [-cy*(1/(cx**2+cy**2)**(1/2)), cx*(1/(cx**2+cy**2)**(1/2)), 0]

        cosOmega = - cy/(cx**2+cy**2)**(1/2) #долгота восх узла

        if cx/(cx**2+cy**2)**(1/2) > 0:
            self.Omega = acos(cosOmega)
        else:
            self.Omega = 2*pi - acos(cosOmega)

        cosomega = (e_N[0]*fx + e_N[1]*fy)/self.F #аргумент перицентра

        if (fz*(cx**2+cy**2)-cz*(fx*cx+fy*cy))/(cx**2+cy**2)**(1/2) > 0:
            self.omega = acos(cosomega)
        else:
            self.omega = 2*pi - acos(cosomega)

        cosnu = (fx*self.x+fy*self.y+fz*self.z)/(self.F*self.R) #истинная аномалия 

        if (fy*self.z-fz*self.y)*cx+(fz*self.x-fx*self.z)*cy+(fx*self.y-fy*self.x)*cz > 0:
            self.nu = acos(cosnu)
        else:
            self.nu = 2*pi - acos(cosnu)

        self.u = self.omega+self.nu #аргумент широты

        self.tpi = None
        if self.t0 is not None:
            a = -MU/self.h #большая полуось

            E0 = 2*atan( (( (1-self.e) / (1+self.e) )**(1/2))*tan(self.nu/2) ) #эксцентрическая аномалия

            n = (MU/(a**3))**(1/2) #среднее движение

            self.tpi = self.t0 - (E0 - self.e*sin(E0))/n #время прохождения перигея

        print('Константы найдены (см. документацию)! \nОсновные константы интегрирования (h, p, e, i, Omega, tpi):')
        print(self.h, self.p, self.e, self.i, self.Omega, self.tpi)
        return
    
    def to2d(self, epsilon=0.0001):
        matrix_A1 = np.array([
            [cos(self.Omega), sin(self.Omega), 0], 
            [-sin(self.Omega), cos(self.Omega), 0], 
            [0, 0, 1]])

        matrix_A2 = np.array([
            [1, 0, 0],
            [0, cos(self.i), sin(self.i)], 
            [0, -sin(self.i), cos(self.i)]])
        
        matrix = matrix_A2.dot(matrix_A1)

        n = len(str(epsilon)) - 2

        r2d = matrix.dot(np.array(self.r))
        v2d = matrix.dot(np.array(self.v))

        x = round(r2d[0], n)
        y = round(r2d[1], n)
        z = round(r2d[2], n)

        vx = round(v2d[0], n)
        vy = round(v2d[1], n)
        vz = round(v2d[2], n)

        return ([x, y, z],[vx, vy, vz])

class Trajectory:
    def __init__(self, start=0, end=100, step=1):
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
    
    def spacecraft(self, mass, mass_fuel, dm, abs_w):
        
        self.mass = mass
        self.mass_fuel = mass_fuel
        self.dm = dm*self.step
        self.abs_w = abs_w*self.step

    def trajectory(self, x_0, y_0, vx_0, vy_0, engine_start=[], engine_dt=[]):
        
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
                       self.start, 
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
                if t in engine_start and self.mass_fuel > 0 and not flag: 
                    count_run += 1
                    flag = True
                    
                if flag:
                    Wx = self.abs_w * self.Vx[i]/sqrt(self.Vx[i]**2+self.Vy[i]**2)
                    Wy = self.abs_w * self.Vy[i]/sqrt(self.Vx[i]**2+self.Vy[i]**2)
                    
                self.Vx.append(self.Vx[i]-MU*(self.X[i+1]/abs_r**3)*t+(self.dm*Wx/self.mass)*t)
                self.Vy.append(self.Vy[i]-MU*(self.Y[i+1]/abs_r**3)*t+(self.dm*Wy/self.mass)*t)

                self.v.append([self.Vx[i],self.Vy[i]])

                if flag:
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
                
                if round(engine_t, 1) == engine_dt[count_run]: 
                    flag = False
                    Wx = 0
                    Wy = 0
                    engine_t = 0

                                    
    def data(self):
        
        return pd.DataFrame(self.q, columns=['fi','X', 'Y', '|r|' ,'Vx', 'Vy', '|V|', 't','mass'])
                    
    def plot(self, radius_vect=False, dot_engine_start=False):
        
        data = self.data()
        max_val = int(data[data['|r|']==max(data['|r|'])]['|r|'].iloc[0]) + 5000
        n = len(str(max_val))-2
        step = 5*10**n
        
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
        
    def pplotly(self):
        
        data = self.data()        
        max_val = int(data[data['|r|']==max(data['|r|'])]['|r|']) + 5000
        n = len(str(max_val))-2
        step = 5*10**n
        
        layout = dict(plot_bgcolor='white',
              margin=dict(t=20, l=20, r=20, b=20),
              xaxis=dict(title='X',
                         range=[-max_val, max_val],
                         linecolor='#d9d9d9',
                         mirror=True,
                         dtick=step),
              yaxis=dict(title='Y',
                         range=[-max_val, max_val],
                         linecolor='#d9d9d9',
                         mirror=True,
                         dtick=step),
              height=1000, 
              width=1000)
        
        val = go.Scatter(x=self.X,
                          y=self.Y,
                          mode='lines+markers+text',
                          marker=dict(color='#5D69B1', size=5),
                          line=dict(color='#52BCA3', width=1, dash='dash'))
        fig = go.Figure(data=val, layout=layout)
        fig.update_xaxes(gridcolor='gray', zerolinecolor='red')
        fig.update_yaxes(gridcolor='gray', zerolinecolor='red')
        fig.show()

    def polar(self, p, e):
        nu = np.arange(0,2*np.pi, 0.1)
        r = p/(1+e*np.cos(nu))

        ax = plt.subplot(111,projection='polar')
        ax.plot(nu, r, color='r', linewidth=3)
        ax.grid(True)

        plt.show()

    def orbit3d(self, i, omega, Omega, p, e, vertical_roll=30, z_roll=30):
        r_earth = 6371

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        ax.plot([-15000, 15000], [0, 0], [0, 0], color='black')
        ax.plot([0, 0], [-15000, 15000], [0, 0], color='black')
        ax.plot([0, 0], [0, 0], [-15000, 15000], color='black')

        u, v = np.mgrid[0:2*np.pi:20j, 0:np.pi:10j]
        x_earth = r_earth*np.cos(u)*np.sin(v)
        y_earth = r_earth*np.sin(u)*np.sin(v)
        z_earth = r_earth*np.cos(v)
        ax.plot_surface(x_earth, y_earth, z_earth, cmap='gist_earth')

        nu = np.linspace(0, 2*np.pi, 100)
        r = p / (1 + e*np.cos(nu))
        x_orbit = r * np.cos(nu)
        y_orbit = r * np.sin(nu)
        z_orbit = np.zeros_like(x_orbit)

        A = np.array([
            [cos(omega)*cos(Omega)-sin(omega)*cos(i)*sin(Omega),-sin(omega)*cos(Omega)-cos(omega)*cos(i)*sin(Omega), sin(i)*sin(Omega)], 
            [cos(omega)*sin(Omega)+sin(omega)*cos(i)*cos(Omega),-sin(omega)*sin(Omega)+cos(omega)*cos(i)*cos(Omega), -sin(i)*cos(Omega)], 
            [sin(omega)*sin(i), cos(omega)*sin(i), cos(i)]])

        xyz = np.array([x_orbit, y_orbit, z_orbit]).T
        xyz = A.dot(xyz.T).T
        x_orbit, y_orbit, z_orbit = xyz[:, 0], xyz[:, 1], xyz[:, 2]
        ax.plot(x_orbit, y_orbit, z_orbit, color='red', alpha=0.7)

        lim = max(r)/2
        ax.set_xlim([-lim, lim])
        ax.set_ylim([-lim, lim])
        ax.set_zlim([-lim, lim])

        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')

        ax.view_init(vertical_roll, z_roll)

        plt.show()