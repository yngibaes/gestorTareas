from flask import Flask, render_template, request, redirect, url_for, session, send_file
import mysql.connector
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer
from itsdangerous.exc import BadSignature
import matplotlib.pyplot as plt

app = Flask(__name__)

#Falta poner todo en bootstrap, tmb hacer el buscar para los usuarios de admin, y las tareas del usuario.

#Configurar conección

app.secret_key='030993'
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
db = mysql.connector.connect(
    host="localhost",
    user = "root",
    password = "",
    database = "gestionTareas"
)

cursor = db.cursor()
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'mariasssa21@gmail.com'
app.config['MAIL_PASSWORD'] = 'apfz rjxf hgxh yztg'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_DEFAULT_SENDER'] = ('Anita Monita', 'mariasssa21@gmail.com')
mail = Mail(app)

@app.route('/', methods=['GET', 'POST'])
def iniciarSesion():
    if request.method == 'POST':  
        usuarioUsu = request.form.get('usuarioUsu')
        contraUsu = request.form.get('contraUsu')

        cursor = db.cursor(dictionary=True)
        query = "SELECT usuarioUsu, contraUsu, rolUsu, idUsuario FROM usuario WHERE usuarioUsu = %s"
        cursor.execute(query, (usuarioUsu,))
        usuario = cursor.fetchone()

        if (usuario and check_password_hash(usuario['contraUsu'], contraUsu)):
            #Crear una sesión
            session['usuarioUsu'] = usuario['usuarioUsu']
            session['rolUsu'] = usuario['rolUsu']
            session['idUsuario'] = usuario['idUsuario']

            if usuario['rolUsu'] == 'Administrador':
                return render_template('admin.html', usuarioUsu=usuarioUsu) 
            else:
                return render_template('usuario.html', usuarioUsu=usuarioUsu)
        return render_template('registroUsuario.html')
    else:
        print('Usuario o contraseña incorrecta, intentar de nuevo')
        return render_template('index.html')

@app.route('/registroUsuario', methods=['GET', 'POST'])
def registrarUsuario():
    if request.method == 'POST':
        nombreUsu = request.form['nombreUsu']
        apellidoUsu = request.form['apellidoUsu']
        emailUsu = request.form['emailUsu']
        usuarioUsu = request.form['usuarioUsu']
        contraUsu = request.form['contraUsu']
        rolUsu = request.form['rolUsu']
        encrip = generate_password_hash(contraUsu)

        cursor = db.cursor()
        cursor.execute("SELECT * from usuario WHERE usuarioUsu = %s or emailUsu = %s",(usuarioUsu, emailUsu,))
        usuario = cursor.fetchone()
        if usuario:
            print("Usuario ya existe")
            return render_template('index.html')
        else:
            cursor.execute("INSERT INTO usuario (nombreUsu, apellidoUsu, emailUsu, usuarioUsu, contraUsu, rolUsu) VALUES (%s, %s, %s, %s, %s, %s)", (nombreUsu, apellidoUsu, emailUsu, usuarioUsu, encrip, rolUsu))
            db.commit()
            print('Usuario registrado')
        return render_template('index.html')
    else:
        print('No se ha podido registrar el usuario')
    return render_template('registroUsuario.html')

def enviarCorreo(email):
    #Genera token para el correo
    token = serializer.dumps(email, salt='Restablecimiento de contraseña')

    #Se crea la URL
    enlace = url_for('restablecerContraseña', token=token, _external=True)

    #Se crea mensaje para enviar al correo
    mensaje = Message(subject='Restablecer Contraseña', recipients = [email], body=f'Para restablecer contraseña, haga click en el siguiente enlace:{enlace}')
    mail.send(mensaje)

@app.route('/restablecerContraseña/<token>', methods=['GET', 'POST'])
def restablecerContraseña(token):
    try:
        email = serializer.loads(token, salt='Restablecimiento de contraseña', max_age=50000)
        if request.method == 'POST':
            newContra = request.form['NewContra']
            conContra = request.form['conContra']

            #Verificar las contraseñas
            if newContra != conContra :
                return 'Contraseñas no coinciden'
            else: 
                passwordnuevo = generate_password_hash(newContra)
                cursor = db.cursor()
                query = 'UPDATE usuario SET contraUsu = %s WHERE emailUsu = %s'
                cursor.execute(query, (passwordnuevo, email))
                db.commit()
                return redirect(url_for('iniciarSesion'))
    except BadSignature:
        return 'Enlace expirado'
    return render_template('restablecerContraseña.html')

