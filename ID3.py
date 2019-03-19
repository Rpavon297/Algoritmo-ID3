import numpy as np

import math, time, random, sys, copy
import numpy as np
from PyQt5.QtGui import QStandardItemModel

from PyQt5.QtWidgets import QMainWindow, QApplication, QWidget, QAction, QTableWidget, QTableWidgetItem, QVBoxLayout, \
    QMessageBox, QTreeWidgetItem, QTreeView
from PyQt5 import uic, QtGui

qtCreatorFile = "GUIID3.ui"

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class Fila:
    def __init__(self, natributos = [], atributos = []):
        self.atributos = []
        self.nombres = []

        for elem in atributos:
            self.atributos.append(elem)
        for elem in natributos:
            self.nombres.append(elem)

    def getDecision(self):
        return self.atributos[-1] == "si"

    def removeAtributo(self, nombre):
        if nombre in self.nombres:
            del self.atributos[self.nombres.index(nombre)]
            self.nombres.remove(nombre)

    def getAtributo(self, nombre):
        if nombre in self.nombres:
            return self.atributos[self.nombres.index(nombre)]
        else: return None

    def getAtributos(self):
        return self.atributos

    def getNColumnas(self):
        return len(self.atributos)

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


    def getNColumnas(self):
        return len(self.atributos)

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

        for i in range(len(self.atributos) - 1):
            columna = self.atributos[i]

            aux = self.meritoCol(columna)

            if aux < mejor:
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

                    if fila.getDecision():
                        posis[i] = posis[i] + 1

        for i in range(len(self.dominio[index])):
            if posis[i] == 0 or posis[i] == cont[i]: return 0
            else:
                p = posis[i]/cont[i]
                n = 1-p
                r = sum(cont)

                merito = merito + (r * self.informacion(p,n))

        return merito

    def informacion(self,p,n):
        return -float(p) * (math.log(float(p),2)) - float(n) * (math.log(float(n),2))

    def getDominio(self,atributo):
        return self.dominio[self.atributos.index(atributo)]

    def sesgar(self, valor):
        for i, columna in enumerate(self.dominio):
            if valor in columna:
                atributo = self.atributos[i]
                for i,fila in enumerate(self.filas):
                    if fila.getAtributo(atributo) != valor:
                        del self.filas[i]

                for fila in self.filas:
                    fila.removeAtributo(atributo)
                self.dominio.remove(columna)
                self.atributos.remove(atributo)

class Nodo:
    def __init__(self,raiz = None, padre = None):
        self.raiz = raiz
        self.padre = padre
        self.hijos = []

    def getPadre(self):
        return self.padre

    def getRaiz(self):
        return self.raiz

    def setHijo(self, hijo):
        self.hijos.append(hijo)

    def getHijos(self):
        return self.hijos

    def __eq__(self,other):
        if isinstance(other, Nodo):
            return self.raiz == other.getRaiz() and self.padre == other.getPadre()
        return False
    def __ne__(self, other):
        return not self.__eq__(other)

class ID3:
    def __init__(self, tabla = None):
        self.tabla = tabla

    def go(self):
        atributo = self.tabla.merito()
        raiz = Nodo(atributo,None)

        for elem in self.tabla.getDominio(atributo):

            self.recurrir(self.tabla,raiz,elem)
        return raiz

    def recurrir(self, ntabla, padre, valor):
        tabla = copy.deepcopy(ntabla)

        #Solo una columna
        if tabla.getNColumnas() == 2:

            for i, fila in enumerate(tabla.getFilas()):
                if fila.getDecision():
                    if Nodo("si",fila.getAtributos()[0]) not in padre.getHijos():
                        padre.setHijo(Nodo("si",fila.getAtributos()[0]))
                else:
                    if Nodo("no", fila.getAtributos()[0]) not in padre.getHijos():
                        padre.setHijo(Nodo("no",fila.getAtributos()[0]))
        else:
            tabla.sesgar(valor);
            atributo = tabla.merito()

            nuevo = Nodo(atributo, valor)
            padre.setHijo(nuevo)

            for elem in tabla.getDominio(atributo):
                self.recurrir(tabla,nuevo,elem)

class MyApp(QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.controlador = Controlador(self)
        self.ui.goButton.clicked.connect(self.go)

        model = QStandardItemModel()
        model.setHorizontalHeaderLabels(["ATRIBUTO", "VALOR ATRIBUTO ANTERIOR:"])

    def go(self):
        self.controlador.cargarTabla(self.ui.input_att.toPlainText(), self.ui.input_cabecera.toPlainText())
        self.controlador.go()

    def mostrar(self, raiz):
        nodos = []
        nodo = QTreeWidgetItem()
        nodo.setText(0, raiz.getRaiz())
        nodo.setText(1, "")
        nodos.append(nodo)

        for hijo in raiz.getHijos():
            nodos.append(self.recurrir(hijo,nodo))

        self.ui.arbol.insertTopLevelItems(0,nodos)

    def recurrir(self, raiz, nodo):
        nodos = []

        nodo = QTreeWidgetItem(raiz)
        nodo.setText(0, raiz.getRaiz())
        nodo.setText(1, raiz.getPadre())
        nodos.append(nodo)

        for hijo in raiz.getHijos():
            nodos.append(self.recurrir(hijo, nodo))

        return nodos

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
        raiz = algoritmo.go()
        cadena = self.toString(raiz)

        self.vista.mostrar(raiz)

    def toString(self, raiz):
        cadena =  [str(raiz.getRaiz()),str(raiz.getPadre())]

        for hijo in raiz.getHijos():
            cadena = cadena + self.toString(hijo)

        return cadena

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    app.exec_()
