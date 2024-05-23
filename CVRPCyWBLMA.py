import random

def leer_instancia(nombre_archivo):
    instancia = {}
    with open(nombre_archivo, 'r') as file:
        for linea in file:
            if linea.startswith('DIMENSION'):
                instancia['dimension'] = int(linea.split(':')[1].strip())
            elif linea.startswith('CAPACITY'):
                instancia['capacity'] = int(linea.split(':')[1].strip())
            elif linea.startswith('EDGE_WEIGHT_SECTION'):
                matriz_distancias = []
                for _ in range(instancia['dimension']):
                    matriz_distancias.append(list(map(int, file.readline().split())))
                instancia['distances'] = matriz_distancias
            elif linea.startswith('DEMAND_SECTION'):
                demandas = {}
                for _ in range(instancia['dimension']):
                    indice, demanda = map(int, file.readline().split())
                    demandas[indice] = demanda
                instancia['demands'] = demandas
            elif linea.startswith('DEPOT_SECTION'):
                instancia['depot'] = int(file.readline().split()[0])
    return instancia

def calcular_distancia_total(ruta, distances):
    distancia_total = 0
    for i in range(len(ruta) - 1):
        distancia_total += distances[ruta[i]][ruta[i + 1]]
    return distancia_total

def busqueda_local_con_alpha(rutas, distances, demands, capacity, alpha):
    def obtener_nodos_de_rutas(rutas):
        nodos = []
        for ruta in rutas:
            for nodo in ruta[1:-1]:  # Excluir el primer y último nodo (supuestos depósitos)
                nodos.append(nodo)
        return nodos

    mejora = True
    while mejora:
        mejora = False
        
        # Obtener todos los nodos excluyendo los depósitos
        nodos = obtener_nodos_de_rutas(rutas)
        
        # Aplicar shuffle a los nodos según el valor de alpha
        if alpha > 0:
            cantidad_nodos = len(nodos)
            cantidad_a_shufflear = int(cantidad_nodos * alpha)
            nodos_a_shufflear = nodos[:cantidad_a_shufflear]
            random.shuffle(nodos_a_shufflear)
            nodos[:cantidad_a_shufflear] = nodos_a_shufflear

        # Realizar la búsqueda local utilizando los nodos mezclados
        for cliente_i in nodos:
            for i in range(len(rutas)):
                if cliente_i in rutas[i]:
                    break
            else:
                continue  # Si el nodo no se encuentra en ninguna ruta, continuar con el siguiente nodo

            for k in range(len(rutas)):
                if i == k:
                    continue
                for l in range(1, len(rutas[k]) - 1):
                    cliente_k = rutas[k][l]
                    if cliente_i == cliente_k or cliente_k in rutas[i]:
                        continue
                    nueva_ruta_i = rutas[i][:]  # Copiar la ruta actual
                    if cliente_i in nueva_ruta_i:
                        nueva_ruta_i.remove(cliente_i)
                    else:
                        continue  # Si por alguna razón el nodo no está en la ruta, continuar
                    nueva_ruta_k = rutas[k][:l] + [cliente_i] + rutas[k][l:]
                    if validar_ruta(nueva_ruta_i, distances, demands, capacity) and \
                            validar_ruta(nueva_ruta_k, distances, demands, capacity):
                        distancia_total_i = calcular_distancia_total(nueva_ruta_i, distances)
                        distancia_total_k = calcular_distancia_total(nueva_ruta_k, distances)
                        distancia_total_original = calcular_distancia_total(rutas[i], distances) + calcular_distancia_total(rutas[k], distances)
                        if distancia_total_i + distancia_total_k < distancia_total_original:
                            rutas[i] = nueva_ruta_i
                            rutas[k] = nueva_ruta_k
                            mejora = True

    return rutas

def validar_ruta(ruta, distances, demands, capacity):
    if len(ruta) <= 2:
        return False
    capacidad_utilizada = sum(demands[cliente] for cliente in ruta[1:-1])
    return capacidad_utilizada <= capacity

