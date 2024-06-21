import numpy as np
import matplotlib.pyplot as plt
import json
import os
from itertools import combinations
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/productionplan', methods=['POST'])
def getData():
    #Solicitamos los datos
    data = request.get_json()

    #Guardamos los datos
    L = data['load']
    fuels = data['fuels']
    powerplants = data['powerplants']
    
    n = len(powerplants)
    
    names = [powerplant['name'] for powerplant in powerplants]
    types = [powerplant['type'] for powerplant in powerplants]
    efficiency = [powerplant['efficiency'] for powerplant in powerplants]
    pmin = [powerplant['pmin'] for powerplant in powerplants]
    pmax = [powerplant['pmax'] for powerplant in powerplants]

    #Calculamos el vector de costes
    costs = np.array([0 for i in range(n)])
    types = np.array(types)
    costs[types == 'gasfired'] = fuels['gas(euro/MWh)']
    costs[types == 'turbojet'] = fuels['kerosine(euro/MWh)']
    
    #Vamos a considerar que la eficiencia de una planta eólica es el viento que hace
    efficiency = np.array(efficiency)
    efficiency[types == 'windturbine'] = fuels['wind(%)']/100 

    #Añadimos las variables de relajación en el vector de costes
    c = np.concatenate((costs, np.zeros(2*n)))
    
    #Calculamos el término independiente de las restricciones
    b = [L] + pmin + pmax
    b = np.array(b)
    
    #Calculamos la matriz de restricciones
    
    #Primera fila: vector de eficiencias
    first_row = np.concatenate((efficiency, np.zeros(2*n)))
    first_row = np.reshape(first_row, (1, 3*n))
    
    #El resto de filas es fácil definirlas por bloques
    #primeras n columnas: variables "reales", P_i
    #siguientes n columnas: variables "pmin", s_i
    #últimas n columnas: variables "pmax", f_i
    identity = np.eye(n)
    zeros = np.zeros((n,n))
    
    pmin_block = np.concatenate((identity, -identity, zeros), axis = 1)
    pmax_block = np.concatenate((identity, zeros, identity), axis = 1)
    
    A = np.concatenate((first_row, pmin_block, pmax_block), axis = 0)

    #Resolvemos
    total = 3*n
    
    #Almacenamos el rango de la matriz
    rango = 2*n + 1
    #Calculamos los índices de las columnas de todas las posibles submatrices
    indices = np.array([[True if i in comb else False for i in range(total)] for comb in combinations(np.arange(total), rango)])
    nrows = np.shape(indices)[0]
        
    solucion = {}
    
    for i in range(nrows):
        #Escogemos la submatriz correspondiente
        submatriz = A[:,indices[i,:]]
            
        try:
            #Tratamos de resolver el sistema correspondiente
            z = np.linalg.solve(submatriz, b)
    
            #La solución la insertamos en un vector lleno de ceros
            sol_real = np.zeros(3*n)
            sol_real[indices[i,:]] = z
            value = c.dot(sol_real)
    
            #Descartamos soluciones con componentes negativas
            if np.sum(sol_real[sol_real != 0] < 0) == 0:
                solucion[i] = {'x': sol_real, 'obj': c.dot(sol_real)}
            else:
                solucion[i] = {'x': None, 'obj': 1e99}
        except:
            #Si surge algún problema devolvemos una solución nula
            solucion[i] = {'x': None, 'obj': 1e99}
    
    #Guardamos los valores obtenidos y buscamos el mínimo
    obj = np.array([solucion[i]['obj'] for i in range(nrows)])
    opt_index = np.argmin(obj)
    #Devolvemos la solución
    sol = {'x': solucion[opt_index]['x'], 'obj': solucion[opt_index]['obj']}

    #Expresamos la solución adecuadamente
    respuesta = [{'name': names[i], 'p': sol['x'][i]} for i in range(n)]

    #Guardamos la solución en el formato correcto
    save_file = open("respuestas\\solucion.json", "w")
    json.dump(data, save_file)  
    save_file.close()  
    return respuesta


if __name__ == '__main__':
    app.run(debug=True)









