import json
import dash
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objs as go
import geopandas as gpd
import shapely.geometry


from dash import html
from dash.html.Button import Button
from dash import dcc
from dash import callback
from dash import State
from dash import callback_context as ctx
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output
from plotly import graph_objs as go
from plotly.graph_objs import *
from datetime import datetime as dt
from shapely.geometry import Polygon, Point

def generate_building_data(num_buildings):
    np.random.seed(42)  # For reproducibility
    latitudes = np.random.uniform(40, 45, num_buildings)  # Adjust latitude range for all Italy
    longitudes = np.random.uniform(10.5, 14.5, num_buildings)  # Adjust longitude range for all Italy
    floors = np.random.randint(-1, 4, num_buildings)
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




app = dash.Dash(
    __name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}],
)
app.title = "Damage Evaluation with Comprehensive Observation Data on Earth"
server = app.server

# colorscale
named_colorscales = px.colors.named_colorscales()

# Plotly mapbox public token
mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNrOWJqb2F4djBnMjEzbG50amg0dnJieG4ifQ.Zme1-Uzoi75IaFbieBDl3A"


# Dictionary of flooded areas in Italy
list_of_locations = {
    "Flood in Tuscany": {"lat": 43.8777049, "lon": 11.102228, "layer": 'EMSR705_aois.json'},
    "Flood in Emilia Romagna (end of April)": {"lat": 44.2924, "lon": 11.8762, "layer": 'EMSR659_aois.json'},
    "Flood in Emilia Romagna (begin of May)": {"lat": 44.2924, "lon": 11.8762, "layer": 'EMSR664_aois.json'},
    #"Bomba d'acqua a Milano": {"lat": 45.4654219, "lon": 9.1859243},
}

# Coordinates for the polygon
# Parse the GeoJSON-like data
# Read GeoJSON-like data from file
with open('EMSR705_aois.json', 'r') as file:
    geojson_data = json.load(file)
    
# Extract polygon coordinates
polygons = []
indexes = []
options = ['All']
for feature in geojson_data['features']:
    properties = feature.get('properties', {})
    name = properties.get('name', '')
    geometry = feature.get('geometry', {})
    if geometry.get('type') == 'Polygon':
        coordinates = geometry.get('coordinates', [])
        polygons.append(Polygon(coordinates[0]))
        indexes.append(name)
        options.append(name)

# Create a GeoDataFrame for GeoJSON-like plotting
# Create a GeoDataFrame for GeoJSON-like plotting
gdf = gpd.GeoDataFrame(geometry=gpd.GeoSeries(polygons))


# Generate 25 building coordinates
num_buildings = 1000
building_data = generate_building_data(num_buildings)

# Add a new column to building_data to check if each point is inside the polygons
building_data['inside_polygon'] = building_data.apply(
    lambda row: any(Point(row['Longitude'], row['Latitude']).within(polygon) for polygon in polygons),
    axis=1
)
building_data['polygon_index'] = building_data.apply(
    lambda row: next((index for index, polygon in zip(indexes, polygons) if Point(row['Longitude'], row['Latitude']).within(polygon)), None),
    axis=1
)


# Define the colors for the building categories
colors = {'white': 'white', 'green': 'green', 'yellow': 'yellow', 'red': 'red'}

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
                                src="https://github.com/Rkomi98/DECODE/blob/main/static/DECODE_logo_2.png?raw=true",
                            ),
                            href="https://github.com/Rkomi98/DECODE",
                        ),
                        html.H2("Damage Evaluation with Comprehensive Observation Data on Earth"),
        
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
                                                {"label": i, "value": i} for i in list_of_locations
                                            ],
                                            value = 'None',
                                            clearable=False,
                                            placeholder="Select a flood event",
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
                                ),
                                html.Div(
                                    className="button-container",
                                    children = html.Button(id='download-button', n_clicks=0, children='Download CSV file'),
                                ),
                                # Add a Download component
                                dcc.Download(id="download")
                            ],
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
                        ),
                        # Add this hidden dcc.Store component to store building_data
                        dcc.Store(
                            id='building-data-store', 
                            data=building_data.to_json(date_format='iso', orient='split')
                            ),
                        dcc.Dropdown(
                            id="dropdown",
                            options=[],
                            multi = True,
                            #value='All',
                            clearable=False,
                            placeholder="Select an area to update the histogram",
                        ),
                        dcc.Graph(id="histogram"),
                        # Display the uploaded data
                        
                    ],
                ),
            ],
        )
    ]
)

@app.callback(
    Output("dropdown", "options"),
    Input("location-dropdown", "value")
)
def update_dropdown_options(selected_location):
    options = []
    if selected_location is None:
        # Return an empty list if no location is selected
        return []

    else:
        # Ensure that list_of_locations[selected_location] is not None
        location_info = list_of_locations.get(selected_location)
        if location_info is None:
            return []
        options = ['All']
        with open(location_info.get('layer', 0), 'r') as file:
            geojson_data = json.load(file)
        for feature in geojson_data['features']:
            properties = feature.get('properties', {})
            name = properties.get('name', '')
            geometry = feature.get('geometry', {})
            if geometry.get('type') == 'Polygon':
                options.append(name)     
        
    return options

