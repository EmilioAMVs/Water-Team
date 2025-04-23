import pytest
from client_system import load_clients, search_by_id, filter_by_city, sort_by_age

CSV_PATH = 'clientes.csv'

def test_load_clients():
    clients, invalid = load_clients(CSV_PATH)
    assert isinstance(clients, list)
    assert len(clients) > 0
    # Al menos 1000 registros válidos según enunciado
    assert len(clients) >= 1000

def test_search_existing():
    clients, _ = load_clients(CSV_PATH)
    sample = clients[0]['id']
    res, t = search_by_id(clients, sample)
    assert res is not None and res['id'] == sample
    assert t <= 500  # ms

def test_search_nonexistent():
    clients, _ = load_clients(CSV_PATH)
    res, _ = search_by_id(clients, -1)
    assert res is None

def test_filter_city_case_insensitive():
    clients, _ = load_clients(CSV_PATH)
    # Elegimos una ciudad conocida:
    city = clients[0]['ciudad']
    up = city.upper()
    r1, _ = filter_by_city(clients, city)
    r2, _ = filter_by_city(clients, up)
    assert len(r1) == len(r2)

def test_sort_by_age():
    clients, _ = load_clients(CSV_PATH)
    sorted_list, t = sort_by_age(clients)
    ages = [c['edad'] for c in sorted_list]
    assert ages == sorted(ages)
    assert t <= 2000  # ms
