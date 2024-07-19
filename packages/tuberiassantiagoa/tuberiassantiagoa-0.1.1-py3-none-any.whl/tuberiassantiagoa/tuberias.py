import numpy as np
import matplotlib.pyplot as plt
import csv

def leer_datos(filename):
	puntos = []
	with open(filename, mode='r') as file:
			csv_reader = csv.DictReader(file)
			for row in csv_reader:
					puntos.append((int(row["point_id"]), float(row["x"]), float(row["y"]), float(row["demand"])))
	return puntos

def leer_datos_desde_diccionario(datos):
	puntos = []
	for dato in datos:
			puntos.append((dato["point_id"], dato["x"], dato["y"], dato["demand"]))
	return puntos

def calcular_distancia(p1, p2):
	return np.sqrt((p1[1] - p2[1])**2 + (p1[2] - p2[2])**2)

def optimizar_red(puntos):
	n = len(puntos)
	matriz_distancias = np.zeros((n, n))
	for i in range(n):
			for j in range(n):
					matriz_distancias[i, j] = calcular_distancia(puntos[i], puntos[j])

	# Este es un lugar donde podrías implementar un algoritmo de optimización.
	# Por simplicidad, vamos a suponer una solución trivial aquí.
	conexiones = [(puntos[i][0], puntos[i+1][0]) for i in range(n-1)]
	return conexiones

def mostrar_red(puntos, conexiones):
	for p in puntos:
			plt.scatter(p[1], p[2], s=100)
			plt.text(p[1], p[2], f'P{p[0]}')

	for c in conexiones:
			p1 = puntos[c[0] - 1]
			p2 = puntos[c[1] - 1]
			plt.plot([p1[1], p2[1]], [p1[2], p2[2]], 'k-')

	plt.xlabel('X')
	plt.ylabel('Y')
	plt.title('Red de Tuberías Optimizada')
	plt.grid()
	plt.show()
