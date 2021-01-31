from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)

from werkzeug.exceptions import abort

from eventosABC.auth import login_required
from eventosABC.db import get_db

bp = Blueprint('evento', __name__)

@bp.route('/')
@login_required
def index():
    db = get_db()
    eventos = db.execute(
        'SELECT e.id, creado, titulo, fecha, hora_inicio, author_id FROM '
        'evento e JOIN user u on e.author_id=u.id WHERE u.id =?'
        ' ORDER BY creado ASC', (g.user['id'],)
    ).fetchall()
    return render_template('eventos/index.html', eventos=eventos)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        titulo = request.form['titulo']
        fecha = request.form['fecha']
        hora_inicio = request.form['hora_inicio']
        hora_fin = request.form['hora_fin']
        descripcion = request.form['descripcion']

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
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO evento (titulo, descripcion, author_id, '
                'fecha, hora_inicio, hora_fin) values(?, ?, ?, ?, ?, ?)',
                (titulo, fecha, g.user['id'], descripcion, hora_inicio, hora_fin, )
            )
            db.commit()
            return redirect(url_for('evento.index'))
    
    return render_template('eventos/create.html')


def get_evento(id, check_author=True):
    evento = get_db().execute(
        'SELECT e.id, titulo, descripcion, creado, fecha, hora_inicio, hora_fin, author_id'
        ' FROM evento e JOIN user u ON e.author_id=u.id WHERE e.id=?', (id,)
    ).fetchone()

    if evento is None:
        abort(404, "El evento que esta buscando no existe.")
    elif check_author and evento['author_id'] != g.user['id']:
        abort(403, "No tienes perimso para ver este evento.")
    
    return evento

@bp.route('/<int:id>/detail', methods=('GET', 'POST'))
@login_required
def detail_evento(id):
    evento = get_evento(id)
    return render_template('eventos/detail.html', evento=evento)

@bp.route('/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update_evento(id):
    evento = get_evento(id)

    if request.method == 'POST':
        titulo = request.form['titulo']
        fecha = request.form['fecha']
        descripcion = request.form['descripcion']
        hora_inicio = request.form['hora_inicio']
        hora_fin = request.form['hora_fin']

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
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE evento SET titulo=?, descripcion=?,'
                'fecha=?, hora_inicio=?, hora_fin=? WHERE id=?',
                (titulo, fecha, descripcion, hora_inicio, hora_fin, evento['id'])
            )
            db.commit()
            return redirect(url_for('evento.index'))
        
    return render_template('eventos/update.html', evento=evento) 

@bp.route('/<int:id>/delete', methods=('POST',))
@login_required
def delete_evento(id):
    db = get_db()
    get_evento(id)
    db.execute('DELETE FROM evento WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('evento.index'))



