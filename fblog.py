import sqlite3
import os
from flask import Flask, request, session, g, redirect, \
    url_for, abort, render_template, flash

from config import setting as s

app = Flask(__name__)
app.config.from_object(__name__)


app.config.update(s)
app.config.from_envvar('FBLOG_SETTING', silent=True)

print(s)
print(app.config)

def connect_db():
    """ Производим соединение с указанной БД. """
    bd = sqlite3.connect(app.config['DATABASE'])
    bd.row_factory = sqlite3.Row
    return bd


def get_db():
    """ Если нет соединение с БД, то открываем
    новое соединение. """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_db(error):
    """Закрываем соединение когда происходит разрыв
     контекста приложения"""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close


def init_db():
    """  """
    with app.app_context():
        db = get_db()
        with app.open_resource('schema.sql', mode='r') as f:
            db.cursor().executescript(f.read())
        db.commit()


@app.route('/')
def show_entries():
    """показываем записи"""
    db = get_db()
    cur = db.execute('select title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('entries.html', entries=entries)


def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values(?, ?)',
               [request.form['title'], request.form['text']])
    db.commit()
    flash('Новая запись была полностью загружена')
    return redirect(url_for('show_entries'))

def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = 'Не правильное имя пользователя'
        elif request.form['password'] != app.config['PASSWORD']:
            error = 'Не правильный пароль'
        else:
            session['logged_in'] = True
            flash('Вы вошли')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)

def logout():
    session.pop('logged_in', None)
    flash('Вы вышли')
    return redirect(url_for('show_entries'))


if __name__ == "__main__":
    app.run()