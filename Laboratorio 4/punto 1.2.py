"""
Script que implementa el método Simplex de forma tabulada para resolver el 
problema de Woodcarving

"""

class Simplex:

    def __init__(self, coeficientes, restricciones, soluciones):
        self.coeficientes = coeficientes
        self.restricciones = restricciones
        self.soluciones = soluciones
        self.m, self.n = len(restricciones), len(restricciones[0])
        self.tabla = []

    def inicializarTabla(self):
        restriccionesAmpliadas = [fila + [0] * self.m for fila in self.restricciones]
        for i in range(self.m):
            restriccionesAmpliadas[i][self.n + i] = 1
        self.tabla = [restriccionesAmpliadas[i] + [self.soluciones[i]] for i in range(self.m)]
        self.tabla.append(self.coeficientes + [0] * (self.m + 1))

    def obtenerColumnaPivote(self):
        return self.tabla[-1].index(min(self.tabla[-1][:-1]))

    def obtenerFilaPivote(self, columnaPivote):
        divisiones = [(self.tabla[i][-1] / self.tabla[i][columnaPivote]
                      if self.tabla[i][columnaPivote] > 0 else float('inf')) for i in range(self.m)]
        return divisiones.index(min(divisiones))

    def realizarPivoteo(self, filaPivote, columnaPivote):
        pivote = self.tabla[filaPivote][columnaPivote]
        self.tabla[filaPivote] = [x / pivote for x in self.tabla[filaPivote]]
        for i in range(self.m + 1):
            if i != filaPivote:
                cociente = self.tabla[i][columnaPivote]
                self.tabla[i] = [self.tabla[i][j] - cociente * self.tabla[filaPivote][j] for j in range(self.n + self.m + 1)]

    def esOptimo(self):
        return min(self.tabla[-1][:-1]) >= 0

    def obtenerSolucion(self):
        solucionOptima = [0] * self.n
        for i in range(self.m):
            if self.tabla[i].index(1) < self.n:
                solucionOptima[self.tabla[i].index(1)] = self.tabla[i][-1]
        return solucionOptima

    def obtenerValorMaximo(self):
        return self.tabla[-1][-1]

    def resolver(self):
        self.inicializarTabla()
        while not self.esOptimo():
            columnaPivote = self.obtenerColumnaPivote()
            filaPivote = self.obtenerFilaPivote(columnaPivote)
            self.realizarPivoteo(filaPivote, columnaPivote)
        solucionOptima = self.obtenerSolucion()
        valorMaximo = self.obtenerValorMaximo()
        return solucionOptima, valorMaximo


def main():
    # Información del problema
    coeficientes = [-3, -2]
    restricciones = [
        [2, 1],
        [1, 1],
        [1, 0]
    ]
    soluciones = [100, 80, 40]

    # Resolución del problema
    simplex = Simplex(coeficientes, restricciones, soluciones)
    solucionOptima, valorMaximo = simplex.resolver()

    print("Solución óptima:", solucionOptima)
    print("Valor máximo de Z:", valorMaximo)

if __name__ == "__main__":
    main()