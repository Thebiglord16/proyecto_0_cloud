from flask import (
    Blueprint, g, request, session, jsonify, json
)

from werkzeug.security import check_password_hash, generate_password_hash

from eventosABC.auth import login_required
from eventosABC.db import get_db
from eventosABC.evento import get_evento

bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/registrar', methods=('POST',))
def registrar():
    """
    en caso de ser una solicitud de post, intenta registrar al usuario dado que ponga una dirección email valida
    y una contraseña que no este vacia. De ser exitoso el registro lo redirecciona a la página de login.

    En caso de ser una solicitud get retorna la plantilla correspondiente al formulario de registro.
    """
    content = request.get_json()
    email = content['email']
    password = content['password']
    db = get_db()
    error = None

    if not email or email.find('@') == -1:
        error = "Dirección de correo faltante o invalida"
    if not password:
        error = "Se requiere una contraseña"
    elif db.execute(
        'SELECT id FROM user where email = ?', (email,)
    ).fetchone() is not None:
        error = "ya existe un usuario registrado con el correo electónico {}".format(email)

    if error is None:
        db.execute(
            'INSERT INTO user (email, password) values (?,?)', (email, generate_password_hash(password))
        )
        db.commit()

        return jsonify(content)
        
    return jsonify(error)

"""
Construye la ruta para que un usuario ingrese a la aplicación web
"""
@bp.route('/login', methods=('POST',))
def login():
    """
    en caso de ser una solicitud de post, intenta ingresar al usuario dado que ponga una dirección email valida,
    una contraseña que no este vacia y se haya registrado previamente, de lograr el ingreso lo redirecciona a sus eventos

    En caso de ser una solicitud get retorna la plantilla correspondiente al formulario de ingreso.
    """
    content = request.get_json()
    email = content['email']
    password = content['password']
    db = get_db()
    error = None

    if not email or email.find('@') == -1:
        error = "Dirección de correo faltante o invalida"
    if not password:
        error = "Se requiere una contraseña"
    else:
        user = db.execute(
            'SELECT * FROM user WHERE email = ?', (email,)
        ).fetchone()
        
        if user is None:
            error = 'correo o contraseña incorrectos'
        elif not check_password_hash(user['password'], password):
            error = 'correo o contraseña incorrectos'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return jsonify("Ingreso correctamente a la aplicación mediante el API")
    return jsonify(error)


@bp.route('/eventos', methods=('GET',))
@login_required
def get_eventos():
    db = get_db()
    eventos = db.execute(
        'SELECT e.id, creado, titulo, fecha, hora_inicio, author_id FROM '
        'evento e JOIN user u on e.author_id=u.id WHERE u.id =?'
        ' ORDER BY creado ASC', (g.user['id'],)
    ).fetchall()

    return jsonify([dict(evento) for evento in eventos])

@bp.route('/eventos/create', methods=('POST',))
@login_required
def create_evento():
    content = request.get_json()
    titulo = content['titulo']
    fecha = content['fecha']
    hora_inicio = content['hora_inicio']
    hora_fin = content['hora_fin']
    descripcion = content['descripcion']

    error = None

    if not titulo:
        error = "Es necesario llenar todos los campos"
    if not fecha:
        error = "Es necesario llenar todos los campos"
    if not descripcion:
        error = "Es necesario llenar todos los campos"
    if not hora_inicio:
        error = "Es necesario llenar todos los campos"
    if not hora_fin:
        error = "Es necesario llenar todos los campos"
    
    if error is not None:
        return jsonify(error)
    
    else:
        db = get_db()
        db.execute(
            'INSERT INTO evento (titulo, descripcion, author_id, '
            'fecha, hora_inicio, hora_fin) values(?, ?, ?, ?, ?, ?)',
            (titulo, fecha, g.user['id'], descripcion, hora_inicio, hora_fin, )
        )
        db.commit()
        return jsonify('se agrego el evento al usuario ? correctamente', (g.user['id'],))

@bp.route('/eventos/<int:id>', methods=('GET',))
@login_required
def detail_evento(id):
    evento = get_evento(id)
    return jsonify(dict(evento))

@bp.route('/eventos/<int:id>', methods=('PUT',))
@login_required
def update_evento(id):
    content = request.get_json()
    titulo = content['titulo']
    fecha = content['fecha']
    hora_inicio = content['hora_inicio']
    hora_fin = content['hora_fin']
    descripcion = content['descripcion']
    evento_viejo = get_evento(id)
    error = None

    if not titulo:
        titulo = evento_viejo['titulo']
    if not fecha:
        fecha = evento_viejo['fecha']
    if not descripcion:
        descripcion = evento_viejo['descripcion']
    if not hora_inicio:
        hora_inicio = evento_viejo['hora_inicio']
    if not hora_fin:
        hora_fin = evento_viejo['hora_fin']
    
    if error is not None:
        return jsonify(error)
    
    else:
        db = get_db()
        db.execute(
            'UPDATE evento SET titulo=?, descripcion=?,'
            'fecha=?, hora_inicio=?, hora_fin=? WHERE id=?',
            (titulo, descripcion, fecha, hora_inicio, hora_fin, evento_viejo['id'])
        )
        db.commit()
        return jsonify('se actualizo el evento correctamente', dict(get_evento(id)))

@bp.route('/eventos/<int:id>', methods=('DELETE',))
@login_required
def delete_evento(id):
    db = get_db()
    get_evento(id)
    db.execute('DELETE FROM evento WHERE id = ?', (id,))
    db.commit()
    return jsonify('se eliminó el evento correctamente')