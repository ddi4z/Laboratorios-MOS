import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from pyomo.environ import *
from pyomo.opt import SolverFactory

# Función que lee los datos del archivo proof_case.csv y los retorna en una lista de nodos y una matriz de adyacencia
def obtenerDatosDeArchivo():
    df = pd.read_csv("Laboratorio 2/proof_case.csv", header = None, delimiter = ',')
    nodos = df.iloc[0].astype(int)
    matriz = df.iloc[1:].astype(float).values
    return nodos, matriz

# Función que crea un grafo de la solución del MTSP
def crearGrafoDeSolucion(M, nodos):
    grafo = nx.DiGraph()
    for nodo in nodos:
        grafo.add_node(nodo)
    for i in M.nodos:
        for j in M.nodos:
            if M.asignacion[i, j].value == 1:
                grafo.add_edge(i, j, color = 'blue')
    return grafo

# Función que grafica la solución del MTSP
def graficarMTSP(grafo):
    pos = nx.spring_layout(grafo)
    plt.figure()
    nx.draw(grafo, pos, edge_color='blue', with_labels=True, node_size=500, node_color='lightblue')
    plt.title(f"El costo total del MTSP es: {M.objetivo()}")
    plt.show()

# Función que obtiene la solución del MTSP
def obtenerSolucion(M, nodos):
    SolverFactory('glpk').solve(M)
    M.display()
    grafo = crearGrafoDeSolucion(M, nodos)
    graficarMTSP(grafo)

# Obtención de los datos del archivo
nodos, matrizDeAdyacencia = obtenerDatosDeArchivo()

# Creación del modelo
M = ConcreteModel()

# Parámetros del modelo
M.numeroDeNodos = Param(within = PositiveIntegers, default = len(nodos))
M.equipos = Param(within = PositiveIntegers, default = 3)

# Conjuntos del modelo
M.nodos = RangeSet(0, M.numeroDeNodos - 1)

# Variables de decisión del modelo
M.asignacion = Var(M.nodos, M.nodos, domain = Binary)
M.posicion = Var(M.nodos, domain = NonNegativeIntegers)

# Función objetivo: Minimizar la suma de los arcos seleccionados
M.objetivo = Objective(expr = sum(M.asignacion[i, j] * matrizDeAdyacencia[i, j] for i in M.nodos for j in M.nodos), sense=minimize)

# Restricciones del modelo

# No se puede ir de un nodo a sí mismo (autociclos)
M.autociclo = ConstraintList()
for i in M.nodos:
    M.autociclo.add(expr = M.asignacion[i, i] == 0)

# Si hay e equipos, entonces deben haber e arcos seleccionados que empiecen en el nodo 0
M.equiposSalientes = Constraint(expr = sum(M.asignacion[0, j] for j in M.nodos) == M.equipos)

# Si hay e equipos que salen del nodo 0, entonces debe haber e equipos que entran al nodo 0
M.equiposEntrantes = Constraint(expr = sum(M.asignacion[i, 0] for i in M.nodos) == M.equipos)

# Se debe entrar una vez en cada nodo
M.unicaEntrada = ConstraintList()
for j in M.nodos:
    if j != 0:
        M.unicaEntrada.add(expr = sum(M.asignacion[i, j] for i in nodos) == 1)

# Se debe salir una vez de cada nodo
M.unicaSalida = ConstraintList()
for i in M.nodos:
    if i != 0:
        M.unicaSalida.add(expr = sum(M.asignacion[i, j] for j in nodos) == 1)

# Eliminacion de subtours
M.subtours = ConstraintList()
for i in M.nodos:
    for j in M.nodos:
        if i != j and min(i, j) != 0:
            M.subtours.add(expr = M.posicion[i] - M.posicion[j] + M.numeroDeNodos * M.asignacion[i, j] <= M.numeroDeNodos - 1)

obtenerSolucion(M, nodos)