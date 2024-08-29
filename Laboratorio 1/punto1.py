"""
    Problema 1:
        Asignación de Tareas en un Equipo de Desarrollo Ágil

    Descripción:
        Un Scrum Master necesita asignar un conjunto de tareas
        a un equipo de desarrollo basado en la prioridad
        de las tareas y los puntos de historia asociados.
        El equipo consiste en 4 desarolladores, y la duración
        del sprint suele ser de 2 semanas. Por regla general
        cada desarollador no debe tener más de 13 puntos de
        historia asociados a ellos mismos. Con base a esta
        información realiza un modelo de optimización que tome
        las tareas que se pueden realizar en este sprint
        teniendo en cuenta que queremos maximiar la cantidad
        de tareas realizadas con la mayor prioridad.

    Nota:
        Para simplificar el problema, la restricción que se
        usará es que el número máximo de puntos no debe ser
        superior a los puntos máximos por trabajador
        multiplicado por el número de trabajadores
"""

from pyomo.environ import *
from pyomo.opt import SolverFactory
from matplotlib import pyplot as plt

# Datos
numeroDesarrolladores = 4
puntosMaximosPorDesarrollador = 13

puntosPorTarea = [5, 3, 13, 1, 21, 2, 2, 5, 8, 13, 21]

prioridadPorTarea = [
    "Maxima",
    "Media alta",
    "Alta",
    "Media baja",
    "Minima",
    "Media",
    "Alta",
    "Media",
    "Baja",
    "Maxima",
    "Alta"
]

valorPorPrioridad = {
    "Maxima": 7,
    "Alta": 6,
    "Media alta": 5,
    "Media": 4,
    "Media baja": 3,
    "Baja": 2,
    "Minima": 1
}

M = ConcreteModel()

# Definición de conjunto (11 tareas)
M.tareas = Var(RangeSet(0,10), domain=Binary)

# Función objetivo
M.obj = Objective(expr = sum(M.tareas[tarea] * valorPorPrioridad[prioridadPorTarea[tarea]] for tarea in M.tareas), sense=maximize)

# Restricciones
M.res = Constraint(expr = sum(M.tareas[tarea] * puntosPorTarea[tarea] for tarea in M.tareas) <= puntosMaximosPorDesarrollador * numeroDesarrolladores )

SolverFactory('glpk').solve(M)

M.display()

#Impresión
for tarea in M.tareas:
    if M.tareas[tarea]() == 1:
        print(f"La tarea {tarea + 1} fue elegida, con prioridad {prioridadPorTarea[tarea]} y {puntosPorTarea[tarea]} puntos.")

# Guardado
tareas = list(M.tareas)
tareasSeleccionadas = [M.tareas[tarea]() for tarea in M.tareas]

# Diagrama de barras
plt.bar(tareas, [sp * selec for sp, selec in zip(puntosPorTarea, tareasSeleccionadas)], color='blue', label='Tareas Seleccionadas')

plt.xlabel("Tareas")
plt.ylabel("Puntos de historia")
plt.title("Asignación de puntos de historia a tareas seleccionadas")
plt.xticks(tareas, [f"T{tarea}" for tarea in tareas])
plt.legend()
plt.show()
