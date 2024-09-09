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
    etiquetasSensoresAsignados = {}
    colores = []

    # Se crean los nodos del grafo y se añaden todos los sensores asignados a cada ubicación
    for ubicacion in M.ubicaciones:
        sensores_en_ubicacion = []
        for sensor in M.sensores:
            if M.asignacion[sensor, ubicacion].value == 1:
                sensores_en_ubicacion.append(informacion["nombreSensores"][sensor])
        sensores_en_ubicacion.sort()

        # Definir las etiquetas y colores de los nodos según si tienen o no sensores asignados
        if sensores_en_ubicacion:
            etiquetasSensoresAsignados[informacion["ubicacionPorId"][ubicacion]] = '\n'.join(sensores_en_ubicacion)
            colores.append('lightgreen')
        else:
            etiquetasSensoresAsignados[informacion["ubicacionPorId"][ubicacion]] = "No sensor"
            colores.append('lightcoral')
        grafo.add_node(informacion["ubicacionPorId"][ubicacion])

    # Se crean las aristas del grafo
    for ubicacionU in range(len(matrizDeAdyacencia)):
        for ubicacionV in range(len(matrizDeAdyacencia[ubicacionU])):
            if ubicacionU != ubicacionV and matrizDeAdyacencia[ubicacionU][ubicacionV] == 1:
                grafo.add_edge(informacion["ubicacionPorId"][ubicacionU], informacion["ubicacionPorId"][ubicacionV])

    pos = nx.spring_layout(grafo)
    pos_etiquetas = {nodo: (x, y + 0.1) for nodo, (x, y) in pos.items()}
    plt.figure(figsize=(15, 10))
    nx.draw(grafo, pos, with_labels=True, node_size=2000, font_size=10, font_weight='bold', arrows=True, node_color=colores)
    nx.draw_networkx_labels(grafo, pos_etiquetas, labels=etiquetasSensoresAsignados, font_size=10, font_color='black')

    # Añadir convenciones (leyenda)
    from matplotlib.lines import Line2D
    legend_elements = [Line2D([0], [0], marker='o', color='w', label='Con sensor', markersize=10, markerfacecolor='lightgreen'),
                       Line2D([0], [0], marker='o', color='w', label='Sin sensor', markersize=10, markerfacecolor='lightcoral')]
    plt.legend(handles=legend_elements, loc='best', fontsize=12)
    plt.title(f"Costo total: {M.objetivo()}", fontsize=14)
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
# Se deben cubrir todas las ubicaciones usando solo sensores validos
M.cobertura = ConstraintList()
for ubicacionU in M.ubicaciones:
    M.cobertura.add(expr = sum(matrizDeAdyacencia[ubicacionU][ubicacionV] * sum(informacion["coberturas"][f"S{sensor+1}"][ubicacionU] * M.asignacion[sensor,ubicacionV] for sensor in M.sensores) for ubicacionV in M.ubicaciones) >= 1)

obtenerSolucion(M, matrizDeAdyacencia, informacion)