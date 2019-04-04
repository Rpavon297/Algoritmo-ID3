import copy
import math
import sys

import numpy as np
from PyQt5 import uic
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMainWindow, QApplication, QGraphicsScene

qtCreatorFile = "GUIID3.ui"

Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class Fila:
    def __init__(self, natributos=[], atributos=[]):
        self.atributos = atributos.copy()
        self.nombres = natributos.copy()

    def getDecision(self):
        return self.atributos[-1] == "si"

    def removeAtributo(self, nombre):
        if nombre in self.nombres:
            del self.atributos[self.nombres.index(nombre)]
            self.nombres.remove(nombre)

    def getAtributo(self, nombre):
        if nombre in self.nombres:
            return self.atributos[self.nombres.index(nombre)]
        else:
            return None

    def getAtributos(self):
        return self.atributos

    def getNColumnas(self):
        return len(self.atributos)

    def __str__(self):
        cad = ""

        for elem in self.atributos:
            cad = cad + elem + ", "

        return cad


class Tabla:
    def __init__(self, cabecera=[], nfilas=[]):
        self.filas = []
        self.atributos = cabecera.copy()
        self.dominio = []

        for i in range(len(cabecera)):
            self.dominio.append([nfilas[0][i]])

        for i, fila in enumerate(nfilas):
            self.filas.append(Fila(cabecera.copy(), fila.copy()))

            for j in range(len(self.dominio)):
                if fila[j] not in self.dominio[j]:
                    self.dominio[j].append(fila[j])

    def getNColumnas(self):
        return len(self.atributos)

    def getNFilas(self):
        return len(self.filas)

    def removeFila(self, i):
        if i < len(self.filas):
            del self.filas[i]

    def removeColumna(self, nombre):
        for fila in self.filas:
            fila.removeAtributo(nombre)

    def getFila(self, i):
        if i < len(self.filas):
            return self.filas[i]
        else:
            return None

    def getFilas(self):
        return self.filas

    def merito(self):
        mejor = math.inf
        ret = self.atributos[0]

        for i in range(len(self.atributos) - 1):
            columna = self.atributos[i]

            aux = self.meritoCol(columna)

            if aux < mejor:
                mejor = aux
                ret = columna

        return ret

    def meritoCol(self, columna):
        merito = 0
        index = self.atributos.index(columna)
        cont = np.zeros(len(self.dominio[index]))
        posis = np.zeros(len(self.dominio[index]))

        for fila in self.filas:
            for i, variable in enumerate(self.dominio[index]):
                if variable == fila.getAtributo(columna):
                    cont[i] = cont[i] + 1

                    if fila.getDecision():
                        posis[i] = posis[i] + 1

        for i in range(len(self.dominio[index])):
            if posis[i] != 0 and posis[i] != cont[i]:
                p = posis[i] / cont[i]
                n = 1 - p
                N = sum(cont)

                r = cont[i] / N

                merito = merito + (r * self.informacion(p, n))

        return merito

    def informacion(self, p, n):
        return -float(p) * (math.log(float(p), 2)) - float(n) * (math.log(float(n), 2))

    def getDominio(self, atributo):
        return self.dominio[self.atributos.index(atributo)]

    def contiene(self, atributo, valor):
        for fila in self.filas:
            if fila.getAtributo(atributo) == valor:
                return True
        return False

    def sesgar(self, atributo, valor):

        nuevaTabla = [fila for fila in self.filas if fila.getAtributo(atributo) == valor]
        self.filas = nuevaTabla

        for fila in self.filas:
            fila.removeAtributo(atributo)

        del self.dominio[self.atributos.index(atributo)]
        self.atributos.remove(atributo)


class Nodo:
    def __init__(self, raiz=None, padre=None):
        self.raiz = raiz
        self.padre = padre
        self.hijos = []

    def getPadre(self):
        return self.padre

    def getRaiz(self):
        return self.raiz

    def setRaiz(self, raiz):
        self.raiz = raiz

    def setHijo(self, hijo):
        self.hijos.append(hijo)

    def setHijos(self, arr):
        self.hijos = arr

    def getHijos(self):
        return self.hijos

    def removeHijos(self):
        self.hijos = []

    def removeHijo(self, nodo):
        self.hijos.remove(nodo)

    def __eq__(self, other):
        if isinstance(other, Nodo):
            return self.raiz == other.getRaiz() and self.padre == other.getPadre()
        return False

    def __ne__(self, other):
        return not self.__eq__(other)