# Callback to handle download button click and trigger download
@app.callback(
    Output("download", "data"),
    Input("download-button", "n_clicks"),
    State("dropdown", "value"),
    prevent_initial_call=True
)
def download_data(n_clicks, selection):
    if n_clicks is None or not ctx.triggered_id or "download-button" not in ctx.triggered_id:
        print('Sono qui punto 0')
        # If the button is not clicked, return no_update
        return dash.no_update
    global building_data  # Assuming building_data is defined
    # Filter building_data to include only rows where polygon_index is not None
    building_data_filtered = building_data[building_data["polygon_index"].notnull()]
    print(building_data_filtered)
    if selection != None:
        print('Sono qui punto 1')
        print(selection[0])
        mask = building_data_filtered["polygon_index"].isin(selection)
        print(mask)
        building_data_new = building_data_filtered[mask]
        print(building_data_new)
    else:
        print('Sono qui punto 2')
        building_data_new = building_data

    if not building_data_new.empty:
        print('Sono qui punto 3')
        # Create a CSV string from the DataFrame
        csv_string = building_data_new.to_csv(index=False, encoding='utf-8-sig')
        # Create a dictionary to be returned as the 'data' property of the Download component
        return dict(content=csv_string, filename="building_data.csv")
    else:
        print('Sono qui punto 4')
        print(n_clicks)
        print(building_data_new)
        # If building_data_new is empty, return no_update
        return dash.no_update

# Update Histogram Figure based on building categories
@app.callback(
    Output("histogram", "figure"),
    [Input("dropdown", "value"),
     Input("download-button", "n_clicks"),
     Input('building-data-store', 'data'),
     ],
    )
