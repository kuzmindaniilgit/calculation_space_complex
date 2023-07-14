from math import *
import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go

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
        
    def plotly_graph(self):
        
        data = self.data()        
        max_val = int(data[data['|r|']==max(data['|r|'])]['|r|']) + 20_000
        d = {3:50, 4:500, 5:5000, 6:50000, 7:500000}
        step = d[len(str(max_val))]
        
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