import dash
import dash_table
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np

#read in data from S3. 
####
#CHANGE IMPORT ACCORDINGLY!
# The readin python code needs to be in the same directory as app_map.py
####
import readindata_18Nov2019
df_orig, df0=readindata_18Nov2019.coi_long_format_from_S3([2014, 2015, 2016, 2017])



#changing column names to column labels for df_orig
#df0 contains variable names and labels. Will change df_orig column names using these 2 vars from df0
df01=df0[["variable", "variable_label"]].drop_duplicates()
d = df01.set_index('variable').to_dict()
#adding key value pairs for the ones not present in d
d["variable_label"].update({'data_sort_id':'data_sort_id', 'metrocode':'metrocode', 'statecode':'statecode', 'Statistics_Label':'Statistics_Label', 'StatID':'StatID', 'year_start':'year_start',
  'year_end':'year_end',     'share':'share',     'number':'number', 'CategoryID':'CategoryID',
'CategoryName':'CategoryName',
'CategorySortOrder':'CategorySortOrder',
'CategorySortOrderName':'CategorySortOrderName',
'prtUS5pyrs':'prtUS5pyrs',
'prtUSLT5yrs':'prtUSLT5yrs',
'Statistics_Label_short':'Statistics_Label_short'
})
#renaming column names with column labels 
df_orig.columns = df_orig.columns.to_series().map(d['variable_label'])    




#color scale for the choropleth
scl = [
    [0.0, 'rgb(207,232,243)'],
    [0.2, 'rgb(162,212,236)'],
    [0.4, 'rgb(115,191,226)'],
    [0.6, 'rgb(70,171,219)'],
    [0.8, 'rgb(22,150,210)'],
    [1.0, 'rgb(18,113,158)']
]

app = dash.Dash()

#df_orig - data for the table & choropleth. Layout of the data is wide
#df_orig = pd.read_csv(r'D:\py_dash\COI\COI_Dash\Orig_data2.csv') 

#df0 -reading in data for the graphs. Layout of the data is long.
#df0 = pd.read_csv(r'D:\py_dash\COI\COI_Dash\alldata2.csv') 
#delete the row that contains the US number - skews scatter plot
df0=df0[df0['statecode'] != 'US' ]
df0=df0[df0['share'] == 0 ]
df0=df0[df0['value'] != -97]
df0=df0[df0['value'] != -98]

##CHANGE PATH!!!
#latitude -longitude codes
df_cd = pd.read_csv(r'D:\py_dash\COI\COI_Dash\latlong_codes.csv') 


#COI data does not exist for statecode=PR
df_cd=df_cd[df_cd['statecode'] != 'PR' ]
#merging in the FIPS code to the COI data
df = pd.merge(df0, df_cd, how='outer', on=['statecode'])
df=df[df["share"] ==0]								#share =0 implies number

###Dropdown variable list
#variable name array for the drop down boxes.
available_indicators = df['variable_label'].unique()
#statistics
stat_indicators=df['Statistics_Label'].unique()
#Variable array list for the Choropleth. Drop off Population total
available_orig = df['variable_label'].unique()
available_orig = available_orig[available_orig != "Population total"]



colorsIdx = {'2015': 'rgb(215,48,39)', '2016': 'rgb(215,148,39)', '2017': 'rgb(0,176,240)', 'text': '#7FDBFF'}

#Dash apps are composed of two parts. 
#The first part is the "layout" of the app and it describes what the application looks like. 
# The second part describes the interactivity of the application

####################################################
### App layout
####################################################

