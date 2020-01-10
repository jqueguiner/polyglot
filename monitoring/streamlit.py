import streamlit as st
import time
import numpy as np
import random

import psycopg2
import yaml
import os
import pandas as pd
import pandas.io.sql as sqlio

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


def query(sql):
    cursor, connection = connectdb()
    data = sqlio.read_sql_query(sql, connection)
    connection = None
    return data

@st.cache
def get_experiments():
    sql = "SELECT id, name, description FROM experiments ORDER BY id LIMIT 1;"
    return query(sql)

@st.cache
def get_progress(experiment_id, metric):
    output = query("""SELECT value, step FROM metrics WHERE experiment_id=%s AND key='%s' ORDER BY timestamp DESC""" % (experiment_id, metric))
    #output = query("""SELECT value, step, to_char(timestamp at time zone 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"') AS timestamp FROM metrics WHERE experiment_id=%s AND key='%s' ORDER BY timestamp DESC""" % (experiment_id, metric))
    return output


st.title('Watch me learn to talk')
st.header("All experiments :")
experiments = get_experiments()
st.write(experiments)


st.header("Experiments metrics :")

for index, experiment in experiments.iterrows():
    st.subheader('experiment : %s' % experiment['name'])
    loss_progress = get_progress(experiment['id'], 'loss')

    if st.checkbox(label='Show raw data', value=False, key=random.getrandbits(128)):
        st.subheader('Raw data')
        st.write(loss_progress)

    st.line_chart(loss_progress)