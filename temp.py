import json
import dash
import pandas as pd
import numpy as np
import plotly.express as px
import geopandas as gpd
import shapely.geometry

from dash import html
from dash.html.Button import Button
from dash import dcc
from dash import callback
from dash import State
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output
from plotly import graph_objs as go
from plotly.graph_objs import *
from datetime import datetime as dt
from shapely.geometry import Polygon



app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],
)
app.title = "DECODE - Damage Evaluation with Comprehensive Observation Data on Earth"
server = app.server

# colorscale
named_colorscales = px.colors.named_colorscales()

# Plotly mapbox public token
mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"


# Dictionary of flooded areas in Italy
list_of_locations = {
    "Alluvione a Prato": {"lat": 43.8777049, "lon": 11.102228},
    "Alluvione in Emilia Romagna": {"lat": 44.2924, "lon": 11.8762},
    "Bomba d'acqua a Milano": {"lat": 45.4654219, "lon": 9.1859243},
}

'''
# Initialize data frame
df1 = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/uber-rides-data1.csv",
    dtype=object,
)
df2 = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/uber-rides-data2.csv",
    dtype=object,
)
df3 = pd.read_csv(
    "https://raw.githubusercontent.com/plotly/datasets/master/uber-rides-data3.csv",
    dtype=object,
)
df = pd.concat([df1, df2, df3], axis=0)
df["Date/Time"] = pd.to_datetime(df["Date/Time"], format="%Y-%m-%d %H:%M:%S")
df.index = df["Date/Time"]
#df.drop("Date/Time", axis = 1, inplace=True)

for month in df.groupby(df.index.month):
    dailyList = []
    for day in month[1].groupby(month[1].index.day):
        dailyList.append(day[1])
    totalList.append(dailyList)
#totalList = np.array(totalList)
'''
totalList = []

## Sample data by PM
data = {
    'lat': [43.6545, 43.7597, 43.6524],
    'lon': [10.5547, 11.0463, 10.5353],
    'name': ['Location 1', 'Location 2', 'Location 3']
}


# Coordinates for the polygon
polygon_coordinates = [
    [10.554735408915095, 43.654514997938946],
    [10.554735408915098, 43.654514997938946],
    [10.645351, 43.711531],
    [10.715524, 43.672453],
    [10.761927, 43.644037],
    [10.53775, 43.500318],
    [10.439732, 43.582154],
    [10.46497, 43.598034],
    [10.476443, 43.654242],
    [10.554735408915095, 43.654514997938946]
]
polygon = shapely.geometry.Polygon(polygon_coordinates)
# Create a GeoDataFrame
gdf = gpd.GeoDataFrame(geometry=gpd.GeoSeries(polygon))

# OpenStreetMap layout
layout = dict(
    autosize=True,
    margin=go.layout.Margin(l=0, r=0, t=0, b=0),
    hovermode='closest',
    mapbox=dict(
        layers=[],
        accesstoken='your-mapbox-access-token',  # Replace with your Mapbox access token
        bearing=0,
        center=dict(
            lat=43.77109369,
            lon=11.24879527
        ),
        pitch=0,
        zoom=10
    ),
)

#HTML
'''
@app.route('/')
def home():
    return render_template('index.html')


external_html = "index.html"
with open(f"{external_html}", "r") as file:
#with open(f"{server.config['TEMPLATE_FOLDER']}/{external_html}", "r") as file:
    external_html_content = file.read()

app.layout = html.Div(
    children=[
        dcc.Markdown(external_html_content),
    ]
)
'''

