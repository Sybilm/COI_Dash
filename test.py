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
	 children=[html.P("Heatmap of age adjusted mortality rates \
                            from poisonings in year {0}".format(df['year_end'].min()),
                                    id="heatmap-title",
                                ),
                                dcc.Graph(
                                    id="county-choropleth",
									
									#hoverData={'points': [{'customdata': 'AK'}]},
                                    figure=dict(
                                        data=[
                                            dict(type="scattermapbox",
                                                lat=df["latitude"],
                                                lon=df["longitude"],
												mode='markers',
                                                text=df["statecode"],
												customdata =df['statecode'],
                                                #clickData={'points': [{'customdata': 'AK'}]},
												
                                            )
                                        ],
                                        layout=dict(
											autosize = True,
											clickmode = 'event+select',
											#hovermode = "closest",
											margin = dict(l = 0, r = 0, t = 0, b = 0),
                                            mapbox=dict(
                                                layers=[],
                                                accesstoken=mapbox_access_token,
                                                
                                                center=dict(
                                                    lat=38.72490, lon=-95.61446
                                                ),
                                                pitch=0,
                                                zoom=3.0,
												style='light',

                                            ),
                                           # autosize=True,
                                        ),
                                    ),
                                ),
                            ], style={'width': '100%', 'display': 'inline-block', 'padding': '0 20'}),

	
	                   

	#dropdown Menu for variable selection for Scatter Plot and Trends
    html.Div([
        html.Div([
            dcc.Dropdown(
                id='crossfilter-xaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='all_children'
            )		
			
        ],
        style={'width': '49%', 'display': 'inline-block'}),

        html.Div([
            dcc.Dropdown(
                id='crossfilter-yaxis-column',
                options=[{'label': i, 'value': i} for i in available_indicators],
                value='imm_children'
            )
        ], style={'width': '49%', 'float': 'right', 'display': 'inline-block'})
    ], style={
        'borderBottom': 'thin lightgrey solid',
        'backgroundColor': 'rgb(250, 250, 250)',
        'padding': '10px 5px'
    }),
	
	#scatter plotl
    html.Div([
        dcc.Graph(
            id='crossfilter-indicator-scatter',
            hoverData={'points': [{'customdata': 'AK'}]}
        )
    ], style={'width': '49%', 'display': 'inline-block', 'padding': '0 20'}),
	
	#Time series plots
	html.Div([
        dcc.Graph(id='x-time-series'),  
		dcc.Graph(id='y-time-series'),
    ], style={'display': 'inline-block', 'width': '49%'}),
 #SM   html.Div([
         
 #SM   ], style={'display': 'inline-block', 'width': '45%'}),
	

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
#fixed- works	
#	html.Div([dcc.Graph(
#    id='bargraph1',
#    figure={
#        'data': [
#            {'x':df['year_end'], 'y':df[df['variable']=='age_0_to_3']['value'], 'type':'bar', 'name':'0-3'} ,
#			{'x':df['year_end'], 'y':df[df['variable']=='age_4_to_5']['value'], 'type':'bar', 'name':'4-5'} ,
#			{'x':df['year_end'], 'y':df[df['variable']=='age_6_to_8']['value'], 'type':'bar', 'name':'6-8'} ,
#			{'x':df['year_end'], 'y':df[df['variable']=='age_9_to_12']['value'], 'type':'bar', 'name':'9-12'} ,
#			{'x':df['year_end'], 'y':df[df['variable']=='age_13_to_15']['value'], 'type':'bar', 'name':'13-15'} ,
#			{'x':df['year_end'], 'y':df[df['variable']=='age_16_to_17']['value'], 'type':'bar', 'name':'16-17'} 
#        
#        ],
#        'layout': {
#            'title': 'Age '
#        }
 #   }
