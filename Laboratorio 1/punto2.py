"""
    Problema 2:
        Asignación de Trabajos a Trabajadores

    Descripción:
        En este problema, los estudiantes abordarán
        un problema básico de optimización
        combinatoria a través de la asignación de
        tareas a trabajadores. Un gerente necesita
        asignar trabajos a un conjunto de trabajadores,
        cada uno con un tiempo disponible. Cada trabajo
        tiene una ganancia asociada y un tiempo de
        realización. El objetivo es asignar los trabajos
        de manera que se maximice la ganancia total sin
        exceder el tiempo disponible para cada trabajador.

    Solución:
        @Author: ddi4z
"""

from pyomo.environ import *
from pyomo.opt import SolverFactory

# Datos del problema
horasDisponiblesPorTrabajador = [8, 10, 6]
gananciaPorTrabajo = [50, 60, 40, 70, 30]
tiempoPorTrabajo = [4, 5, 3, 6, 2]

# Creación del modelo
M = ConcreteModel()

# Definición de conjuntos (3 trabajadores y 5 tareas)
Trabajadores = RangeSet(0,2)
Tareas = RangeSet(0,4)
M.trabajadores = Trabajadores
M.tareas = Tareas

# Matriz de M.tareas x M.trabajadores
# 1 si la tarea i es asignada al trabajador j, 0 en otro caso
M.asignacion = Var(M.tareas, M.trabajadores, domain=Binary)

# Función objetivo
M.obj = Objective(expr=sum(M.asignacion[tarea,trabajador] * gananciaPorTrabajo[tarea] for tarea in M.tareas for trabajador in M.trabajadores), sense=maximize)

# Restricciones

# Cada tarea debe ser asignada a un único trabajador
M.unicidad = ConstraintList()
for tarea in M.tareas:
    M.unicidad.add(expr=sum(M.asignacion[tarea, trabajador] for trabajador in M.trabajadores) == 1)

# Cada trabajador no puede exceder su límite de horas
M.limiteHoras = ConstraintList()
for trabajador in M.trabajadores:
    M.limiteHoras.add(expr=sum(M.asignacion[tarea, trabajador] * tiempoPorTrabajo[tarea] for tarea in M.tareas) <= horasDisponiblesPorTrabajador[trabajador])

SolverFactory('glpk').solve(M)

M.display()

for trabajador in M.trabajadores:
    print(f"Trabajador {trabajador + 1}:")
    tiempo, ganancia = 0, 0
    for tarea in M.tareas:
        if M.asignacion[tarea, trabajador]() == 1:
            print(f"\tTarea {tarea + 1} con ganancia {gananciaPorTrabajo[tarea]} y tiempo {tiempoPorTrabajo[tarea]}")
            tiempo += tiempoPorTrabajo[tarea]
            ganancia += gananciaPorTrabajo[tarea]
    print(f"\n\tTiempo total: {tiempo} horas de {horasDisponiblesPorTrabajador[trabajador]} disponibles")
    print(f"\tGanancia total: {ganancia}\n")