@app.route('/olvidarContraseña', methods=['GET', 'POST'])
def olvidarContraseña():
    if request.method == 'POST':
        email = request.form['email']
        enviarCorreo(email)
        return redirect(url_for('iniciarSesion'))
    return render_template('olvidarContraseña.html')

#ADMIN
@app.route('/adminUsuarios', methods=['GET', 'POST'])
def adminUsuarios():
    if 'rolUsu' in session and session['rolUsu'] == 'Administrador':
        cursor = db.cursor()
        cursor.execute("SELECT * FROM usuario")  # Ejecuta la consulta de todos los usuarios
        usuarios = cursor.fetchall()  # Obtiene todos los resultados
    return render_template('adminUsuarios.html', usuarios=usuarios)  # Pasa los resultados a la plantilla

@app.route('/eliminarUsuarios/<int:id>', methods=['GET'])
def eliminarUsuario(id):
    cursor = db.cursor()
    cursor.execute('DELETE FROM usuario WHERE idUsuario= %s',(id,))
    db.commit()
    return redirect(url_for('adminUsuarios'))

@app.route('/editarUsuario/<int:id>', methods=['GET', 'POST'])
def editarUsuario(id):
    cursor.execute('SELECT * FROM usuario WHERE idUsuario = %s',(id,))
    usuario = cursor.fetchall()
    if request.method == 'POST':
        nombreUsu = request.form['nombreUsu']
        apellidoUsu = request.form['apellidoUsu']
        emailUsu = request.form['emailUsu']
        usuarioUsu = request.form['usuarioUsu']
        rolUsu = request.form['rolUsu']
        sql= "UPDATE usuario SET nombreUsu = %s, apellidoUsu = %s, emailUsu = %s, usuarioUsu = %s, rolUsu = %s WHERE idUsuario = %s"
        cursor.execute(sql, (nombreUsu, apellidoUsu, emailUsu, usuarioUsu, rolUsu, id))
        db.commit()
        return redirect(url_for('adminUsuarios'))
    else:
        return render_template("adminAcUsu.html" , usuario=usuario[0])

@app.route('/adminTareas', methods=['GET', 'POST'])
def adminTareas():
    if 'rolUsu' in session and session['rolUsu'] == 'Administrador':
        cursor = db.cursor()
        cursor.execute("SELECT idTareas, usuarioUsu, nombreTar, fechaInicio, fechaFin, estadoTar from usuario INNER JOIN tareas ON usuario.IdUsuario = tareas.fkUsuario")  
        tareas = cursor.fetchall()  # Obtiene todos los resultados
    return render_template('adminTareas.html', tareas=tareas)  # Pasa los resultados a la plantilla

@app.route('/eliminarTareas/<int:id>', methods=['GET'])
def eliminarTareas(id):
    cursor = db.cursor()
    cursor.execute('DELETE FROM tareas WHERE idTareas= %s',(id,))
    db.commit()
    return redirect(url_for('adminTareas'))

@app.route('/editarTareas/<int:id>', methods=['GET', 'POST'])
def editarTareas(id):
    cursor = db.cursor()
    cursor.execute('SELECT idTareas, usuarioUsu, nombreTar, fechaInicio, fechaFin, estadoTar FROM usuario INNER JOIN tareas ON usuario.idUsuario = tareas.fkUsuario WHERE idTareas = %s',(id,))
    tarea = cursor.fetchone()  # Use fetchone() instead of fetchall() to get a single row
    if tarea is not None:  # Check if tarea is not None before accessing its properties
        nombreTar = request.form['nombreTar']
        fechaInicio = request.form['fechaInicio']
        fechaFin = request.form['fechaFin']
        estadoTar = request.form['estadoTar']
        sql= "UPDATE tareas SET nombreTar = %s, fechaInicio = %s, fechaFin = %s, estadoTar = %s WHERE idTareas = %s"
        cursor.execute(sql, (nombreTar, fechaInicio, fechaFin, estadoTar, id))
        db.commit()
        return redirect(url_for('adminTareas'))
    else:
        return render_template("adminAcTareas.html" , tarea=tarea[0])

