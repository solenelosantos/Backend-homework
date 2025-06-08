from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from flask import request, jsonify
import json
from flask import render_template
import requests
from flask import redirect
from flask_socketio import SocketIO

## usual Flask initilization
app = Flask(__name__)
VERSION = "01"
socketio = SocketIO(app)




db_name = 'note.db'
# how do we connect to the database ?
# here we say it's by looking in a file named chat.db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_name
# this variable, db, will be used for all SQLAlchemy commands
db = SQLAlchemy(app)

@app.route('/')
def hello_world():
    # redirect to /front/users
    # actually this is just a rsponse with a 301 HTTP code
    return redirect('/front/notes')


@app.route('/db/alive')
def db_alive():
    try:
        result = db.session.execute(text('SELECT 1'))
        print(result)
        return dict(status="healthy", message="Database connection is alive")
    except Exception as e:
        # e holds description of the error
        error_text = "<p>The error:<br>" + str(e) + "</p>"
        hed = '<h1>Something is broken.</h1>'
        return hed + error_text

@app.route('/api/version')
def version():
    return dict(version=VERSION)

class Note(db.Model):
    __tablename__ = 'notes'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    content = db.Column(db.String)
    done = db.Column(db.Boolean)

# actually create the database (i.e. tables etc)
with app.app_context():
    db.create_all()

@app.route('/api/notes', methods=['POST'])
def create_note():
    # we expect the user to send a JSON object
    # with the 3 fields name email and nickname
    try:
        parameters = json.loads(request.data)
        id=parameters['id']
        title = parameters['title']
        content = parameters['content']
        done = parameters.get('done') == 'true'
        
        new_note = Note(id=id, title=title, content=content, done=done)
        db.session.add(new_note)
        db.session.commit()
        return parameters
    except Exception as exc:
        return dict(error=f"{type(exc)}: {exc}"), 422

@app.route('/api/notes', methods=['GET'])
def list_notes():
    notes = Note.query.all()
    return [dict(
            id= note.id, title=note.title, content=note.content, done=note.done)
        for note in notes]

@app.route('/front/notes')
def front_notes():
  
    url = request.url_root + '/api/notes'
    req = requests.get(url)
    if not (200 <= req.status_code < 300):
        # return render_template('errors.html', error='...')
        return dict(error=f"could not request notes list", url=url,
                    status=req.status_code, text=req.text)
    notes = req.json()
    return render_template('notes.html.j2', notes=notes,  version=VERSION)


@app.route('/api/notes/<int:id>', methods=['DELETE'])
def delete_note(id):
    try:
    
        note = Note.query.get(id)
        
        if not note:
            return jsonify(error="Note not found"), 404
        
        # We delete the note
        db.session.delete(note)
        
        # We commit
        db.session.commit()
        
        return jsonify(message="Note deleted successfully"), 200
    except Exception as exc:
        
        return jsonify(error=f"{type(exc).__name__}: {exc}"), 422


@app.route('/api/notes/<int:id>/done', methods=['POST'])
def update_note_done(id):
    note = Note.query.get(id)  
    if not note:
        return jsonify({"ok": False, "status": "not found"}), 404

    done = request.json.get('done', False)
    note.done = done
    db.session.commit()

    # We send to all the browsers connected the note updated
    socketio.emit('note-updated', {
        'id': note.id,
        'done': note.done
    })

    return jsonify({"ok": True})

@socketio.on('connect-ack') # the decorator is @socketio.on instead of @app.route
def connect_ack(message): #connect_ack is the name of the channel
    print(f'received ACK message: {message} of type {type(message)}')

if __name__ == '__main__':
    socketio.run(app, debug=True,allow_unsafe_werkzeug=True)