app.layout = html.Div(
    children=[
        
        html.Div(
            className="row",
            children=[
                # Column for user controls
                html.Div(
                    className="four columns div-user-controls",
                    children=[
                        html.A(
                            html.Img(
                                className="logo",
                                src="https://github.com/Rkomi98/DECODE/blob/main/static/DECODE_logo.png?raw=true",
                            ),
                            href="https://plotly.com/dash/",
                        ),
                        html.H2("DECODE - Damage Evaluation with Comprehensive Observation Data on Earth"),
                        html.P(
                            """Select different days using the date picker or by selecting
                            different time frames on the histogram."""
                        ),
                        html.Div(
                            className="div-for-dropdown",
                            children=[
                                dcc.DatePickerSingle(
                                    id="date-picker",
                                    min_date_allowed=dt(2014, 4, 1),
                                    max_date_allowed=dt(2014, 9, 30),
                                    initial_visible_month=dt(2014, 4, 1),
                                    date=dt(2014, 4, 1).date(),
                                    display_format="MMMM D, YYYY",
                                    style={"border": "0px solid black"},
                                )
                            ],
                        ),
                        # Change to side-by-side for mobile layout
                        html.Div(
                            className="row",
                            children=[
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown for locations on map
                                        dcc.Dropdown(
                                            id="location-dropdown",
                                            options=[
                                                {"label": i, "value": i}
                                                for i in list_of_locations
                                            ],
                                            placeholder="Select a location",
                                        )
                                    ],
                                ),
                                html.Div(
                                    className="div-for-dropdown",
                                    children=[
                                        # Dropdown to select times
                                        dcc.Dropdown(
                                            id="bar-selector",
                                            options=[
                                                {
                                                    "label": str(n) + ":00",
                                                    "value": str(n),
                                                }
                                                for n in range(24)
                                            ],
                                            multi=True,
                                            placeholder="Select certain hours",
                                        )
                                    ],
                                ),
                                html.Div(
                                    className="button-container",
                                    children=[
                                        dcc.Upload(
                                            id='upload-json',
                                            children=html.Button('Upload JSON File'),
                                            multiple=False,
                                            accept='.json',
                                        ),
                                        
                                        # File upload for GPKG
                                        dcc.Upload(
                                            id='upload-gpkg',
                                            children=html.Button('Upload GPKG File'),
                                            multiple=True,
                                            accept='.gpkg, csv, shp',  # Specify accepted file types
                                        ),
                                    ]
                                )
                            ],
                        ),
                        html.P(id="total-rides"),
                        html.P(id="total-rides-selection"),
                        html.P(id="date-value"),
                        dcc.Markdown(
                            """
                            Source: [FiveThirtyEight](https://github.com/fivethirtyeight/uber-tlc-foil-response/tree/master/uber-trip-data)
                            Links: [Source Code](https://github.com/plotly/dash-sample-apps/tree/main/apps/dash-uber-rides-demo) | [Enterprise Demo](https://plotly.com/get-demo/)
                            """
                        ),
                    ],
                ),
                # Column for app graphs and plots
                html.Div(
                    className="eight columns div-for-charts bg-grey",
                    #className="mapboxgl-map",
                    children=[
                        html.Div(
                            #dcc.Graph(id="map-graph"),
                            dcc.Graph(id="map_new"),
                            '''
                            dcc.Graph(
                                id='map_new',
                                figure=px.scatter_mapbox(
                                    color_continuous_scale = [
                                        "#F4EC15",
                                        "#DAF017",
                                        "#BBEC19",
                                        "#9DE81B",
                                        "#80E41D",
                                        "#66E01F",
                                        "#4CDC20",
                                        "#34D822",
                                        "#24D249",
                                        "#25D042",
                                        "#26CC58",
                                        "#28C86D",
                                        "#29C481",
                                        "#2AC093",
                                        "#2BBCA4",
                                        "#2BB5B8",
                                        "#2C99B4",
                                        "#2D7EB0",
                                        "#2D65AC",
                                        "#2E4EA4",
                                        "#2E38A4",
                                        "#3B2FA0",
                                        "#4E2F9C",
                                        "#603099",
                                    ],
                                    data_frame=data,
                                    lat='lat',
                                    lon='lon',
                                    text='name',
                                    mapbox_style='carto-darkmatter',  # Use OpenStreetMap as the base map
                                ).update_layout(layout)
                            ) 
                            '''
                        ),
                        html.Div(
                            className="text-padding",
                            children=[
                                "Select any of the bars on the histogram to section data by time."
                            ],
                        ),
                        #dcc.Graph(id="histogram"),
                        # Display the uploaded data
                        
                    ],
                ),
            ],
        )
    ]
)

