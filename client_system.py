import csv
import time

def load_clients(file_path):
    """
    Carga los clientes desde file_path. 
    Devuelve (lista_de_dicts, invalid_count).
    Sólo usa id,nombre,email,ciudad,edad; ignora filas mal formadas o faltantes.
    """
    clients = []
    invalid = 0
    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Validar existencia de claves y valores no vacíos
                for k in ('id','nombre','email','ciudad','edad'):
                    if k not in row or row[k] is None or row[k].strip() == '':
                        raise ValueError()
                cid = int(row['id'])
                age = int(row['edad'])
            except Exception:
                invalid += 1
                continue
            clients.append({
                'id': cid,
                'nombre': row['nombre'].strip(),
                'email': row['email'].strip(),
                'ciudad': row['ciudad'].strip(),
                'edad': age
            })
    return clients, invalid

def search_by_id(clients, client_id):
    """Busca cliente por ID; mide y devuelve (resultado_o_None, ms)"""
    start = time.perf_counter()
    res = next((c for c in clients if c['id'] == client_id), None)
    ms = (time.perf_counter() - start) * 1000
    return res, ms

def filter_by_city(clients, city):
    """Filtra case-insensitive; devuelve (lista, ms)"""
    start = time.perf_counter()
    city_l = city.strip().lower()
    res = [c for c in clients if c['ciudad'].lower() == city_l]
    ms = (time.perf_counter() - start) * 1000
    return res, ms

def sort_by_age(clients):
    """Ordena por edad asc y en empate por ID; devuelve (lista, ms)"""
    start = time.perf_counter()
    res = sorted(clients, key=lambda c: (c['edad'], c['id']))
    ms = (time.perf_counter() - start) * 1000
    return res, ms
