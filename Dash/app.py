#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
import itertools

import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import dash_table as dtab
from dash.dependencies import Input, Output, Event, State
# import random
# import dash_auth

from datetime import datetime
import time
from collections import OrderedDict


import plotly.graph_objs as go
from plotly.graph_objs.layout import *
# from dash.exceptions import PreventUpdate


from flask import Flask, render_template, redirect, url_for, request
# from flask_login import LoginManager


import pandas as pd
import numpy as np
import networkx as nx
import json
import sqlite3
import os

# my imports
# from Dash.DataProvider.data_handler import DataProcessor
# from Dash.Elastic.elastic_dash import ElasticDash

from Dash.DataProvider.data_handler import DataProcessor
from Dash.Elastic.elastic_dash import ElasticDash

# from Dash.dash_flask_login.flask_login_auth2 import FlaskLoginAuth


# IMPORT THE DATA
data_package = DataProcessor()
funding_data = data_package.data
personnel_data = data_package.personnel_data
outcome_data = data_package.outcome_data

# ElasticSearch Instance
elastic_dash = ElasticDash()
# search_ids = []

print("The working directory is ", os.getcwd())

# images
def img_encode(image_filename):
    return base64.b64encode(open(image_filename, 'rb').read())


kindi_logo = img_encode('Static/images/kindi_logo.png')
qnrf_logo = img_encode('Static/images/qnrf_logo.png')
qu_logo = img_encode('Static/images/qu_logo.png')


################# REQUIRED FUNCTIONS FOR PRE PROCESSING IN DASH ######################
######################################################################################
######################################################################################

def year_dropdown_populator():
    """
    Populates the year dropdown for listing number of research grants per Institution
    :return: A list containing dictionary values of years ('label': i, 'value': i)
                Need a label and a value so that dash app picks up the label value pair inside options keyword
    """
    start_year_unique = funding_data['start_year'].unique()

    year_list = []
    for i in start_year_unique:
        if i == -1:
            # print({'label': i, 'value': i})
            # NA values has been changes to -1
            year_list.append({'label': 'NA', 'value': -1})
        else:
            x = int(i)
            # print({'label': x, 'value': i})
            year_list.append({'label': i, 'value': i})
    return year_list


# TODO : Write a populator function which can get return information for all populators.

def institution_populator():
    """
    Populates the Institution dropdown for filtering
    :return: a list containing instituion names ,('label': i, 'value': i)
             Need a label and a value so that dash app picks up the label value pair inside options keyword
    """
    institution_list = funding_data["Submitting Institution Name:"].unique()
    # print(type(institution_list))
    # print(institution_list)
    # print(type(institution_list[0]))

    return [{'label': i, 'value': i} for i in institution_list]


def funding_program_populator():
    """
    Populates the Funding Program dropdown for filtering
    :return:  a list containing funding programs (Unique "Program Cycle:"), ('label': i, 'value': i)
                Need a label and a value so that dash app picks up the label value pair inside options keyword
    """
    funding_program_list = funding_data["Program Cycle:"].unique()
    return [{'label': i, 'value': i} for i in funding_program_list]


def award_status_populator():
    """
    Populates the Award Status dropdown filtering
    :return: a string corresponding to Project Status:
    """
    award_status_list = funding_data["Project Status:"].unique()
    return [{'label': i, 'value': i} for i in award_status_list]


def generate_table(data, max_rows=10):
    """

    :param data:
    :param max_rows: Displays only max_rows number of rows on the webpage
    :return:
    """
    return html.Table(
        # Header
        [html.Tr([html.Th(col) for col in data.columns])] +

        # Body
        [html.Tr([
            html.Td(data.iloc[i][col]) for col in data.columns
        ]) for i in range(min(len(data), max_rows))]
    )


def create_graph_network(start_node, connections):
    """
    Create a Graph network for displaying relationships between nodes and edge
    This function works with node data for professors
    :param start_node:
    :param connections:
    :return:
    """
    graph = nx.Graph()
    graph.add_node(start_node)
    print(connections.index)
    graph.add_nodes_from(connections.index)
    edge_list = list(zip(itertools.repeat(start_node), connections.index))
    print("edge list is ", edge_list)
    graph.add_edges_from(edge_list)
    for i in graph.edges():
        graph[i[0]][i[1]]['weight'] = connections.loc[i[1]]['count']
        # graph[i[0]][i[1]]['proposal_number'] = connections.loc[i[1]]['proposal_number']
        # graph[i[0]][i[1]]['institution'] = connections.loc[i[1]]['institution']
        # graph[i[0]][i[1]]['proposal_title'] = connections.loc[i[1]]['proposal_title']
        # graph[i[0]][i[1]]['project_status'] = connections.loc[i[1]]['project_status']

    # Adding random position data to the graph.
    # pos = nx.spring_layout(graph, k=1)
    pos = nx.circular_layout(graph)
    nx.set_node_attributes(graph, 'pos', pos)
    return graph


def create_graph_network_visualization(graph_network, connections, connections_grouped):
    """
    Creates the graph network visualization for Dash App
    :param graph_network:
    :param connections:
    :param connections_grouped:
    :return:
    """

    edge_trace = go.Scatter(
        x=[],
        y=[],
        customdata=[],
        text=[],
        line=dict(width=2, color='#888'),
        hoverinfo='all',
        mode='lines+text',
        textposition='top left',
    )
    edge_label_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        textposition='top left',
        mode='markers+text',
        hoverinfo='none',
        marker=go.Marker(
            opacity=0
        ),
        textfont=dict(size=20, color='black')
    )

    for edge in graph_network.edges():
        x0, y0 = graph_network.node[edge[0]]['pos']
        x1, y1 = graph_network.node[edge[1]]['pos']
        edge_weight = graph_network.node[edge[1]]['pos']
        edge_trace['x'] += tuple([x0, x1, None])
        edge_trace['y'] += tuple([y0, y1, None])

        text = graph_network[edge[0]][edge[1]]['weight']
        edge_label_trace['x'] += tuple([(x0 + x1) / 2])
        edge_label_trace['y'] += tuple([(y0 + y1) / 2])
        edge_label_trace['text'] += tuple([text])

        # writing to edge customdata
        edge_trace['customdata'] += graph_network[edge[0]][edge[1]]['weight']
        edge_trace['text'] = str(graph_network[edge[0]][edge[1]]['weight'])
        #     edge_trace['marker']['size'] += professor_graph[edge[0]][edge[1]]['weight']
        # print(graph_network[edge[0]][edge[1]]['weight'])

    node_trace = go.Scatter(
        x=[],
        y=[],
        text=[],
        hovertext=[],
        mode="markers+text",
        hoverinfo='text',
        textposition='bottom center',
        marker=dict(
            showscale=False,
            # colorscale options
            # ['Greys', 'YlGnBu', 'Greens', 'YlOrRd', 'Bluered', 'RdBu',
            #  'Reds', 'Blues', 'Picnic', 'Rainbow', 'Portland', 'Jet',
            #  'Hot', 'Blackbody', 'Earth', 'Electric', 'Viridis', 'Cividis]
            colorscale='YlGnBu',
            reversescale=True,
            color=[],
            size=40,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            ),
            line=dict(width=2))
    )

    entry_bool = True

    for node in graph_network.nodes():
        x, y = graph_network.node[node]['pos']
        node_trace['x'] += tuple([x])
        node_trace['y'] += tuple([y])
        # node_trace['text'].append(node)

        # x, y = professor_graph.node[node]['pos']
        # node_trace['x'].append(x)
        # node_trace['y'].append(y)

        if entry_bool:
            # node_trace['text'].append(node)
            node_trace['text'] += tuple([node])
            entry_bool = False
            total_projects = "Total Projects: {}".format(len(connections["Proposal Number:"].unique()))
            print("Total Projects", total_projects)
            node_trace['hovertext'] += tuple([total_projects])
        else:
            # node_trace['text'].append(node)
            node_trace['text'] += tuple([node])
            some_text = []
            some_text.append(node + "<br>")
            for i in range(len(connections_grouped.loc[node]['proposal_number'])):
                if i > 0:
                    some_text.append("<br>")
                print("list index is ", i)
                print("prop number is ", connections_grouped.loc[node]['proposal_number'][i])
                some_text.append(connections_grouped.loc[node]['proposal_number'][i])
                #             import pdb
                #             pdb.set_trace()
                some_text.append("<br>")
                some_text.append(connections_grouped.loc[node]['proposal_title'][i])
                some_text.append("<br>")
                some_text.append(connections_grouped.loc[node]['project_status'][i])
                some_text.append("<br>")
                some_text.append(connections_grouped.loc[node]['institution'][i])
                some_text.append("<br>")
            some_text = [x for x in some_text if str(x) != 'nan']

            some_text = "".join(some_text)
            print(node)
            print("yo is ", some_text)
            # node_trace['hovertext'].append(some_text)
            node_trace['hovertext'] += tuple([some_text])

    for node, adjacencies in enumerate(graph_network.adjacency_list()):
        #     print(node,adjacencies)
        #     print(professor_graph[node])
        node_trace['marker']['color'] += tuple([len(adjacencies)])

    return node_trace, edge_trace, edge_label_trace


