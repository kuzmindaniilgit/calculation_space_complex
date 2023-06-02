ru
Данный класс позволяет построить переходную орбиту, после чего выполнить n компланарных переходов между орбитами.
1. При инициализации вводится начальный, конечный моменты времени (start, end),
    а также шаг интегрирования (step);
2. Далее инициализируются параметры КА с РБ:
    mass - масса КА,
    mass_fuel - масса топлива,
    dm - массовый расход,
    abs_w - модуль вектора скорости истечения газа из сопла;
3. Далее необходимо задать компоненты начального радиуса-вектора (x_0, y_0) и вектора скорости (vx_0, vy_0)
    и два параметра (engine_start, engine_dt):
        engine_start передается списком, указываются моменты времени запуска двигателя,
        engine_dt передается список, указывается время работы двигателя.
        Позиции в списке соотвествуют друг другу;
4. Метод data позволяет работать с табличными данными (таблица - это матрица состояния);
5. Метод plot - выводит график, имеет параметры radius_vector = False по-умолчанию. 
    Параметр отвечает за отображение радиус-векторов; 
    А также параметр dot_engine_start = False по-умолчанию. 
    Параметр отвечает за отображение точек включения двигателя;
6. Метод plotly_graph - выводит интерактивный график задействующий библиотеку plotly ;

en
This class allows you to build a transition orbit, then perform n coplanar transitions between orbits.
 1. During initialization, the initial, final time points (start, end),
as well as the integration step (step) are entered;
 2. Next, the parameters of the spacecraft with US (upper stage) are initialized:
mass - mass of the spacecraft,
 mass_fuel - fuel mass,
dm - mass flow rate,
abs_w - modulus of the velocity vector of gas outflow from the nozzle;
 3. Next, you need to set the components of the initial radius-the vector (x_0, y_0) and the velocity vector (vx_0, vy_0)
and two parameters (engine_start, engine_dt):
engine_start is transmitted in a list, the engine start times are specified,
engine_dt is transmitted in a list, the engine running time is specified.
 The positions in the list correspond to each other;
 4. The data method allows you to work with tabular data (a table is a state matrix);
 5. The plot method - displays a graph, has the parameters radius_vector = False by default. 
The parameter is responsible for displaying radius vectors; 
And also the dot_engine_start = False parameter by default. 
The parameter is responsible for displaying the engine start points;
 6. The plotly_graph method - displays an interactive graph using the plotly library;
