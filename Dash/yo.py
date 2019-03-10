import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, Event, State
from dash.exceptions import PreventUpdate

app = dash.Dash()

app.layout = html.Div([

    dcc.Dropdown(id='dropdown', multi=True,
                 options=[{'label': i, 'value': i} for i in range(10)],
                 value=[1]),
    html.Div([
        dcc.Checklist(id='select-all',
                      options=[{'label': 'Select All', 'value': 1},
                               {'label': 'Select All', 'value': 0}],
                      values=[])
    ], id='checklist-container')
])

@app.callback(
    Output('dropdown', 'value'),
    [Input('select-all', 'values')],
    [State('dropdown', 'options'),
     State('select-all', 'options')])
def test(selected, options_1, options_2):
    print(selected)
    print(options_1)
    print(len(options_1))
    print(options_2)
    if len(selected) > 0:
        if selected[0] == 1:
            print([i['value'] for i in options_1])

            return [i['value'] for i in options_1]
        else:
            print("Empty list wil be returned")
            return []
    raise PreventUpdate()


@app.callback(
    Output('checklist-container', 'children'),
    [Input('dropdown', 'value')],
    [State('dropdown', 'options'),
     State('select-all', 'values')])
def tester(selected, options_1, checked):
    print(selected)

    if len(selected) < len(options_1) and len(checked) == 0:
        raise PreventUpdate()

    if len(selected) < len(options_1) and len(checked) == 1:
        return dcc.Checklist(id='select-all',
                             options=[{'label': 'Select All', 'value': 1}],
                             values=[])

    elif len(selected) == len(options_1) and len(checked) == 1:
        raise PreventUpdate()

    return dcc.Checklist(id='select-all',
                         options=[{'label': 'Select All', 'value': 1}],
                         values=[1])


if __name__ == '__main__':
    app.run_server(debug=True, port=8051)