# TODO: Combine both the vertical and horizontal annotation in to one function?
def make_annotation_vertical(x, y):
    """
    Create an vertical annotation for graphs, annotation is smaller than 33 characters.
    :param x: text data and text position
    :param y: unused for now
    :return: Annotation object of Dash
    """
    text = str(x)
    if len(text) > 33:
        text = text[0:33]+".."
    return Annotation(
        text=text,     # text is the y-coord
        showarrow=False, # annotation w/o arrows, default is True
        x=x,               # set x position
        xref='x',          # position text horizontally with x-coords
        xanchor='center',  # x position corresp. to center of text
        yref='y',            # set y position
        yanchor='bottom',       # position text vertically with y-coords
        y=0,                 # y position corresp. to top of text
        textangle=-90,       # Rotating the text upwards
        font=annotation.Font(
            color='#FFFFFF',  # set font color
            size=13           #   and size
        )
    )

# Define an annotation-generating function
def make_annotation_horizontal(x, y):
    """
    Create an horizontal annotation for graphs, annotation is smaller than 33 characters.
    :param x: text data and text position
    :param y: unused
    :return: Annotation object of Dash
    """
    text = str(x)
    if len(text) > 33:
        text = text[0:33]+".."
    return Annotation(
        text=text,     # text is the y-coord
        showarrow=False,  # annotation w/o arrows, default is True
        x=0,               # set x position
        xref='x',          # position text horizontally with x-coords
        xanchor='left',  # x position corresp. to center of text
        y=x,  # y position corresp. to top of text
        yref='y',            # set y position
        yanchor='auto',       # position text vertically with y-coords
        textangle=0,       # Not Rotating the text
        font=annotation.Font(
            color='#FFFFFF',  # set font color
            size=13           #   and size
        )
    )



# SERVER
server = Flask(__name__)

# Database Connection
server.database = "dash_user.db"

# define for IIS module registration.
wsgi_app = server.wsgi_app



############################### DASH BASIC AUTH ###########################################################
# app = dash.Dash('auth')
# auth = dash_auth.BasicAuth(
#     app,
#     VALID_USERNAME_PASSWORD_PAIRS
# )


# DASH APP
app = dash.Dash(__name__, server=server, url_base_pathname='/dash/')
# app = dash.Dash(__name__, server=server)
app.config['suppress_callback_exceptions'] = True
# auth = FlaskLoginAuth(app, use_default_views=True, users=[('mohammed','shinoy'),('admin','admin'),('rachel','fernandes')])
# auth = FlaskLoginAuth(app, use_default_views=True, users=server.database)
# auth = FlaskLoginAuth(app, use_default_views=False, users=server.database)
# auth = dash_auth.BasicAuth(
#     app,
#     VALID_USERNAME_PASSWORD_PAIRS
# )

####### CSS VERSION ######
#  app.css.append_css({'external_url': 'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})
app.css.append_css({'external_url': 'https://codepen.io/shinz4u/pen/MBBxpY.css'})


############### DASH LAYOUT #############################################################
#########################################################################################
#########################################################################################
#########################################################################################


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
    html.Div(dt.DataTable(rows=[{}]), style={'display': 'none'})
])