app.layout = html.Div([
	#Main Title
	html.H1(
        children='Children of Immigrants',
        style={
            'textAlign': 'center',
            'color': colorsIdx['text']
        },),
	html.Br(),	
	html.Br(),	
	
	#SLIDER 
	html.P("Drag the slider to select a year:", id="slider-text",),	
    html.Div(
		dcc.Slider(
			id='crossfilter-year--slider',
			min=df['year_end'].min(),
			max=df['year_end'].max(),
			value=df['year_end'].max(),
			step=None,
			marks={str(year):{"label": str(year), "style": {"color": "#7fafdf"},} for year in df['year_end'].unique()},
			included=False
				), style={'width': '50%', 'padding': '0px 80px 20px 40px', 'float': 'center'}
			),


	html.Br(),
	html.Br(),
	
	
	#BLOCK: DROPDOWN BOXES
	html.Div([
		#LEFT SIDE: Variable dropedown for Choropleth & Statistic
		html.Div([
				html.Label([ "Select statistic. Statistic selection affects all graphs on the dashboard", 
							dcc.Dropdown(
								id='crossfilter-statistic-column',
								options=[{'label': i, 'value': i} for i in stat_indicators],
								value='Asian'
								), 
							]),
				html.Br(),
				html.Label([ "Select variable for Choropleth",
							dcc.Dropdown(
								id='var_choice'  , 
								value='All children'  , 
								options=[{'label': i, 'value': i} for i in available_orig],
								),
							]),														
				], style={'display': 'inline-block',   'width': '45%'}),
							
	
		#RIGHT SIDE: Variable dropdown for Trend charts		
		html.Div([	

				html.Label(["Select Variable 1",
							dcc.Dropdown(
								id='crossfilter-var1',
								options=[{'label': i, 'value': i} for i in available_indicators],
								value='All children'
								),
							]),		
				html.Br(),
				html.Label(["Select Variable 2",
							dcc.Dropdown(
								id='crossfilter-var2',
								options=[{'label': i, 'value': i} for i in available_indicators],
								value='US-born children'
								)
							]),
				], style={'display': 'inline-block',   'width': '45%', 'float': 'right'}),
	]),
	#END of dropdown block
	html.Br(),
	#BLOCK : Choropleth and trend charts
	html.Div([
		#LEFT SIDE: Choropleth
		html.Div([
				dcc.Graph(id='county-choropleth',
						hoverData={'points': [{'customdata': 'AK'}]},
						figure=dict(
									data=[],
									layout={},
									),
						)
				],style={'display': 'inline-block',  'width': '48%',}),
		#RIGHT SIDE: TIME series
		html.Div([				
				dcc.Graph(id='y-time-series'),
				], style={'display': 'inline-block',  'width': '45%', 'float': 'right', 'verticalAlign' : "bottom", }),
	]),

	#END OF BLOCK : Choropleth and trend charts		

	#Trend charts over the years
	#heading
	html.H1(
		children='Trends over the years',
		style={
			'textAlign': 'center',
			'color': colorsIdx['text']
			}
		),
			
	html.Br(),

	# Trends over all the years of data - The variables for this is fixed. Ask if they need to be variable
	#Age of children in state
	html.Div([
		dcc.Graph(id='bargraph0')],style={'margin':'auto', 'width':'75%'  }),
	#Race and ethnicity of children in state
	html.Div([
		dcc.Graph(id='bargraph1'),],style={'margin':'auto', 'width':'75%'  }),
	#Origin of parents
	html.Div([
		dcc.Graph(id='bargraph2'),],style={'margin':'auto', 'width':'75%'  }),	
	#End of trends
	
	#BLOCK: Data table
	html.Div([
	html.Div([
		dash_table.DataTable(
			id='datatable-row-ids',
			columns=[
				{"name": i, "id": i, "selectable": True} for i in df_orig.columns
			],
			data=df_orig.to_dict('records'),
			editable=True,
			filter_action="native",
			sort_action="native",
			sort_mode="multi",
			row_selectable="multi",
			column_selectable="multi",
	#		row_deletable=True,
			selected_columns=[],
			selected_rows=[],
			page_action="native",
			page_current= 0,
			page_size= 10,
			style_table={ 'maxHeight': '300', 'overflowX': 'scroll'},
			),
		#html.Div(id='datatable-row-ids-container')
	]),
	]),
	html.Br(),
	html.Br(),
	#End block data table

		
#	html.Div([
#		dcc.Graph(id='bargraph0'),],style={'display':'none'}),
])




####################################################
### Interactivity of the application
####################################################

# Choropleth
@app.callback(dash.dependencies.Output('county-choropleth' , 'figure') ,
              [dash.dependencies.Input('crossfilter-year--slider', 'value') ,
				dash.dependencies.Input('var_choice', 'value'),
				dash.dependencies.Input('crossfilter-statistic-column', 'value')
				])
