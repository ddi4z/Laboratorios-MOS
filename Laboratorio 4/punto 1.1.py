"""
** Integrantes - Grupo 15 **

Daniel Felipe Diaz Moreno y Sara Sofía Cárdenas Rodríguez

Script que calcula el Frente de Pareto (metodo de e-constraint) de dos funciones 
objetivo del modelo matematico.

"""

##############################################################################
#####################        LIBRERÍAS        ################################
##############################################################################

# Plot Imports
import matplotlib.pyplot as plt

# Pyomo Imports (Modelo Matemático)
from pyomo.environ import *
from pyomo.opt import SolverFactory

##############################################################################
#####################        FUNCIONES        ################################
##############################################################################

# Función eliminar componente
def delete_component(Model, comp_name):
    list_del = [vr for vr in vars(Model)
                if comp_name == vr
                or vr.startswith(comp_name + '_index')
                or vr.startswith(comp_name + '_domain')]

    list_del_str = ', '.join(list_del)
    print('Deleting model components ({}).'.format(list_del_str))

    for kk in list_del:
        Model.del_component(kk)

##############################################################################
#####################        MODELO           ################################
##############################################################################

# Configuración Iteraciones --------------------------------------------------
# ACTUALIZACIÓN: A diferencia del script anterior, en este caso solo es necesario almacenar un epsilon por cada posible valor maximo de número de nodos.
epsilons = [i for i in reversed(range(1,6))]

# Creación Modelo ------------------------------------------------------------
Model = ConcreteModel()

# Conjuntos y parámetros -----------------------------------------------------
numNodes = 5
Model.N = RangeSet(1, numNodes)

# Saltos (Hops) --------------------------------------------------------------
Model.h = Param(Model.N, Model.N, mutable=True)

for i in Model.N:
    for j in Model.N:
        Model.h[i,j] = 999

Model.h[1,2] = 1
Model.h[1,3] = 1
Model.h[2,5] = 1
Model.h[3,4] = 1
Model.h[4,5] = 1

# Costos ---------------------------------------------------------------------
Model.c = Param(Model.N, Model.N, mutable=True)

for i in Model.N:
    for j in Model.N:
        Model.c[i,j] = 999

Model.c[1,2] = 10
Model.c[1,3] = 5
Model.c[2,5] = 10
Model.c[3,4] = 5
Model.c[4,5] = 5

# Nodo origen y destino ------------------------------------------------------
s = 1
d = 5

# Variables de decisión ------------------------------------------------------

#X: Variable binaria que indica si el enlace (i,j) es seleccionado para hacer  
# parte del camino que va del nodo fuente al nodo destino.

Model.x = Var(Model.N, Model.N, domain=Binary)


# Funciones objetivo ---------------------------------------------------------

# Función de saltos (hops)
Model.f1 = sum(Model.x[i,j] * Model.h[i,j] for i in Model.N for j in Model.N)

# Función de costos
Model.f2 = sum(Model.x[i,j] * Model.c[i,j] for i in Model.N for j in Model.N)

# Proceso para ejecutar varias veces el modelo matemático con el fin de aplicar
# el método de e-constraint ---------------------------------------------------

f1_vec=[]
f2_vec=[]

for epsilon in epsilons:
    # Función objetivo general
    Model.O_z = Objective(expr= Model.f2, sense=minimize)

    # Restricción nodo origen
    def source_rule(Model,i):
        if i==s:
            return sum(Model.x[i,j] for j in Model.N) == 1
        else:
            return Constraint.Skip

    Model.source=Constraint(Model.N, rule=source_rule)

    # Restricción nodo destino
    def destination_rule(Model,j):
        if j==d:
            return sum(Model.x[i,j] for i in Model.N) == 1
        else:
            return Constraint.Skip

    Model.destination=Constraint(Model.N, rule=destination_rule)

    # Restricción nodo intermedio
    def intermediate_rule(Model,i):
        if i!=s and i!=d:
            return sum(Model.x[i,j] for j in Model.N) - sum(Model.x[j,i] for j in Model.N) == 0
        else:
            return Constraint.Skip

    Model.intermediate=Constraint(Model.N, rule=intermediate_rule)

    # Restricción de saltos (hops)
    # ACTUALIZACIÓN: Esta es una nueva restricción que restringe el número de saltos
    Model.hops = Constraint(expr=Model.f1 <= epsilon)

    # Resolución del modelo
    SolverFactory('glpk').solve(Model)
    valorF1 = value(Model.f1)
    valorF2 = value(Model.f2)
    f1_vec.append(valorF1)
    f2_vec.append(valorF2)

    # Borrado de componentes
    delete_component(Model, 'O_z')
    delete_component(Model, 'source')
    delete_component(Model, 'destination')
    delete_component(Model, 'intermediate')
    # ACTUALIZACIÓN: Se elimina la restricción de saltos (hops)
    delete_component(Model, 'hops')
    # Termina el ciclo

# Gráfica Pareto  ------------------------------------------------------------
plt.plot(f1_vec, f2_vec, 'o-.')
plt.title('Frente óptimo de Pareto')
plt.xlabel('F1')
plt.ylabel('F2')
plt.grid(True)
plt.show()