# Gets the amount of days in the specified month
# Index represents month (0 is April, 1 is May, ... etc.)
daysInMonth = [30, 31, 30, 31, 31, 30]

# Get index for the specified month in the dataframe
monthIndex = pd.Index(["Apr", "May", "June", "July", "Aug", "Sept"])

# Get the amount of rides per hour based on the time selected
# This also higlights the color of the histogram bars based on
# if the hours are selected
def get_selection(month, day, selection):
    xVal = []
    yVal = []
    xSelected = []
    colorVal = [
        "#F4EC15",
        "#DAF017",
        "#BBEC19",
        "#9DE81B",
        "#80E41D",
        "#66E01F",
        "#4CDC20",
        "#34D822",
        "#24D249",
        "#25D042",
        "#26CC58",
        "#28C86D",
        "#29C481",
        "#2AC093",
        "#2BBCA4",
        "#2BB5B8",
        "#2C99B4",
        "#2D7EB0",
        "#2D65AC",
        "#2E4EA4",
        "#2E38A4",
        "#3B2FA0",
        "#4E2F9C",
        "#603099",
    ]

    # Put selected times into a list of numbers xSelected
    xSelected.extend([int(x) for x in selection])

    for i in range(24):
        # If bar is selected then color it white
        if i in xSelected and len(xSelected) < 24:
            colorVal[i] = "#FFFFFF"
        xVal.append(i)
        # Get the number of rides at a particular time
        yVal.append(len(totalList[month][day][totalList[month][day].index.hour == i]))
    return [np.array(xVal), np.array(yVal), np.array(colorVal)]


# Selected Data in the Histogram updates the Values in the Hours selection dropdown menu
@app.callback(
    Output("bar-selector", "value"),
    [Input("histogram", "selectedData"), Input("histogram", "clickData")],
)
def update_bar_selector(value, clickData):
    holder = []
    if clickData:
        holder.append(str(int(clickData["points"][0]["x"])))
    if value:
        for x in value["points"]:
            holder.append(str(int(x["x"])))
    return list(set(holder))


# Clear Selected Data if Click Data is used
@app.callback(Output("histogram", "selectedData"), [Input("histogram", "clickData")])
def update_selected_data(clickData):
    if clickData:
        return {"points": []}


# Update the total number of rides Tag
@app.callback(Output("total-rides", "children"), [Input("date-picker", "date")])
def update_total_rides(datePicked):
    date_picked = dt.strptime(datePicked, "%Y-%m-%d")
    return "Total Number of rides: {:,d}".format(
        len(totalList[date_picked.month - 4][date_picked.day - 1])
    )


# Update the total number of rides in selected times
@app.callback(
    [Output("total-rides-selection", "children"), Output("date-value", "children")],
    [Input("date-picker", "date"), Input("bar-selector", "value")],
)
def update_total_rides_selection(datePicked, selection):
    firstOutput = ""

    if selection != None or len(selection) != 0:
        date_picked = dt.strptime(datePicked, "%Y-%m-%d")
        totalInSelection = 0
        for x in selection:
            totalInSelection += len(
                totalList[date_picked.month - 4][date_picked.day - 1][
                    totalList[date_picked.month - 4][date_picked.day - 1].index.hour
                    == int(x)
                ]
            )
        firstOutput = "Total rides in selection: {:,d}".format(totalInSelection)

    if (
        datePicked is None
        or selection is None
        or len(selection) == 24
        or len(selection) == 0
    ):
        return firstOutput, (datePicked, " - showing hour(s): All")

    holder = sorted([int(x) for x in selection])

    if holder == list(range(min(holder), max(holder) + 1)):
        return (
            firstOutput,
            (
                datePicked,
                " - showing hour(s): ",
                holder[0],
                "-",
                holder[len(holder) - 1],
            ),
        )

    holder_to_string = ", ".join(str(x) for x in holder)
    return firstOutput, (datePicked, " - showing hour(s): ", holder_to_string)


