import streamlit as st
import time
import numpy as np
import random

import psycopg2
from psycopg2 import sql
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
    sql = "SELECT id, name FROM experiments ORDER BY id ;"

    return query(sql).set_index('id')

@st.cache
def get_progress(experiment_id, y, x):
    output = query("""SELECT value AS {}, {} FROM metrics WHERE experiment_id={} AND key='{}' ORDER BY timestamp DESC""" .format(y, x, experiment_id, y))
    return output.set_index(x)

@st.cache
def get_all_progress(experiments, y, x):
    selected_ids = list()
    for exp in experiments:
        selected_ids.append(exp[0])
    selected_ids = tuple(selected_ids)

    if len(selected_ids) > 0:
        if len(selected_ids) < 2:
            sql = """SELECT experiment, {}, {} FROM (SELECT value AS {}, {}, name AS experiment FROM metrics LEFT JOIN experiments ON metrics.experiment_id = experiments.id WHERE experiment_id={} AND key='{}' ORDER BY RANDOM() LIMIT 1000) AS metrics ORDER BY {} DESC""" .format(x, y, y, x, selected_ids[0], y, x)
        else:
            sql = """SELECT experiment, {}, {} FROM (SELECT value AS {}, {}, name AS experiment FROM metrics LEFT JOIN experiments ON metrics.experiment_id = experiments.id WHERE experiment_id IN {} AND key='{}' ORDER BY RANDOM() LIMIT 1000) AS metrics  ORDER BY {} DESC""".format(x, y, y, x, selected_ids, y, x)
    else:
        sql = """SELECT name AS experiment, {}, {} FROM metrics LEFT JOIN experiments ON metrics.experiment_id = experiments.id WHERE 1 = 0 AND key='{}' ORDER BY step DESC""" .format(x, y, experiment_id, y)
    metrics = query(sql)
    return metrics

@st.cache
def get_text(experiment_id, tag):
    output = query("""SELECT timestamp, step, loss, value AS {} FROM texts WHERE experiment_id={} AND key='{}' ORDER BY timestamp DESC""" .format(tag, experiment_id, tag))
    return output.set_index('timestamp')

def get_text_tags(experiments):
    selected_ids = list()
    for exp in experiments:
        selected_ids.append(exp[0])
    selected_ids = tuple(selected_ids)
    if len(selected_ids) > 0:
        if len(selected_ids) < 2:
            sql = """SELECT DISTINCT(key) AS tags FROM texts WHERE experiment_id = {} GROUP BY key""".format(selected_ids[0])
        else:
            sql = """SELECT DISTINCT(key) AS tags FROM texts WHERE experiment_id IN {} GROUP BY key""".format(selected_ids)
    else:
        sql = """SELECT DISTINCT(key) AS tags FROM texts WHERE 1 = 0 GROUP BY key"""
    tags = query(sql)
    return tags

def get_metric_tags(experiments):
    selected_ids = list()
    for exp in experiments:
        selected_ids.append(exp[0])
    selected_ids = tuple(selected_ids)

    if len(selected_ids) > 0:
        if len(selected_ids) < 2:
            sql = """SELECT DISTINCT(key) AS tags FROM metrics WHERE experiment_id = {} GROUP BY key""".format(selected_ids[0])
        else:
            sql = """SELECT DISTINCT(key) AS tags FROM metrics WHERE experiment_id IN {} GROUP BY key""".format(selected_ids)
    else:
        sql = """SELECT DISTINCT(key) AS tags FROM metrics WHERE 1 = 0 GROUP BY key"""
    tags = query(sql)
    return tags


st.title('Watch me learn to talk')
st.header("All experiments :")
experiments = get_experiments()
st.table(experiments)



st.header("Experiments metrics :")




progress_bar = st.sidebar.progress(0)

exps = tuple(zip(experiments.index, experiments.name))
selected_experiments = st.sidebar.multiselect('Select your experiments', exps)

graphs = list()
metrics_tags = get_metric_tags(selected_experiments)
for x in ['timestamp', 'step']:
    for y in tuple(metrics_tags.tags):
        graphs.append({'x': x, 'y': y})


selected_graphs = st.sidebar.multiselect('Select your graphs', graphs)

st.sidebar.text("learn about date formatting :")
st.sidebar.text("""https://vega.github.io/vega-lite/docs/timeunit.html""")

time_formats = [
    "year", "yearquarter", "yearquartermonth", "yearmonth", "yearmonthdate", "yearmonthdatehours", "yearmonthdatehoursminutes", "yearmonthdatehoursminutesseconds",
    "quarter", "quartermonth",
    "month", "monthdate",
    "date",
    "day",
    "hours", "hoursminutes", "hoursminutesseconds",
    "minutes", "minutesseconds",
    "seconds", "secondsmilliseconds",
    "milliseconds"
    ]

