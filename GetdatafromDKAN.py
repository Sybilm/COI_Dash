# -*- coding: utf-8 -*-
"""
Created on Wed Nov  6 09:09:54 2019

@author: smendonc
"""
import pandas as pd

def get_coi_data(statids,years):
    import pandas as pd
    import requests
    import re
    
    recs_sofar = 0
    
    # make initial request to the DKAN API
    # filtering for a list of statids
    # put resulting records in pd dataframe
    #
    # Note: we're leaving out the fields[] parameter, as the default is all fields in original order
    #       there were problems passing in specific multiple field names
    #
       

    
    # define a dictionary of program resourceids by dataset years in the COI catalog entry
    mydata_resources = {'2015'       :'952ed020-84e9-4898-9beb-9329df5f078c',
                        '2016'       :'063eb46a-faa8-45f1-9e47-3570ecb25fdd',
                        '2017'       :'0e76edbe-91c5-453a-b166-e9b73a1b3e9f'}       
#
#    print ('Program name is: ',mydatarequest)
#    if ( mydatarequest == "ERROR"):
#        print("Error, invalid statid:", statid)
#        return()
#    
    
    dfs = {}
    
    myurl = 'https://datacatalog.urban.org/api/action/datastore/search.json'
    for year in years:
        yearindex = str(year)
        myresource_id = mydata_resources[yearindex]
        myparams = {'resource_id': myresource_id,
                  'sort[statid]':'asc',                
                  'sort[statecode]': 'asc',
                  'filters[statid]': '103',
                  'limit': 100,
                  'offset': 0
                  }
        mystring = re.sub("\[|\]| ", "", str(statids))  #remove "[", "]"
        myparams['filters[statid]'] = mystring          #stringified list is used as filter
        
        # make the initial request
        r = requests.get(url = myurl,params = myparams)
        x = r.json()
        #print ( r.url )
        dfs[yearindex] = pd.DataFrame(x['result']['records'])
        totalrecs = x['result']['total']
        recswegot = len(x['result']['records'])
        recs_sofar = recs_sofar + recswegot
        # end initial request
        
        # keep making requests until we get all the data for the statid
        while ( recs_sofar < totalrecs) :
            myparams['offset'] = myparams['offset'] + recswegot
            r = requests.get(url = myurl,params = myparams)
            x = r.json()       
            dfs[yearindex] = dfs[yearindex].append(x['result']['records'])
            recs_sofar = recs_sofar + len(x['result']['records'])
        #ok, done
    
    print('Total recs for statids:',totalrecs)
    print('Total retrieved       :',recs_sofar)    
    return(dfs)
    
#  get_COI_meta(statid)
a=get_coi_data(1,[2015,2016, 2017])
#dfs.head()

d_15=a['2015']
d_16=a['2016']
d_17=a['2017']

d_all0 =d_15.append(d_16)
d_all=d_all0.append(d_17)
d_all['year_end'].unique()
#text for map
#d_all['text'] = d_all['all_children'] + d_all['below_pov'] + d_all['children_imm_parents']




d_all_T = pd.melt(d_all, id_vars=['statecode', 'year_end'], value_vars=['all_children', 'imm_children', 'nat_children', 'children_imm_parents', 'children_native_parents', 'children_unknown_parents', 'second_gener', 'fb_children_imm_parents', 'nb_children_nb_parents', 'noncitizen_prt', 'citizen_prt', 'citizen_children_noncit_parents', 'noncit_children_noncit_parents', 'cit_children_cit_parents', 'children_from_europe', 'children_from_mexico', 'children_from_central_america', 'children_from_south_america', 'children_from_southeast_asia', 'children_from_east_asia', 'children_from_middle_east', 'children_prts_from_africa', 'hispanic', 'black', 'asian', 'white', 'natamer', 'othmult', 'age_0_to_3', 'age_4_to_5', 'age_6_to_8', 'age_9_to_12', 'age_13_to_15', 'age_16_to_17', 'below_pov', 'above_pov','low_income',	'high_income', 'children_liwf_imm_prts', 'children_liwf_native_prts', 'nofamdis', 'hasfamdis', 'novehic', 'hasvehic', 'noprtvets', 'hasprtvets', 	'not_hcb', 'hcb_any'])

