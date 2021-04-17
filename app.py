import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash.dependencies import Input, Output, State
from services.station_service import StationService
from utilities import config, utility
from services.preditor import Predictor

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.config.suppress_callback_exceptions = True

stationsvc = StationService()
predictor = Predictor()
stations = stationsvc.get_station_location_api()

app.layout = html.Div([
    html.Div(
        html.H1(children='Best Bang for Your Bike Share')
    ),
    dbc.Row(
        [
            dbc.Col(html.Div(dcc.Graph(id='divvy-bike-station')), width=8),
            dbc.Col([
                # Bike Station Selection
                html.Div("Bike Station"),
                html.Div([
                    dcc.Dropdown(
                        id="Station",
                        options=[{'label': row['station_name'], 'value': row['id']} for index, row in
                                 stations.iterrows()]),
                ], style={'width': '100%', 'display': 'inline-block'}),
                # Weather Selection
                html.Div("Weather"),
                html.Div([
                    dcc.Dropdown(
                        id="Weather",
                        options=[{'label': val, 'value': key} for key, val in config.weathers.items()],
                        value=0),
                ], style={'width': '100%', 'display': 'inline-block'}),
                # Gender Selection
                html.Div("Gender"),
                html.Div([
                    dcc.Dropdown(
                        id="Gender",
                        options=[{'label': val, 'value': key} for key, val in config.gender.items()],
                        value=0)

                ], style={'width': '100%', 'display': 'inline-block'}),
                # Trip Time Selection
                html.Div("Trip Time"),
                html.Div([
                    dcc.Dropdown(
                        id="TripTime",
                        options=[{'label': val, 'value': key} for key, val in config.trip_time.items()],
                        value=5)

                ], style={'width': '100%', 'display': 'inline-block'}),
                # Day of Week Selection
                html.Div("Day of Week"),
                html.Div([
                    dcc.Dropdown(
                        id="DayofWeek",
                        options=[{'label': val, 'value': key} for key, val in config.day_of_week.items()],
                        value=0
                    )
                ], style={'width': '50%', 'display': 'inline-block'}),
                # Pickup Hour Selection
                html.Div("Pickup Hour"),
                html.Div([
                    dcc.Dropdown(
                        id="PickupHour",
                        options=[{'label': val, 'value': key} for key, val in config.hour_group.items()],
                        value=0
                    )
                ], style={'width': '50%', 'display': 'inline-block'}),
                html.Div([
                    dbc.Button('Submit', id='submit-val', n_clicks=0, color="info", className="mr-1"),
                ]),
            ], width=3),
        ], justify="center"),
    html.Footer("CSE6424 - Spring 21 - Team 128")
])


# green = [359, 23, 236, 182, 291, 27, 364, 620, 46, 176, 118, 331, 365, 48, 140, 172, 301, 180, 1436495096608724634,
#           289, 126, 268, 60, 20, 28, 141, 224, 31, 337, 106, 85, 111
#           ]
# orange = [145, 25, 173, 161, 110, 53, 627, 181, 212, 672, 636, 100, 133, 74, 56, 84, 54, 92, 186, 54, 635, 211, 199, 86, 29, 666, 93, 288,
#           94, 143, 144, 255, 113, 225, 1436495105198659242, 673, 177, 34, 313, 327, 223, 315, 333, 210, 30, 350, 277, 217,
#           71, 1436495105198659246, 1436495109493626546, 96, 66, 164, 51, 38, 47, 125, 196, 24, 26, 142, 99, 35
#           ]

@app.callback(
    Output('divvy-bike-station', 'figure'),
    [Input('submit-val', 'n_clicks')],
    [State('Station', 'value'),
     State('Weather', 'value'),
     State('Gender', 'value'),
     State('TripTime', 'value'),
     State('DayofWeek', 'value'),
     State('PickupHour', 'value')
     ])
def update_graph(n_clicks, Station, Weather=0, Gender=0, TripTime=5, DayofWeek=0, PickupHour=0):
    if Station is None:
        green = orange = red = []
        lat = 41.88
        long = -87.65
    else:
        green, orange, red = predictor.get_station_segmentation(stations=stations, station_id=Station, weather=Weather, gender=Gender,
                                                                trip_time=TripTime, day_of_week=DayofWeek, pickup_hour=PickupHour)
        station = stations[stations.id == Station].copy()
        lat = station.latitude.values[0]
        long = station.longitude.values[0]

    fig = go.Figure(go.Scattermapbox(
        lat=stations['latitude'],
        lon=stations['longitude'],
        mode='markers+text',
        marker=go.scattermapbox.Marker(
            autocolorscale=True,
            size=12,
            color=[utility.set_color(row.id, green, orange, red) for index, row in stations.iterrows()]
        ),
        text=stations.station_name,
        hoverinfo='text',
    ))

    fig.update_layout(
        autosize=True,
        height=630,
        margin=dict(t=0, b=0, l=0, r=0),
        hovermode='closest',
        mapbox=dict(
            accesstoken=config.mapbox_access_token,
            bearing=0,
            center=dict(
                lat=lat,
                lon=long
            ),
            pitch=0,
            zoom=13
        ),
    )
    return fig


if __name__ == '__main__':
    app.run_server(debug=False, port=5555, host='127.0.0.1')