# Update Histogram Figure based on Month, Day and Times Chosen
@app.callback(
    Output("histogram", "figure"),
    [Input("date-picker", "date"), Input("bar-selector", "value")],
)
def update_histogram(datePicked, selection):
    date_picked = dt.strptime(datePicked, "%Y-%m-%d")
    monthPicked = date_picked.month - 4
    dayPicked = date_picked.day - 1

    [xVal, yVal, colorVal] = get_selection(monthPicked, dayPicked, selection)

    layout = go.Layout(
        bargap=0.01,
        bargroupgap=0,
        barmode="group",
        margin=go.layout.Margin(l=10, r=0, t=0, b=50),
        showlegend=False,
        plot_bgcolor="#323130",
        paper_bgcolor="#323130",
        dragmode="select",
        font=dict(color="white"),
        xaxis=dict(
            range=[-0.5, 23.5],
            showgrid=False,
            nticks=25,
            fixedrange=True,
            ticksuffix=":00",
        ),
        yaxis=dict(
            range=[0, max(yVal) + max(yVal) / 4],
            showticklabels=False,
            showgrid=False,
            fixedrange=True,
            rangemode="nonnegative",
            zeroline=False,
        ),
        annotations=[
            dict(
                x=xi,
                y=yi,
                text=str(yi),
                xanchor="center",
                yanchor="bottom",
                showarrow=False,
                font=dict(color="white"),
            )
            for xi, yi in zip(xVal, yVal)
        ],
    )

    return go.Figure(
        data=[
            go.Bar(x=xVal, y=yVal, marker=dict(color=colorVal), hoverinfo="x"),
            go.Scatter(
                opacity=0,
                x=xVal,
                y=yVal / 2,
                hoverinfo="none",
                mode="markers",
                marker=dict(color="rgb(66, 134, 244, 0)", symbol="square", size=40),
                visible=True,
            ),
        ],
        layout=layout,
    )


# Get the Coordinates of the chosen months, dates and times
def getLatLonColor(selectedData, month, day):
    listCoords = totalList[month][day]

    # No times selected, output all times for chosen month and date
    if selectedData is None or len(selectedData) == 0:
        return listCoords
    listStr = "listCoords["
    for time in selectedData:
        if selectedData.index(time) is not len(selectedData) - 1:
            listStr += "(totalList[month][day].index.hour==" + str(int(time)) + ") | "
        else:
            listStr += "(totalList[month][day].index.hour==" + str(int(time)) + ")]"
    return eval(listStr)

def read_json(contents):
    content_type, content_string = contents.split(',')
    decoded = content_string.encode('utf-8')
    return json.load(decoded)

def read_gpkg(contents):
    content_type, content_string = contents.split(',')
    decoded = content_string.encode('utf-8')
    gdf = gpd.read_file(decoded, driver='GPKG')
    return gdf
# Function to generate random building data
def generate_building_data(num_buildings):
    np.random.seed(42)  # For reproducibility
    latitudes = np.random.uniform(43.5, 44, num_buildings)  # Adjust latitude range as needed
    longitudes = np.random.uniform(10.5, 11.5, num_buildings)  # Adjust longitude range as needed
    floors = np.random.randint(-1, 7, num_buildings)
    areas = np.random.uniform(0, 300, num_buildings)  # Adjust area range as needed
    values = np.random.uniform(100000, 500000, num_buildings)  # Adjust value range as needed

    building_data = pd.DataFrame({
        'Latitude': latitudes,
        'Longitude': longitudes,
        'Floor': floors,
        'Area': areas,
        'Value': values
    })

    return building_data


@app.callback(
    Output('map_new', 'figure'),
    [Input('upload-json', 'contents'),
     Input('upload-gpkg', 'contents')],
    [State('upload-json', 'filename'),
     State('upload-gpkg', 'filename')]
)

