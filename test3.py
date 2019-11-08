import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd



app = dash.Dash()

#reading in the Data
df0 = pd.read_csv(r'D:\py_dash\COI\COI_Dash\alldata.csv') 
#delete the row that contains the US number - skews scatter plot
df0=df0[df0['statecode'] != 'US' ]


#latitude -longitude codes
df_cd = pd.read_csv(r'D:\py_dash\COI\COI_Dash\latlong_codes.csv') 
df_cd=df_cd[df_cd['statecode'] != 'PR' ]
df = pd.merge(df0, df_cd, how='outer', on=['statecode'])



mapbox_access_token = "pk.eyJ1IjoicGxvdGx5bWFwYm94IiwiYSI6ImNqdnBvNDMyaTAxYzkzeW5ubWdpZ2VjbmMifQ.TXcBE-xg9BFdV2ocecc_7g"
mapbox_style = "mapbox://styles/plotlymapbox/cjvprkf3t1kns1cqjxuxmwixz"

available_indicators = df['variable'].unique()
scl = [ [0,"rgb(5, 10, 172)"],[0.35,"rgb(40, 60, 190)"],[0.5,"rgb(70, 100, 245)"],\
    [0.6,"rgb(90, 120, 245)"],[0.7,"rgb(106, 137, 247)"],[1,"rgb(220, 220, 220)"] ]
colorsIdx = {'2015': 'rgb(215,48,39)', '2016': 'rgb(215,148,39)', '2017': 'rgb(0,176,240)', 'text': '#7FDBFF'}
colabc      = df['year_end'].map(colorsIdx)

#allcol={statecode	year_end	variable	value}
columns=[{'name': i, 'id': i} for i in df.columns]

#begin layout of app
app.layout = html.Div([
	#Main Title
	html.H1(
        children='Children of Immigrants',
        style={
            'textAlign': 'center',
            'color': colorsIdx['text']
        },),
	html.P(id='description',
				children ='Since 2006, Urban has used data from the American Community Survey to understand the trends in the population of children born at least one foreign-born parent—that is, children of immigrants. \n',
				),
    

	html.P("Click on a state to see variable trends year {0}".format(df['year_end'].min()),
                          id="heatmap-title",
                         ),
	                           
    html.P(id="slider-text",
           children="Drag the slider to change the year:",),					 
	#Slider
    html.Div(dcc.Slider(
        id='crossfilter-year--slider',
        min=df['year_end'].min(),
        max=df['year_end'].max(),
        value=df['year_end'].max(),
        step=None,
        marks={str(year):{"label": str(year), "style": {"color": "#7fafdf"},} for year in df['year_end'].unique()}
    ), style={'width': '45%', 'padding': '0px 20px 20px 40px'}),

	
	#US Map
	 html.Div(
		id="heatmap-container",
		children=[
			html.Div([					 
					html.Div([dcc.Graph(
							id="county-choropleth",
							figure=dict(
									data=[
										dict(type="scattermapbox",
											lat=df["latitude"],
											lon=df["longitude"],
											mode='markers',
											text=df["statecode"],
											customdata =df['statecode'],
											)
										  ],
									layout=dict(
										autosize = True,
										clickmode = 'event+select',
										margin = dict(l = 0, r = 0, t = 0, b = 0),
										mapbox=dict(
												layers=[],
												accesstoken=mapbox_access_token,                                            
												center=dict(lat=38.72490, 
															lon=-95.61446
															),
												pitch=0,
												zoom=2.8,
												style='light',
												),
												),
										),
									),
								], style={'display': 'inline-block',  'width': '45%'}), 
							
					html.Div([
							dcc.Dropdown(
									id='crossfilter-yaxis-column',
									options=[{'label': i, 'value': i} for i in available_indicators],
									value='all_children'
								),
							dcc.Graph(id='y-time-series'),
							], style={'display': 'inline-block',  'width': '45%', 'float': 'right'}),
					] ),
		]),
								
   
	

	#Header for Trends over the years
	html.Div([
	html.H1(
        children='Trends over the years',
        style={
            'textAlign': 'center',
            'color': colorsIdx['text']
        }
    )]),

	# Trends over all the years of data - The variables for this is fixed. Ask if they need to be variable
	html.Div([
		dcc.Graph(id='bargraph0'),]),
	html.Div([
		dcc.Graph(id='bargraph1'),]),
	html.Div([
		dcc.Graph(id='bargraph2'),]),	


	#Data table

	html.Div([
	dash_table.DataTable(
		id='datatable-row-ids',
		columns=[
			{"name": i, "id": i, "selectable": True} for i in df.columns
		],
		data=df.to_dict('records'),
		editable=True,
		filter_action="native",
        sort_action="native",
        sort_mode="multi",
#       row_selectable="multi",
#		row_deletable=True,
        selected_columns=[],
        page_action="native",
        page_current= 0,
        page_size= 10,
		style_table={ 'maxHeight': '300', 'overflowX': 'scroll'},
		),
		html.Div(id='datatable-row-ids-container')
])
		
])

def create_time_series(dff,  title):	    
    return {
        'data': [go.Scatter(
            x=dff['year_end'],
            y=dff['value'],
            mode='lines+markers'
        )],
        'layout': {
            'height': 400,
            'margin': {'l': 40, 'b': 20, 'r': 10, 't': 10},
			'annotations': [{
                'x': 0, 'y': 0.85, 'xanchor': 'left', 'yanchor': 'bottom',
                'xref': 'paper', 'yref': 'paper', 'showarrow': False,
                'align': 'left', 'bgcolor': 'rgba(255, 255, 255, 0.5)',
                'text': title
				
            }],

            'yaxis': {'showgrid': True},
            'xaxis': {'showgrid': False , 
						'tickmode' : 'linear',
						'tick0' : dff['year_end'].min(),
						'dtick' : 1},
			'textAlign': 'center'
        }
    }
 
