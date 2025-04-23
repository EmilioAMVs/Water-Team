import csv
import time
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'supersecret-key'

clientes = []

def parse_csv_stream(stream):
    """Parsee el CSV del stream y retorne la lista de clientes válidos."""
    parsed = []
    reader = csv.DictReader(stream.read().decode('utf-8').splitlines())
    for fila in reader:
        try:
            parsed.append({
                'id': int(fila['id']),
                'nombre': fila['nombre'],
                'email': fila['email'],
                'ciudad': fila['ciudad'],
                'edad': int(fila['edad'])
            })
        except (ValueError, KeyError):
            # Omitir registros mal formados
            continue
    return parsed

@app.route('/', methods=['GET'])
def index():
    # Si no hay clientes aún, solo muestro el form de subida
    return render_template('index.html', clientes=clientes, tiempo=None)

@app.route('/upload', methods=['POST'])
def upload():
    global clientes
    file = request.files.get('csv_file')
    if not file or not file.filename.lower().endswith('.csv'):
        flash('Error: Solo se permiten archivos con extensión .csv', 'danger')
        return redirect(url_for('index'))

    try:
        clientes = parse_csv_stream(file.stream)
        flash(f'Archivo cargado correctamente: {len(clientes)} registros válidos', 'success')
    except Exception as e:
        flash(f'Error al procesar el archivo: {e}', 'danger')
        clientes = []

    return redirect(url_for('index'))

@app.route('/buscar', methods=['POST'])
def buscar():
    inicio = time.perf_counter()
    client_id = request.form.get('id')
    resultado = next((c for c in clientes if str(c['id']) == client_id), None)
    tiempo = round((time.perf_counter() - inicio) * 1000, 2)
    if not resultado:
        flash("Cliente no encontrado", "warning")
        return render_template('index.html', clientes=[], tiempo=tiempo)
    return render_template('index.html', clientes=[resultado], tiempo=tiempo)

@app.route('/ciudad', methods=['POST'])
def por_ciudad():
    ciudad = request.form.get('ciudad', '').lower()
    inicio = time.perf_counter()
    filtrados = [c for c in clientes if c['ciudad'].lower() == ciudad]
    tiempo = round((time.perf_counter() - inicio) * 1000, 2)
    if not filtrados:
        flash("No hay clientes en esa ciudad", "warning")
    return render_template('index.html', clientes=filtrados, tiempo=tiempo)

@app.route('/ordenar', methods=['GET'])
def ordenar():
    inicio = time.perf_counter()
    ordenados = sorted(clientes, key=lambda x: (x['edad'], x['id']))
    tiempo = round((time.perf_counter() - inicio) * 1000, 2)
    return render_template('index.html', clientes=ordenados, tiempo=tiempo)

if __name__ == '__main__':
    app.run(debug=True)