def update_histogram(selection, download_button_clicks, building_data_str):
    global building_data, colors  # Declare building_data and colors as global variables
    # Update the building_data variable
    if building_data_str and building_data_str!='Null':
        #print(building_data_str)
        #print('Cosa sto vedendo')
        building_data = pd.read_json(building_data_str, orient='split')
    else:
        print('Se ciaooo. Non so dove sono finito')
    # Print types and unique values of relevant columns
    #print("Type of 'polygon_index':", building_data["polygon_index"].dtype)
    #print("Unique values of 'polygon_index':", building_data["polygon_index"].unique())

    if (not selection) or (len(selection) == 1 and selection[0] is None) or ('All' in selection):
        print("Empty selection")
        building_data_new = building_data
    else:
        print("Selection:", selection)
        mask = building_data["polygon_index"].isin(selection)
        building_data_new = building_data[mask]
        print("Filtered building_data:")
        print(building_data_new)
        print(download_button_clicks)
    # Increment download_button_clicks to trigger the callback
    # Check if building_data_new is empty
    if building_data_new.empty:
        # Create an empty DataFrame for the histogram
        histogram_data = pd.DataFrame(columns=['color'])
        print('Sono qui')
        # If no location is selected, return an empty histogram
        layout = go.Layout(
            title="No Building affected",
            bargap=0.01,
            bargroupgap=0,
            barmode="group",
            margin=go.layout.Margin(l=10, r=10, t=50, b=0),
            showlegend=False,
            plot_bgcolor="#323130",
            paper_bgcolor="#323130",
            dragmode="select",
            font=dict(color="white"),
            xaxis=dict(
                showgrid=False,
                fixedrange=True,
            ),
            yaxis=dict(
                showticklabels=False,
                showgrid=False,
                fixedrange=True,
                rangemode="nonnegative",
                zeroline=False,
                range=[0, 10],  # Adjust the range for the desired height
            ),
        )
        return go.Figure(
            data=[
                go.Bar(x=['white', 'green', 'yellow', 'red'],
                       y=[0, 0, 0, 0], ),
            ],
            layout=layout,
        )

    else:
        histogram_data = pd.DataFrame({
            'color': building_data_new.apply(
                lambda row: 'white' if not row['inside_polygon'] else (
                    'green' if row['Floor'] >= 2 else (
                        'yellow' if row['Floor'] >= 0 else 'red'
                    )
                ),
                axis=1
            ).astype('category')  # Ensure the column is of type category
        })
        
        # Count the occurrences of each color category
        color_counts = histogram_data['color'].value_counts()

        # Extract data for the bar chart
        xVal = list(color_counts.index)
        yVal = color_counts.values

        layout = go.Layout(
            bargap=0.01,
            bargroupgap=0,
            barmode="group",
            margin=go.layout.Margin(l=50, r=50, t=0, b=0),
            showlegend=False,
            plot_bgcolor="#323130",
            paper_bgcolor="#323130",
            dragmode="select",
            font=dict(color="white"),
            xaxis=dict(
                showgrid=False,
                fixedrange=True,
            ),
            yaxis=dict(
                showticklabels=False,
                showgrid=False,
                fixedrange=True,
                rangemode="nonnegative",
                zeroline=False,
                range=[0, max(yVal) + max(yVal) / 8],  # Adjust the range for the desired height
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
                go.Bar(x=xVal,
                       y=yVal,
                       marker=dict(color=[colors[color] for color in xVal]),  # Assuming colors is defined
                       hoverinfo="x"),
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


@app.callback(
    [Output('map_new', 'figure'),
     Output('building-data-store', 'data')],
    [Input("location-dropdown", "value"),
     Input('upload-json', 'contents'),
     Input('upload-gpkg', 'contents'),
     ],
    [State('upload-json', 'filename'),
     State('upload-gpkg', 'filename')]
)

def update_map(selected_location, json_contents, gpkg_contents, json_filename, gpkg_filename):
    if not json_contents and not gpkg_contents:
        # Generate 25 building coordinates
        num_buildings = 1000
        building_data = generate_building_data(num_buildings)
        # Set default center and zoom
        center = dict(lat=43.654514997938946, lon=10.554735408915095)
        print(selected_location)
    
        if selected_location and selected_location != 'None':
            # If a location is selected, update center and zoom based on the selected location
            selected_location_info = list_of_locations[selected_location]
            center = dict(lat=selected_location_info.get('lat', 0), lon=selected_location_info.get('lon', 0))
            print(selected_location_info.get('lat', 0))
            print(selected_location_info.get('lon', 0))
            with open(selected_location_info.get('layer', 0), 'r') as file: #EMSR705_aois.json
                geojson_data = json.load(file)
        else:
            print(selected_location)        
            # Coordinates for the polygon
            # Parse the GeoJSON-like data
            # Read GeoJSON-like data from file
            with open('EMSR705_aois.json', 'r') as file: #EMSR705_aois.json
                geojson_data = json.load(file)
            
        # Extract polygon coordinates
        polygons = []
        indexes = []
        options = []
        for feature in geojson_data['features']:
            properties = feature.get('properties', {})
            name = properties.get('name', '')
            geometry = feature.get('geometry', {})
            if geometry.get('type') == 'Polygon':
                coordinates = geometry.get('coordinates', [])
                polygons.append(Polygon(coordinates[0]))
                indexes.append(name)
                options.append(name)
        
        # Create a GeoDataFrame for GeoJSON-like plotting
        gdf = gpd.GeoDataFrame(geometry=gpd.GeoSeries(polygons))

        # Add a new column to building_data to check if each point is inside the polygons
        building_data['inside_polygon'] = building_data.apply(
            lambda row: any(Point(row['Longitude'], row['Latitude']).within(polygon) for polygon in polygons),
            axis=1
        )
        building_data['polygon_index'] = building_data.apply(
            lambda row: next((index for index, polygon in zip(indexes, polygons) if Point(row['Longitude'], row['Latitude']).within(polygon)), None),
            axis=1
        )

        # Set the color based on the floor and inside_polygon columns
        building_data['color'] = building_data.apply(
            lambda row: 'white' if not row['inside_polygon'] else (
                'green' if row['Floor'] >= 2 else (
                    'yellow' if row['Floor'] >= 0 else 'red'
                )
            ),
            axis=1
        )
        
        
        # Plot polygons using GeoPandas
        fig = px.choropleth_mapbox(
            gdf,
            geojson=gdf.geometry.__geo_interface__,
            zoom=9,
            center=center,
            locations=gdf.index,
            color=indexes,  # Use the "indexes" list for coloring
            hover_name=indexes,  # Show names on hover
            mapbox_style='carto-darkmatter',  # Use OpenStreetMap as the base map
            color_discrete_sequence=px.colors.sequential.Viridis_r,
            opacity=0.4,
        )
        
        # Add scatter mapbox trace for building points
        # Plot the building points with the specified colors
        scatter_trace = px.scatter_mapbox(
            building_data,
            lat='Latitude',
            lon='Longitude',
            hover_data=['Floor', 'Area', 'Value'],
            mapbox_style='carto-darkmatter',
        )
        
        # Set the color for each point based on the 'color' column
        scatter_trace.update_traces(marker=dict(color=building_data['color']))
        
        fig.add_trace(scatter_trace.data[0])
        
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
        # Output the building_data as a string
        building_data_str = building_data.to_json(date_format='iso', orient='split')


        return fig, building_data_str


    if json_contents:
        data = read_json(json_contents)
        features = data.get('features', [])

        # Extract polygon coordinates
        polygons = []
        indexes = []
        options = ['All']
        for feature in geojson_data['features']:
            properties = feature.get('properties', {})
            name = properties.get('name', '')
            geometry = feature.get('geometry', {})
            if geometry.get('type') == 'Polygon':
                coordinates = geometry.get('coordinates', [])
                polygons.append(Polygon(coordinates[0]))
                indexes.append(name)
                options.append(name)

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

        return fig, data

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

        return fig, data


if __name__ == "__main__":
    app.run_server(debug=False)