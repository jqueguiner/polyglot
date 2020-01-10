from flask import render_template
from flask import Flask
from flask import request
import flask
from app import app
import requests
import json

import psycopg2
import yaml
import os

filepath = os.environ['CONFIG_FILE_PATH']

with open(filepath, 'r') as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)

dbconf=cfg['pgsql']

def connectdb():
    connection = psycopg2.connect(user=dbconf['user'],
                              password=dbconf["password"],
                              host=dbconf["host"],
                              port=dbconf["port"],
                              database=dbconf["database"])
    cursor = connection.cursor()
    return cursor, connection


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='A.I. Experiments')

@app.route('/get_experiments', methods=['POST', 'GET'])
def get_experiments():
    cursor, connection = connectdb()
    experiments = []
    columns = ('id', 'name', 'description')
    cursor.execute("""SELECT %s, %s, %s FROM experiments ORDER BY id""" % columns)
    for row in cursor.fetchall():
        experiments.append(dict(zip(columns, row)))

    connection.close()
    return experiments


@app.route('/get_experiment_by_id', methods=['POST', 'GET'])
def get_experiment_by_id():
    content = request.get_json(force=True)

    cursor, connection = connectdb()
    experiments = []

    columns = ('id', 'name', 'description')

    cursor.execute("""SELECT %s, %s, %s FROM experiments WHERE id = %d""" % ('id', 'name', 'description', content['id']))

    for row in cursor.fetchall():
        experiments.append(dict(zip(columns, row)))

    connection.close()

    return json.dumps(experiments), 200

@app.route('/get_experiment_by_name', methods=['POST', 'GET'])
def get_experiment_by_name():
    content = request.get_json(force=True)

    cursor, connection = connectdb()

    columns = ('id', 'name', 'description')

    cursor.execute("""SELECT %s, %s, %s FROM experiments WHERE name = '%s'""" % ('id', 'name', 'description', content['name']))

    try:
        experiment = dict(zip(columns, cursor.fetchone()))
    except:
        experiment = {'id': 0, 'name': 'does not exists', 'description': 'does not exists'}

    connection.close()

    return json.dumps(experiment), 200


@app.route('/create_experiment', methods=['POST', 'GET'])
def create_experiment():
    content = request.get_json(force=True)

    cursor, connection = connectdb()

    postgres_insert_query = """INSERT INTO experiments (name, description) VALUES (%s, %s)  RETURNING id;"""
    record_to_insert = (content['name'], content['description'])

    cursor.execute(postgres_insert_query, record_to_insert)
    experiment = {'id': cursor.fetchone()[0]}

    connection.commit()
    connection.close()

    return json.dumps(experiment), 200


@app.route('/get_progress', methods=['POST', 'GET'])
def get_progress():
    content = request.get_json(force=True)
    cursor, connection = connectdb()
    experiments = get_experiments()
    progress = []
    for experiment in experiments:
        experiment_id = experiment['id']
        cursor.execute("""SELECT key, value, step, time, timestamp FROM (SELECT key, value, step, time, to_char(timestamp at time zone 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"') AS timestamp FROM metrics WHERE experiment_id=%s AND key='%s' ORDER BY RANDOM() LIMIT 1000) AS sample ORDER BY timestamp""" % (experiment_id, content['y']))
        columns_metrics = ('key', 'value', 'step', 'time','timestamp')
        metrics = []
        texts = []
        for row in cursor.fetchall():
           metrics.append(dict(zip(columns_metrics, row)))

        columns_text = ('key', 'value', 'text_en', 'step', 'loss', 'time', 'timestamp')
#        cursor.execute("""(SELECT key, value, text_en, step, loss, time, to_char(timestamp at time zone 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"') AS timestamp FROM texts WHERE experiment_id=%s AND key = 'best_loss' ORDER BY loss ASC LIMIT 25) UNION (SELECT key, value, text_en, step, loss, time, to_char(timestamp at time zone 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"') AS timestamp FROM texts WHERE experiment_id=%s AND key != 'best_loss' ORDER BY RANDOM() LIMIT 25)""" % (experiment_id, experiment_id))
        query = ("""SELECT key, value, text_en, step, loss, time, timestamp FROM ((SELECT key, value, text_en, step, loss, time, to_char(timestamp at time zone 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"') AS timestamp FROM texts WHERE experiment_id=%s AND key = 'best_loss' ORDER BY loss ASC LIMIT 25) UNION (SELECT key, value, text_en, step, loss, time, to_char(timestamp at time zone 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"') AS timestamp FROM texts WHERE experiment_id=%s AND key != 'best_loss' ORDER BY RANDOM() LIMIT 25) UNION (SELECT key, value, text_en, step, loss, time, to_char(timestamp at time zone 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"') AS timestamp FROM texts WHERE experiment_id=%s AND key != 'best_loss' ORDER BY step DESC LIMIT 10)) AS texts""") % (experiment_id, experiment_id, experiment_id)
        cursor.execute(query)
        for row in cursor.fetchall():
           texts.append(dict(zip(columns_text, row)))

        progress.append({'experiment': experiment, 'metrics': metrics, 'text': texts })

    connection.close()
    if flask.request.method == 'POST':
        return json.dumps(progress), 200
    elif flask.request.method == 'GET':
        return render_template('json.html', data=progress)
    else :
        return progress


@app.route('/progress')
def progress():
    experiments = get_experiments()

    return render_template('progress.html', title='A.I. Expermients', experiments=experiments)


@app.route('/push_metric', methods=['POST'])
def push_metric():
    content = request.get_json(force=True)
    cursor, connection = connectdb()

    postgres_insert_query = """ INSERT INTO metrics (experiment_id, key, value, step) VALUES (%s, %s, %s, %s) """
    record_to_insert = (content['experiment_id'], content['key'], content['value'], content['step'])
    cursor.execute(postgres_insert_query, record_to_insert)

    connection.commit()
    connection.close()

    return 'ok', 200


@app.route('/push_text', methods=['POST'])
def push_text():
    content = request.get_json(force=True)
    cursor, connection = connectdb()

    postgres_insert_query = """ INSERT INTO texts (experiment_id, key, value, text_en, step, loss, time) VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    record_to_insert = (content['experiment_id'], content['key'], content['value'], content['text_en'], content['step'], content['loss'], content['time'])
    print("pushing %s with loss %  for step %s" % (content['key'], content['loss'], content['step']))
    cursor.execute(postgres_insert_query, record_to_insert)

    connection.commit()
    connection.close()

    return 'ok', 200



