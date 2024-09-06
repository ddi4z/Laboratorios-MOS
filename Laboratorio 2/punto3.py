import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from pyomo.environ import *
from pyomo.opt import SolverFactory


# Función que carga los archivos de datos y los retorna en un diccionario
def cargarArchivos():
    informacion = {}
    informacion["comunicaciones"] = pd.read_csv("Laboratorio 2/communication_costs.csv", delimiter = ',')
    informacion["energias"] = pd.read_csv("Laboratorio 2/energy_consumption.csv", delimiter = ',')
    informacion["instalaciones"] = pd.read_csv("Laboratorio 2/installation_costs.csv", delimiter = ',')
    informacion["ubicaciones"] = pd.read_csv("Laboratorio 2/locations.csv", delimiter = ',')
    informacion["coberturas"] = pd.read_csv("Laboratorio 2/sensor_coverage.csv", delimiter = ',')
    informacion["nombreSensores"] = pd.read_csv("Laboratorio 2/sensors.csv", delimiter = ',').columns
    informacion["nombreSensores"] = {i: informacion["nombreSensores"][i] for i in range(len(informacion["nombreSensores"]))}
    informacion["idSensores"] = informacion["energias"]["SensorType"]
    informacion["ubicacionPorId"] = {i: informacion["ubicaciones"].columns[i] for i in range(len(informacion["ubicaciones"].columns))}
    return informacion

# Función que lee los datos del archivo zone_coverage.csv y los retorna en una lista de nodos y una matriz de adyacencia
def obtenerDatosDeArchivo():
    df = pd.read_csv("Laboratorio 2/zone_coverage.csv", header = None, delimiter = ',')
    matriz = df.iloc[1:].astype(int).values
    return matriz

# Función que grafica la solución del problema como un grafo
def graficarSolucion(M, matrizDeAdyacencia, informacion):
    grafo = nx.DiGraph()
    coloresPorSensor = ["yellow", "red", "blue"]
    leyenda_colores = {informacion["nombreSensores"][i]: coloresPorSensor[i] for i in range(len(coloresPorSensor))}
    leyenda_colores["No sensor"] = "gray"

    # Se crean los nodos del grafo dependiendo el color del sensor
    for ubicacion in M.ubicaciones:
        tieneSensor = False
        for sensor in M.sensores:
            if M.asignacion[sensor, ubicacion].value == 1:
                grafo.add_node(informacion["ubicacionPorId"][ubicacion], color = coloresPorSensor[sensor])
                tieneSensor = True
        if not tieneSensor:
            grafo.add_node(informacion["ubicacionPorId"][ubicacion], color = "gray")

    # Se crean las aristas del grafo
    for ubicacionU in range(len(matrizDeAdyacencia)):
        for ubicacionV in range(len(matrizDeAdyacencia[ubicacionU])):
            if ubicacionU != ubicacionV and matrizDeAdyacencia[ubicacionU][ubicacionV] == 1:
                grafo.add_edge(informacion["ubicacionPorId"][ubicacionU], informacion["ubicacionPorId"][ubicacionV])
    pos = nx.spring_layout(grafo)

    # Dibuja el grafo con los colores de los nodos
    nx.draw(grafo, pos, with_labels = True,
            node_color = [grafo.nodes[nodo]["color"] for nodo in grafo.nodes],
            node_size = 2000, font_size = 10, font_weight = 'bold', arrows = True)

    # Añade las convenciones al gráfico
    handles = [plt.Line2D([0], [0], marker='o', color = 'w', markerfacecolor = color, markersize = 15, label = label)
               for label, color in leyenda_colores.items()]
    plt.legend(handles = handles, loc = "best", title = "Legends")
    plt.show()

# Función que obtiene la solución del problema
def obtenerSolucion(M, matrizDeAdyacencia,informacion):
    SolverFactory('glpk').solve(M)
    M.display()
    graficarSolucion(M, matrizDeAdyacencia, informacion)

# Obtención de los datos de los archivos
informacion = cargarArchivos()
matrizDeAdyacencia = obtenerDatosDeArchivo()

# Creación del modelo
M = ConcreteModel()

# Conjuntos del modelo
M.sensores = RangeSet(0, len(informacion["idSensores"]) - 1)
M.ubicaciones = RangeSet(0, len(informacion["ubicaciones"].columns) - 1)

# Variable de decisión del modelo
M.asignacion = Var(M.sensores, M.ubicaciones, domain = Binary)

# Calcula el costo de energía total al implementar los n sensores de distintos tipos
def costoEnergia():
    return sum(informacion["energias"]["EnergyConsumption"][sensor] * sum(M.asignacion[sensor, ubicacion] for ubicacion in M.ubicaciones) for sensor in M.sensores)

# Calcula el costo de comunicación total al implementar los n sensores de distintos tipos
def costoComunicacion():
    return sum(informacion["comunicaciones"]["CommunicationCost"][sensor * len(informacion["ubicaciones"]) + ubicacion] * M.asignacion[sensor, ubicacion] for sensor in M.sensores for ubicacion in M.ubicaciones)

# Calcula el costo de instalación total al implementar los n sensores de distintos tipos
def costoInstalacion():
    return sum(informacion["instalaciones"]["InstallationCost"][ubicacion] * sum(M.asignacion[sensor, ubicacion] for sensor in M.sensores) for ubicacion in M.ubicaciones)

# Función objetivo: Minimizar la suma de los costos de energía, comunicación e instalación
M.objetivo = Objective(expr = costoEnergia() + costoComunicacion() + costoInstalacion(), sense = minimize)

# Restricciones del modelo

# Solo se puede asignar un tipo de sensor a una ubicación
M.unicidad = ConstraintList()
for ubicacion in M.ubicaciones:
    M.unicidad.add(expr = sum(M.asignacion[sensor, ubicacion] for sensor in M.sensores) <= 1)

# Se deben asignar los sensores en las ubicaciones válidas según el archivo sensor_coverage.csv
M.ubicacionesValidas = ConstraintList()
for sensor in M.sensores:
    for ubicacion in M.ubicaciones:
        M.ubicacionesValidas.add(expr = M.asignacion[sensor, ubicacion] <= informacion["coberturas"][f"S{sensor+1}"][ubicacion])

# Se deben cubrir todas las ubicaciones
M.cobertura = ConstraintList()
for ubicacionU in M.ubicaciones:
    M.cobertura.add(expr = sum(matrizDeAdyacencia[ubicacionU][ubicacionV] * sum(M.asignacion[sensor,ubicacionV] for sensor in M.sensores) for ubicacionV in M.ubicaciones) >= 1)

obtenerSolucion(M, matrizDeAdyacencia, informacion)