@app.route('/adminRTareas', methods=['GET', 'POST'])
def adminRtareas():
    """Registrar Tareas"""
    if request.method == 'POST':
        #Capturar datos de la base de datos
        usuarioUsu = request.form['usuarioUsu']
        nombreTar = request.form['nombreTar']
        fechaInicio = request.form['fechaInicio']
        fechaFin = request.form['fechaFin']
        estadoTar = request.form['estadoTar']
        cursor = db.cursor()

        print(usuarioUsu)
        query = "SELECT idUsuario FROM usuario WHERE usuarioUsu = %s"
        cursor.execute(query,(usuarioUsu,))
        idUsuario = cursor.fetchone()[0]
        print(idUsuario)

        #Verificar el nombre de la tarea no este registrado
        cursor.execute("SELECT * from tareas WHERE nombreTar = %s",(nombreTar,))
        tarea = cursor.fetchone()
        if tarea:
            print("Tarea ya existe")
            return render_template('adminRtareas.html')
        else:
            #Enviar datos de la tarea
            cursor.execute("INSERT INTO tareas (nombreTar, fechaInicio, fechaFin, estadoTar, fkUsuario) VALUES (%s, %s, %s, %s, %s)", (nombreTar, fechaInicio, fechaFin, estadoTar, idUsuario))
            db.commit()
            return render_template('adminRtareas.html')
    else:
        print('No se ha podido registrar la tarea')

    return render_template('adminRtareas.html') #Carga vista html

@app.route('/buscar', methods=['GET', 'POST'])
def buscarTarea():
    if request.method == 'POST':
        idUsuario = session['idUsuario']
        buscar = request.form['buscar']
        cursor = db.cursor(dictionary=True)
        
        # Verifica el rol del usuario
        if session['rolUsu'] == 'Administrador':
            # Si el usuario es un administrador, busca todas las tareas
            cursor.execute("SELECT idTareas, usuarioUsu, nombreTar, fechaInicio, fechaFin, estadoTar from usuario INNER JOIN tareas ON usuario.IdUsuario = tareas.fkUsuario WHERE nombreTar LIKE %s", ('%' + buscar + '%',))
            tareas = cursor.fetchall()
        else:
            # Si el usuario no es un administrador, solo busca sus propias tareas
            cursor.execute("SELECT idTareas, usuarioUsu, nombreTar, fechaInicio, fechaFin, estadoTar from usuario INNER JOIN tareas ON usuario.IdUsuario = tareas.fkUsuario WHERE nombreTar LIKE %s AND usuario.IdUsuario = %s", ('%' + buscar + '%', idUsuario,))
            tareasUsu = cursor.fetchall()
            return render_template('usuarioResTareas.html', tareas=tareasUsu, buscar=buscar)
        usuarios = []
        if not tareas:
            cursor.execute("SELECT idUsuario, nombreUsu, apellidoUsu, emailUsu, usuarioUsu, contraUsu, rolUsu from usuario WHERE nombreUsu LIKE %s", ('%' + buscar + '%',))
            usuarios = cursor.fetchall()
            return render_template('adminResUsu.html', usuarios=usuarios, buscar=buscar)
        return render_template('adminResTareas.html', tareas=tareas, buscar=buscar)
    else:
        return redirect(url_for('buscarTarea'))

@app.route('/estadisAdmin', methods=['GET'])
def estadisAdmin():
    cursor = db.cursor()

    cursor.execute('SELECT * FROM usuario')
    usuario = cursor.fetchall()

    cursor.execute('SELECT * FROM tareas')
    tareas = cursor.fetchall()

    cursor.execute('SELECT * FROM tareas WHERE estadoTar="Pendiente"')
    tareas_pendientes = cursor.fetchall()

    cursor.execute('SELECT * FROM tareas WHERE estadoTar="Completado"')
    tareas_completadas = cursor.fetchall()

    num_usuarios = len(usuario) if usuario is not None else 0
    num_tareas = len(tareas) if tareas is not None else 0
    num_tareas_pendientes = len(tareas_pendientes) if tareas_pendientes is not None else 0
    num_tareas_completadas = len(tareas_completadas) if tareas_completadas is not None else 0

    cate = ['Usuarios', 'Tareas', 'Completados', 'Pendientes']
    count = [num_usuarios, num_tareas, num_tareas_completadas, num_tareas_pendientes]
    bar_colors = ['tab:brown', 'tab:purple', 'tab:pink', 'tab:cyan']

    plt.bar(cate, count, color=bar_colors)
    plt.ylabel('Número')
    plt.title('Estadística')
    plt.show()
    return render_template('admin.html')


