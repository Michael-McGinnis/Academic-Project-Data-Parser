'''
https://youtu.be/hSPmj7mK6ng Excellent tutorial for learning about the basics of Dash
This was very helpful for my first time using this package
'''

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table as dt

import base64
import io
import pandas as pd
import plotly.express as px
from collections import OrderedDict

app = dash.Dash(__name__, suppress_callback_exceptions=True)  # This exception was needed in order to not have errors
# with the callback parameters when you chain them together

app.layout = html.Div([
    html.Div([
        html.Plaintext("Welcome To My Second Python Project!"),
        html.Plaintext("Class: CS 632P, Professor: Tassos Sarbanes"),
        html.Plaintext(""),
    ]),

    # Container/Div for Part 1: CSV/File upload from the user
    html.Div([
        dcc.Upload(  # document upload
            id='csv-upload',
            children=html.Div([
                'Drag and drop or upload your file'
            ]),
            style={
                'width': '99%',
                'height': '60px',
                'lineHeight': '60px',
                'borderWidth': '2px',
                'borderStyle': 'dashed',
                'borderRadius': '1px',
                'textAlign': 'center',
                'margin': '10px',
            },
            multiple=False  # If you want the user to upload multiple files. Set it to false
            # as this program does not support mulitple uploads
        ),
        html.Div(id='csv-data'),
    ],
        style={
            'borderStyle': 'solid',
            'borderColor': '#A2A3AA',
            'margin': '200',
            'padding': '',
        },
    ),

    # Container/Div for Part 2: Describe data
    html.H1(""),
    html.Div(
        id='data-desc',
        style={
            'borderStyle': 'solid',
            'borderColor': '#A2A3AA',
            'margin': '200',
            'padding': '',
        },
    ),

    # Container/Div for Part 3: Preview the data
    html.H1(""),
    html.Div(
        id='data-preview',
        style={
            'borderStyle': 'solid',
            'borderColor': '#A2A3AA',
            'margin': '200',
            'padding': '',
        },
    ),

    # Container/Div for Part 4: Display the filtered data and graph filtered data
    html.H1(""),
    html.Div(
        id='data-display-graph'
    ),
])


# Function for Part 1 (uploading user's file)
# In this section I included a try and exception to catch a wrong file a user inputs
# In addition, I added this since I misplaced them in the functions for the first project
def upload_parse(contents, filename):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    try:  # Using try and except to produce an error to the user if their
        # data file is not supported

        if 'csv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

        elif 'xls' in filename:
            df = pd.read_excel(io.BytesIO(decoded))

        elif 'txt' or 'tsv' in filename:
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')), delimiter=r'\s+')
            # return html.Div([
            #     html.H6(
            #         "I'm sorry, there was an error processing your file."
            #         'Please upload correct file'
            #     )
    except Exception as e:  # If the user's data file is not supported, produce error
        print(e)
        return html.Div(['**There was an error processing this file** Please select the proper data file'])

    return html.Div([
        html.Div([
            html.H6("Thank you. Your file was successfully uploaded"),
            html.H1(""),
        ],
            style={
                'textAlign': 'center',
            }
        ),
        # Container/Div for parsing button. The html.Button will be used as an activation to proceed further in the app
        # n_clicks will be set to 0. A button click will trigger the app callback and respective functions
        html.Div([
            html.Button(
                id='parse-button',
                children=['Parse Data'],
                n_clicks=0,
                style={
                    'BackgroundColor': '#F3F3F3'
                },
            ),
            html.H1(""),
        ],
            style={
                'width': '99.9%',
                'textAlign': 'center',
            },
        )
    ])


# function for part 2 (describing data)
def describe_data(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    '''
    In the initial code, I could not figure out how to program in the ignore option checkbox for the columns
    Instead I used a row delete solution, but in order to do that, I had to modify the user's input first
    The column names contained in the CSV file was put into a list, and than modified again into a dictionary

    Without using the dictionary, when the user selects the data they want previewed, that information was
    added into the string. Putting the user's selected information into dictionary avoided this issue. 
    '''

    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
    column_names = []
    for i in df.columns:
        column_names.append(i)

    df_for_dropdowns = pd.DataFrame(OrderedDict([
        ('Column-Name', column_names),
        ('Data-Type', 'None'),
    ]))

    return html.Div([
        html.H5('Your data was successfully parsed! Columns must be assigned a data type or deleted.'),
        html.Div([
            dt.DataTable(
                id='data-desc-table',
                data=df_for_dropdowns.to_dict('records'),  # data will store all changes made by user
                columns=[
                    {'id': 'Column-Name', 'name': 'Column Name', 'editable': False},
                    # do not want the columns to be editable
                    {'id': 'Data-Type', 'name': 'Data Type', 'presentation': 'dropdown', 'editable': True},
                    # this information must be editable
                    # this is where the user will select what data type to select from the dropdown
                ],
                row_deletable=True,  # will allow a row to be deleted. This is the work around I mentioned above
                dropdown_conditional=[{
                    'if': {
                        'column_id': 'Data-Type',
                    },
                    'options': [
                        {'label': i, 'value': i}
                        for i in [
                            'Data-Time',
                            'Numerical',
                            'String/Categorical'
                            # These are the data type options the user has to select for the information they
                            # want previewed/plotted on a graph
                        ]
                    ],
                }]
            ),
            html.Div(id='table-dropdown-container'),
            html.H1(""),
        ],
            style={
                'width': '75%'
            },
        ),

    ])


# Function for part 3 (previewing data)
def display_data(contents, data_list):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)

    df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))

    remaining_column_names = []
    column_data_types = []
    only_numerical_columns = []

    '''
    As mentioned earlier, a modification was needed for the data set in order to use row delete. To get the function
    to return the proper information. In the string if i % 2 == 0, this will represent an even index which equals the column
    names and if % == 1, than it will be odd, which will be a data type. If the data type == Numerical, than this will 
    be appended to the string at the index i -1
    '''

    for i in range(0, len(data_list)):
        if i % 2 == 0:
            remaining_column_names.append(data_list[i])
        else:
            column_data_types.append(data_list[i])
    # for good troubleshooting print(remaining_column_names)

    for i in range(0, len(data_list)):
        if data_list[i] == 'Numerical':
            only_numerical_columns.append(data_list[i - 1])

    # for good troubleshooting print(only_numerical_columns)

    return html.Div([
        html.H3('Step 3: Preview your data'),
        html.Div([
            html.H1(""),
            dt.DataTable(
                id='new-data-table',
                data=df.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in df.loc[:, remaining_column_names]],
            ),
            html.H1(""),
            html.H4("Please select which stocks you would like to plot"),
            dcc.Dropdown(
                id='stocks-selection-dropdown',
                options=[
                    {'label': i, 'value': i} for i in df.Stock.unique()
                ],
                multi=True,
                placeholder='Select the values(s)'
            ),
            html.H1(""),
            html.H4("Please select which data you want to plot:"),
            dcc.Dropdown(
                id='data-to-plot',
                options=[
                    {'label': i, 'value': i} for i in only_numerical_columns
                ],
                multi=False,
                placeholder='Select the values(s)'
            ),
            html.H1("")
        ],
            style={
                'width': '75%',
            },
        ),
    ])


