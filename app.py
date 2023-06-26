from flask import Flask,flash,render_template, request, redirect 
from flaskext.mysql import MySQL
from flask import send_from_directory
from datetime import datetime
import os

 

app= Flask(__name__)
app.secret_key="Masiv"

MySQL= MySQL()
app.config['MYSQL_DATABASE_HOST']='localhost'
app.config['MYSQL_DATABASE_USER']='root'
app.config['MYSQL_DATABASE_PASSWORD']=''
app.config['MYSQL_DATABASE_DB']='project'
MySQL.init_app(app)

CARPETA= os.path.join('uploads')
app.config['CARPETA']=CARPETA

@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'],nombreFoto)

@app.route("/")
def index():

    sql = "SELECT * FROM `empleados`;"
    conn= MySQL.connect()
    cursor= conn.cursor()
    cursor.execute(sql)
    empleados=cursor.fetchall()
 
    conn.commit()

    return render_template('empleados/index.html', empleados=empleados)

@app.route('/delete/<int:id>')
def delete(id):
    conn = MySQL.connect()
    cursor = conn.cursor()

    # Obtener el nombre del archivo a eliminar
    cursor.execute("SELECT foto FROM empleados WHERE id=%s", (id,))
    fila = cursor.fetchone()
    foto = fila[0] if fila else None

    # Eliminar el registro de la base de datos
    cursor.execute("DELETE FROM empleados WHERE id=%s", (id,))
    conn.commit()

    # Eliminar el archivo si existe
    if foto:
        ruta_archivo = os.path.join(app.config['CARPETA'], foto)
        if os.path.exists(ruta_archivo):
            os.remove(ruta_archivo)

    # Verificar si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM empleados")
    count = cursor.fetchone()[0]

    if count == 0:
        # Reiniciar el autoincremento del ID a 1
        cursor.execute("ALTER TABLE empleados AUTO_INCREMENT = 1")
        conn.commit()

    return redirect('/')

@app.route('/edit/<int:id>')
def edit(id):
    conn=MySQL.connect()
    cursor=conn.cursor()

    cursor.execute("SELECT * FROM empleados WHERE id=%s",(id))

    empleados=cursor.fetchall()
    conn.commit()
    print(empleados)
    return render_template('empleados/edit.html',empleados=empleados)

@app.route('/update', methods=['POST'])
def update():

    _nombre=request.form["txtNombre"]
    _correo=request.form["txtCorreo"]
    _foto=request.files["txtFoto"]
    id=request.form['txtID']

    if not _nombre or not _correo:
        return render_template('empleados/edit.html')

    sql = "UPDATE empleados SET nombre=%s, correo=%s WHERE id=%s;"
    datos=(_nombre,_correo,id)

    conn=MySQL.connect()
    cursor=conn.cursor()

    now= datetime.now()
    tiempo=now.strftime("%Y%H%M%S")

    if _foto.filename!='':

        nuevoNombreFoto=tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)

        cursor.execute("SELECT foto FROM empleados WHERE id=%s", id)
        fila=cursor.fetchall()

        os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))
        cursor.execute("UPDATE empleados SET foto=%s WHERE id=%s",(nuevoNombreFoto, id))
        conn.commit()


    cursor.execute(sql,datos)
    conn.commit()
    return redirect('/') 

@app.route('/create')
def create():
    return render_template('empleados/create.html')

@app.route('/store', methods=['POST'])
def storage():
    _nombre=request.form["txtNombre"]
    _correo=request.form["txtCorreo"]

    _foto=request.files["txtFoto"]

    if not _nombre or not _correo or not _foto:
        flash("Debe llenar todos los campos")
        return render_template('empleados/create.html')
    

    now= datetime.now()
    tiempo=now.strftime("%Y%H%M%S")


    if _foto.filename!='':
        nuevoNombreFoto=tiempo+_foto.filename
        _foto.save("uploads/"+nuevoNombreFoto)

    sql = "INSERT INTO `empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL,%s, %s, %s);"
    datos=(_nombre,_correo,nuevoNombreFoto)

    conn= MySQL.connect()
    cursor= conn.cursor()
    cursor.execute(sql,datos)
    conn.commit()

    return redirect('/')


if __name__== '__main__':
    app.run(debug=True)