def update_figure(value, varchoice, stvalue):
    #drop missing values
	df_orig0=df_orig[df_orig['year_end'] == value]							#subsetting for year selected on the slider.
	df_orig0=df_orig0[df_orig0["share"] ==1]								#share =1 implies percent
	df_orig0=df_orig0[df_orig0[varchoice] != -98]
	df_orig0=df_orig0[df_orig0[varchoice] != -97]
	df_orig0=df_orig0[df_orig0["Statistics_Label"] != "Population total"]	# population total is not relevant to the choropleth
	df_orig1=df_orig0[df_orig0["Statistics_Label"] == stvalue]				#subsetting for statistics selected using the dropdown
	
	
	for col in df_orig1.columns:
		df_orig1[col] = df_orig1[col].astype(str)
	
	data = [go.Choropleth(
				colorscale = scl,
				autocolorscale = False,
				customdata =df_orig1['statecode'],
				locations = df_orig1['statecode'],
				z = df_orig1[varchoice].astype(float),
				locationmode = 'USA-states',
				text=df_orig1["statecode"],
				#hoverinfo='text',
				
				marker = go.choropleth.Marker(
					line = go.choropleth.marker.Line(
						color = 'rgb(255,255,255)',
						width = 2
					)),
				colorbar = go.choropleth.ColorBar(
					
					len=0.75,
					thickness=8)
			)]
	layout = go.Layout(
				title = go.layout.Title(
										text = '<br> Choropleth of {}'.format(varchoice)
										),
				autosize=False,
				width=720,
				#SMMheight=600,
				clickmode = 'event+select',
			    margin=go.layout.Margin(
										l=20,
										r=20,
										b=20,
										t=30,
										pad=4,
										),
			#	clickmode = 'event+select',
				geo = go.layout.Geo(
									scope = 'usa',
									projection = go.layout.geo.Projection(type = 'albers usa'),
									showlakes = True,
									lakecolor = 'rgb(255, 255, 255)'),
									)
	return {"data": data,
			"layout": layout}




# Function that creates the Time series chart
def create_time_series(dff, var1, var2, country_name):
	trace1 = go.Scatter( x=dff['year_end'], y=dff[dff['variable_label'] == var1]['value'], mode='lines+markers', name=var1, marker_color='rgb(22, 150, 210)') 
	trace2 = go.Scatter( x=dff['year_end'], y=dff[dff['variable_label'] == var2]['value'], mode='lines+markers' , name=var2, marker_color='rgb(253, 191, 17)')
	data = [trace2, trace1] 
	return {
        'data': data,
		'layout': {
				'title': "Trend Lines for {}".format(country_name),
				'margin': {'l': 60, 'b': 80, 'r': 40, 't': 90},
				'annotations': [{
					'x': 0, 
					'y': 0.85, 
					'xanchor': 'left', 
					'yanchor': 'bottom',
					'xref': 'paper', 
					'yref': 'paper', 
					'showarrow': False,
					'align': 'middle', 
					'bgcolor': 'rgba(255, 255, 255, 0.5)',
					'text': ' ',
				
				}],
			
		            'yaxis': {'showgrid': True},
					'xaxis': {'showgrid': False , 
					'tickmode' : 'linear',
					'tick0' : dff['year_end'].min(),
					'dtick' : 1},
					'legend_orientation':"h"}
		}
		
        
# time series  
@app.callback(
    dash.dependencies.Output('y-time-series', 'figure'),
    [
	dash.dependencies.Input('county-choropleth', 'clickData'),
     dash.dependencies.Input('crossfilter-var1', 'value'),
	 dash.dependencies.Input('crossfilter-var2', 'value'),
	 dash.dependencies.Input('crossfilter-statistic-column', 'value')])
def update_y_timeseries(selection, var1, var2, stat_name):
	if selection is None:
		country_name = 'AK'								#set AK as default selection of state. State is selected by clicking on the choropleth
	else:
		country_name = selection['points'][0]['text']	
	dff0 = df[df['statecode'] == country_name]					#subset by statecode selected
	dff= dff0[dff0['Statistics_Label'] == stat_name]			#subset by statistics selected from the dropdown
	var1=var1													#variable1 selected from the dropdown menu.
	var2=var2													#variable2 selected from the dropdown menu.
	return create_time_series(dff, var1, var2, country_name)
	


#age bar graph
@app.callback(
    dash.dependencies.Output('bargraph0', 'figure'),
    [dash.dependencies.Input('county-choropleth', 'clickData'),
	 dash.dependencies.Input('crossfilter-statistic-column', 'value')])
