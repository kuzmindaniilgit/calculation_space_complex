# Coplanar_orbit.py
Данная библиотека позволяет работать с компланарными орбитами, а также с движение КА по этой орбите с отслеживанием его матрицы состояния $(\phi, x, y, r,V_x, V_y, V, t, m)$.
 - Класс `Trajectory` позволяет построить переходную орбиту, после чего выполнить n компланарных переходов между орбитами.

<b> Для упрощения работы выполнен графический интерфейс. Для работы с графическим интерфейсом достаточно скачать архив `CoOrbits.rar`. </b>

---

This library allows you to work with coplanar orbits, as well as with the movement of the spacecraft along this orbit with tracking its state matrix $(\phi, x, y, r, V_x, V_y, V, t, m)$.
 - The `Trajectory` class allows you to build a transition orbit, and then perform n coplanar transitions between orbits.

<b> To simplify the work, a graphical interface has been created. To work with the graphical interface, it is enough to download the archive `CoOrbits.rar`.</b>

## Применение / Usage
При работе с классом выполняются шаги в данной последовательности [(пример)](example_usage.ipynb):
1. При инициализации вводится начальный, конечный моменты времени `(start, end)`, а также шаг интегрирования `(step)`;
```Python
    tj = Trajectory(start=0, end=100, step=1)
```
2. Далее инициализируются параметры КА с РБ:

    `mass` - масса КА,<br>
    `mass_fuel `- масса топлива,<br>
    `dm `- массовый расход,<br>
    `abs_w` - модуль вектора скорости истечения газа из сопла;
```Python
    tj._spacecraft_param(
        mass=20_000,
        mass_fuel=15_000,
        dm=20,
        abs_w=3
    )
```
3. Далее необходимо задать компоненты начального радиуса-вектора $(x_0, y_0)$ и вектора скорости в начальный момент времени $(V_x, V_y)$ и два параметра `(engine_start, engine_dt)`: 

    `engine_start` передается списком, указываются моменты времени запуска двигателя, <br>
    `engine_dt` передается список, указывается время работы двигателя. <br>
    <b> Позиции в списке должны соответствовать друг другу; </b>
```Python
    tj.trajectory(
        x_0=6500,
        y_0=0,
        vx_0=0,
        vy_0=7.8,
        engine_start=[],
        engine_dt=[]
    )
```
4. Метод `data` позволяет работать с табличными данными (таблица - это матрица состояния);

5. Метод `plot` - выводит график, имеет параметры:
- `radius_vector = False ` по-умолчанию. <br>
Параметр отвечает за отображение радиус-векторов; 
- `dot_engine_start = False` по-умолчанию. <br>
    Параметр отвечает за отображение точек включения двигателя;

6. Метод `plotly_graph` - выводит интерактивный график задействующий библиотеку plotly;

---

Check the example how to use that class [here](example_usage.ipynb) and follow the instruction below. <br>

This class allows you to build a transition orbit, then perform n coplanar transitions between orbits.
 1. During initialization, the initial, final time points `(start, end)`, as well as the integration step `(step)` are entered;
 2. Next, the parameters of the spacecraft with US (upper stage) are initialized:

`mass` - mass of the spacecraft, <br>
`mass_fuel` - fuel mass, <br>
`dm` - mass flow rate, <br>
`abs_w` - modulus of the velocity vector of gas outflow from the nozzle;

 3. Next, you need to set the components of the initial radius-the vector $(x_0, y_0)$ and the velocity vector $(V_x, V_y)$ for $x=x_0$, $y=y_0$
and two parameters `(engine_start, engine_dt)`:

`engine_start` is transmitted in a list, the engine start times are specified, <br>
`engine_dt` is transmitted in a list, the engine running time is specified. <br>
 <b> The positions in the list correspond to each other; </b>

 4. The `data` method allows you to work with tabular data (a table is a state matrix);

 5. The `plot` method - displays a graph, has the parameters:
- `radius_vector = False` by default. <br>
The parameter is responsible for displaying radius vectors; 
- `dot_engine_start = False` by default. <br>
The parameter is responsible for displaying the engine start points;

 6. The `plotly_graph` method - displays an interactive graph using the plotly library;