topic_search_page_layout = html.Div(children=
    [
        html.Div(
            [
            html.Div(
                    [
                        html.Img(
                            src='data:image/png;base64,{}'.format(kindi_logo.decode()),
                            # className='eight columns',
                            style={
                                'display':'block',
                                'float': 'left',
                                'margin-left':'auto',
                                'margin-right':'auto',
                                'max-height': '150px',
                                'width': 'auto',
                                'height': 'auto',
                            },
                        ),
                    ],
                    className='four columns',
                    style={
                        'height': '150px',
                    },
            ),
            html.Div(
                    [
                        html.H1(
                            'QNRF Dashboard',
                            # className='four columns',
                            style={
                                'position': 'relative',
                                'top': '50%',
                                'transform': 'translateY(-50%)',
                                'text-align': 'center',
                                # 'padding': '70px 0',
                                # 'max-height': '150px',
                                # 'margin-left':'auto',
                                # 'margin-right':'auto',
                            },
                        ),
                    ],
                    className='four columns',
                    style={
                        'height': '150px',
                    },
            ),
            html.Div(
                    [
                        html.Img(
                            src='data:image/png;base64,{}'.format(qu_logo.decode()),

                            style={
                                'display':'block',
                                'float': 'center',
                                'margin-left': 'auto',
                                'margin-right': 'auto',
                                'max-width': '100%',
                                'max-height': '150px',
                                'width': 'auto',
                                'height': 'auto',
                            },
                        ),
                    ],
                    className='four columns',
                    style={
                        'height': '150px',
                    },
            )
            ],
            className='twelve columns',
        ),

        html.Div([
            # dcc.Link('Navigate to "/professor-search-page"', href='/professor-search-page'),
            dcc.Link(html.Button('Go to Professor Search', className="button-primary",style={'margin':'0 5%', 'margin-right':'20px'}),
                     href='/professor-search-page'),
        ],
        style={'float':'right'}
        ),


        # html.Button('Navigate to "/professor-search-page',
        #             id='button-clear-values',
        #             className="button-primary",
        #             n_clicks=0,
        #             href='/professor-search-page',
        #             style={
        #                 'margin':'0 5%',
        #             },
        # ),


    # # SIGN OUT DASH BUTTON ############################
    # html.Div(
    #     id='sign-out-hidden',
    #     # children=,
    #     hidden='true',
    #     style={
    #         'visibility': 'hidden'},
    #     ),
    #
    # html.Div(children=[
    #     html.Button('Sign Out',
    #                 id='sign-out',
    #                 className="button-primary",
    #                 n_clicks=0,
    #                 style={
    #                     'margin': '0 5%',
    #                 },
    #     )
    # ]),


    # SEARCH FORM (TITLE) FOR RESEARCH KEYWORD AND FILTERS #############################
    html.Div(children=[
        html.Div(children='''
                Search by Research Keyword or Title :
                ''',
                 style={'float': 'left', 'display': 'inline-block'},
                 className='four columns',
                 ),
        html.Div(children='''
                Filter out topics containing:
                ''',
                 style={'float': 'center', 'display': 'inline-block'},
                 className='four columns',
                 ),
        ],
        style={'width': '100%', 'display': 'inline-block'}
        ),

    # HIDDEN DIV FOR STORING SEARCH VALUE FROM ELASTICSEARCH
    html.Div(
        id='search-ids-keywords',
        # children=,
        hidden='true',
        style={
            'visibility': 'hidden'},
        ),

    html.Div(
        id='filter-out-keyword-ids',
        # children=,
        hidden='true',
        style={
            'visibility': 'hidden'},
        ),

    # # TODO: DOES THIS WORK?
    # html.Div(
    #     id='common-dataframe',
    #     style={
    #         'display': 'none'},
    # ),


    # SEARCH FORM FOR RESEARCH KEYWORD AND FILTER
    html.Div([
        dcc.Input(
            id='search-keywords',
            className='four columns',
            placeholder='Search For Keyword',
            type='search',
            value=''
        ),
        dcc.Input(
            id='filter-out-keywords',
            className='four columns',
            placeholder='Keywords to filter out',
            type='search',
            value=''
        ),
        html.Button('Clear Keywords and Professors',
                    id='button-clear-values',
                    className="button-primary",
                    n_clicks=0,
                    style={
                        'margin':'0 5%',
                    },
        )
    ]),

    dcc.RadioItems(
        id='search-type',
        options=[
            {'label': 'Free Form Search', 'value': 'freeform'},
            {'label': 'Perfect Query (String Match)', 'value': 'stringmatch'},
        ],

        value='freeform'
    ),


    dcc.Dropdown(
        id='year-dropdown',
        options=year_dropdown_populator(),
        # value=data.start_year.unique(),
        # value=[y['value'] for y in options if 'value' in y],
        value=[],
        multi=True,
        placeholder="Filter by Years"
    ),

    dcc.Checklist(id='select-all-year',
                  options=[{'label': 'Select All Years', 'value': 0}],
                  values=[0]
    ),

    dcc.Dropdown(
        id='filter-by-institution-dropdown',
        options=institution_populator(),
        # options=[{'label':'WOHO', 'value':'LULU'}],
        # value=data.start_year.unique(),
        # value=[y['value'] for y in options if 'value' in y],
        value=[],
        multi=True,
        placeholder="Filter by University"
    ),
    dcc.Checklist(id='select-all-institution',
                  options=[{'label': 'Select All Universities', 'value': 0}],
                  values=[0]
    ),

    dcc.Dropdown(
        id='filter-by-funding-program-dropdown',
        options=funding_program_populator(),
        # options=[{'label':'WOHO', 'value':'LULU'}],
        # value=data.start_year.unique(),
        # value=[y['value'] for y in options if 'value' in y],
        value=[],
        multi=True,
        placeholder="Filter by Funding Program"
    ),
    dcc.Checklist(id='select-all-funding-program',
                  options=[{'label': 'Select All Funding Programs', 'value': 0}],
                  values=[0]
    ),
    dcc.Dropdown(
        id='filter-by-award-status-dropdown',
        options=award_status_populator(),
        # value=data.start_year.unique(),
        # value=[y['value'] for y in options if 'value' in y],
        value=[],
        multi=True,
        placeholder = "Filter by Award Status"
    ),

    dcc.Checklist(
        id='select-all-award-status',
        options=[{'label': 'Select All Award Status', 'value': 0}],
        values=[0]
    ),



    # MAIN GRAPH

    dcc.Graph(id='institution-count',
              config={'displayModeBar': False},# Remove the hover toolbar of plotly (default is True)
              hoverData={'points': [{'customdata': ''}]},
              clickData={'points': [{'customdata': ''}]},
              ),

    # GRAPHS FOR INSTITUTION COMPARISON

    html.Div(children=[
        html.Div(
            dcc.Graph(
                id='professor-count-1',
                hoverData={'points': [{'customdata': ''}]},
                clickData={'points': [{'customdata': ''}]},
                config={'displayModeBar': False},
                # style={'height': '1000px'}
            )
            , style={'max-height': '50vh', 'width': '50%', 'display': 'inline-block', 'overflowY': 'scroll'}
        ),
        html.Div(children=[
            html.H4("Projects of personnel selected"),
            html.Div(
                dtab.DataTable(
                    data=[{}],
                    columns=[{"name": i, "id": i} for i in ["Proposal Number:", "Proposal Title:"]],
                    # columns=[{'id': c, 'name': c} for c in professor_data.columns],

                    style_table={'maxHeight':'40vh',
                                 # 'overflowX': 'scroll',
                                 'overflowY': 'scroll'},
                    style_data={'whiteSpace': 'normal'},
                    n_fixed_rows=1,
                    editable=True,
                    # row_selectable='multi',
                    style_cell={'textAlign': 'left',
                                'maxWidth': '180px'},
                    style_cell_conditional=[
                        {'if': {'column_id': 'Proposal Number:'},
                         'width': '30%'},
                        {
                            'if': {'row_index': 'odd'},
                            'backgroundColor': 'rgb(248, 248, 248)'
                        }
                    ],
                    style_header={
                        'backgroundColor': 'white',
                        'fontWeight': 'bold'
                    },
                    # filterable=False,
                    # column_widths=[200, 600],
                    # sortable=False,
                    # selected_row_indices=[],
                    css=[{
                        'selector': '.dash-cell div.dash-cell-value',
                        'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
                    }],
                    id='professor-table'
                )
            )
        ],
            style={'max-height': '50vh', 'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}
        )

        ],
        style={'height': '100%', 'width': '100%', 'display': 'inline-block'}
    ),


    # GRAPHS FOR NETWORK OF PROFESSORS
    html.Div(children=[
        html.Div(
            dcc.Graph(
                id='researcher-personnel-connections-1',
                hoverData={'points': [{'customdata': ''}]},
                config={'displayModeBar': False}
            )
            , style={'width': '100%', 'display': 'inline-block'}
        )
        ],
        style={'width': '100%', 'display': 'inline-block'}
    ),
    # # TABLES FOR PROVIDING DATA (HTML DIV)
    # html.Div(children=[
    #     html.Div(
    #         children=generate_table(funding_data),
    #         id = 'table-1'
    #         # dcc.Graph(id='info-1')
    #         , style={'width': '50%','display': 'inline-block'}
    #     ),
    #     html.Div(
    #         children=generate_table(funding_data),
    #         id = 'table-2'
    #         # dcc.Graph(id='info-2')
    #         , style={'width': '50%','display': 'inline-block'}
    #     )
    #     ],
    #     style={'width': '100%', 'display': 'inline-block'}
    # )
])
















app.title= "QNRF Dashboard"


###### SERVER BASED FUNCTIONS ###########################################################
#########################################################################################
#########################################################################################
#########################################################################################


def start_dbconnection():
    conn = sqlite3.connect(server.database)
    return conn


def stop_dbconnection():
    pass


def get_database_values():
    try:
        conn = sqlite3.connect(server.database)
        cursor = conn.execute("SELECT users_id, username, password, is_admin FROM users")
        result_set = cursor.fetchall()
        # users = UserMap([DefaultUser(result_set[i][0], result_set[i][1], self.auto_hash, self.hash_function) for i in
        #                       range(len(result_set))])
        users = {}
        for i in range(len(result_set)):
            users[result_set[i][0]] = [result_set[i][1],result_set[i][2],result_set[i][3]]
        print(users)
        conn.close()
        return users
    except sqlite3.Error as er:
        print("error while getting values", er.message)


def delete_database_values(id):
    try:
        id = str(id)
        conn = sqlite3.connect(server.database)
        cur = conn.cursor()
        print(id)
        sql_query = "DELETE FROM users WHERE users_id = ?"
        cur.execute(sql_query, (id,))
        conn.commit()
        conn.close()
    except sqlite3.Error as er:
        print("error while deleting values", er.message)


def add_database_rows(row):
    try:
        conn = sqlite3.connect(server.database)
        conn.execute("INSERT INTO users VALUES(?)", row)
        conn.close()
    except sqlite3.Error as er:
        print("error while adding values", er.message)

###### SERVER ROUTING CODE ##############################################################
#########################################################################################
#########################################################################################
#########################################################################################

@server.route("/")
def index():
    return redirect(url_for('/dash/'))


@server.route("/admin", methods=['GET', 'POST'])
def admin():
    print("at the admin login page")
    return render_template('admin_login.html')


@server.route("/admin-page", methods=['GET'])
def admin_page():
    print("at the admin page")
    id = request.args.get('delete-val')
    if id:
        id = int(id)
        print(id)
        print(type(id))
        delete_database_values(id)
    users = get_database_values()
    return render_template('admin_page.html', users=[users])


# @server.route("/")
# def index():
#     return redirect(url_for('login'))
#
# @server.route('/login', methods=['GET', 'POST'])
# def login():
#     error = None
#     if request.method == 'POST':
#         if request.form['username'] != 'admin' or request.form['password'] != 'admin':
#             error = 'Invalid Credentials. Please try again.'
#         else:
#             return redirect(url_for('/dash/'))
#     return render_template('login.html', error=error)



###### DASH CALLBACK CODES ##############################################################
#########################################################################################
#########################################################################################
#########################################################################################

@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname')])
def display_page(pathname):
    print(pathname)
    if pathname == '/professor-search-page':
        return professor_search_page_layout
    elif pathname == '/topic-search-page':
        return topic_search_page_layout
    else:
        return topic_search_page_layout
    # You could also return a 404 "URL not found" page here

# @app.callback(
#     Output('common-dataframe','children'),
#     [Input('year-dropdown', 'value'),
#      Input('filter-by-institution-dropdown', 'value'),
#      Input('filter-by-funding-program-dropdown', 'value'),
#      Input('filter-by-award-status-dropdown', 'value'),
#      # Input('search-ids-keywords', 'children'),
#      # Input('filter-out-keyword-ids', 'children'),
#      # Input('search-keywords', 'value'),
#      # Input('filter-out-keywords', 'value')
#      ])
# def common_dataframe(selected_year, selected_uni, selected_funding, selected_award_status):
#
#     filtered_data = funding_data[funding_data.start_year.isin(selected_year)
#                                  & funding_data['Submitting Institution Name:'].isin(selected_uni)
#                                  & funding_data['Project Status:'].isin(selected_award_status)
#                                  & funding_data['Program Cycle:'].isin(selected_funding)]
#
#     return filtered_data.to_json(date_format='iso', orient='split')


@app.callback(
    Output('institution-count', 'figure'),
    [Input('year-dropdown', 'value'),
     Input('filter-by-institution-dropdown', 'value'),
     Input('filter-by-funding-program-dropdown', 'value'),
     Input('filter-by-award-status-dropdown', 'value'),
     Input('search-ids-keywords', 'children'),
     Input('filter-out-keyword-ids', 'children'),
     Input('search-keywords', 'value'),
     Input('filter-out-keywords', 'value')])
def generate_graph(selected_year, selected_uni, selected_funding, selected_award_status, search_ids_keywords, filter_keywords_ids, search_keywords, filter_keywords):
    # proposal_number = data["Proposal Number"]
    # submitting_institution_name = data["Submitting Institution Name:"]
    print("selected_year is", selected_year)
    print("selected_uni's are", selected_uni)
    print("selected_funding's are", selected_funding)
    print("selected_Awards's are", selected_award_status)


    # search id keywords json convert
    print("Search ID keywords are before JSON.LOADS", search_ids_keywords)

    if search_ids_keywords:
        search_ids_keywords = json.loads(search_ids_keywords)
        search_ids_keywords = np.array(search_ids_keywords)
    # search_ids_keywords = dict(json.loads(search_ids_keywords))
    # print("selected_id keywords are", search_ids_keywords)

    # search id professor json convert
    # search_ids_professors = json.loads(search_ids_professors)
    # print("selected_id professors are", search_ids_professors)

    # Filters data on the selected year and selected university

    #TODO: Selected insitutition when its -1 and below three selected it creates a single graph with bogus values
    filtered_data = funding_data[funding_data.start_year.isin(selected_year)
                                 & funding_data['Submitting Institution Name:'].isin(selected_uni)
                                 & funding_data['Project Status:'].isin(selected_award_status)
                                 & funding_data['Program Cycle:'].isin(selected_funding)]


    # Filters data on the search id and professors if content present in search box
    if search_keywords:
        if len(search_keywords) > 0 and len(search_ids_keywords) > 0:
            filtered_data = filtered_data.loc[filtered_data._id.isin(search_ids_keywords[0:,0])]

    if filter_keywords == 0:
        if len(filter_keywords) > 0 and len(filter_keywords_ids) > 0:
            filtered_data = filtered_data.loc[filtered_data._id.isin(filter_keywords_ids)]

    # filtered_data = filtered_data.iloc[search_ids]
    # dff = df[df['Well_Status'].isin(well_statuses)
    #          & df['Well_Type'].isin(well_types)
    #          & (df['Date_Well_Completed'] > dt.datetime(year_slider[0], 1, 1))
    #          & (df['Date_Well_Completed'] < dt.datetime(year_slider[1], 1, 1))]

    submitting_institution_name_count = filtered_data["Submitting Institution Name:"].value_counts()

    print("number of values in graph 1 is", len(submitting_institution_name_count))

    trace1 = go.Bar(x=submitting_institution_name_count.index,
                    y=submitting_institution_name_count,
                    name='Total Count',
                    customdata=submitting_institution_name_count.index
                    # text=submitting_institution_name_count.index,
                    # textposition='auto'
                    )

    return {
        'data' : [trace1],
        'layout': go.Layout(
            # autosize=False,
            title='Count of projects at Institutions in {search_term} domains'.format(search_term =search_keywords or 'all'),
            # title="Lead Investigators at {uni}".format(uni=selected_uni)
            # xaxis=dict(tickangle=-45),
            xaxis=dict(
                tickangle=-45,
                zeroline=False,  # no thick y=0 line
                showgrid=False,  # no horizontal grid lines
                showticklabels=False,  # no y-axis tick labels
            ),
            yaxis=dict(
                # type='log'
            ),
            showlegend=True,
            # legend=go.Legend(
            #     x=0,
            #     y=1.0
            # ),
            # bargap =0.5,
            # width = 100,
            # autosize=F,
            margin = go.Margin(l=40, r=0, t=40, b=30),
            # paper_bgcolor='rgb(233,233,233)',  # set paper (outside plot)
            plot_bgcolor='rgb(192,192,192)',  # plot color to grey
            annotations=list([make_annotation_vertical(x,y) for x,y in zip(submitting_institution_name_count.index, submitting_institution_name_count)])
        )
    }


@app.callback(
    Output('professor-count-1', 'figure'),
    [Input('year-dropdown', 'value'),
     Input('filter-by-funding-program-dropdown', 'value'),
     Input('search-ids-keywords', 'children'),
     Input('search-keywords', 'value'),
     # Input('select-first-institution', 'value'),
     Input('institution-count', 'clickData'),])
def generate_graph1(selected_year, selected_funding, search_ids_keywords, search_keywords, clickData):
    # proposal_number = data["Proposal Number"]
    # submitting_institution_name = data["Submitting Institution Name:"]
    # selected_uni = [selected_uni]
    start_time = time.time()
    selected_uni = clickData['points'][0]['customdata']
    print(selected_uni)

    print("selected_year is", selected_year)

    if len(selected_uni) < 1:
        selected_uni = None
    print("selected_uni in graph1 is", selected_uni)

    # search id keywords json convert
    # search_ids_keywords = json.loads(search_ids_keywords)
    if search_ids_keywords:
        search_ids_keywords = json.loads(search_ids_keywords)
        search_ids_keywords = np.array(search_ids_keywords)
    # print("selected_id keywords are", search_ids_keywords)

    # Filters data on the selected year and selected university
    filtered_data = funding_data[(funding_data.start_year.isin(selected_year))
                                 & (funding_data['Submitting Institution Name:'] == selected_uni)
                                 & (funding_data['Program Cycle:'].isin(selected_funding))]

    # Filters data on the search id if content present in search box
    if search_keywords and search_ids_keywords.any():
        if len(search_keywords) > 0 and len(search_ids_keywords) > 0:
            # filtered_data = filtered_data.loc[filtered_data._id.isin(search_ids_keywords)]
            filtered_data = filtered_data.loc[filtered_data._id.isin(search_ids_keywords[0:, 0])]

        # filtered_data = filtered_data.iloc[search_ids]
    # dff = df[df['Well_Status'].isin(well_statuses)
    #          & df['Well_Type'].isin(well_types)
    #          & (df['Date_Well_Completed'] > dt.datetime(year_slider[0], 1, 1))
    #          & (df['Date_Well_Completed'] < dt.datetime(year_slider[1], 1, 1))]

    # submitting_institution_name_count = filtered_data["Submitting Institution Name:"].value_counts()

    lead_investigators = filtered_data["Lead Investigator:"].value_counts()


    # TODO: Reduce the total number of bars displayed if above 30

    total_lead_investigators = len(lead_investigators)

    # while total_lead_investigators > 30:
    #     if search_keywords and search_ids_keywords.any():
    #         if len(search_keywords) > 0 and len(search_ids_keywords) > 0:
    #             difference = total_lead_investigators - 30
    #             search_ids_keywords = search_ids_keywords[:-difference]
    #
    #             filtered_data = filtered_data.loc[filtered_data._id.isin(search_ids_keywords[0:, 0])]
    #             lead_investigators = filtered_data["Lead Investigator:"].value_counts()
    #
    #             total_lead_investigators = len(lead_investigators)
    #
    #     lead_investigators = lead_investigators[0:30]
    #     total_lead_investigators = len(lead_investigators)



    bar_width = np.full((total_lead_investigators,), .7)
    print(total_lead_investigators)

    if total_lead_investigators > 20:
        graph_height = total_lead_investigators * 15
        # if graph_height < 450:
        #     graph_height = 450
        print("Graph height is", graph_height)
    else:
        graph_height = 300
        print("Graph height is", graph_height)


    # trace1 = go.Bar(x=lead_investigators, y=lead_investigators.index, name='Total Count',orientation = 'h', customdata=lead_investigators.index)
    trace1 = go.Bar(x=lead_investigators, y=lead_investigators.index, name='Total Count', orientation='h',
                    customdata=lead_investigators.index)


    title = "Lead Investigators at {uni}".format(uni=selected_uni)

    print("Total number of lead investigators at {uni} is {num}".format(uni=selected_uni, num=len(lead_investigators)))

    end_time = time.time()
    print("Total time taken for professor-count-1, ", (end_time - start_time))

    return {
        'data': [trace1],
        'layout': go.Layout(
            # autosize=True
            # width=800,
            height=graph_height,
            title=title,
            xaxis=dict(
                # tickangle=-45,
                zeroline=False,  # no thick y=0 line
                showgrid=True,  #  Vertical grid lines
                showticklabels=True,  # x-axis tick labels
                dtick=1
            ),
            yaxis=dict(
                showticklabels=False  # no y-axis tick labels
            ),
            showlegend=True,
            legend=go.Legend(
                x=1.0,
                y=1.0
            ),
            # bargap=0.5,
            # margin=go.Margin(l=10, r=10, t=10, b=10),
            margin=go.Margin(l=40, r=5, t=40, b=30),
            plot_bgcolor='rgb(192,192,192)',  # plot color to grey
            hovermode='closest',
            annotations=list([make_annotation_horizontal(x, y) for x, y in zip(lead_investigators.index, lead_investigators)])
        )
    }


@app.callback(
    Output('year-dropdown', 'value'),
    [Input('select-all-year', 'values')],
    [State('year-dropdown', 'options'),
     State('year-dropdown', 'value')])
def select_all_year(selected, options, values):
    print(selected)
    print(options)
    print(values)
    if len(selected) > 0:
        print([i['value'] for i in options])
        return [i['value'] for i in options]
    else:
        return []


@app.callback(
    Output('filter-by-institution-dropdown', 'value'),
    [Input('select-all-institution', 'values')],
    [State('filter-by-institution-dropdown', 'options'),
     State('filter-by-institution-dropdown', 'value')])
def select_all_institution(selected, options, values):
    print(selected)
    print(options)
    print(values)
    if len(selected) > 0:
        print([i['value'] for i in options])
        return [i['value'] for i in options]
    else:
        return []

@app.callback(
    Output('filter-by-funding-program-dropdown', 'value'),
    [Input('select-all-funding-program', 'values')],
    [State('filter-by-funding-program-dropdown', 'options'),
     State('filter-by-funding-program-dropdown', 'value')])
def select_all_funding_program(selected, options, values):
    print(selected)
    print(options)
    print(values)
    if len(selected) > 0:
        print([i['value'] for i in options])
        return [i['value'] for i in options]
    else:
        return []

@app.callback(
    Output('filter-by-award-status-dropdown', 'value'),
    [Input('select-all-award-status', 'values')],
    [State('filter-by-award-status-dropdown', 'options'),
     State('filter-by-award-status-dropdown', 'value')])
def select_all_award_status(selected, options, values):
    print(selected)
    print(options)
    print(values)
    if len(selected) > 0:
        print([i['value'] for i in options])
        return [i['value'] for i in options]
    else:
        return []


# SEARCH FUNCTIONS
@app.callback(
    Output('search-ids-keywords', 'children'),
    [Input('search-keywords', 'value'),
     Input('filter-out-keywords', 'value')],
    [State('search-keywords', 'value'),
     State('search-type','value')])
def search_keywords(search_term, must_not_term, state, search_type):
    """
    Gets the search term from the dash app for searching.
    :param search_term: User entered search term
    :return: json.dumps of dictionary
    """
    print("search_type is ", search_type)

    # Search types are freeform and stringmatch

    if search_type == "freeform":
        print("Freeform Search")
        print(search_term)
        print("search_keywords must not",must_not_term)
        if search_term == "" or search_term is None:
            return json.dumps([])
        else:
            # pandas_index_list = elastic_dash.test_search(search_term, must_not_term)
            pandas_index_list = elastic_dash.test_search_standard(search_term, must_not_term)
            # pandas_index_list = elastic_dash.test_search_desc2(search_term, must_not_term)
            # pandas_index_list = elastic_dash.test_search_fivegrams(search_term, must_not_term)
            return json.dumps(pandas_index_list)
    else:
        print("Perfect Search")
        print(search_term)
        print("search_keywords must not", must_not_term)
        if search_term == "" or search_term is None:
            return json.dumps([])
        else:
            # pandas_index_list = elastic_dash.test_search(search_term, must_not_term)
            # pandas_index_list = elastic_dash.test_search_standard(search_term, must_not_term)
            pandas_index_list = elastic_dash.test_search_standard_perfect(search_term, must_not_term)
            # pandas_index_list = elastic_dash.test_search_desc2(search_term, must_not_term)
            # pandas_index_list = elastic_dash.test_search_fivegrams(search_term, must_not_term)
            return json.dumps(pandas_index_list)




# PROFESSOR RELATIONSHIP
@app.callback(
    Output('researcher-personnel-connections-1', 'figure'),
    [Input('professor-count-1', 'clickData')],
    [State('year-dropdown', 'value'),
     State('search-ids-keywords', 'children'),
     State('search-keywords', 'value'),
     State('filter-by-funding-program-dropdown', 'value')])
def generate_personnel_graph_1(clickData, selected_year, search_ids, search_keywords, selected_funding):
    prof_name = clickData['points'][0]['customdata']
    print("selected professor for network graph is ", prof_name)


    # Search Id is a string here.
    if search_keywords and len(search_keywords) > 0 and search_ids:
        search_ids = json.loads(search_ids)

    professor_data = funding_data[(funding_data['Lead Investigator:'] == prof_name)
                                  # & (funding_data.start_year.isin(selected_year))
                                  # & (funding_data.index.isin(search_ids))
                                  & (funding_data['Program Cycle:'].isin(selected_funding))]

    merged = personnel_data.merge(professor_data, on="Proposal Number:")

    collaborating_personnel = merged[merged["investigator"] != prof_name]

    # collaborating_personnel_counts = collaborating_personnel.investigator.value_counts()






    def custom_apply(x):
        return pd.Series(dict(institution=list(x["institution"]),
                              proposal_number=list(x["Proposal Number:"]),
                              proposal_title=list(x["Proposal Title:"]),
                              count=x["investigator"].count(),
                              project_status=list(x["Project Status:"]),
                              ))

    collaborating_personnel_counts = collaborating_personnel.groupby('investigator').apply(custom_apply)

    professor_graph = create_graph_network(start_node=prof_name, connections=collaborating_personnel_counts)

    print(professor_graph.nodes(), "/n")
    print(professor_graph.edges())
    # Now to modularize
    node_trace, edge_trace, edge_label_trace = create_graph_network_visualization(graph_network=professor_graph, connections=collaborating_personnel, connections_grouped=collaborating_personnel_counts)

    title = "Personnel who worked with {prof_name}".format(prof_name=prof_name)

    fig = go.Figure(data=[edge_trace, edge_label_trace, node_trace],
                    layout=go.Layout(
                        # title=('Personnel who worked with %s', prof_name),
                        title=title,
                        titlefont=dict(size=16),
                        showlegend=False,
                        hovermode='closest',
                        margin=dict(b=20, l=5, r=5, t=40),
                        # annotations=[dict(
                        #     text="Python code: <a href='https://plot.ly/ipython-notebooks/network-graphs/'> https://plot.ly/ipython-notebooks/network-graphs/</a>",
                        #     showarrow=False,
                        #     xref="paper", yref="paper",
                        #     x=0.005, y=-0.002)],
                        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

    return fig

# UPDATING PROFESSOR DATATABLE
@app.callback(
    Output('professor-table', 'data'),
    [Input('professor-count-1', 'clickData')],
    [State('year-dropdown', 'value'),
     State('search-ids-keywords', 'children'),
     State('search-keywords', 'value'),
     State('filter-by-funding-program-dropdown', 'value')])
def update_datatable(clickData, selected_year, search_ids_keywords, search_keywords, selected_funding):
    """
    For user selections, return the relevant table
    """

    prof_name = clickData['points'][0]['customdata']
    print("selected professor for network graph is ", prof_name)

    # TODO: Handle no search_ids or Nonetype search ids DONE
        # print(" Search IDS ************* 8********** ****** here are this", search_ids_keywords[0:,0])

    professor_data = funding_data[(funding_data['Lead Investigator:'] == prof_name)
                                  & (funding_data.start_year.isin(selected_year))
                                  # & (funding_data._id.isin(search_ids_keywords[0:,0]))
                                  & (funding_data['Program Cycle:'].isin(selected_funding))]

    if search_keywords and len(search_keywords) > 0:
        search_ids_keywords = json.loads(search_ids_keywords)
        search_ids_keywords = np.array(search_ids_keywords)
        professor_data = professor_data[(professor_data._id.isin(search_ids_keywords[0:, 0]))]


    # collaborating_personnel_counts = collaborating_personnel.investigator.value_counts()
    professor_data = professor_data[
        ["Proposal Number:", "Proposal Title:"]]

    # ["Proposal Number:", "Submitting Institution Name:", "Project Status:", "Proposal Title:"]]
    return professor_data.to_dict("rows")
    # return professor_data


##############################################################################
##############################################################################
######################LOGOUT##################################################


# # Logout
# @app.callback(
#     Output('sign-out-hidden', 'children'),
#     [Input('sign-out','n_clicks')])
# def logout(n_clicks):
#     if n_clicks:
#         # auth.login_manager.
#         # print(app)
#         # print(redirect('logout'))
#         print ("why lord")
#         auth.logout()
#         # redirect('/logout')


# Reset Forms and Dropdown lists
@app.callback(
    Output('search-keywords', 'value'),
    [Input('button-clear-values','n_clicks')])
def reset_search_keywords(n_clicks):
    if n_clicks:
        return ''

@app.callback(
    Output('filter-out-keywords', 'value'),
    [Input('button-clear-values','n_clicks')])
def reset_filter_out_keywords(n_clicks):
    if n_clicks:
        return ''

# @app.callback(
#     Output('year-dropdown', 'value'),
#     [Input('button-clear-values','n_clicks')])
# def reset_year_dropdown(n_clicks):
#     if n_clicks:
#         return []
#
# @app.callback(
#     Output('filter-by-institution-dropdown', 'value'),
#     [Input('button-clear-values','n_clicks')])
# def reset_filter_by_institution_dropdown(n_clicks):
#     if n_clicks:
#         return []

###### PROFESSOR PAGE LAYOUT ###########################################################
#########################################################################################
#########################################################################################
#########################################################################################

# TODO: MAKE THE SEARCH PAGE FOR PROFESSORS


professor_search_page_layout =  html.Div([

    html.Div(
        [
            html.Div(
                    [
                        html.Img(
                            src='data:image/png;base64,{}'.format(kindi_logo.decode()),
                            # className='eight columns',
                            style={
                                'display':'block',
                                'float': 'left',
                                'margin-left':'auto',
                                'margin-right':'auto',
                                'max-height': '150px',
                                'width': 'auto',
                                'height': 'auto',
                            },
                        ),
                    ],
                    className='four columns',
                    style={
                        'height': '150px',
                    },
            ),
            html.Div(
                    [
                        html.H1(
                            'QNRF Dashboard',
                            # className='four columns',
                            style={
                                'position': 'relative',
                                'top': '50%',
                                'transform': 'translateY(-50%)',
                                'text-align': 'center',
                                # 'padding': '70px 0',
                                # 'max-height': '150px',
                                # 'margin-left':'auto',
                                # 'margin-right':'auto',
                            },
                        ),
                    ],
                    className='four columns',
                    style={
                        'height': '150px',
                    },
            ),
            html.Div(
                    [
                        html.Img(
                            src='data:image/png;base64,{}'.format(qu_logo.decode()),

                            style={
                                'display':'block',
                                'float': 'center',
                                'margin-left': 'auto',
                                'margin-right': 'auto',
                                'max-width': '100%',
                                'max-height': '150px',
                                'width': 'auto',
                                'height': 'auto',
                            },
                        ),
                    ],
                    className='four columns',
                    style={
                        'height': '150px',
                    },
            )
            ],
            className='twelve columns',
        ),

    html.Div([
        dcc.Link(html.Button('Go to Project Search', className="button-primary", style={'margin':'0 5%', 'margin-right':'20px'}),
                 href='/topic-search-page'),
    ],
        style={'float': 'right'}),


    html.Div(children=[
        html.Div(children='''
                Search by Professor Name:
                ''',
                 style={'float': 'left', 'display': 'inline-block'},
                 className='four columns',
                 ),
        html.Div(children='''
                Search by Professors Research Domain:
                ''',
                 style={'float': 'center', 'display': 'inline-block'},
                 className='four columns',
                 ),
        ],
        style={'width': '100%', 'display': 'inline-block'}
        ),
    html.Div(children=[
        dcc.Input(
            id='search-personnel',
            className='four columns',
            placeholder='Search for a Professor',
            type='search',
            # value="",
            style={'float': 'left'},
        ),
        dcc.Input(
            id='search-keywords-two',
            className='four columns',
            placeholder='Search for a Keyword',
            type='search',
            # value="",
            style={'float': 'center'},
        ),
    ],
        style={'width': '100%', 'display': 'inline-block'}
    ),

    # HIDDEN DIV FOR STORING SEARCH VALUE FROM ELASTICSEARCH

html.Div(children=[

    html.Div(
        id='search-ids-professors-keywords',
        # children=,
        hidden='true',
        # style={
        #     'visibility': 'hidden'},
    ),

    html.Div(
        id='search-ids-personnel',
        # children=,
        hidden='true',
        # style={
        #     'visibility': 'hidden'},
    ),
    ],
        # style={'display': 'none'},
    ),

    dcc.Dropdown(
        id='filter-by-funding-program-dropdown',
        options=funding_program_populator(),
        # options=[{'label':'WOHO', 'value':'LULU'}],
        # value=data.start_year.unique(),
        # value=[y['value'] for y in options if 'value' in y],
        value=[],
        multi=True,
        placeholder="Filter by Funding Program"
    ),
    dcc.Checklist(id='select-all-funding-program',
                  options=[{'label': 'Select All Funding Programs', 'value': 0}],
                  values=[0]
    ),

    dcc.Dropdown(
        id='year-dropdown',
        options=year_dropdown_populator(),
        # value=data.start_year.unique(),
        # value=[y['value'] for y in options if 'value' in y],
        value=[],
        multi=True,
        placeholder="Filter by Years"
    ),

    dcc.Checklist(id='select-all-year',
                  options=[{'label': 'Select All Years', 'value': 0}],
                  values=[0]
    ),

    html.Div(children=[
        html.Div(
            dtab.DataTable(
                id='personnel-search-table',
                data=[{}],
                columns=[{"name": i, "id": i} for i in ["Personnel", "Total Projects"]],

                style_table={
                    'maxHeight':'40vh',
                    # 'height': '50vh',
                    # 'overflowX': 'scroll',
                    'overflowY': 'scroll',
                    'border': 'thin lightgrey solid'
                             },
                style_cell={'textAlign': 'left',
                            'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
                            },
                style_header={
                    'backgroundColor': 'white',
                    'fontWeight': 'bold'
                },

                n_fixed_rows=1,
                row_selectable=True,

                # filterable=False,
                # column_widths=[200, 600],
                # sortable=False,
                selected_rows=[],
                # pagination_mode=False,
                css=[{
                        'selector': '.dash-cell div.dash-cell-value',
                        'rule': 'display: inline; white-space: inherit; overflow: inherit; text-overflow: inherit;'
                    }],
                # pagination_settings={
                #     'page_size':'10000',
                # }
                ),
            style={'height': '50vh', 'width': '50%', 'display': 'inline-block', 'vertical-align': 'top'},
        ),
        html.Div(
            dcc.Graph(id='personnel-trend-graph',
                      config={'displayModeBar': False},  # Remove the hover toolbar of plotly (default is True)
                      hoverData={'points': [{'customdata': ''}]},
                      clickData={'points': [{'customdata': ''}]},
                      ),
            style={'height': '100%', 'width': '50%', 'display': 'inline-block','vertical-align': 'top'}
        ),

    ],
        style={'height':'50vh','width': '100%', 'display': 'inline-block', 'vertical-align': 'top'}
    ),

    html.Div([
        html.H3(children=["init"], id="selected-profsy")
    ]),

    html.Div(children=[
        html.Div(
            dt.DataTable(
                id='personnel-table-two',
                rows=[{}],
                # columns=professor_data.columns,
                row_selectable=True,
                filterable=False,
                column_widths=[200, 600],
                sortable=False,
                selected_row_indices=[],

            ),
            style={'height':'100%','width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}
        ),
        html.Div(
            dcc.Graph(id='personnel-outcome-pie-chart',
                      config={'displayModeBar': False},  # Remove the hover toolbar of plotly (default is True)
                      hoverData={'points': [{'customdata': ''}]},
            ),
            style={'height': '100%','width': '50%', 'display': 'inline-block', 'vertical-align': 'top'}
        )
    ],
        style={'height': '100%', 'width': '100%', 'display': 'inline-block', 'vertical-align': 'top'}
    ),

])

# html.Div(children=[
#                       html.Div(
#                           dcc.Graph(
#                               id='professor-count-1',
#                               hoverData={'points': [{'customdata': ''}]},
#                               clickData={'points': [{'customdata': ''}]},
#                               config={'displayModeBar': False}
#                           )
#                           , style={'height': '100%', 'width': '50%', 'overflowY': 'scroll', 'display': 'inline-block'}
#                       ),



@app.callback(
    Output('search-ids-personnel', 'children'),
    [Input('search-personnel', 'value')])
def search_professors(search_term):
    """
    Gets the search term from the dash app for searching.
    :param search_term: User entered search term
    :return: None
    """
    print("Professor to search", search_term)
    if search_term == "" or search_term is None:
        return json.dumps([])
    else:
        # pandas_index_list = elastic_dash.search_professors(search_term)
        pandas_index_list = elastic_dash.search_personnel(search_term)
        print("pandas index list ", pandas_index_list)
        return json.dumps(pandas_index_list)


@app.callback(
    Output('search-ids-professors-keywords', 'children'),
    [Input('search-keywords-two', 'value')])
def search_professors_keywords(search_term):
    """
    Gets the search term from the dash app for searching.
    :param search_term: User entered search term
    :return: json.dumps of dictionary
    """
    print(search_term)
    # print("search_keywords must not",must_not_term)
    if search_term == "" or search_term is None:
        return json.dumps([])
    else:
        # pandas_index_list = elastic_dash.test_search(search_term, must_not_term)
        pandas_index_list = elastic_dash.test_search_standard(search_term, "")
        # pandas_index_list = elastic_dash.test_search_desc2(search_term, must_not_term)
        # pandas_index_list = elastic_dash.test_search_fivegrams(search_term, must_not_term)
        return json.dumps(pandas_index_list)

@app.callback(
    Output('selected-profsy', 'children'),
    [Input('personnel-search-table', 'selected_rows')],
    [State('personnel-search-table', 'data')])
def selected_professor(personnel_search_table_selected_indices, rows):
    personnel = pd.DataFrame(rows)
    name = None
    if personnel_search_table_selected_indices:
        print(personnel_search_table_selected_indices)
        print(type(personnel_search_table_selected_indices))
        name = personnel["Personnel"].iloc[personnel_search_table_selected_indices[0]]
        # personnel_search_table_selected_indices = str(personnel_search_table_selected_indices)

    if name:
        return "Selected Professor is ", name
    else:
        return "No Professor Selected"


@app.callback(
    Output('personnel-trend-graph', 'figure'),
    [Input('filter-by-funding-program-dropdown', 'value'),
     Input('year-dropdown', 'value'),
     Input('personnel-search-table', 'selected_rows'),
     Input('personnel-search-table', 'data'),
     Input('search-ids-personnel', 'children'),
     Input('search-ids-professors-keywords', 'children')],
    [State('search-personnel', 'value'),
     State('search-keywords-two', 'value')])
def generate_personnel_trend_graph(selected_funding, selected_year, selected_row_indices, rows, search_ids_personnel, search_ids_professors_keywords, personnel_name, search_keywords):
    """
    Create the Personnel Trend Graph with scatterplot
    :param selected_row_indices:
    :param rows:
    :return:
    """

    names = []
    personnel = pd.DataFrame(rows)
    if selected_row_indices:
        names = personnel["Personnel"].iloc[selected_row_indices]


    filtered_data = funding_data[
        funding_data.start_year.isin(selected_year)
        # & funding_data['Submitting Institution Name:'].isin(selected_uni)
        # & funding_data['Project Status:'].isin(selected_award_status)
        & funding_data['Program Cycle:'].isin(selected_funding)]


    selected_personnel_data = filtered_data.loc[filtered_data["Lead Investigator:"].isin(names)]



    # Getting the projects of the selected names from personnel_data

    personnel_data_filtered = personnel_data
    personnel_data_filtered = personnel_data_filtered[
        personnel_data_filtered["Proposal Number:"].isin(filtered_data["Proposal Number:"])]

    personnel_data_filtered = personnel_data_filtered[personnel_data_filtered["investigator"].isin(names)]

    # A pandas dataframe containg the list of projects for each selected personnel

    if search_keywords and len(search_keywords) > 0:
        if len(search_ids_professors_keywords) > 0:
            search_ids_professors_keywords = json.loads(search_ids_professors_keywords)
            search_ids_professors_keywords = np.array(search_ids_professors_keywords)

            # Using the dataset only to get relevant names of the personnel who are involved in the project
            # from personnel_data
            filtered_data = filtered_data[filtered_data._id.isin(search_ids_professors_keywords[0:, 0])]
            list_of_projects = filtered_data["Proposal Number:"]
            personnel_data_filtered = personnel_data_filtered[
                personnel_data_filtered["Proposal Number:"].isin(list_of_projects)]

            # print("Personnel Projects list is ", personnel_projects_list)
            # personnel_names = personnel_data_filtered["investigator"].unique()
            # print("Personnel Who have worked in this field are ", personnel_names)

    personnel_projects_list = personnel_data_filtered.groupby('investigator')['Proposal Number:'].apply(list)
    print("Personnel Projects list is ", personnel_projects_list)




    # if personnel_name and len(personnel_name) > 0:
    #     if len(search_ids_personnel) > 0:
    #         # Using the dataset only to get relevant names of the personnel who are involved in the project
    #         # from personnel_data
    #
    #         personnel_data_filtered = personnel_data_filtered[personnel_data_filtered._id.isin(search_ids_personnel)]
    #
    #         # Filtering the datasets based on search ids and filtered_data
    #         # Find a better way to do filters by join?
    #
    #         filtered_data = filtered_data[
    #             filtered_data["Proposal Number:"].isin(personnel_data_filtered["Proposal Number:"])]
    #
    #         personnel_projects_list = personnel_data_filtered[["investigator", "Proposal Number:"]].groupby(
    #             'investigator').agg({"Proposal Number:": lambda x: [].append(x)})
    #
    #         print("Personnel Projects list is ", personnel_projects_list)
    #         personnel_names = personnel_data_filtered["investigator"].unique()
    #         print("Personnel Who have worked in this field are ", personnel_names)


    def make_project_count_dict(df):
        """
        From the DF that is passed ( containing one personnel with all his projects, calculates the number of years a
        project was active,
        :param df:
        :return: An Ordered Dictionary with the number of projects active per year for that personnel.
        """
        year_lists = []
        null_date_info_projects = 0
        for i in range(len(df)):
            start_date = df["Start Date:"].iloc[i]
            end_date = df["End Date:"].iloc[i]
            if (start_date == -1) or (end_date == -1):
                null_date_info_projects += 1
                continue
            year_lists.append(list(range(start_date.year, end_date.year + 1))) # +1 because the project is active that year. It needs to show on graph
        print(year_lists)
        year_count_dict = OrderedDict.fromkeys(range(2000, datetime.now().year + 5), 0)
        print(year_count_dict)
        for i in year_lists:
            for j in i:
                year_count_dict[j] += 1
        return year_count_dict, null_date_info_projects

    def make_traces(names, personnel_projects_list):
        traces = []
        null_date_info_projects = 0
        for i in names:
            list_of_projects = personnel_projects_list.loc[i]
            # list_of_projects = personnel_projects_list["Proposal Number:"].loc[personnel_projects_list["investigator"] == i]
            list_of_project_records = filtered_data.loc[filtered_data["Proposal Number:"].isin(list_of_projects)] # Passing the DF containing all the projects that a personnel was involved with
            personnel_year_count_dict, null_date_info_projects = make_project_count_dict(list_of_project_records)
            sample_trace_object = go.Scatter(
                x=list(personnel_year_count_dict.keys()),
                y=list(personnel_year_count_dict.values()),
                opacity=0.7,
                # Adding the null_date_info_projects into the name
                name=i +" "+ str(null_date_info_projects),
                line=dict(
                    # color=('rgb(22, 96, 167)'),
                    width=4,
                    shape='hv'
                    # colorscale='YlGnBu'
                ),
                mode='lines+markers'
            )
            traces.append(sample_trace_object)
        return traces

    traces = make_traces(names, personnel_projects_list)


    # years = [i for i in range(2008,2018)]
    # numbers = random.choices(population=[0, 1, 2, 3], k=len(years))

    # personnel = "Doctor Name"

    # trace1 = go.Scatter(
    #     x=years,
    #     y=numbers,
    #     name='Professor Name Here',
    #     line=dict(
    #         color=('rgb(22, 96, 167)'),
    #         width=4,
    #     ),
    #     mode='lines+markers'
    # )


    return {
        'data': traces,
        'layout': go.Layout(
            # autosize=False,
            title='Projects in a year for selected personnel',
            xaxis=dict(
                # tickangle=-45,
                zeroline=False,  # no thick y=0 line
                showgrid=False,  # no horizontal grid lines
                showticklabels=True,  # no y-axis tick labels
                dtick=1,
            ),
            yaxis=dict(
                # type='log'
                dtick=1,
            ),
            showlegend=True,
            # legend=go.Legend(
            #     x=0,
            #     y=1.0
            # ),
            # legend=dict(x=.75, y=1),
            # bargap =0.5,
            # width = 100,
            # autosize=F,
            margin=go.layout.Margin(l=40, r=0, t=30, b=40),
            # paper_bgcolor='rgb(233,233,233)',  # set paper (outside plot)
            plot_bgcolor='rgb(192,192,192)',  # plot color to grey
        )
    }

#
# @app.callback(
#     Output('personnel-search-table', 'rows'),
#     [Input('search-ids-personnel','children'),
#      Input('filter-by-funding-program-dropdown','value'),
#      Input('year-dropdown', 'value'),
#      Input('search-personnel', 'value')])
# def personnel_search_table(personnel_ids, selected_funding, selected_year, personnel_name):
#     """
#     Creates the table for personnel at universities.
#     :param personnel_ids:
#     :return:
#     """
#     # print("search_ids are ", search_ids_professors_keywords)
#     # print(type(search_ids_professors_keywords))
#
#     print("I AM HERE WOHOOOO")
#
#     if personnel_ids:
#
#         print("personnel_ids are ", personnel_ids)
#         print(type(personnel_ids))
#
#         personnel_ids = json.loads(personnel_ids)
#         print("Loaded personal ID's are", personnel_ids)
#
#         # personnel_ids = np.array(personnel_ids)
#
#     filtered_data = funding_data[
#         funding_data.start_year.isin(selected_year)
#         # & funding_data['Submitting Institution Name:'].isin(selected_uni)
#         # & funding_data['Project Status:'].isin(selected_award_status)
#         & funding_data['Program Cycle:'].isin(selected_funding)]
#
#     # personnel_names = []
#     # print("search_ids_professors_keywords are in personnel_search_table", search_ids_professors_keywords)
#     # if search_keywords and len(search_keywords) > 0:
#     #     search_ids_professors_keywords = json.loads(search_ids_professors_keywords)
#     #     search_ids_professors_keywords = np.array(search_ids_professors_keywords)
#     #     # Using the dataset only to get relevant names out
#     #     some_data = filtered_data.loc[(filtered_data._id.isin(search_ids_professors_keywords[0:, 0]))]
#     #     personnel_names = some_data["Lead Investigator:"].unique()
#
#     # Filtering out the required professors only
#
#     # if len(personnel_names) > 0:
#     #     filtered_data = filtered_data.loc[filtered_data["Lead Investigator:"].isin(personnel_names)]
#
#     # common_dataframe = pd.read_json(common_dataframe, orient='split')
#
#     # Filters data on the search id and professors if content present in search box
#     if personnel_name:
#         if len(personnel_name) > 0:
#             # personnel_ids = json.loads(personnel_ids)
#             filtered_data = filtered_data.loc[filtered_data._id.isin(personnel_ids)]
#
#
#     # prof_name = clickData['points'][0]['customdata']
#     # print("selected professor for network graph is ", prof_name)
#
#     # TODO: Handle no search_ids or Nonetype search ids DONE
#         # print(" Search IDS ************* 8********** ****** here are this", search_ids_keywords[0:,0])
#
#     # professor_data = funding_data[(funding_data['Lead Investigator:'] == prof_name)
#     #                               & (funding_data.start_year.isin(selected_year))
#     #                               # & (funding_data._id.isin(search_ids_keywords[0:,0]))
#     #                               & (funding_data['Program Cycle:'].isin(selected_funding))]
#
#     # if search_keywords and len(search_keywords) > 0:
#     #     search_ids_keywords = json.loads(search_ids_keywords)
#     #     search_ids_keywords = np.array(search_ids_keywords)
#     #     professor_data = professor_data[(professor_data._id.isin(search_ids_keywords[0:, 0]))]
#
#
#     # collaborating_personnel_counts = collaborating_personnel.investigator.value_counts()
#
#     filtered_data = filtered_data["Lead Investigator:"]
#
#     filtered_data = filtered_data.value_counts()
#     filtered_data = filtered_data.reset_index()
#     filtered_data.rename({"index":"Personnel", "Lead Investigator:":"Total Projects"}, inplace=True, axis=1)
#     # ["Proposal Number:", "Submitting Institution Name:", "Project Status:", "Proposal Title:"]]
#     print("filtered_data is ", filtered_data)
#     return filtered_data.to_dict('records')


@app.callback(
    Output('personnel-search-table', 'data'),
    [Input('filter-by-funding-program-dropdown', 'value'),
     Input('year-dropdown', 'value'),
     Input('search-ids-personnel', 'children'),
     Input('search-ids-professors-keywords', 'children')],
    [State('search-personnel', 'value'),
     State('search-keywords-two', 'value')])
def personnel_search_table(selected_funding, selected_year, search_ids_personnel, search_ids_professors_keywords, personnel_name, search_keywords):
    """
    Creates the table for personnel at universities.
    :param search_ids_personnel:
    :return:
    """
    if search_ids_personnel:
        print("personnel_ids are ", search_ids_personnel)
        print(type(search_ids_personnel))

    if search_ids_professors_keywords:
        print("search_ids are ", search_ids_professors_keywords)
        print(type(search_ids_professors_keywords))

    if search_ids_personnel:
        search_ids_personnel = json.loads(search_ids_personnel)
        # personnel_ids = np.array(personnel_ids)
        print(search_ids_personnel)

    filtered_data = funding_data[
        funding_data.start_year.isin(selected_year)
        # & funding_data['Submitting Institution Name:'].isin(selected_uni)
        # & funding_data['Project Status:'].isin(selected_award_status)
        & funding_data['Program Cycle:'].isin(selected_funding)]

    # Using the dataset only to get relevant names of the personnel who are involved in the project
    # from personnel_data

    personnel_data_filtered = personnel_data
    personnel_data_filtered = personnel_data_filtered[
        personnel_data_filtered["Proposal Number:"].isin(filtered_data["Proposal Number:"])]


    # Implementation of personnel-search-table table with ES search on personnel data

    personnel_names = []
    personnel_projects_list = []

    if search_keywords and len(search_keywords) > 0:
        if len(search_ids_professors_keywords) > 0:

            # USE NPRP LISTS

            search_ids_professors_keywords = json.loads(search_ids_professors_keywords)
            search_ids_professors_keywords = np.array(search_ids_professors_keywords)

            # Using the dataset only to get relevant names of the personnel who are involved in the project
            # from personnel_data
            filtered_data = filtered_data[filtered_data._id.isin(search_ids_professors_keywords[0:, 0])]
            list_of_projects = filtered_data["Proposal Number:"]
            personnel_data_filtered = personnel_data_filtered[personnel_data_filtered["Proposal Number:"].isin(list_of_projects)]

            personnel_projects_list = personnel_data_filtered[["investigator", "Proposal Number:"]].groupby(
                'investigator').agg({"Proposal Number:": lambda x: [].append(x)})

            print("Personnel Projects list is ", personnel_projects_list)
            personnel_names = personnel_data_filtered["investigator"].unique()
            print("Personnel Who have worked in this field are ", personnel_names)

            # some_data = filtered_data.loc[(filtered_data._id.isin(search_ids_professors_keywords[0:, 0]))]
            # personnel_names = some_data["Lead Investigator:"].unique()



    # Implementation of personnel-search-table table with ES search on funding data
    # personnel_names = []
    # if search_keywords and len(search_keywords) > 0:
    #     if len(search_ids_professors_keywords) > 0:
    #         search_ids_professors_keywords = json.loads(search_ids_professors_keywords)
    #         search_ids_professors_keywords = np.array(search_ids_professors_keywords)
    #         # Using the dataset only to get relevant names out
    #         some_data = filtered_data.loc[(filtered_data._id.isin(search_ids_professors_keywords[0:, 0]))]
    #         personnel_names = some_data["Lead Investigator:"].unique()



    # Filtering out the required professors only
    # if len(personnel_names) > 0:
    #     filtered_data = filtered_data.loc[filtered_data["Lead Investigator:"].isin(personnel_names)]

    # common_dataframe = pd.read_json(common_dataframe, orient='split')

    # Filters data on the search id and professors if content present in search box
    if personnel_name and len(personnel_name) > 0:
        if len(search_ids_personnel) > 0:
            # Using the dataset only to get relevant names of the personnel who are involved in the project
            # from personnel_data

            personnel_data_filtered = personnel_data_filtered[personnel_data_filtered._id.isin(search_ids_personnel)]

            # Filtering the datasets based on search ids and filtered_data
            # Find a better way to do filters by join?

            filtered_data = filtered_data[
                filtered_data["Proposal Number:"].isin(personnel_data_filtered["Proposal Number:"])]

            personnel_projects_list = personnel_data_filtered[["investigator", "Proposal Number:"]].groupby(
                'investigator').agg({"Proposal Number:": lambda x: [].append(x)})

            print("Personnel Projects list is ", personnel_projects_list)
            personnel_names = personnel_data_filtered["investigator"].unique()
            print("Personnel Who have worked in this field are ", personnel_names)

            # filtered_data = filtered_data.loc[filtered_data._id.isin(search_ids_personnel)]

    # prof_name = clickData['points'][0]['customdata']
    # print("selected professor for network graph is ", prof_name)

    # TODO: Handle no search_ids or Nonetype search ids DONE
        # print(" Search IDS ************* 8********** ****** here are this", search_ids_keywords[0:,0])

    # professor_data = funding_data[(funding_data['Lead Investigator:'] == prof_name)
    #                               & (funding_data.start_year.isin(selected_year))
    #                               # & (funding_data._id.isin(search_ids_keywords[0:,0]))
    #                               & (funding_data['Program Cycle:'].isin(selected_funding))]

    # if search_keywords and len(search_keywords) > 0:
    #     search_ids_keywords = json.loads(search_ids_keywords)
    #     search_ids_keywords = np.array(search_ids_keywords)
    #     professor_data = professor_data[(professor_data._id.isin(search_ids_keywords[0:, 0]))]


    # collaborating_personnel_counts = collaborating_personnel.investigator.value_counts()

    # filtered_data = filtered_data["Lead Investigator:"]

    # proposal_numbers = filtered_data["Proposal Number:"]
    # some_data = personnel_data[personnel_data["proposal_numbers"].isin(proposal_numbers)]
    # some_data = some_data[]

    personnel_data_filtered = personnel_data_filtered["investigator"]
    personnel_data_filtered = personnel_data_filtered.value_counts()
    personnel_data_filtered = personnel_data_filtered.reset_index()
    personnel_data_filtered.rename({"index": "Personnel", "investigator": "Total Projects"}, inplace=True, axis=1)


    # filtered_data = filtered_data.value_counts()
    # filtered_data = filtered_data.reset_index()
    # filtered_data.rename({"index":"Personnel", "Lead Investigator:":"Total Projects"}, inplace=True, axis=1)
    # ["Proposal Number:", "Submitting Institution Name:", "Project Status:", "Proposal Title:"]]
    print("filtered_data is ", personnel_data_filtered)
    return personnel_data_filtered.to_dict('rows')


def personnel_outcomes_helper(personnel_search_table_selected_indices, selected_funding, selected_year, rows):
    """
    HELPER FUNCTION FOR THE PIE CHART AND PUBLICATION RECORDS
    :param personnel_search_table_selected_indices:
    :param rows:
    :return:
    """
    personnel = pd.DataFrame(rows)
    personnel_name = None
    if personnel_search_table_selected_indices:
        print(personnel_search_table_selected_indices)

        # Get the name of the last clicked row.
        personnel_name = personnel["Personnel"].iloc[personnel_search_table_selected_indices[-1]]
        # personnel_search_table_selected_indices = str(personnel_search_table_selected_indices)

    filtered_data = funding_data[
        funding_data.start_year.isin(selected_year)
        # & funding_data['Submitting Institution Name:'].isin(selected_uni)
        # & funding_data['Project Status:'].isin(selected_award_status)
        & funding_data['Program Cycle:'].isin(selected_funding)]

    # Using the dataset only to get relevant names of the personnel who are involved in the project
    # from personnel_data

    personnel_data_filtered = personnel_data
    personnel_data_filtered = personnel_data_filtered[
        personnel_data_filtered["Proposal Number:"].isin(filtered_data["Proposal Number:"])]

    # TODO : FIND THE PROPOSAL NUMBERS
    personnel_outcome_data = None
    if personnel_name:
        personnel_data_filtered = personnel_data_filtered[personnel_data_filtered["investigator"] == personnel_name]
        personnel_project_list = personnel_data_filtered["Proposal Number:"]
        personnel_outcome_data = outcome_data[outcome_data["Proposal Number:"].isin(personnel_project_list)]

    return personnel_outcome_data, personnel_name or None


# UPDATING PROFESSOR DATATABLE
@app.callback(
    Output('personnel-table-two', 'rows'),
    [Input('personnel-search-table', 'selected_rows'),
     Input('filter-by-funding-program-dropdown', 'value'),
     Input('year-dropdown', 'value')],
    [State('personnel-search-table', 'data')])
def personnel_projects_table(personnel_search_table_selected_indices, selected_funding, selected_year, rows):
    """
    For user selections, return the relevant table
    """
    personnel_outcome_data, personnel_name = personnel_outcomes_helper(personnel_search_table_selected_indices, selected_funding, selected_year, rows)
    if personnel_outcome_data is not None:
        personnel_outcome_data = personnel_outcome_data[["type", "pub_title"]]
        return personnel_outcome_data.to_dict('records')

    return pd.DataFrame(data=None, columns=["type", "pub_title"]).to_dict('records') # None cannot be passed back as it will cause an error.


@app.callback(
    Output('personnel-outcome-pie-chart', 'figure'),
    [Input('personnel-search-table', 'selected_rows'),
     Input('filter-by-funding-program-dropdown', 'value'),
     Input('year-dropdown', 'value')],
    [State('personnel-search-table', 'data')])
def generate_personnel_outcome_pie_chart(personnel_search_table_selected_indices, selected_funding, selected_year, rows):
    """
    Return the graph content for a pie chart
    Values of Records, Names and a Figure for the given personnel
    :param personnel_search_table_selected_indices:
    :param rows:
    :return:
    """
    personnel_outcome_data, personnel_name = personnel_outcomes_helper(personnel_search_table_selected_indices,
                                                                       selected_funding, selected_year, rows)
    personnel_outcome_type_value_count = {}
    if personnel_outcome_data is not None:
        personnel_outcome_type_value_count = personnel_outcome_data.type.value_counts()
        personnel_outcome_type_value_count = personnel_outcome_type_value_count.to_dict()


    print("Inside PIE CHART", personnel_outcome_type_value_count)
    print("Inside PIE CHART", personnel_name)


    trace = go.Pie(
        labels=list(personnel_outcome_type_value_count.keys()),
        values=list(personnel_outcome_type_value_count.values()),
        name=personnel_name,
        hoverinfo='label+percent',
        textinfo='value',
        textfont=dict(size=20),
        # marker=dict(colors=colors, line=dict(color='#000000', width=2)),
    )

    return{
        "data": [trace],
        "layout": go.Layout(
        # autosize=False,
        title='Professor Publications Breakdown',
        showlegend=True,
        # legend=go.Legend(
        #     x=0,
        #     y=1.0
        # ),
        # bargap =0.5,
        # width = 100,
        # autosize=F,
        margin=go.layout.Margin(l=40, r=0, t=40, b=30),
        # paper_bgcolor='rgb(233,233,233)',  # set paper (outside plot)
        plot_bgcolor='rgb(192,192,192)',  # plot color to grey
        )
    }


if __name__ == '__main__':
    app.run_server(debug=True, port=8050)