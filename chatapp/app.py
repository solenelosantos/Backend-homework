from flask import Flask

## usual Flask initilization
app = Flask(__name__)
VERSION = "01"


from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from flask import request
import json
from flask import render_template
import requests
from flask import redirect
from datetime import datetime as DateTime
from sqlalchemy.sql import or_

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
        title = parameters['title']
        content = parameters['content']
        done = parameters.get('done') == 'true'
        
        new_note = Note(title=title, content=content, done=done)
        db.session.add(new_note)
        db.session.commit()
        return parameters
    except Exception as exc:
        return dict(error=f"{type(exc)}: {exc}"), 422

@app.route('/api/notes', methods=['GET'])
def list_notes():
    notes = Note.query.all()
    return [dict(
            title=note.title, content=note.content, done=note.done)
        for note in notes]

if __name__ == '__main__':
    app.run()