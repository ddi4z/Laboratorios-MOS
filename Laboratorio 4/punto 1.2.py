"""
** Integrantes - Grupo 15 **

Daniel Felipe Diaz Moreno y Sara Sofía Cárdenas Rodríguez

Script que implementa el método Simplex de forma tabulada para resolver el 
problema de Woodcarving. Este código emplea el método Simplex para maximizar
una función objetivo lineal, sujeta a restricciones lineales.

"""

class Simplex:

    """
        Inicializa los datos necesarios para el algoritmo Simplex
        Parámetros:
        - coeficientes: lista de coeficientes de la función objetivo (negativos para maximización)
        - restricciones: matriz con los coeficientes de las restricciones
        - soluciones: lista con los valores en el lado derecho de las desigualdades de restricción
    """
    def __init__(self, coeficientes, restricciones, soluciones):
        self.coeficientes = coeficientes
        self.restricciones = restricciones
        self.soluciones = soluciones
        # Dimensiones de la tabla
        self.m, self.n = len(restricciones), len(restricciones[0])  
        # Tabla del método simplex, inicializada más adelante
        self.tabla = []

    """
        Inicializa la tabla del Simplex con las restricciones y coeficientes de la función objetivo
        Agrega variables de holgura para convertir las desigualdades en igualdades
    """
    def inicializarTabla(self):
        # Expandimos cada restricción con variables de holgura (una por restricción)
        restriccionesAmpliadas = [fila + [0] * self.m for fila in self.restricciones]
        for i in range(self.m):
            # Agrega 1 en la posición de la variable de holgura
            restriccionesAmpliadas[i][self.n + i] = 1
        # Agrega los términos independientes (lado derecho de las restricciones) y la función objetivo
        self.tabla = [restriccionesAmpliadas[i] + [self.soluciones[i]] for i in range(self.m)]
        # Agrega la fila de la función objetivo al final de la tabla
        self.tabla.append(self.coeficientes + [0] * (self.m + 1))

    """
        Encuentra la columna pivote, que corresponde a la variable que más incrementará
        la función objetivo si aumenta. Selecciona la columna con el valor más negativo.
    """
    def obtenerColumnaPivote(self):
        return self.tabla[-1].index(min(self.tabla[-1][:-1])) # Columna con valor mínimo

    """
        Encuentra la fila pivote utilizando la razón mínima. Divide el término independiente
        entre el valor en la columna pivote para cada fila, eligiendo la menor razón positiva.
    """
    def obtenerFilaPivote(self, columnaPivote):
        # Se evitan las divisiones por cero
        divisiones = [(self.tabla[i][-1] / self.tabla[i][columnaPivote]
                      if self.tabla[i][columnaPivote] > 0 else float('inf')) for i in range(self.m)] 
        return divisiones.index(min(divisiones)) # Fila con la menor razón positiva

    """
        Realiza el proceso de pivoteo para hacer 1 el valor en la posición pivote
        y 0 en el resto de la columna. Ajusta la tabla en base a esta operación.
    """
    def realizarPivoteo(self, filaPivote, columnaPivote):
        # Divide la fila pivote por el valor del pivote para que sea 1
        pivote = self.tabla[filaPivote][columnaPivote]
        self.tabla[filaPivote] = [x / pivote for x in self.tabla[filaPivote]]
        # Hace 0 en el resto de la columna pivote para las otras filas
        for i in range(self.m + 1):
            if i != filaPivote:
                cociente = self.tabla[i][columnaPivote]
                self.tabla[i] = [self.tabla[i][j] - cociente * self.tabla[filaPivote][j] for j in range(self.n + self.m + 1)]

    """
        Verifica si la solución actual es óptima. La solución es óptima si no hay
        valores negativos en la fila de la función objetivo.
    """
    def esOptimo(self):
        return min(self.tabla[-1][:-1]) >= 0 # Verifica si todos los valores son no negativos

    """
        Extrae la solución óptima de la tabla. Si una variable básica aparece en una columna,
        se toma el valor en la columna de términos independientes como su valor en la solución.
    """
    def obtenerSolucion(self):
        solucionOptima = [0] * self.n
        for i in range(self.m):
            if self.tabla[i].index(1) < self.n:
                solucionOptima[self.tabla[i].index(1)] = self.tabla[i][-1]
        return solucionOptima  # Lista con los valores óptimos de las variables

    """
        Obtiene el valor máximo de la función objetivo a partir de la última posición de la tabla.
    """
    def obtenerValorMaximo(self):
        return self.tabla[-1][-1] # Valor en el extremo derecho de la fila de la función objetivo

    """
        Resuelve el problema de optimización utilizando el método Simplex.
        Itera hasta que se alcanza la solución óptima.
    """
    def resolver(self):
        # Configura la tabla inicial
        self.inicializarTabla() 
        # Repite hasta que la solución sea óptima
        while not self.esOptimo():
            columnaPivote = self.obtenerColumnaPivote()
            filaPivote = self.obtenerFilaPivote(columnaPivote)
            self.realizarPivoteo(filaPivote, columnaPivote)
        # Retorna la solución óptima y el valor máximo de la función objetivo
        solucionOptima = self.obtenerSolucion()
        valorMaximo = self.obtenerValorMaximo()
        return solucionOptima, valorMaximo

"""
    Define el problema específico y utiliza la clase Simplex para resolverlo.
"""
def main():
    # Información del problema
    # Maximizar: 3x1 + 2x2 -> Coeficientes de la función objetivo
    coeficientes = [-3, -2]
    # Sujeto a:
    #     2x1 + x2 <= 100 -> Restricción 1 y Solución 1 (Lado derecho)
    #     x1 + x2 <= 80 -> Restricción 2 y Solución 2 (Lado derecho)
    #     x1 <= 40 -> Restricción 3 y Solución 3 (Lado derecho)
    #     x1 >= 0, x2 >= 0 -> Restricciones de no negatividad
    restricciones = [
        [2, 1],
        [1, 1],
        [1, 0]
    ]
    soluciones = [100, 80, 40]

    # Resolución del problema
    simplex = Simplex(coeficientes, restricciones, soluciones)
    solucionOptima, valorMaximo = simplex.resolver()

    # Muestra de los resultados
    print("Solución óptima:", solucionOptima)
    print("Valor máximo de Z:", valorMaximo)

if __name__ == "__main__":
    main()