def update_graph(selection, stat_name): 
	if selection is None:
		country_name = 'AK'
		#return {}
	else:
		country_name = selection['points'][0]['customdata']
	dff0 = df[df['statecode'] == country_name]
	dff= dff0[dff0['Statistics_Label'] == stat_name]			#subset by statistics selected from the dropdown

	trace1 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='age_0_to_3']['value'], name='0-3' ,marker_color='rgb(22, 150, 210)') 
	trace2 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='age_4_to_5']['value'], name='4-5', marker_color='rgb(253, 191, 17)') 
	trace3 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='age_6_to_8']['value'], name='6-8', marker_color='rgb(210, 210, 210)') 	
	trace4 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='age_9_to_12']['value'], name='9-12',marker_color='rgb(115,191,226)' ) 

	trace5 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='age_13_to_15']['value'], name='13-15', marker_color='rgb(252, 227, 158)') 

	trace6 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='age_16_to_17']['value'], name='16-17', marker_color='rgb(92, 88, 89)') 
	return {
		'data': [trace1, trace2, trace3, trace4, trace5, trace6],
        'layout': {
            'title': 'Age of children in {}'.format(country_name)
        }
    }

#race and ethnicity
@app.callback(
    dash.dependencies.Output('bargraph1', 'figure'),
    [dash.dependencies.Input('county-choropleth', 'clickData'),
	 dash.dependencies.Input('crossfilter-statistic-column', 'value')])
def update_graph(selection, stat_name): 
	if selection is None:
		country_name = 'AK'
	else:
		country_name = selection['points'][0]['customdata']
		
	dff0 = df[df['statecode'] == country_name]			#subsetting for state selected
	dff= dff0[dff0['Statistics_Label'] == stat_name]			#subset by statistics selected from the dropdown
	
	trace1 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='asian']['value'], name='Asian' ,marker_color='rgb(115,191,226)') 
	trace2 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='black']['value'], name='African American',marker_color='rgb(253, 191, 17)' ) 
	trace3 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='hispanic']['value'], name='Hispanic', marker_color='rgb(210, 210, 210)') 
	trace4 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='natamer']['value'], name='Native American', marker_color='rgb(252, 227, 158)') 
	trace5 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='white']['value'], name='White', marker_color='rgb(22, 150, 210)') 
		
	return {
		'data': [trace1, trace2, trace3, trace4, trace5],
        'layout': {
            'title': 'Race  and ethnicity in {}'.format(country_name),

        }
    }


#Origin of parents
@app.callback(
    dash.dependencies.Output('bargraph2', 'figure'),
    [dash.dependencies.Input('county-choropleth', 'clickData'),
	dash.dependencies.Input('crossfilter-statistic-column', 'value')])
def update_graph(selection, stat_name):
	if selection is None:
		country_name = 'AK'
	else:
		country_name = selection['points'][0]['customdata']
	dff0 = df[df['statecode'] == country_name]
	dff= dff0[dff0['Statistics_Label'] == stat_name]			#subset by statistics selected from the dropdown
	
	
	trace0 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='all_children']['value'], name='All Children' ,marker_color='rgb(0, 0, 0)') 
	trace1 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='children_from_europe']['value'], name='Europe' ,marker_color='rgb(22, 150, 210)') 
	trace2 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='children_from_mexico']['value'], name='Mexico',marker_color='rgb(253, 191, 17)' ) 
	trace3 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='children_from_central_america']['value'], name='Central America', marker_color='rgb(210, 210, 210)') 
	trace4 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='children_from_south_america']['value'], name='South America', marker_color='rgb(115,191,226)') 
	trace5 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='children_from_southeast_asia']['value'], name='Southeast Asia', marker_color='rgb(85, 183, 72)') 
	trace6 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='children_from_east_asia']['value'], name='East Asia', marker_color='rgb(232, 142, 45)') 
	trace7 =go.Bar(x=dff['year_end'], y=dff[dff['variable']=='children_from_middle_east']['value'], name='Middle East', marker_color='rgb(252, 227, 158)') 

	return {
		'data': [trace0, trace1, trace2, trace3, trace4, trace5, trace6, trace7],
        'layout': {
            'title': 'Origin of Parents in {}'.format(country_name)
        }
    }	
	

if __name__ == '__main__':
    app.run_server(debug=True)