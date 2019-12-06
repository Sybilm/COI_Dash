# -*- coding: utf-8 -*-
"""
Created on Thu Nov 14 15:13:52 2019

@author: smendonc
"""

def coi_long_format_from_S3(years):
    """
    
    
    Gets COI data via for a list of years directly from CSV files on AWS S3 bucket, and returns a dataframe with all data in "long" format -- one value per row.
    For use by a data tool or user program, we need a dataframe in a format somewhat like this::
    
         i	statecode	year_end	variable	value
         0	AK	        2015	all_children	186000
         1	AL	        2015	all_children	1107000
         2	AR	        2015	all_children	707000
         3	AZ	        2015	all_children	1621000
         4	CA	        2015	all_children	9127000
         5	CO	        2015	all_children	1252000
         
    
        
    also we'll add other things like variable_label, statid, statistics_label, etc.    
    
    Parameters:
                -`years`: List of integer years, one for each year to return data for
            
    Returns: 
        `Dataframe` object with all data for years requested.
    
    """
    import os
#    os.chdir("D://python//coi//DKAN/")
    
    import pandas as pd
    import datetime as dt
    import time
    import gc

    start_time = time.time()
    start_time_formatted = dt.datetime.now()
    print("Starting at ...",start_time_formatted)
    s3_string = "https://urban-coi.s3.amazonaws.com/COI_data_state_level_"
    dfs = {}
    for year in years:
        # =====================================================================================
        # get the data from S3 instead
        yearindex = str(year)
        mys3file = s3_string + yearindex + ".csv"
        print(mys3file)
        dfs[yearindex] = pd.read_csv(mys3file)
        # =====================================================================================
    
    # =====================================================================================
    # append into one big df
    # df = pd.concat(list_of_dataframes)
    d_all   = pd.concat(dfs)
  #  d_all["text"]= d_all.apply(lambda row: "All children: " + str(int(row["all_children"])) + " Immigrant ch: " + str(d_all["imm_children"]), axis=1)
    #d_all["text"] = "All children: " + str(d_all["all_children"]) 
    #+ " Immigrant ch: " + str(d_all["imm_children"])
    #print(d_all["text"])
    
    d_all_T = pd.melt(d_all, id_vars=['statecode', 'year_end','Statistics_Label', 'StatID','share', 'number'], value_vars=['all_children', 'imm_children', 'nat_children', 'children_imm_parents', 'children_native_parents', 'children_unknown_parents', 'second_gener', 'fb_children_imm_parents', 'nb_children_nb_parents', 'noncitizen_prt', 'citizen_prt', 'citizen_children_noncit_parents', 'noncit_children_noncit_parents', 'cit_children_cit_parents', 'children_from_europe', 'children_from_mexico', 'children_from_central_america', 'children_from_south_america', 'children_from_southeast_asia', 'children_from_east_asia', 'children_from_middle_east', 'children_prts_from_africa', 'hispanic', 'black', 'asian', 'white', 'natamer', 'othmult', 'age_0_to_3', 'age_4_to_5', 'age_6_to_8', 'age_9_to_12', 'age_13_to_15', 'age_16_to_17', 'below_pov', 'above_pov','low_income',             'high_income', 'children_liwf_imm_prts', 'children_liwf_native_prts', 'nofamdis', 'hasfamdis', 'novehic', 'hasvehic', 'noprtvets', 'hasprtvets','not_hcb', 'hcb_any' ])
    # =====================================================================================
    
    # =====================================================================================
    # Finally, merge on the variable label from the variable metadata
    # get all the variable meta data
    df_vars_meta = pd.read_csv("https://urban-coi.s3.amazonaws.com/variables_ref_v3.csv") 
    
    # make a new df with only ‘Variable’ and ‘variable_label’ as columns
    dfvmeta = df_vars_meta.loc[:,['Variable','variable_label']]
    
    # merge that into the main df
    d_all_T_merged = d_all_T.merge(dfvmeta, left_on='variable', right_on='Variable')
    d_all_T_merged.drop(columns=['Variable'])
    # =====================================================================================
    
    
    elapsed_time = time.time() - start_time
    
    print("Started at :",start_time_formatted)
    print("Ended at   :",dt.datetime.now())
    print("Elapsed time:",elapsed_time)
    
    #release the memory
    #del [[d_all,dfvmeta]]
    #del [dfs]
    #gc.collect()
    
    return d_all, d_all_T_merged
    
#df_orig, df0=coi_long_format_from_S3([2014, 2015, 2016, 2017])



#df01=df0[["variable", "variable_label"]].drop_duplicates()

#d = df01.set_index('variable').to_dict()

#d["variable_label"].update({'data_sort_id':'data_sort_id', 'metrocode':'metrocode', 'statecode':'statecode', 'Statistics_Label':'Statistics_Label', 'StatID':'StatID', 'year_start':'year_start',
#  'year_end':'year_end',     'share':'share',     'number':'number', 'CategoryID':'CategoryID',
#'CategoryName':'CategoryName',
#'CategorySortOrder':'CategorySortOrder',
#'CategorySortOrderName':'CategorySortOrderName',
#'prtUS5pyrs':'prtUS5pyrs',
#'prtUSLT5yrs':'prtUSLT5yrs',
#'Statistics_Label_short':'Statistics_Label_short'
#})
 
#df_orig.columns = df_orig.columns.to_series().map(d['variable_label'])    
#Example: https://stackoverflow.com/questions/36531675/rename-columns-in-pandas-based-on-dictionary


#a.to_csv("D:/py_dash/COI/COI_Dash/alldata2.csv")
#b.to_csv("D:/py_dash/COI/COI_Dash/Orig_data2.csv")
#a_test=a[a['variable'] =='age_0_to_3']
