# OrbitPy
Библиотека позволяет работать с околоземными орбитами: производить расчет элементов орбиты, визуализировать орбиту в плоскости и пространстве, анализировать траекторию движения c помощью табличных данных. Включает в себя два класса.

## Описание
- Класс `IntegrationConstants` позволяет получить все константы интегрирования (элементы орбиты), а также все вектора, характеризующие орбиту и положение КА:

    1. Вектора и их модули<br>

    $r$ - радиус-вектор, <br>
    $v$ - вектор скорости, <br>
    $\sigma (c)$ - вектор площадей, <br>
    $\lambda (f)$ - вектор Лапласа; <br>
    ```Python
        self.r = [x, y, z]
        self.v = [vx,vy,vz]
        self.c = [cx, cy, cz]
        self.f = [fx,fy,fz]

        self.R
        self.V
        self.C
        self.F
    ```
    2. Константы <br>

    $h$ - константа энергии ,<br>
    $p$ - фокальный параметр, <br>
    $e$ - эксцентриситет, <br>
    $i$ - наклонение, <br>
    $\Omega (Omega)$ - долгота восходящего узла, <br>
    $\omega (omega)$ - аргумент перигея, <br>
    $\nu (nu)$ - истинная аномалия, <br>
    $u$ - аргумент широты, <br>
    $t_\pi$ - время прохождения перигея; <br>
    ```Python
        self.h
        self.p
        self.e
        self.i
        self.Omega
        self.omega
        self.nu
        self.u
        self.tpi
    ```

 - Класс `Trajectory` позволяет построить переходную орбиту, после чего выполнить $n$ компланарных переходов между орбитами.

    Для упрощения работы выполнен графический интерфейс. Для работы с графическим интерфейсом достаточно скачать архив [`CoOrbits.rar`](https://drive.google.com/drive/folders/17P1J4EJGzzcqf8U4UE_4dyKV3q8pbJ0R?usp=share_link).

---
The library allows you to work with near-Earth orbits: calculate the elements of the orbit, visualize the orbit in the plane and in space, analyze the trajectory of movement by means of working with tabular data. It includes two classes.

- The `Integration Constants` class allows you to get all the integration constants (orbit elements), as well as all vectors characterizing the orbit and position of the spacecraft.
 - The `Trajectory` class allows you to build a transition orbit, and then perform n coplanar transitions between orbits.

    To simplify the work, a graphical interface has been created. To work with the graphical interface, it is enough to download the archive [`CoOrbits.rar`](https://drive.google.com/drive/folders/17P1J4EJGzzcqf8U4UE_4dyKV3q8pbJ0R?usp=share_link).

## Применение / Usage
Пример использования `Trajectory` - [тут](example_usage.ipynb) <br>
Пример совместного использования `Trajectory` и `IntegrationConstants` - [тут](example_connection.ipynb)

### IntegrationConstants <br>
При работе с классом выполняются шаги в данной последовательности:
1. Инициализация начальным радиусом-вектором и начальным вектором скорости, также можно указать начальный момент времени `t0=None - по-умолчанию` ;
```Python
    ic = IntegrationConstants(x=1500, y=-6700, z=-7900, vx=-8, vy=-1, vz=1, t0=21600)
    #или
    ic = IntegrationConstants(x=1500, y=-6700, z=-7900, vx=-8, vy=-1, vz=1)
```
2. Вызов метода `find` для нахождения всех элементов;
```Python
    ic.find()
```
Для взаимодействия с классом `Trajectory` необходимо задать одинаковые системы координат или же выполнить вращение системы координат класса `IntegrationConstants` до совмещения плоскости $xOy$ c плоскостью орбиты. Метод `to_2D` позволяет это сделать. Результатом его работы являются два плоских вектора - $[x,y,z], [v_x,v_y,v_z]$. Параметр `epsilon` определяет точность координат векторов. Их мы передаем в метод `Trajectory.trajectory` [(пример)](example_connection.ipynb).
```Python
    vect = ic.to_2D(epsilon=0.001)
    r = vect[0]
    v = vect[1]
```
---
When working with a class, the steps are performed in this sequence:
1. Initialization with the initial radius vector and the initial velocity vector, you can also specify the initial time `t0=None - by default`;
2. Calling the `find` method to find all the elements; 

To interact with the `Trajectory` class, it is necessary to set the same coordinate systems or rotate the coordinate system of the `IntegrationConstants` class to align the $xOy$ plane with the orbit plane. The `to_2D` method allows you to do this. The result of his work are two flat vectors - $[x,y,z], [v_x,v_y,v_z]$. The epsilon parameter determines the accuracy of the coordinates of the vectors. We pass them to the `Trajectory.trajectory` method [(example)](example_connection.ipynb).

### Trajectory<br>
При работе с классом выполняются шаги в данной последовательности [(пример)](example_usage.ipynb):
1. При инициализации вводится начальный, конечный моменты времени `(start, end)`, а также шаг интегрирования `(step)`. По-умолчанию: `start=0, end=100, step=1`;
```Python
    tj = Trajectory(start=0, end=100, step=1)
    #или
    tj = Trajectory()
```
2. Далее инициализируются параметры КА с РБ:

    `mass` - масса КА,<br>
    `mass_fuel `- масса топлива,<br>
    `dm `- массовый расход,<br>
    `abs_w` - модуль вектора скорости истечения газа из сопла;
```Python
    tj.spacecraft(mass=20_000, mass_fuel=15_000, dm=20, abs_w=3)
```
3. Далее необходимо задать компоненты начального радиуса-вектора $(x_0, y_0)$ и вектора скорости в начальный момент времени $(V_x, V_y)$ и два параметра `(engine_start, engine_dt)`: 

    `engine_start` передается списком, указываются моменты времени запуска двигателя, <br>
    `engine_dt` передается список, указывается время работы двигателя. <br>
    <b> Позиции в списке должны соответствовать друг другу; </b>
```Python
    tj.trajectory(x_0=6500,
                y_0=0,
                vx_0=0,
                vy_0=7.8,
                engine_start=[],
                engine_dt=[])
    #или
    tj.trajectory(x_0=6500,
                y_0=0,
                vx_0=0,
                vy_0=7.8)

```
4. Метод `data` позволяет работать с табличными данными (таблица - это матрица состояния);

5. Метод `plot` выводит график, имеет параметры:
- `radius_vector = False ` по-умолчанию. <br>
Параметр отвечает за отображение радиус-векторов,
- `dot_engine_start = False` по-умолчанию;<br>
    Параметр отвечает за отображение точек включения двигателя;

6. Метод `pplotly` выводит интерактивный график задействующий библиотеку plotly;
7. Метод `polar` выводит орбиту в полярных координатах, используя элементы орбиты $p,e$ [(пример)](example_connection.ipynb).

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
The parameter is responsible for displaying radius vectors,
- `dot_engine_start = False` by default. <br>
The parameter is responsible for displaying the engine start points;

 6. The `pplotly` method - displays an interactive graph using the plotly library;
 7. The `polar` method outputs the orbit in polar coordinates using the orbit elements $p,e$ [(check here)](example_connection.ipynb).