import pathlib as pl

import numpy as np
import pandas as pd

from flask import Flask, jsonify, request
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

data = pl.Path(__file__).parent.absolute() / 'data'

# Charger les données CSV
associations_df = pd.read_csv(data / 'associations_etudiantes.csv')
evenements_df = pd.read_csv(data / 'evenements_associations.csv')

## Vous devez ajouter les routes ici : 
@app.route('/api/alive', methods=['GET'])
def alive():
    return jsonify({"message": "Alive"}), 200

@app.route('/api/associations', methods=['GET'])
def get_all_associations():
    associations_list = associations_df.to_dict(orient='records')
    return jsonify(associations_list)

@app.route('/api/association/<int:id>', methods=['GET'])
def get_association_details(id):
    associations_list = associations_df.to_dict(orient='records')
    for asso in associations_list:
        if int(asso['id'])==id:
            return jsonify(asso)
    return jsonify({"error": "Association not found"}), 404

@app.route('/api/evenements', methods=['GET'])
def get_all_evenements():
    evenements_list = evenements_df.to_dict(orient='records')
    return jsonify(evenements_list)

@app.route('/api/evenement/<int:id>', methods=['GET'])
def get_evenement_details(id):
    evenements_list = evenements_df.to_dict(orient='records')
    for event in evenements_list:
        if int(event['id'])==id:
            return jsonify(event)
    return jsonify({"error": "Event not found"}), 404

@app.route('/api/association/<int:id>/evenements', methods=['GET'])
def get_list_events(id):
    evenements_list = evenements_df.to_dict(orient='records')
    list_events=[]
    for event in evenements_list:
        if int(event['association_id'])==id:
            list_events.append(event)
    if list_events==[]:
        return jsonify({"error": "Event not found"}), 404
    return jsonify(list_events)

## Si on veut juste la liste des noms des événements sans leur description, on remplace list_events.append(event) par list_events.append(event['nom'])

@app.route('/api/associations/type/<type>', methods=['GET'])
def get_type_asso(type):
    associations_list = associations_df.to_dict(orient='records')
    list_type=[]
    for asso in associations_list:
        if asso['type']==type:
            list_type.append(asso)
    if list_type==[]:
        return jsonify({"error": "Type not found"}), 404
    return jsonify(list_type)

if __name__ == '__main__':
    app.run(debug=False)
