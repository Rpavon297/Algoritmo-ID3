import numpy as np

from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction, QTableWidget,QTableWidgetItem,QVBoxLayout, QMessageBox
from PyQt5 import uic, QtGui
import math

class Fila:
    def __init__(self, atributos = [], natributos = []):
        self.atributos = []
        self.nombres = []

        for elem in atributos:
            self.atributos.append(elem)
        for elem in natributos:
            self.nombres.append(elem)

    def removeAtributo(self, nombre):
        if nombre in self.nombres:
            del self.atributos[self.nombres.index(nombre)]

    def getAtributo(self, nombre):
        if nombre in self.nombres:
            return self.atributos[self.nombres.index(nombre)]
        else: return None

    def getAtributos(self):
        return self.atributos

class Tabla:
    def __init__(self,cabecera = [], nfilas = []):
        self.filas = []
        self.atributos = cabecera.copy()
        self.dominio = []

        for i in range(len(cabecera)):
            self.dominio.append([nfilas[0][i]])

        for i,fila in enumerate(nfilas):
            self.filas.append(Fila(cabecera.copy(),fila.copy()))

            for j in range(len(self.dominio)):
                if fila[j] not in self.dominio[j]:
                    self.dominio[j].append(fila[j])


    def removeFila(self, i):
        if i < len(self.filas):
            del self.filas[i]

    def removeColumna(self, nombre):
        for fila in self.filas:
            fila.removeAtributo(nombre)

    def getFila(self, i):
        if i < len(self.filas): return self.filas[i]
        else: return None

    def getFilas(self):
        return self.filas

    def merito(self):
        mejor = 0
        ret = None
        for columna in self.atributos:
            aux = self.meritoCol(columna)

            if aux == -2: return "NEGATIVO"
            if aux == -1: return "POSITIVO"

            if aux > mejor:
                mejor = aux
                ret = columna

        return columna

    def meritoCol(self, columna):
        merito = 0
        index = self.atributos.index(columna)
        cont = np.zeros(len(self.dominio[index]))
        posis = np.zeros(len(self.dominio[index]))


        for fila in self.filas:
            for i,variable in enumerate(self.dominio[index]):
                if variable == fila.getAtributo(columna):
                    cont[i] = cont[i] + 1

                    if fila[-1] == "si":
                        posis[i] = posis[i] + 1
        if 0 not in posis:
            return -1
        if sum(posis) == 0:
            return -2
        for i, in range(len(self.dominio)):
            p = posis[i]/cont[i]
            n = 1-p
            r = sum(cont)

            merito = merito + (r * self.informacion(p,n))

        return merito

    def informacion(self,p,n):
        return -p * (math.log(p,2)) - n * (math.log(n,2))

    def getDominio(self,atributo):
        return self.dominio[self.atributos.index(atributo)]

    def sesgar(self, valor):
        atributo = self.atributos.index(valor)

        for i,fila in enumerate(self.filas):
            if fila[self.atributos.index(atributo)] == valor:
                del self.filas[i]
            else:
                del fila[self.atributos.index(atributo)]

class ID3:
    def __init__(self, tabla = None):
        self.tabla = tabla

class Controlador:
    def __init__(self, vista = None):
        self.vista = vista
        self.tabla = None

    def cargarTabla(self, atributos, cabecera):
        array = []

        file = open(cabecera, "r")
        cabeceras = file.read().strip("\n").split(",")
        file.close()

        file = open(atributos, "r")
        atributos = file.readlines()

        for linea in atributos:
            array.append(linea.strip("\n").split(","))

        del array[-1]
        self.tabla = Tabla(cabeceras,array)
        print("stop")

    def go(self):
        algoritmo = ID3(self.tabla)
        algoritmo.go()
class Nodo:
    def __init__(self,raiz = None, padre = None):
        self.raiz = raiz
        self.padre = padre
        self.hijos = []

    def getRaiz(self):
        return self.raiz

    def setHijo(self, hijo):
        self.hijos.append(hijo)

class ID3:
    def __init__(self, tabla = None):
        self.tabla = tabla

    def go(self):
        atributo = self.tabla.merito()
        raiz = Nodo(atributo)

        for elem in self.tabla.getDominio(atributo):
            ntabla = self.tabla.copy().sesgar(elem)
            self.recurrir(ntabla,raiz,elem)
        print("stop3")

    def recurrir(self, tabla,padre,var):
        pos = np.zeros(len(tabla))
        if len(tabla[0]) == 2:
            for i, fila in enumerate(tabla):
                if fila[-1] == "si":
                    pos[i] = pos[i] + 1

            if 0 not in pos:
                padre.setHijo(Nodo("si","cualquiera"))
            elif sum(pos) == 0:
                padre.setHijo(Nodo("no","cualquiera"))
            else:
                for i, p in enumerate(pos):
                    raiz = "si"
                    if p == 0: raiz = "no"

                    padre.setHijo(Nodo(raiz,tabla[i]))

        else:
            ntabla =  tabla.copy().sesgar(var)

            att = ntabla.merito()
            raiz = Nodo(att)

            for elem in self.tabla.getDominio(att):
                self.recurrir(self.tabla, raiz, elem)

#qtCreatorFile = "GUIastar.ui"

#Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class MyApp(QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        self.ui = Ui_MainWindow()




if __name__ == "__main__":
    controlador = Controlador()
    controlador.cargarTabla("Juego.txt", "AtributosJuego.txt")
    controlador.go()