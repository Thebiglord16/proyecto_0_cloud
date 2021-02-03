import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)

from werkzeug.security import check_password_hash, generate_password_hash

from eventosABC.db import get_db

"""Define el blueprint al que corresponde la url"""
bp = Blueprint('auth', __name__, url_prefix='/auth')

"""
construye la ruta para que un usuario se registre en la aplicación web
"""
@bp.route('/registrar', methods=('GET', 'POST'))
def registrar():
    """
    en caso de ser una solicitud de post, intenta registrar al usuario dado que ponga una dirección email valida
    y una contraseña que no este vacia. De ser exitoso el registro lo redirecciona a la página de login.

    En caso de ser una solicitud get retorna la plantilla correspondiente al formulario de registro.
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
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

            return redirect(url_for('auth.login'))
        
        flash(error)
    return render_template('auth/registrar.html')

"""
Construye la ruta para que un usuario ingrese a la aplicación web
"""
@bp.route('/login', methods=('GET', 'POST'))
def login():
    """
    en caso de ser una solicitud de post, intenta ingresar al usuario dado que ponga una dirección email valida,
    una contraseña que no este vacia y se haya registrado previamente, de lograr el ingreso lo redirecciona a sus eventos

    En caso de ser una solicitud get retorna la plantilla correspondiente al formulario de ingreso.
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None

        if not email or email.find('@') == -1:
            error = "Dirección de correo faltante o invalida"
        if not password:
            error = "Se requiere una contraseña"
        else:
            user = db.execute(
                'SELECT * FROM user where email = ?', (email,)
            ).fetchone() 
        
            if user is None:
                error = 'correo o contraseña incorrectos'
            elif not check_password_hash(user['password'], password):
                error = 'correo o contraseña incorrectos'

            if error is None:
                session.clear()
                session['user_id'] = user['id']
                return redirect(url_for('index'))

        flash(error)

    return render_template('auth/login.html')

"""
asigna el usuario al objeto global g, el decorador permita que lo haga antes de cada operación que requiera 
haber ingresado a la aplicacion
"""
@bp.before_app_request
def cargar_usuario():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id=?', (user_id,)
        ).fetchone()


"""
Permite salir del sistema si previamente se ha ingresado
"""
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

"""
construte un decorador para las acciones que requieran que el usuario este registrado en la aplicacion
"""
def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)

    return wrapped_view