#Usuarios
@app.route('/usuTareas', methods=['GET', 'POST'])
def usuTareas():
    if 'rolUsu' in session and session['rolUsu'] == 'Usuario':
        idUsuario = session['idUsuario']
        cursor = db.cursor()
        query = ("SELECT * from tareas WHERE fkUsuario = %s")
        cursor.execute(query,(idUsuario,))
        tareasUsu = cursor.fetchall()  # Obtiene todos los resultados
        print(tareasUsu)
    return render_template('usuarioTareas.html', tareasUsu=tareasUsu)  # Pasa los resultados a la plantilla

@app.route('/usuEliminarTareas/<int:id>', methods=['GET'])
def usuEliminarTareas(id):
    cursor = db.cursor()
    cursor.execute('DELETE FROM tareas WHERE idTareas= %s',(id,))
    db.commit()
    return redirect(url_for('usuTareas'))

@app.route('/usuEditarTareas/<int:id>', methods=['GET', 'POST'])
def usuEditarTareas(id):
    idUsuario = session['idUsuario']
    cursor = db.cursor()
    cursor.execute('SELECT * FROM tareas WHERE idTareas = %s AND fkUsuario = %s',(id, idUsuario,))
    tarea = cursor.fetchall()
    print(tarea)
    if request.method == 'POST':
        nombreTar = request.form['nombreTar']
        fechaInicio = request.form['fechaInicio']
        fechaFin = request.form['fechaFin']
        estadoTar = request.form['estadoTar']
        sql= "UPDATE tareas SET nombreTar = %s, fechaInicio = %s, fechaFin = %s, estadoTar = %s WHERE idTareas = %s"
        cursor.execute(sql, (nombreTar, fechaInicio, fechaFin, estadoTar, id))
        db.commit()
        return redirect(url_for('usuTareas'))
    else:
        return render_template("usuarioAcTareas.html" , tarea=tarea[0])

@app.route('/usuRTareas', methods=['GET', 'POST'])
def usuRTareas():
    """Registrar Tareas"""
    if request.method == 'POST':
        #Capturar datos de la base de datos
        idUsuario = session['idUsuario']
        nombreTar = request.form['nombreTar']
        fechaInicio = request.form['fechaInicio']
        fechaFin = request.form['fechaFin']
        estadoTar = request.form['estadoTar']
        cursor = db.cursor()

        #Verificar el nombre de la tarea no este registrado
        cursor.execute("SELECT * from tareas WHERE nombreTar = %s",(nombreTar,))
        tarea = cursor.fetchone()
        if tarea:
            print("Tarea ya existe")
            return redirect(url_for('usuTareas'))
        else:
            #Enviar datos de la tarea
            cursor.execute("INSERT INTO tareas (nombreTar, fechaInicio, fechaFin, estadoTar, fkUsuario) VALUES (%s, %s, %s, %s, %s)", (nombreTar, fechaInicio, fechaFin, estadoTar, idUsuario))
            db.commit()
            return redirect(url_for('usuTareas'))
    else:
        print('No se ha podido registrar la tarea')

    return render_template('usuarioRtareas.html') #Carga vista html

@app.route('/estadisUsu', methods=['GET'])
def estadisusu():
    cursor = db.cursor()
    idUsuario = session['idUsuario']
    cursor.execute('SELECT * FROM tareas WHERE estadoTar="Pendiente" AND fkUsuario = %s',(idUsuario,))
    tareas_pendientes = cursor.fetchall()

    cursor.execute('SELECT * FROM tareas WHERE estadoTar="Completado" AND fkUsuario = %s',(idUsuario,))
    tareas_completadas = cursor.fetchall()

    num_tareas_pendientes = len(tareas_pendientes)  if tareas_pendientes is not None else 0
    num_tareas_completadas = len(tareas_completadas) if tareas_completadas is not None else 0

    cate = ['Completado', 'Pendientes']
    count = [num_tareas_completadas, num_tareas_pendientes]
    bar_colors = ['tab:purple', 'tab:pink']

    plt.bar(cate, count, color=bar_colors)
    plt.ylabel('Número')
    plt.title('Estadística')
    plt.show()
    return render_template('usuario.html')

@app.route('/logOut', methods=['GET', 'POST'])
def logOut():
    session.pop('usuarioUsu', None)
    return redirect(url_for('iniciarSesion'))

#No almacenar el cache de la pagina 
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-cache,no-store,must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = 0 
    return response

if __name__ == '__main__':
    app.run(debug=True)
    app.add_url_rule('/', view_func=iniciarSesion)