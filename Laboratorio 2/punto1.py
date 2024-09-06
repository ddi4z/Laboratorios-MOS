import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from pyomo.environ import *
from pyomo.opt import SolverFactory

# Función que crea los grafos de las ciudades
def crearGrafos(M):
    # Se obtienen los resultados
    resultadosBogota = [M.toneladasDesdeBogota[ciudad].value for ciudad in M.ciudades]
    resultadosMedellin = [M.toneladasDesdeMedellin[ciudad].value for ciudad in M.ciudades]
    resultadosTotales = [resultadosBogota[i] + resultadosMedellin[i] for i in range(len(resultadosBogota))]

    # Se crean los grafos
    G_bogota = nx.DiGraph()
    G_medellin = nx.DiGraph()
    G_resumen = nx.DiGraph()
    G_bogota.add_node("Bogotá")
    G_medellin.add_node("Medellín")
    G_resumen.add_node("Bogotá y Medellín")

    # Se agregan los nodos y aristas
    for i, ciudad in enumerate(ciudadPorIndice):
        G_bogota.add_node(ciudad)
        G_bogota.add_edge("Bogotá", ciudad, weight = resultadosBogota[i])
        G_medellin.add_node(ciudad)
        G_medellin.add_edge("Medellín", ciudad, weight = resultadosMedellin[i])
        G_resumen.add_node(ciudad)
        G_resumen.add_edge("Bogotá y Medellín", ciudad, weight = resultadosTotales[i])
    return G_bogota, G_medellin, G_resumen

# Función que grafica un grafo con los costos de transporte desde una ciudad
def graficarGrafo(G, ax, titulo, color):
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels = True, ax = ax, node_color = color, node_size = 2000, font_size = 10, font_weight = 'bold', arrows = True)
    nx.draw_networkx_edge_labels(G, pos, edge_labels = {(u, v): int(d["weight"]) for u, v, d in G.edges(data = True)}, ax = ax)
    ax.set_title(titulo)


# Función que grafica el número de toneladas que se envían desde Bogotá y Medellín a cada ciudad
def graficarCostos(G_bogota, G_medellin, G_resumen):
    fig, ax = plt.subplots(1, 3, figsize = (14, 7))
    graficarGrafo(G_bogota, ax[0], "Distribución desde Bogotá", "lightblue")
    graficarGrafo(G_medellin, ax[1], "Distribución desde Medellín", "gold")
    graficarGrafo(G_resumen, ax[2], "Distribución total", "yellow")
    plt.show()


# Muestra la solución del modelo
def obtenerSolucion(M):
    SolverFactory('glpk').solve(M)
    M.display()
    G_bogota, G_medellin, G_resumen = crearGrafos(M)
    graficarCostos(G_bogota, G_medellin, G_resumen)

# Creación del modelo
M = ConcreteModel()


# Datos de entrada

# Ciudades origen
# Bogota
M.ofertaBogota = Param(within = NonNegativeIntegers, default = 550)
costosTrasporteBogota = [1e8, 2.5, 1.6, 1.4, 0.8, 1.4]

# Medellin
M.ofertaMedellin = Param(within = NonNegativeIntegers, default = 700)
costosTrasporteMedellin = [2.5, 1e8, 2.0, 1.0, 1.0, 0.8]

# Ciudades destino
demandaPorCiudad = [125, 175, 225, 250, 225,200]
ciudadPorIndice = ["Cali", "Barranquilla", "Pasto", "Tunja", "Chía", "Manizales"]
M.cantidadCiudades = Param(within = NonNegativeIntegers, default = len(demandaPorCiudad))
M.ciudades = RangeSet(0, M.cantidadCiudades - 1)

# Variables
M.toneladasDesdeBogota = Var(M.ciudades, domain = NonNegativeIntegers)
M.toneladasDesdeMedellin = Var(M.ciudades, domain = NonNegativeIntegers)

# Función objetivo: Minimizar el costo total de transporte
M.obj = Objective(expr = sum(M.toneladasDesdeBogota[ciudad] * costosTrasporteBogota[ciudad] for ciudad in M.ciudades) + sum(M.toneladasDesdeMedellin[ciudad] * costosTrasporteMedellin[ciudad] for ciudad in M.ciudades), sense=minimize)

# Restricciones

# Todas las ciudades deben recibir la cantidad de toneladas que demandan
M.demandaPorCiudad = ConstraintList()
for ciudad in M.ciudades:
    M.demandaPorCiudad.add(expr = M.toneladasDesdeBogota[ciudad] + M.toneladasDesdeMedellin[ciudad] == demandaPorCiudad[ciudad])

# No se puede enviar más toneladas de las que se tienen disponibles
M.ofertaDesdeBogota = Constraint(expr = sum(M.toneladasDesdeBogota[ciudad] for ciudad in M.ciudades) <= M.ofertaBogota)
M.ofertaDesdeMedellin = Constraint(expr = sum(M.toneladasDesdeMedellin[ciudad] for ciudad in M.ciudades) <= M.ofertaMedellin)

obtenerSolucion(M)