#	)])

	#Data table

	html.Div([
	dash_table.DataTable(
	#data=map_data.to_dict('records'),
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
		
		
#		fixed_rows={ 'headers': True, 'data': 0 },
		
		#style_cell={
			# all three widths are needed
	#		'minWidth': '180px', 'width': '180px', 'maxWidth': '180px',
	#		'overflow': 'hidden',
	#		'textOverflow': 'ellipsis',
	#	},
	#	)
	#	])
])





#@app.callback(
#	dash.dependencies.Output('heatmap-title', 'children'), 
	#[dash.dependencies.Input('crossfilter-year--slider', 'value')]
	#)
#def update_map_title(year_value):
#	return "Heatmap in year {0}".format(year_value)

#scatter
@app.callback(
    dash.dependencies.Output('crossfilter-indicator-scatter', 'figure'),
    [dash.dependencies.Input('crossfilter-xaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-yaxis-column', 'value'),
     dash.dependencies.Input('crossfilter-year--slider', 'value')])
def update_graph(xaxis_column_name, yaxis_column_name, 
				year_value):
    dff = df[df['year_end'] == year_value ]

    return {
        'data': [go.Scatter(
            x=dff[dff['variable'] == xaxis_column_name]['value'],
            y=dff[dff['variable'] == yaxis_column_name]['value'],
            text=dff[dff['variable'] == yaxis_column_name]['statecode'],
			textposition='top center',
            customdata=dff[dff['variable'] == yaxis_column_name]['statecode'],
            mode='markers',
            marker={
                'size': 15,
                'opacity': 0.5,
                'line': {'width': 0.5, 'color': 'white'},
				'color': 'rgb(22, 150, 210)'
	            }			
        )],
        'layout': go.Layout(
            xaxis={
                'title': xaxis_column_name
            },
            yaxis={
                'title': yaxis_column_name
            },
            margin={'l': 40, 'b': 30, 't': 10, 'r': 20},
            height=450,
            hovermode='closest'
        )
    }

def create_time_series(dff,  title):	    
    return {
        'data': [go.Scatter(
            x=dff['year_end'],
            y=dff['value'],
            mode='lines+markers'
        )],
        'layout': {
            'height': 225,
            'margin': {'l': 20, 'b': 30, 'r': 10, 't': 10},
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
# dash.dependencies.Output('county-choropleth_test', 'figure'),
@app.callback(
    dash.dependencies.Output('x-time-series', 'figure'),
    [
	dash.dependencies.Input('county-choropleth', 'clickData'),
	#dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData'),
     dash.dependencies.Input('crossfilter-xaxis-column', 'value')])
def update_x_timeseries(selection, xaxis_column_name):
	if selection is None:
		return {}
	else:
		country_name = selection['points'][0]['text']
	#country_name = clickData['points'][0]['customdata']
	
	#country_name = hoverData['points'][0]['customdata']
	 #AAA       x_data = np.linspace(0,500,500)
     #AAAA   y_data = np.random.rand(500)
		dff = df[df['statecode'] == country_name]
		dff = dff[dff['variable'] == xaxis_column_name]
		title = '<b>{}</b><br>{}'.format(country_name, xaxis_column_name)
	return create_time_series(dff, title)
#	return create_time_series(dff, xaxis_column_name)
    

	

@app.callback(
    dash.dependencies.Output('y-time-series', 'figure'),
    [
	dash.dependencies.Input('county-choropleth', 'clickData'),
	#dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData'),
     dash.dependencies.Input('crossfilter-yaxis-column', 'value')])
def update_y_timeseries(selection, yaxis_column_name):
	if selection is None:
		return {}
	else:
		#country_name = clickData['points'][0]['customdata']
		country_name = selection['points'][0]['text']
		dff = df[df['statecode'] == selection['points'][0]['customdata']]
		dff = dff[dff['variable'] == yaxis_column_name]
	return create_time_series(dff, yaxis_column_name)
#	title = '<b>{}</b><br>{}'.format(country_name, yaxis_column_name)
#	return create_time_series(dff, title)



#age bar graph
@app.callback(
    dash.dependencies.Output('bargraph0', 'figure'),
    [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData'),
     dash.dependencies.Input('crossfilter-yaxis-column', 'value')])
def update_graph(hoverData, yaxis_column_name):
	country_name = hoverData['points'][0]['customdata']
	dff = df[df['statecode'] == hoverData['points'][0]['customdata']]
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
    [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData'),
     dash.dependencies.Input('crossfilter-yaxis-column', 'value')])
def update_graph(hoverData, yaxis_column_name):
	country_name = hoverData['points'][0]['customdata']
	dff = df[df['statecode'] == hoverData['points'][0]['customdata']]
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
    [dash.dependencies.Input('crossfilter-indicator-scatter', 'hoverData'),
     dash.dependencies.Input('crossfilter-yaxis-column', 'value')])
def update_graph(hoverData, yaxis_column_name):
	country_name = hoverData['points'][0]['customdata']
	dff = df[df['statecode'] == hoverData['points'][0]['customdata']]
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