selected_timeformat = st.sidebar.selectbox('timestamp format', time_formats, 7)


st.sidebar.text("learn about aggregations :")
st.sidebar.text("https://vega.github.io/vega-lite/docs/aggregate.html#encoding")
aggregations = [
    'count', 'valid', 'missing', 'distinct', 
    'sum', 'mean', 'average', 'variance', 'variancep',
    'stdev', 'stdevp', 'stderr', 'median', 
    'q1', 'q3',
    'ci0', 'ci1',
    'min', 'max',
    'argmin', 'argmax'
    ]
selected_aggregation = st.sidebar.selectbox('aggregation type', aggregations, 6)

text_tags = get_text_tags(selected_experiments)

selected_texts = st.sidebar.multiselect('text samples ', tuple(text_tags.tags))

total_steps = len(selected_experiments) * (len(selected_graphs) + len(selected_texts))
step = 0
for experiment in selected_experiments:
    index, name = experiment
    st.subheader('experiment : %s' % name)


    for graph in selected_graphs:
        step += 1
        progress_bar.progress(int(step / total_steps * 100))
        progress = get_progress(index, graph['y'], graph['x'])

        if st.checkbox(label='Show %s raw data for %s vs %s' % (name, graph['y'], graph['x']), value=False):
            st.write(progress)

        if graph['x'] == 'timestamp':
            progress = progress.reset_index()
            st.vega_lite_chart(progress, {
                "mark": {
                    "type": "line", 
                    "interpolate": "monotone"
                    },
                "config": {
                    "axis": {"shortTimeLabels": "true"}
                },
                "selection": {
                    "grid": {
                        "type": "interval", 
                        "bind": "scales"
                    }
                }, 
                'encoding': {
                    "tooltip": [
                        {
                         "field": "timestamp", 
                         "type": "temporal",
                         'timeunit': selected_timeformat
                        },
                        {
                         "field": graph['y'], 
                         "type": "quantitative"
                         }
               	         ],
                     'x': {
                         'field': 'timestamp', 
                         'type': 'temporal',
                         'timeunit': selected_timeformat
                         },
                     'y': {
                         'field': graph['y'], 
                         'type': 'quantitative',
                         'aggregate': selected_aggregation,
                         'title': "%s(%s)" % (selected_aggregation, graph['y'])
                         },
                     },
                })
        else:
            st.line_chart(progress)

    for text in selected_texts:
        step += 1
        progress_bar.progress(int(step / total_steps * 100))
        
        if st.checkbox(label='Show %s for %s ' % (text, name), value=False):
            st.dataframe(get_text(index, text).style.highlight_min(axis=0), 2000)
            st.table(get_text(index, text).style.highlight_min(axis=0))
        
status_text = st.sidebar.empty()




st.header("OVERALL COMPARISON")
for graph in selected_graphs:
    all_progresses = get_all_progress(selected_experiments, graph['y'], graph['x'])
    if graph['x'] == 'timestamp':
        st.vega_lite_chart(all_progresses, {
        "mark": {
            "type": "line", 
            "interpolate": "monotone"
            },
        "config": {
            "axis": {"shortTimeLabels": "true"}
        },
        "selection": {
            "grid": {
                "type": "interval", 
                "bind": "scales"
            }
        }, 
        'encoding': {
            "tooltip": [
                {
                 "field": "timestamp", 
                 "type": "temporal",
                 'timeunit': selected_timeformat
                },
                {
                 "field": graph['y'], 
                 "type": "quantitative"
                 }
       	         ],
             'x': {
                 'field': 'timestamp', 
                 'type': 'temporal',
                 'timeunit': selected_timeformat
                 },
             'y': {
                 'field': graph['y'], 
                 'type': 'quantitative',
                 'aggregate': selected_aggregation,
                 'title': "%s(%s)" % (selected_aggregation, graph['y'])
                 },
              "color": {
                 'field': 'experiment', 
                 'type': 'nominal'
                 }
             },
            })
    else:
#        st.line_chart(all_progresses.set_index(graph['x']))
         st.vega_lite_chart(all_progresses, {
             "mark": {
                "type": "line",
                "interpolate": "monotone"
                },
            "config": {
            },
            "selection": {
                "grid": {
                    "type": "interval",
                    "bind": "scales"
                }
            },
            'encoding': {
                "tooltip": [
                    {
                     "field": graph['x'],
                     "type": "quantitative",
                    },
                    {
                     "field": graph['y'],
                     "type": "quantitative",
                    }
                 ],
             'x': {
                 'field': graph['x'],
                 'type': 'quantitative',
                 'scale': {'zero': 'false'}
                 },
             'y': {
                 'field': graph['y'],
                 'type': 'quantitative',
                 'scale': {'zero': 'false'}
                 },
              "color": {
                 'field': 'experiment',
                 'type': 'nominal'
                 }
             },
            })


st.button("Re-run")