def update_map(json_contents, gpkg_contents, json_filename, gpkg_filename):
    if not json_contents and not gpkg_contents:
        # Generate 25 building coordinates
        num_buildings = 25
        building_data = generate_building_data(num_buildings)
        
        # Coordinates for the polygon
        # Parse the GeoJSON-like data
        # Read GeoJSON-like data from file
        with open('EMSR705_aois.json', 'r') as file:
            geojson_data = json.load(file)
            
        # Extract polygon coordinates
        polygons = []
        indexes = []
        for feature in geojson_data['features']:
            properties = feature.get('properties', {})
            name = properties.get('name', '')
            geometry = feature.get('geometry', {})
            if geometry.get('type') == 'Polygon':
                coordinates = geometry.get('coordinates', [])
                polygons.append(coordinates)
                indexes.append(name)

        # Create a GeoDataFrame for GeoJSON-like plotting
        gdf = gpd.GeoDataFrame(geometry=gpd.GeoSeries([Polygon(polygon[0]) for polygon in polygons]))
        # Plot polygons using GeoPandas
        fig = px.choropleth_mapbox(
            gdf,
            geojson=gdf.geometry.__geo_interface__,
            zoom=10, 
            center=dict(lat=43.654514997938946, lon=10.554735408915095),
            locations=gdf.index,
            color=indexes,  # Use the "indexes" list for coloring
            hover_name=indexes,  # Show names on hover
            mapbox_style='carto-darkmatter',  # Use OpenStreetMap as the base map
            #color_discrete_sequence ='viridis',  # Set the desired color scale
            opacity = 0.4,
        )
        # Add scatter mapbox trace for building points
        fig.add_trace(
            px.scatter_mapbox(
                building_data,
                lat='Latitude',
                lon='Longitude',
                hover_data=['Floor', 'Area', 'Value'],
                mapbox_style='carto-darkmatter',
            ).data[0]
        )
        
        # Set margin to 0
        fig.update_layout(margin=dict(l=0, r=0, t=0, b=0))
        
        # Modify legend
        fig.update_layout(
            legend=dict(
                bgcolor='rgba(255, 255, 255, 0.5)',  # Adjust the transparency of the background
                x=0,  # Float the legend to the left
                y=1,  # Float the legend to the bottom
                title="Flooded areas",
                font=dict(
                    size=14
                    ),
            )
        )

        #fig.update_geos(fitbounds="locations", visible=False)

        return fig

    if json_contents:
        data = read_json(json_contents)
        features = data.get('features', [])

        # Extract polygon coordinates
        polygons = []
        indexes = []
        for feature in geojson_data['features']:
            properties = feature.get('properties', {})
            name = properties.get('name', '')
            geometry = feature.get('geometry', {})
            if geometry.get('type') == 'Polygon':
                coordinates = geometry.get('coordinates', [])
                polygons.append(coordinates)
                indexes.append(name)

        # Create a GeoDataFrame for GeoJSON-like plotting
        gdf = gpd.GeoDataFrame(geometry=gpd.GeoSeries([Polygon(polygon[0]) for polygon in polygons]))
        # Plot polygons using GeoPandas
        fig = px.choropleth_mapbox(
            gdf,
            geojson=gdf.geometry.__geo_interface__,
            zoom=10, 
            center=dict(lat=43.654514997938946, lon=10.554735408915095),
            locations=gdf.index,
            color=indexes,  # Use the "indexes" list for coloring
            hover_name=indexes,  # Show names on hover
            mapbox_style='carto-darkmatter',  # Use OpenStreetMap as the base map
            #color_discrete_sequence ='viridis',  # Set the desired color scale
            opacity = 0.4,
        )
        
        #fig.update_geos(fitbounds="locations", visible=False)

        return fig

    if gpkg_contents:
        data = read_gpkg(gpkg_contents)
        # Process the GeoPackage data as needed
        # ...

        # Use the processed data to update the map
        # For example, you can use Plotly Express to create a scatter map
        fig = px.scatter_mapbox(
            lat=data['lat'],  # Update with the actual column names from your data
            lon=data['lon'],
            mapbox_style='open-street-map',
        ).update_layout(
            mapbox=dict(
                center=dict(lat=data['lat'].mean(), lon=data['lon'].mean()),
                zoom=12,
            ),
        )

        return fig


