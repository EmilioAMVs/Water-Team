from flask import Flask, render_template, request, redirect, url_for, flash, session
import csv
import time

app = Flask(__name__)
app.secret_key = 'cambiar_por_una_clave_segura'

REQUIRED_FIELDS = {'id', 'nombre', 'email', 'ciudad', 'edad', 'extra'}

def parse_csv_stream(stream):
    """
    Parsea el CSV desde el stream y retorna (clients, invalid_count).
    - Valida encabezado: debe contener al menos los campos REQUIRED_FIELDS.
    - Ignora registros mal formados o incompletos.
    """
    text = stream.read().decode('utf-8').splitlines()
    reader = csv.DictReader(text)
    
    # Validar encabezado
    headers = set(reader.fieldnames or [])
    if not REQUIRED_FIELDS.issubset(headers):
        raise ValueError(
            f"El CSV debe contener las columnas: {', '.join(REQUIRED_FIELDS)}"
        )
    
    clients = []
    invalid = 0
    for row in reader:
        try:
            # Validar cada campo requerido
            for k in REQUIRED_FIELDS:
                if row.get(k) is None or row[k].strip() == '':
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
            'edad': age,
            'extra': row['extra'].strip()
        })
    return clients, invalid

@app.route('/', methods=['GET'])
def upload_view():
    session.clear()
    return render_template('upload.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('csv_file')
    if not file or not file.filename.lower().endswith('.csv'):
        flash('Error: solo archivos con extensión .csv', 'danger')
        return redirect(url_for('upload_view'))
    try:
        clients, invalid = parse_csv_stream(file.stream)
    except ValueError as e:
        flash(f'Error de CSV: {e}', 'danger')
        return redirect(url_for('upload_view'))
    except Exception as e:
        flash(f'Error al procesar CSV: {e}', 'danger')
        return redirect(url_for('upload_view'))

    # Guardar en sesión
    session['clients'] = clients
    session['invalid'] = invalid
    session['view_clients'] = clients[:]  # copia
    flash(f'Archivo cargado: {len(clients)} válidos, {invalid} inválidos', 'success')
    return redirect(url_for('dashboard'))

@app.route('/dashboard', methods=['GET'])
def dashboard():
    if 'clients' not in session:
        return redirect(url_for('upload_view'))
    return render_template(
        'dashboard.html',
        clients=session.get('view_clients', []),
        invalid=session.get('invalid', 0),
        tiempo=session.pop('tiempo', None)
    )

@app.route('/reset_all')
def reset_all():
    session.clear()
    return redirect(url_for('upload_view'))

@app.route('/clear_filters')
def clear_filters():
    session['view_clients'] = session.get('clients', [])
    return redirect(url_for('dashboard'))

@app.route('/buscar', methods=['POST'])
def buscar():
    cid_str = request.form.get('id','').strip()
    try:
        cid = int(cid_str)
    except ValueError:
        flash('ID inválido', 'warning')
        return redirect(url_for('dashboard'))
    start = time.perf_counter()
    result = next((c for c in session['clients'] if c['id'] == cid), None)
    ms = round((time.perf_counter() - start)*1000, 2)
    session['tiempo'] = ms
    if result:
        session['view_clients'] = [result]
    else:
        session['view_clients'] = []
        flash('Cliente no encontrado', 'warning')
    return redirect(url_for('dashboard'))

@app.route('/ciudad', methods=['POST'])
def por_ciudad():
    city = request.form.get('ciudad','').strip().lower()
    start = time.perf_counter()
    filtered = [c for c in session['clients'] if c['ciudad'].lower() == city]
    ms = round((time.perf_counter() - start)*1000, 2)
    session['tiempo'] = ms
    if not filtered:
        flash('No hay clientes en esa ciudad', 'warning')
    session['view_clients'] = filtered
    return redirect(url_for('dashboard'))

@app.route('/ordenar')
def ordenar():
    start = time.perf_counter()
    ordered = sorted(session.get('clients', []), key=lambda c: (c['edad'], c['id']))
    ms = round((time.perf_counter() - start)*1000, 2)
    session['tiempo'] = ms
    session['view_clients'] = ordered
    return redirect(url_for('dashboard'))

if __name__ == '__main__':
    app.run(debug=True)
