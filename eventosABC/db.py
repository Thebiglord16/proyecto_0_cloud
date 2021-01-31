import sqlite3

import click
from flask import current_app, g
from flask.cli import with_appcontext

"""
Metodo que retorna la instancia que representa la base de datos
"""
def get_db():
    """
    Confirma si ya existe una instancia de la base de datos asignada al objeto global de flask g,
    de lo contrario, construye una instancia de la base de datos con sqlite3 y la asigna al objeto global g
    """
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory=sqlite3.Row
    
    return g.db

"""
Metodo que remueve la base de datos del obejto global de flask g y cierra la conexión de la base de datos
"""
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

"""
Metodo que inicializa y construye la base de datos usando el archivo schema.sql
"""
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

"""
le pasa a la función decoradora de click la función que inicializa la base de datos para que esta quede 
registrada como un comando del paquete
"""
@click.command('init-db')
@with_appcontext
def init_db_command():
    """Elimina la base de datos"""
    init_db()
    click.echo('Initialized the database.')

"""
Inicializa la aplicación y construye el comando de inicializar la base de datos
"""
def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