@app.callback(
    dash.dependencies.Output('y-time-series', 'figure'),
    [
	dash.dependencies.Input('county-choropleth', 'clickData'),
     dash.dependencies.Input('crossfilter-yaxis-column', 'value')])
def update_y_timeseries(selection, yaxis_column_name):
	if selection is None:
		country_name = 'AK'
		#return {}
	else:
		country_name = selection['points'][0]['text']
	dff = df[df['statecode'] == country_name]
	dff = dff[dff['variable'] == yaxis_column_name]
	return create_time_series(dff, yaxis_column_name)

#age bar graph
@app.callback(
    dash.dependencies.Output('bargraph0', 'figure'),
    [dash.dependencies.Input('county-choropleth', 'clickData'),
     dash.dependencies.Input('crossfilter-yaxis-column', 'value')])
def update_graph(selection, yaxis_column_name):
	if selection is None:
		country_name = 'AK'
		#return {}
	else:
		country_name = selection['points'][0]['customdata']
	dff = df[df['statecode'] == country_name]
	#sttext= df[df['variable'] == yaxis_column_name]['statecode']
	#dff = df[df['statecode'] == sttext ]
	trace1 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='age_0_to_3']['value'], name='0-3' ,marker_color='rgb(22, 150, 210)') 
	trace2 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='age_4_to_5']['value'], name='4-5', marker_color='rgb(253, 191, 17)') 
	trace3 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='age_6_to_8']['value'], name='6-8', marker_color='rgb(210, 210, 210)') 
	trace4 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='age_9_to_12']['value'], name='9-12',marker_color='rgb(236, 0, 139)' ) 
	trace5 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='age_13_to_15']['value'], name='13-15', marker_color='rgb(85, 183, 72)') 
	trace6 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='age_16_to_17']['value'], name='16-17', marker_color='rgb(92, 88, 89)') 
	return {
		'data': [trace1, trace2, trace3, trace4, trace5, trace6],
        'layout': {
            'title': 'Age of children in {}'.format(country_name)
        }
    }

#race
@app.callback(
    dash.dependencies.Output('bargraph1', 'figure'),
    [dash.dependencies.Input('county-choropleth', 'clickData'),
     dash.dependencies.Input('crossfilter-yaxis-column', 'value')])
def update_graph(selection, yaxis_column_name):
	if selection is None:
		country_name = 'AK'
		#return {}
	else:
		country_name = selection['points'][0]['customdata']
	dff = df[df['statecode'] == country_name]
	
	#sttext= df[df['variable'] == yaxis_column_name]['statecode']
	#dff = df[df['statecode'] == sttext ]
	trace1 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='asian']['value'], name='Asian' ,marker_color='rgb(22, 150, 210)') 
	trace2 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='black']['value'], name='African American',marker_color='rgb(253, 191, 17)' ) 
	trace3 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='hispanic']['value'], name='Hispanic', marker_color='rgb(210, 210, 210)') 
	trace4 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='natamer']['value'], name='Native American', marker_color='rgb(236, 0, 139)') 
	trace5 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='white']['value'], name='White', marker_color='rgb(85, 183, 72)') 
		
	return {
		'data': [trace1, trace2, trace3, trace4, trace5],
        'layout': {
            'title': 'Race of children in {}'.format(country_name)
        }
    }


#sub plots
@app.callback(
    dash.dependencies.Output('bargraph2', 'figure'),
    [dash.dependencies.Input('county-choropleth', 'clickData'),
     dash.dependencies.Input('crossfilter-yaxis-column', 'value')])
def update_graph(selection, yaxis_column_name):
	if selection is None:
		country_name = 'AK'
		#return {}
	else:
		country_name = selection['points'][0]['customdata']
	dff = df[df['statecode'] == country_name]
	trace0 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='all_children']['value'], name='All Children' ,marker_color='rgb(0, 0, 0)') 
	trace1 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='children_from_europe']['value'], name='Europe' ,marker_color='rgb(22, 150, 210)') 
	trace2 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='children_from_mexico']['value'], name='Mexico',marker_color='rgb(253, 191, 17)' ) 
	trace3 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='children_from_central_america']['value'], name='Central America', marker_color='rgb(210, 210, 210)') 
	trace4 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='children_from_south_america']['value'], name='South America', marker_color='rgb(236, 0, 139)') 
	trace5 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='children_from_southeast_asia']['value'], name='Southeast Asia', marker_color='rgb(85, 183, 72)') 
	trace6 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='children_from_east_asia']['value'], name='East Asia', marker_color='rgb(236, 0, 139)') 
	trace7 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='children_from_middle_east']['value'], name='Middle East', marker_color='rgb(85, 183, 72)') 

	return {
		'data': [trace0, trace1, trace2, trace3, trace4, trace5, trace6, trace7],
        'layout': {
            'title': 'Population {}'.format(country_name)
        }
    }	
	

#data table	

	
	
	
	
app.css.append_css({
    'external_url': 'https://codepen.io/chriddyp/pen/bWLwgP.css'
})
@app.server.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'


if __name__ == '__main__':
    app.run_server(debug=True)