from flask import Flask, render_template, request, redirect, url_for, flash, session
import numpy as np
import os

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

DATOS_PRUEBA = {
    'matriz': [
        [0, 15, 24, 36, 56, 42, 35, 38, 20, 8],
        [15, 0, 15, 27, 47, 33, 44, 47, 35, 23],
        [24, 15, 0, 12, 32, 18, 29, 32, 44, 16],
        [36, 27, 12, 0, 20, 30, 41, 44, 56, 28],
        [56, 47, 32, 20, 0, 39, 50, 25, 43, 48],
        [42, 33, 18, 30, 39, 0, 11, 14, 26, 34],
        [35, 44, 29, 41, 50, 11, 0, 25, 15, 43],
        [38, 47, 32, 44, 25, 14, 25, 0, 18, 46],
        [20, 35, 44, 56, 43, 26, 15, 18, 0, 28],
        [8, 23, 16, 28, 48, 34, 43, 46, 28, 0]
    ],
    'demandas': [8, 10, 7, 12, 6, 9, 5, 8, 11, 6],
    'costos_fijos': [50, 30, 60, 20, 40, 80, 40, 30, 70, 80],
    'costo_por_km': 0.15
}

@app.route('/')
def index():
    session.clear()
    return render_template('index.html')


@app.route('/configurar_matriz', methods=['POST'])
def configurar_matriz():
    try:
        filas = int(request.form['filas'])
        columnas = int(request.form['columnas'])

        if filas <= 0 or columnas <= 0:
            flash("Debe ingresar valores positivos", "error")
            return redirect(url_for('index'))

        session['filas'] = filas
        session['columnas'] = columnas
        session['matriz'] = [[0 for _ in range(columnas)] for _ in range(filas)]

        return render_template('editar_matriz.html',
                               filas=filas,
                               columnas=columnas,
                               matriz=session['matriz'])
    except ValueError:
        flash("Ingrese números válidos", "error")
        return redirect(url_for('index'))

@app.route('/actualizar_matriz', methods=['POST'])
def actualizar_matriz():
    try:
        filas = session['filas']
        columnas = session['columnas']
        nueva_matriz = []

        for i in range(filas):
            fila = []
            for j in range(columnas):
                valor = float(request.form[f'matriz_{i}_{j}'])
                if valor < 0:
                    flash("Distancias no pueden ser negativas", "error")
                    return redirect(url_for('configurar_matriz'))
                fila.append(valor)
            nueva_matriz.append(fila)

        session['matriz'] = nueva_matriz
        return redirect(url_for('ingresar_parametros'))

    except ValueError:
        flash("Valores numéricos inválidos", "error")
        return redirect(url_for('configurar_matriz'))

@app.route('/ingresar_parametros')
def ingresar_parametros():
    if 'matriz' not in session:
        return redirect(url_for('index'))

    return render_template('ingresar_parametros.html',
                           filas=len(session.get('matriz', [])),
                           columnas=len(session.get('matriz', [[]])[0]))

@app.route('/procesar_parametros', methods=['POST'])
def procesar_parametros():
    try:
        session['demandas'] = [float(request.form[f'demanda_{j}'])
                                    for j in range(session['columnas'])]
        session['costos_fijos'] = [float(request.form[f'costo_fijo_{i}'])
                                        for i in range(session['filas'])]
        session['costo_por_km'] = float(request.form['costo_por_km'])

        return redirect(url_for('mostrar_resultados'))
    except ValueError:
        flash("Ingrese valores numéricos válidos", "error")
        return redirect(url_for('ingresar_parametros'))
    
@app.route('/ejecutar_algoritmo')
def ejecutar_algoritmo():
    # Asumimos que los datos del formulario ya están en la sesión
    # después de pasar por /procesar_parametros
    return redirect(url_for('mostrar_resultados'))

@app.route('/cargar_datos_prueba')
def cargar_datos_prueba():
    session.clear()
    session.update(DATOS_PRUEBA)
    session['filas'] = len(DATOS_PRUEBA['matriz'])
    session['columnas'] = len(DATOS_PRUEBA['matriz'][0])
    return redirect(url_for('mostrar_resultados'))

@app.route('/ejecutar_con_datos_prueba')
def ejecutar_con_datos_prueba():
    session.clear()
    session.update(DATOS_PRUEBA)
    session['filas'] = len(DATOS_PRUEBA['matriz'])
    session['columnas'] = len(DATOS_PRUEBA['matriz'][0])
    return redirect(url_for('mostrar_resultados'))

@app.route('/mostrar_resultados')
def mostrar_resultados():
    try:
        from algoritmo_drop import algoritmo_drop
        
        print(f"Sesión al entrar a mostrar_resultados: {session}") # Debug

        if not all(key in session for key in ['matriz', 'demandas', 'costos_fijos', 'costo_por_km']):
            flash("Faltan datos necesarios", "error")
            return redirect(url_for('index'))

        matriz_np = np.array(session['matriz'])
        demandas = session['demandas']
        costos_fijos = session['costos_fijos']
        costo_por_km = session['costo_por_km']

        costos_variables = [
            [float(demandas[j] * matriz_np[i][j] * costo_por_km)
             for j in range(len(demandas))]
            for i in range(len(costos_fijos))
        ]

        instalaciones, costo = algoritmo_drop(costos_variables, costos_fijos)

        print(f"Resultados calculados: {instalaciones}, {costo}")  # Debug

        resultados = {
            'instalaciones_abiertas': instalaciones,
            'costo_total': round(costo, 2),
            'matriz_costos': session['matriz'],
            'demandas': demandas,
            'costos_fijos': costos_fijos,
            'costo_por_km': costo_por_km
        }

        return render_template('results.html', resultados=resultados)

    except Exception as e:
        print(f"Error en mostrar_resultados: {str(e)}")  # Debug
        flash(f"Error al mostrar resultados: {str(e)}", "error")
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)