# Update Map Graph based on date-picker, selected data on histogram and location dropdown
@app.callback(
    Output("map-graph", "figure"),
    [
        Input("date-picker", "date"),
        Input("bar-selector", "value"),
        Input("location-dropdown", "value"),
    ],
)
def update_graph(datePicked, selectedData, selectedLocation):
    zoom = 12.0
    latInitial = 40.7272
    lonInitial = -73.991251
    bearing = 0

    if selectedLocation:
        zoom = 15.0
        latInitial = list_of_locations[selectedLocation]["lat"]
        lonInitial = list_of_locations[selectedLocation]["lon"]

    date_picked = dt.strptime(datePicked, "%Y-%m-%d")
    monthPicked = date_picked.month - 4
    dayPicked = date_picked.day - 1
    listCoords = getLatLonColor(selectedData, monthPicked, dayPicked)

    return go.Figure(
        data=[
            # Data for all rides based on date and time
            Scattermapbox(
                lat=listCoords["Lat"],
                lon=listCoords["Lon"],
                mode="markers",
                hoverinfo="lat+lon+text",
                text=listCoords.index.hour,
                marker=dict(
                    showscale=True,
                    color=np.append(np.insert(listCoords.index.hour, 0, 0), 23),
                    opacity=0.5,
                    size=5,
                    colorscale=[
                        [0, "#F4EC15"],
                        [0.04167, "#DAF017"],
                        [0.0833, "#BBEC19"],
                        [0.125, "#9DE81B"],
                        [0.1667, "#80E41D"],
                        [0.2083, "#66E01F"],
                        [0.25, "#4CDC20"],
                        [0.292, "#34D822"],
                        [0.333, "#24D249"],
                        [0.375, "#25D042"],
                        [0.4167, "#26CC58"],
                        [0.4583, "#28C86D"],
                        [0.50, "#29C481"],
                        [0.54167, "#2AC093"],
                        [0.5833, "#2BBCA4"],
                        [1.0, "#613099"],
                    ],
                    colorbar=dict(
                        title="Time of<br>Day",
                        x=0.93,
                        xpad=0,
                        nticks=24,
                        tickfont=dict(color="#d8d8d8"),
                        titlefont=dict(color="#d8d8d8"),
                        thicknessmode="pixels",
                    ),
                ),
            ),
            # Plot of important locations on the map
            Scattermapbox(
                lat=[list_of_locations[i]["lat"] for i in list_of_locations],
                lon=[list_of_locations[i]["lon"] for i in list_of_locations],
                mode="markers",
                hoverinfo="text",
                text=[i for i in list_of_locations],
                marker=dict(size=8, color="#ffa0a0"),
            ),
        ],
        layout=Layout(
            autosize=True,
            margin=go.layout.Margin(l=0, r=0, t=0, b=0),
            showlegend=False,
            mapbox=dict(
                accesstoken=mapbox_access_token,
                center=dict(lat=latInitial, lon=lonInitial),  # 40.7272  # -73.991251
                style="dark",
                bearing=bearing,
                zoom=zoom,
            ),
            updatemenus=[
                dict(
                    buttons=(
                        [
                            dict(
                                args=[
                                    {
                                        "mapbox.zoom": 12,
                                        "mapbox.center.lon": "-73.991251",
                                        "mapbox.center.lat": "40.7272",
                                        "mapbox.bearing": 0,
                                        "mapbox.style": "dark",
                                    }
                                ],
                                label="Reset Zoom",
                                method="relayout",
                            )
                        ]
                    ),
                    direction="left",
                    pad={"r": 0, "t": 0, "b": 0, "l": 0},
                    showactive=False,
                    type="buttons",
                    x=0.45,
                    y=0.02,
                    xanchor="left",
                    yanchor="bottom",
                    bgcolor="#323130",
                    borderwidth=1,
                    bordercolor="#6d6d6d",
                    font=dict(color="#FFFFFF"),
                )
            ],
        ),
    )


if __name__ == "__main__":
    app.run_server(debug=False)