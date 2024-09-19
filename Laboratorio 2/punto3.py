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

# Función que grafica la solución del problema para cada sensor con sus respectivas ubicaciones
def graficarSolucion(M, matrizDeAdyacencia, informacion):
    colorPorTipoSensor = ["red", "green", "blue"]
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    for sensor in M.sensores:
        G = nx.DiGraph()
        for u in M.ubicaciones:
            for v in M.ubicaciones:
                if u != v and matrizDeAdyacencia[u][v] == 1:
                    if M.asignacion[sensor, u]() == 1 and informacion["coberturas"][f"S{sensor+1}"][v] == 1:
                        G.add_edge(u + 1, v + 1, color = colorPorTipoSensor[sensor])
                    else:
                        G.add_edge(u + 1, v + 1, color = 'gray')
        coloresNodo = []
        for u in G.nodes():
            if M.asignacion[sensor, u - 1]() == 1:
                coloresNodo.append(colorPorTipoSensor[sensor])
            else:
                coloresNodo.append('lightgray')
        coloresArcos = [G[u][v]['color'] for u, v in G.edges]
        pos = nx.spring_layout(G)
        nx.draw(G, pos, ax=axes[sensor], node_color = coloresNodo, edge_color = coloresArcos, with_labels = True, node_size = 500, font_weight = 'bold', arrows = True)
        axes[sensor].set_title(f"Sensor: s{sensor+1}", fontsize=15)
    plt.tight_layout()
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
    return sum(sum(informacion["energias"]["EnergyConsumption"][sensor] * M.asignacion[sensor, ubicacion] for sensor in M.sensores) for ubicacion in M.ubicaciones)

# Calcula el costo de comunicación total al implementar los n sensores de distintos tipos
def costoComunicacion():
    return sum(sum(informacion["comunicaciones"]["CommunicationCost"][sensor * len(informacion["ubicaciones"]) + ubicacion] * M.asignacion[sensor, ubicacion] for ubicacion in M.ubicaciones) for sensor in M.sensores)

# Calcula el costo de instalación total al implementar los n sensores de distintos tipos
def costoInstalacion():
    return sum(sum(informacion["instalaciones"]["InstallationCost"][ubicacion] * M.asignacion[sensor, ubicacion] for ubicacion in M.ubicaciones) for sensor in M.sensores)

# Función objetivo: Minimizar la suma de los costos de energía, comunicación e instalación
M.objetivo = Objective(expr = costoEnergia() + costoComunicacion() + costoInstalacion(), sense = minimize)

# Restricciones del modelo
# Se deben cubrir todas las ubicaciones garantizando que se cuente con todos los sensores necesarios por ubicación
M.cobertura = ConstraintList()
for ubicacionU in M.ubicaciones:
    for sensor in M.sensores:
        M.cobertura.add(expr = sum(matrizDeAdyacencia[ubicacionU][ubicacionV] * M.asignacion[sensor,ubicacionV] for ubicacionV in M.ubicaciones) >= informacion["coberturas"][f"S{sensor+1}"][ubicacionU])

obtenerSolucion(M, matrizDeAdyacencia, informacion)