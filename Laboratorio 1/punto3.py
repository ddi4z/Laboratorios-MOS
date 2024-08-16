"""
    Problema 3:
        Problema Complejo de Misión Humanitaria en Zambia

    Descripción:
        Este problema está basado en un caso real de una misión
        humanitaria en Zambia. En respuesta a una crisis
        humanitaria, SenecaLibre ha sido comisionada para
        coordinar el transporte de recursos esenciales mediante
        una flota de aviones. Cada avión tiene una capacidad
        específica en peso y volumen, y cada recurso tiene
        características propias que incluyen peso, volumen y un
        nivel de importancia para la misión. El objetivo es
        maximizar la importancia total de los recursos
        transportados, respetando las limitaciones de los
        aviones y algunas restricciones logísticas y de seguridad.

    Solución:
        @Author: ddi4z
"""

from pyomo.environ import *
from pyomo.opt import SolverFactory

M = ConcreteModel()

# Datos
    # Recursos
nombrePorRecurso = ["Alimentos Básicos", "Medicinas", "Equipos Médicos", "Agua Potable", "Mantas" ]
valorPorRecurso = [50, 100, 120, 60, 40]
pesoPorRecurso = [15, 5, 20, 18, 10]
volumenPorRecurso = [8, 2, 10, 12, 6]
    # Aviones
pesoPorAvion = [30, 40, 50]
volumenPorAvion = [25, 30, 35]

# Definición de conjuntos (5 recursos y 3 aviones)
M.recursos = RangeSet(0,4)
M.aviones = RangeSet(0,2)

# Matriz de M.recursos x M.aviones
M.asignacion = Var(M.recursos, M.aviones, domain=Binary)

# Función objetivo
M.obj = Objective(expr=sum(M.asignacion[i,j] * valorPorRecurso[i] for i in M.recursos for j in M.aviones), sense=maximize)

# Restricciones

# Cada recurso debe ser asignado a un único avión
M.unicidad = ConstraintList()
for i in M.recursos:
    M.unicidad.add(expr=sum(M.asignacion[i, j] for j in M.aviones) == 1)

# Cada avión no puede exceder su límite de peso ni de volumen
M.limitePeso = ConstraintList()
M.limiteVolumen = ConstraintList()
for j in M.aviones:
    M.limitePeso.add(expr=sum(M.asignacion[i,j] * pesoPorRecurso[i] for i in M.recursos) <= pesoPorAvion[j])
    M.limiteVolumen.add(expr=sum(M.asignacion[i,j] * volumenPorRecurso[i] for i in M.recursos) <= volumenPorAvion[j])


"""
    Restricciones de Almacenamiento de Recursos:
        Seguridad de Medicamentos:
            No se puede transportar a las Medicinas en el Avión 1
            por la falta de condiciones para mantener la
            temperatura controlada, crucial para la efectividad
            de los medicamentos.

        Compatibilidad de Equipos Médicos y Agua Potable:
            Los Equipos Médicos y el Agua Potable no pueden ser transportados en el mismo avión debido al riesgo de contaminación cruzada. El derrame de agua podría dañar los equipos médicos delicados.
"""


SolverFactory('glpk').solve(M)

M.display()

for avion in M.aviones:
    print(f"Avión {avion + 1}:")
    for recurso in M.recursos:
        if M.asignacion[recurso, avion]() == 1:
            print(f"\tRecurso {nombrePorRecurso[recurso]} con valor {valorPorRecurso[recurso]}, peso {pesoPorRecurso[recurso]} y volumen {volumenPorRecurso[recurso]}")