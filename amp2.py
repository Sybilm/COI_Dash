     	#us map2
	html.Div(
	 id="heatmap-container2",
	 children=[ dcc.Graph(
                                    id="county-choropleth_test",
									hoverData={'points': [{'customdata': 'AK'}]},
                                    figure=dict(
                                        data=[
                                            dict(
                                                lat=df["latitude"],
                                                lon=df["longitude"],
                                                text=df["statecode"],
                                                type="scattergeo",
										        locationmode = 'USA-states',
												mode = 'markers',
												marker = dict(
													size = 8,
													opacity = 0.8,
													reversescale = True,
													autocolorscale = False,
													symbol = 'square',
													line = dict(
														width=1,
														color='rgba(102, 102, 102)'
													),
												colorscale = scl,
												cmin = 0,
												color = df['value'],
												cmax = df['value'].max(),
												colorbar=dict(
													title="Incoming flightsFebruary 2011"
												)	
													
													
                                            ))
                                        ],
                                        layout=dict(
											colorbar = True,
											
                                            geo=dict(
													scope='usa',
													projection=dict( type='albers usa' ),
													showland = True,
													landcolor = "rgb(250, 250, 250)",
													subunitcolor = "rgb(217, 217, 217)",
													countrycolor = "rgb(217, 217, 217)",
													countrywidth = 0.5,
													subunitwidth = 0.5
													),
											)
											))]),