class ID3:
    def __init__(self, tabla=None):
        self.tabla = tabla

    def go(self):
        atributo = self.tabla.merito()
        raiz = Nodo(atributo, None)

        for elem in self.tabla.getDominio(atributo):
            try:
                tabla_c = copy.deepcopy(self.tabla)
                tabla_c.sesgar(atributo, elem)
                self.recurrir(tabla_c, raiz, elem)
            except Exception as e:
                print(str(e))
        return raiz

    def recurrir(self, tabla, padre, valor):

        if tabla.getNColumnas() > 0 and tabla.getNFilas() > 0:
            cpos = 0

            for fila in tabla.getFilas():
                if fila.getDecision():
                    cpos = cpos + 1

            if cpos == 0:
                padre.setHijo(Nodo("no", valor))
            elif cpos == tabla.getNFilas():
                padre.setHijo(Nodo("si", valor))
            else:
                atributo = tabla.merito()
                nuevo = Nodo(atributo, valor)

                for elem in tabla.getDominio(atributo):
                    tabla_c = copy.deepcopy(tabla)
                    tabla_c.sesgar(atributo, elem)
                    self.recurrir(tabla_c, nuevo, elem)
                if nuevo.getHijos():
                    padre.setHijo(nuevo)
                    posis = 0
                    negas = 0
                    nhijos = len(nuevo.getHijos())

                    for hijo in nuevo.getHijos():
                        if hijo.getRaiz() == "si":
                            posis = posis + 1
                        elif hijo.getRaiz() == "no":
                            negas = negas + 1

                    if negas == nhijos:
                        # nuevo.removeHijos()
                        nuevo.setRaiz("no")
                    elif posis == nhijos:
                        # nuevo.removeHijos()
                        nuevo.setRaiz("si")


class MyApp(QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.controlador = Controlador(self)
        self.ui.goButton.clicked.connect(self.go)
        self.conteo = np.zeros(0)
        self.raiz = Nodo()
        self.ui.error1.hide()

    def go(self):

        self.ui.error1.hide()

        try:
            self.controlador.cargarTabla(self.ui.input_att.toPlainText(), self.ui.input_cabecera.toPlainText())
        except Exception as e:
            print(str(e))
            self.ui.error1.show()

        self.controlador.go()

    def mostrar(self, raiz):
        scene = QGraphicsScene()

        elipse = scene.addEllipse(0, 0, 100, 50)
        elipse.setBrush(QColor(245, 235, 255))

        text = scene.addText(raiz.getRaiz())

        text1 = scene.addText("RAIZ")

        self.raiz = Nodo(elipse, [text, text1])

        self.conteo = np.zeros(self.controlador.getNAtributos() + 1)
        self.conteo[0] = 2

        if (raiz.getHijos()):
            self.recurrir(raiz.getHijos(), 0, scene, self.raiz)
            self.redim(self.raiz, 0, scene)
            self.unir(self.raiz, scene)

        self.ui.viewer.setScene(scene)
        self.ui.viewer.show()
        self.ui.viewer.verticalScrollBar().setValue(self.ui.viewer.verticalScrollBar().minimum())
        self.ui.viewer.horizontalScrollBar().setValue(int(self.ui.viewer.horizontalScrollBar().maximum() / 2))

    def unir(self, padre, scene):
        for hijo in padre.getHijos():
            scene.addLine(padre.getRaiz().x() + 40, padre.getRaiz().y() + 50, hijo.getRaiz().x() + 50,
                          hijo.getRaiz().y())
            self.unir(hijo, scene)

    def redim(self, padre, nivel, scene):
        elipse = padre.getRaiz()
        text1 = padre.getPadre()[0]
        text2 = padre.getPadre()[1]

        desplazamiento = (np.amax(self.conteo) - self.conteo[nivel]) / 2
        elipse.setPos(elipse.x() + desplazamiento * 100, elipse.y())
        text1.setPos(elipse.x() + 18, elipse.y() + 13)
        text2.setPos(elipse.x(), elipse.y() - 30)

        for hijo in padre.getHijos():
            self.redim(hijo, nivel + 1, scene)

    def recurrir(self, nodos, nivel, scene, npadre):
        nivel = nivel + 1
        elipses = []
        textos = []
        tam = len(nodos)
        for nodo in nodos:
            elipse = scene.addEllipse(0, 0, 100, 45)
            elipse.setPos(100 * self.conteo[nivel], nivel * 150)
            elipse.setBrush(QColor(240, 240, 255))

            text = scene.addText(nodo.getRaiz())
            text2 = scene.addText(nodo.getPadre())

            npadre.setHijo(Nodo(elipse, [text, text2]))

            elipses.append(elipse)
            textos.append(text)

            self.conteo[nivel] = self.conteo[nivel] + 1

        self.conteo[nivel] = self.conteo[nivel] + 1
        hoja = True
        for i, nodo in enumerate(nodos):
            if (nodo.getHijos()):
                self.recurrir(nodo.getHijos(), nivel, scene, npadre.getHijos()[i])
                hoja = False

        if hoja: return len(nodos)
        return tam


class Controlador:
    def __init__(self, vista=None):
        self.vista = vista
        self.tabla = None

    def cargarTabla(self, atributos, cabecera):
        array = []
        file = open(cabecera, "r")

        cabeceras = file.read().strip("\n").split(",")
        file.close()
        app.processEvents()

        file = open(atributos, "r")
        atributos = file.readlines()

        for linea in atributos:
            array.append(linea.strip("\n").split(","))

        self.tabla = Tabla(cabeceras, array)

    def getNFilas(self):
        return self.tabla.getNFilas()

    def getNAtributos(self):
        return self.tabla.getNColumnas()

    def go(self):
        algoritmo = ID3(self.tabla)
        raiz = algoritmo.go()

        self.vista.mostrar(raiz)

    def toString(self, raiz):
        cadena = [str(raiz.getRaiz()), str(raiz.getPadre())]

        for hijo in raiz.getHijos():
            cadena = cadena + self.toString(hijo)

        return cadena


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyApp()
    window.show()
    app.exec_()
