# -*- coding: utf-8 -*-
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import numpy as np



from flask import Flask, redirect, url_for
import pandas as pd


data = pd.read_csv("Static/data/qnrf_funding_data.csv")



# Modifying the data
data["Start Date:"] = pd.to_datetime(data["Start Date:"])
start_date = data["Start Date:"]

data['start_year'] = pd.DatetimeIndex(start_date).year
data['start_month'] = pd.DatetimeIndex(start_date).month


server = Flask(__name__)

@server.route("/")
def index():
    return redirect(url_for('/dash'))


# define for IIS module registration.
wsgi_app = server.wsgi_app

app = dash.Dash(__name__, server=server, url_base_pathname='/dash')


# Proposal Number:,Program Cycle:,Submitting Institution Name:,Project Status:,Start Date:,Lead Investigator:,
# Project Duration:,End Date:,SubmissionType:,Proposal Title:,Research Keyword 1,Research Keyword 2,Research Keyword 3,
# Research Keyword 4,Research Keyword 5,Research Type:,Personnel,Institution,URL

@app.callback(
    dash.dependencies.Output('universities_count', 'figure'),
    [dash.dependencies.Input('year_dropdown', 'value')])
def generate_graph(selected_year=[data['start_year'].unique()]):

    # proposal_number = data["Proposal Number"]
    # submitting_institution_name = data["Submitting Institution Name:"]

    filtered_data = data[data.year.isin(selected_year)]
    submitting_institution_name_count = filtered_data["Submitting Institution Name:"].value_counts()

    trace1 = go.Bar(x=submitting_institution_name_count.index, y=submitting_institution_name_count, name='counter')

    graph_to_return = html.Div(
        dcc.Graph(
        figure=go.Figure(
            id = 'universities_count',
            data=[trace1],
            # data=[
            #     go.Bar(
            #         x=[1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003,
            #            2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012],
            #         y=[219, 146, 112, 127, 124, 180, 236, 207, 236, 263,
            #            350, 430, 474, 526, 488, 537, 500, 439],
            #         name='Rest of world',
            #         marker=go.Marker(
            #             color='rgb(55, 83, 109)'
            #         )
            #     ),
            #     go.Bar(
            #         x=[1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003,
            #            2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012],
            #         y=[16, 13, 10, 11, 28, 37, 43, 55, 56, 88, 105, 156, 270,
            #            299, 340, 403, 549, 499],
            #         name='China',
            #         marker=go.Marker(
            #             color='rgb(26, 118, 255)'
            #         )
            #     )
            # ],
            layout=go.Layout(
                # autosize=False,
                title='Split of Universities with projects ',
                showlegend=True,
                legend=go.Legend(
                    x=0,
                    y=1.0
                ),
                # xaxis=dict(tickangle=-45),
                margin=go.Margin(l=100, r=0, t=40, b=150)
            )
        ),
        style={'height': 400},
        id='my-graph'
    )
    )
    return graph_to_return


def year_slider():

    start_year_unique = data['start_year'].unique()

    year_list = []
    for i in start_year_unique:
        if np.isnan(i):
            # print({'label': i, 'value': i})
            year_list.append({'label': 'nan', 'value': 'nan'})
        else:
            x = int(i)
            # print({'label': x, 'value': i})
            year_list.append({'label': i, 'value': i})

    return html.Div([
        html.Label('Year Dropdown'),
        dcc.Dropdown(
            id='year_dropdown',
            options=year_list,
            value=[y['value'] for y in year_list if 'value' in y],
            multi=True
        )
    ], style={'columnCount': 1})




def update_output(value):
    return 'You have selected "{}"'.format(value)




app.layout = html.Div(children=[
    html.H1(children="QNRF Dashboard"),

    html.Div(children='''
    Visualization for QNRF Funding
    '''),
    year_slider(),
    generate_graph()
])

if __name__ == '__main__':
    app.run_server(debug=True, port=8050)

#
#
# app.layout = html.Div([
#     dcc.Graph(id='graph-with-slider'),
#     dcc.Slider(
#         id='year-slider',
#         min=df['year'].min(),
#         max=df['year'].max(),
#         value=df['year'].min(),
#         step=None,
#         marks={str(year): str(year) for year in df['year'].unique()}
#     )
#
# ])
#
#
# @app.callback(
#     dash.dependencies.Output('graph-with-slider', 'figure'),
#     [dash.dependencies.Input('year-slider', 'value')])
# def update_figure(selected_year):
#     filtered_df = df[df.year == selected_year]
#     traces = []
#     for i in filtered_df.continent.unique():
#         df_by_continent = filtered_df[filtered_df['continent'] == i]
#         traces.append(go.Scatter(
#             x=df_by_continent['gdpPercap'],
#             y=df_by_continent['lifeExp'],
#             text=df_by_continent['country'],
#             mode='markers',
#             opacity=0.7,
#             marker={
#                 'size': 15,
#                 'line': {'width': 0.5, 'color': 'white'}
#             },
#             name=i
#         ))
#
#     return {
#         'data': traces,
#         'layout': go.Layout(
#             xaxis={'type': 'log', 'title': 'GDP Per Capita'},
#             yaxis={'title': 'Life Expectancy', 'range': [20, 90]},
#             margin={'l': 40, 'b': 40, 't': 10, 'r': 10},
#             legend={'x': 0, 'y': 1},
#             hovermode='closest'
#         )
#     }
#
#
# if __name__ == '__main__':
#     app.run_server()