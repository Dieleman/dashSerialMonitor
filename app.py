# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import multiprocessing
import serialProcess
import time
import plotly
import pandas as pd
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import dash_daq as daq
taskQ = multiprocessing.Queue()
resultQ = multiprocessing.Queue()
global sp
global r

sp = serialProcess.SerialProcess(taskQ, resultQ)
#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
mapbox_access_token = "pk.eyJ1IjoiamFja2x1byIsImEiOiJjajNlcnh3MzEwMHZtMzNueGw3NWw5ZXF5In0.fk8k06T96Ml9CLGgKmk81w"

app = dash.Dash(__name__) #, external_stylesheets=external_stylesheets)
layout = dict(
    autosize=True,
    automargin=True,
    #margin=dict(l=30, r=30, b=20, t=40),
    hovermode="closest",
    plot_bgcolor="#F9F9F9",
    paper_bgcolor="#F9F9F9",
    legend=dict(font=dict(size=10), orientation="h"),
    title="Satellite Overview",
)

app.layout = html.Div(children=[
    html.H1(children='Live lab monitor'),

    html.Div(id='live-update-text',children='''
        Dash: A web application framework for Python niet.
    '''),

    html.Div( [
        html.Div( [


            daq.Gauge(
                id="gauge",
                color={"gradient":True,"ranges":{"green":[0,20],"yellow":[20,40],"red":[40,50]}},
                value=2,
                label='Power',
                max=50,
                min=0,
                showCurrentValue=True,
                units="W"
            ),
            daq.LEDDisplay(
                id='pw_display',
                value="3.14159",
                label='Pulsewidth'
            )

        ], className="mini_container"),

        html.Div(
            dcc.Graph(
                id='example-graph'

            ), className="pretty_container ten columns"),

    ],className="row flex-display"),


    dcc.Interval(
        id='interval-component',
        interval=250,  # in milliseconds
        n_intervals=0
    )

])



def checkResults(lastestOnly=False):
    # try:
    try:
        df = pd.read_csv('log.txt')
        df['Datetime'] = pd.to_datetime(df['Datetime'])
        if(lastestOnly):
            return df.tail(1)
        return df
    except:
        return None
    # except:
    #     print("No data yet")
    result = -1
    while not resultQ.empty():
        result = resultQ.get()
        print("tornado received from arduino: " + result)
    return int(result)


@app.callback(Output('gauge', 'value'),
               [Input('example-graph', 'figure')])
def update_gauge(n):
    df = checkResults(lastestOnly=True)
    try:
        if "PW (ns)" in df.columns:
            value = df['Power (W)'].iloc[-1]
            print(value)
            return value
    except:
        return -1


@app.callback(Output('live-update-text', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_metrics(n):
    global sp

    lon, lat, alt = 1,2,4
    style = {'padding': '5px', 'fontSize': '16px'}
    if (sp.is_alive()):
        return html.Span("Process is alive")
    else:
        sp = serialProcess.SerialProcess(taskQ, resultQ)
        # sp.daemon = True
        sp.start()
        return html.Span("Process is dead, restarting...")
    # return [
    #     html.Span('Longitude: {0:.2f}'.format(lon), style=style),
    #     html.Span('Latitude: {0:.2f}'.format(lat), style=style),
    #     html.Span('Altitude: {0:0.2f}'.format(alt), style=style)
    # ]

@app.callback(Output('example-graph', 'figure'),
              [Input('interval-component', 'n_intervals')])
def update_graph_live(n):

    r = checkResults()

    colors = ['#1f77b4','#ff7f0e','#2ca02c','#d62728','#9467bd','#8c564b','#e377c2','#7f7f7f','#bcbd22','#17becf']
    # if r == -1:
    #     pass
    y = [1]
    y2 = [1]
    x = [1]
    try:
        if "PW (ns)" in r.columns:
            print("Yes")
            y = r['Power (W)']
            y2 = r['PW (ns)']
            x = r['Datetime']
    except:
        pass

    data = [
                {'x': x, 'y': y, 'type': 'scatter', 'name': 'Power'},
                {'x':  x, 'y': y2, 'type': 'scatter', 'name': 'Pulsewidth', 'secondary_y':True,'yaxis':'y2'},
        ]
    layout_new = {
        'title': 'Live power and pulsewidth',
        'yaxis': {'title': 'Powerr (W)', 'side': 'left','titlefont':{'color':colors[0]},'tickfont':{'color':colors[0]}},
        'yaxis2': {'title': 'Pulsewidth (ns)','side':'right','overlaying':'y','titlefont':{'color':colors[1]},'tickfont':{'color':colors[1]}},
        'uirevision': 2
    }
    lay = {**layout, **layout_new}
    f = {}
    f['data'] = data
    f['layout'] = lay

    return f

if __name__ == '__main__':





    sp.daemon = True
   #

    # wait a second before sending first task

    sp.start()
    taskQ.put("first task")
    taskQ.put("second task")
    app.run_server(debug=True)