def CVRP_ClarkeWright(instancia):
    dimension = instancia['dimension']
    depot = instancia['depot']
    vehicle_capacity = instancia['capacity']
    distances = instancia['distances']
    demands = instancia['demands']

    # Calcular los ahorros para todas las combinaciones de clientes
    savings = []
    for i in range(2, dimension):  # Empezamos desde 2 para omitir el depósito (índice 1)
        for j in range(i + 1, dimension):
            saving = distances[1][i] + distances[1][j] - distances[i][j]  # Corregimos el índice del depósito
            savings.append((i, j, saving))

    # Ordenar los ahorros en orden descendente
    savings.sort(key=lambda x: x[2], reverse=True)

    # Inicializar la lista de rutas de vehículos
    vehicle_routes = []

    # Inicializar un conjunto para rastrear los clientes visitados
    visited_customers = set()

    # Iterar a través de los ahorros en orden aleatorio
    for (customer_i, customer_j, saving) in savings:
        # Si ambos clientes no han sido visitados aún
        if customer_i not in visited_customers and customer_j not in visited_customers:
            # Comprobar si combinar las rutas de customer_i y customer_j no excede la capacidad del vehículo
            if demands[customer_i] + demands[customer_j] <= vehicle_capacity:
                # Combinar las rutas de customer_i y customer_j
                route = [1, customer_i, customer_j, 1]  # 1 representa el depósito
                vehicle_routes.append(route)

                # Marcar ambos clientes como visitados
                visited_customers.add(customer_i)
                visited_customers.add(customer_j)

    # Asignar los clientes restantes a los vehículos utilizando la heurística del vecino más cercano
    for vehicle in range(len(vehicle_routes)):
        remaining_customers = [i for i in range(2, dimension) if i not in visited_customers]  # Excluimos el depósito
        route = [1]  # Comenzamos desde el depósito
        current_capacity = vehicle_capacity
        current_location = 1  # El depósito es el punto de partida inicial
        while remaining_customers:
            nearest_customer = min(remaining_customers, key=lambda x: distances[current_location][x])
            if demands[nearest_customer] <= current_capacity:
                route.append(nearest_customer)
                visited_customers.add(nearest_customer)  # Marcamos el cliente como visitado
                remaining_customers.remove(nearest_customer)
                current_capacity -= demands[nearest_customer]
                current_location = nearest_customer
            else:
                route.append(1)  # Solo agregamos el depósito una vez cuando la capacidad no es suficiente
        route.append(1)  # Regresar al depósito al final del recorrido
        vehicle_routes.append(route)

    return vehicle_routes

nombre_archivo = 'C:/Users/Mario Diaz/OneDrive/Escritorio/CVRPinstancias/cvrp-S-G-200-20.txt'
instancia = leer_instancia(nombre_archivo)

routes_cw = CVRP_ClarkeWright(instancia)
routes_cw = busqueda_local_con_alpha(routes_cw, instancia['distances'], instancia['demands'], instancia['capacity'],alpha=0.4)

total_distance = 0
total_savings = 0

print("Routes made with Clarke and Wright with local search:")
for i, route in enumerate(routes_cw):
    if len(route) <= 2:
        continue
    distancia_total = calcular_distancia_total(route, instancia['distances'])
    ahorro = instancia['distances'][1][route[1]] + instancia['distances'][1][route[-2]] - instancia['distances'][route[1]][route[-2]]
    capacidad_utilizada = sum(instancia['demands'][cliente] for cliente in route if cliente != 1)
    cantidad_clientes = len(route) - 2  # Excluyendo el depósito
    
    total_distance += distancia_total
    total_savings += ahorro

    print(f"Route {i + 1}: {route}, Total distance: {distancia_total}, Saving: {ahorro}, Used capacity: {capacidad_utilizada}, Amount of costumers: {cantidad_clientes}")

print(f"Total distance traveled: {total_distance}")
print(f"Total savings: {total_savings}")