# function for part 4 (final data displays)
def display_graph(data, stock_values, value, data_list):
    remaining_column_names = []
    for i in range(0, len(data_list)):
        if i % 2 == 0:
            remaining_column_names.append(data_list[i])
    # Filter the securities chosen by the user and appending them to filtered_data string
    filtered_data = []
    for stock in stock_values:
        for dictionary in data:
            if stock in dictionary.values():
                filtered_data.append(dictionary)

    df = pd.DataFrame.from_dict(filtered_data)

    fig = px.line(df, x='Date', y=value, color='Stock')

    return html.Div([
        html.H1('Filtered Data & Graph Plot:'),
        html.Div([
            dt.DataTable(
                id='filtered-data-table',
                data=df.to_dict('records'),
                columns=[{'name': i, 'id': i} for i in df.loc[:, remaining_column_names]],
            ),
        ],
            style={'width': '75%'
                   },
        ),
        html.H1(""),
        html.H1('Graph of Date vs.' + value),
        html.Div([
            dcc.Graph(figure=fig)
        ]),
    ])


# Dash Callbacks Sections and Function Calls

# Callback for Part 1:
@app.callback(Output('csv-data', 'children'),
              Input('csv-upload', 'contents'),  # User's file upload
              State('csv-upload', 'filename'),  # Chain the state from part 1 into part 2
              )
def update_file_upload(contents, filename):  # children is set to the parsed contents of the uploaded file
    if contents is not None:
        children = [
            upload_parse(contents, filename)  # function call of upload_parse
        ]
        return children


# Callback for Part 2:
@app.callback(Output('data-desc', 'children'),  # Output for the user will be the describe data table
              Input('parse-button', 'n_clicks'),  # User must click the parse button in order to move on
              State('csv-upload', 'contents'),  # Chain the state from part 1 & 2 into part 3
              )
def start_part_2(n_clicks,
                 contents):  # Will not move on until user clicks "parse data". Children is now the described data
    if n_clicks != 0:
        children = [
            describe_data(contents)  # Function call of describe_data
        ]
        return children


# Callback for Part 3:
@app.callback(Output('data-preview', 'children'),
              # Output a preview of what the user selects from the table dropdown options
              Input('data-desc-table', 'data'),  # This will pass in what the user is selecting for their data
              State('csv-upload', 'contents'),  # Chain the state from part 1. & 2, into part 3
              )
def start_part_3(data, contents):  # Children is now the preview_data that the user selects from the table dropdown
    data_list = []
    for dictionary in data:
        for values in dictionary.values():  # For column names and data types chosen
            data_list.append(values)
    table_incomplete = True in (item == 'None' for item in data_list)

    if not table_incomplete:
        children = [
            display_data(contents, data_list)  # function call of display_data
        ]
        return children


# Callbacks for Part 4:
@app.callback(Output('data-display-graph', 'children'),  # Output the graph of user's data and stock(s) selection
              Input('new-data-table', 'data'),  # File Uploaded from the user, modified into a dictionary
              Input('stocks-selection-dropdown', 'value'),  # Securities chosen by the user
              Input('data-to-plot', 'value'),  # User's choices of data they want to display from dropdown
              State('data-desc-table', 'data'),  # User's choices from above turned into a dictionary. CSV-Upload is
              # no longer necessary, because data is parsed, described, & previewed, and is now ready to be graphed
              )
def display_final_data(data, stocks_value, data_value, desc_data):  # Children is now set to display_graph
    data_list = []
    for dictionary in desc_data:
        for values in dictionary.values():
            data_list.append(values)

    if stocks_value is not None and data_value is not None:
        children = [
            display_graph(data, stocks_value, data_value, data_list)  # function call of display_graph
        ]
        return children


if __name__ == '__main__':
    app.run_server(debug=True)

# or debug=True, host='0.0.0.0', port=8000
# running from terminal python3 main.py, will start a new webserver @ http://localhost:8000






