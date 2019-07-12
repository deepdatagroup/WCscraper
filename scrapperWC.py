# -*- coding: utf-8 -*-
"""
Created on Fri Jul 27 13:05:50 2018

@author: JHON PARRA-PC
"""
###CODE TO SCRAP FROM FIFA WC BRAZIL 2014 ACHIVE FILE  
### CELSIA
### DATA SCIENTIST TEST

import pandas as pd
from bs4 import BeautifulSoup
import requests
import csv
import pandas as pd
import numpy as np
import re

##THE WEBSITE HAS A PATTERN IN WORLD CUP RESULTS: "https://www.fifa.com/worldcup/archive/"+lowercase_country+year+"/matches/index.html". SO IF WE CREATE A VECTOR WITH ALL THE WORLD CUP PLACES-YEAR, WOULD BE POSSIBLE TO
##BUILD A FUNCTION THAT RETRIEVES ALL THIS INFORMATION.
#
#object.prettify() allows to see the html page as a tree-based code. Its easier and faster to get the patterns where data is allocated.
#print(page.prettify())

####################################################CONCLUSIONS FROM INSPECTION OF THE HTML CODE######################################.

#*HOME TEAMS IN EVERY GAME ARE LABELED AS "t home"
#*AWAY TEAM IN EVERY GAME ARE LABELED AS "t away"
#*STADIUMS ARE LABELED AS mu-i-stadium.
# AFTER FIRST ROUND, THERE MUST BE A WINNER SO THEY DETAIL OF HOW A TEAM WON IS LABELED AS mu-reasonwin
#WCscrapper is a function that returns a pd.DataFrame with information from the world cup needed "placeyear": eg. WCscrapper(italy1990).

def WCscrapper(placeyear):
    url_fifa="https://www.fifa.com/worldcup/archive/"+ placeyear +"/matches/index.html"
    page_raw = requests.get(url_fifa)
    page = BeautifulSoup(page_raw.text, 'html.parser')
    m_number=page.find_all(class_="mu-i-matchnum")
    n_rows=len(m_number)
    home=page.find_all("div",{'class':['t home']})  
    away=page.find_all("div",{'class':['t away']})
    score=page.find_all(class_="s-scoreText")
    det=page.find_all(class_="mu-reasonwin")
    pla=page.find_all(class_="mu-i-stadium")
    dataWC=pd.DataFrame(columns=['home','away','score','match_number','place','detail'])
    for i in range(n_rows):
        h=home[i].getText()[-3:]
        a=away[i].getText()[-3:]
        s=score[i].getText()
        n=m_number[i].getText()
        d=det[i].getText()
        p=pla[i].getText()
        dataWC.loc[i]={'home':h,'away':a,'score':s,'match_number':n,'place':p,'detail':d}
## DUE TO THE WEBSITE STRUCTURE, RIGHT IN THE MIDDLE THERE WAS A SNIPPET WHICH WAS DUPLICATING RESULTS, SO WE DELETE THESE RECORDS WITH THE NEXT
## drop.duplicates() FUNCTION
## WE ADD COLUMNS TO DETERMINE HOW MANY GOALS WERE SCORED BY HOME AND VISITOR TEAM, AS WELL AS WHO WON THE MATCH GIVEN ALL POSSIBILITIES (PENALTY SHOOTOUT-EXTRA TIME GOALS)        
    dataWC.drop_duplicates(keep='last')
    dataWC['WC']=np.repeat(placeyear,len(dataWC['home']))
    success = False
    while not success:
        try:
            dataWC['detWinner']=dataWC['detail'].str.split("(").str[1].str[:5].str.split("-").str[0].astype(float)-dataWC['detail'].str.split("(").str[1].str[:5].str.split("-").str[1].astype(float) #TO DETERMINE WETHER A MATCH THAT ENDED AS TIE AFTER 120 MIN HAD A WINNER BY PENALTY SHOOTOUT
            success = True
        except:
            dataWC['detWinner']=0 
            success=True
    
    dataWC['score']=dataWC['score'].astype(str)
    dataWC['goalH']=dataWC['score'].str.split('-').str[0].astype(int)
    dataWC['goalA']=dataWC['score'].str.split('-').str[1].astype(int)
    dataWC['winner']="H"
    dataWC.loc[dataWC['goalH']<dataWC['goalA'],'winner']="V"
    dataWC.loc[dataWC['goalH']==dataWC['goalA'],'winner']="D"
    dataWC.loc[(dataWC['winner']=="D") & (dataWC['detWinner']>0),'winner']="H"
    dataWC.loc[(dataWC['winner']=="D") & (dataWC['detWinner']<0),'winner']="V"
    del dataWC['detWinner']
    print(placeyear + '...done')

    return dataWC

WCscrapper("koreajapan2002") ##Example of how it works individually


def RussiaScrapper(placeyear):
    url_fifa=placeyear
    page_raw = requests.get(url_fifa)
    page = BeautifulSoup(page_raw.text, 'html.parser')
    m_number=page.find_all(class_="fi__info__matchnumber")
    n_rows=len(m_number)
    home=page.find_all("div",{'class':['fi-t fi-i--4 home']})  
    away=page.find_all("div",{'class':['fi-t fi-i--4 away']}) 
    score=page.find_all(class_="fi-s__scoreText")
    det=page.find_all(True,{'class':['fi-mu__reasonwin-wrap']})
    pla=page.find_all(class_="fi__info__stadium")
    dataWC=pd.DataFrame(columns=['home','away','score','match_number','place','detail'])
    for i in range(n_rows):
        h=home[i].getText()[-5:-2]  
        a=away[i].getText()[-5:-2]  
        s=score[i].getText()[2:5]
        n=re.sub('[\n]',' ', m_number[i].getText())[1:9]
        final=False
        while not final:
            try:
                d=det[i].getText().split("\r\n")[1]
                final=True
            except:
                d=det[i].getText()
                final=True
        p=pla[i].getText()
        dataWC.loc[i]={'home':h,'away':a,'score':s,'match_number':n,'place':p,'detail':d}
    dataWC.drop_duplicates(keep='last')
    dataWC['WC']=np.repeat("russia2018",len(dataWC['home']))
    success = False
    while not success:
        try:
            dataWC['detWinner']=dataWC['detail'].str.split("(").str[1].str[:5].str.split("-").str[0].astype(float)-dataWC['detail'].str.split("(").str[1].str[:5].str.split("-").str[1].astype(float) #TO DETERMINE WETHER A MATCH THAT ENDED AS TIE AFTER 120 MIN HAD A WINNER BY PENALTY SHOOTOUT
            success = True
        except:
            dataWC['detWinner']=0 
            success=True
    
    dataWC['score']=dataWC['score'].astype(str)
    dataWC['goalH']=dataWC['score'].str.split('-').str[0].astype(int)
    dataWC['goalA']=dataWC['score'].str.split('-').str[1].astype(int)
    dataWC['winner']="H"
    dataWC.loc[dataWC['goalH']<dataWC['goalA'],'winner']="V"
    dataWC.loc[dataWC['goalH']==dataWC['goalA'],'winner']="D"
    dataWC.loc[(dataWC['winner']=="D") & (dataWC['detWinner']>0),'winner']="H"
    dataWC.loc[(dataWC['winner']=="D") & (dataWC['detWinner']<0),'winner']="V"
    del dataWC['detWinner']
    print(placeyear + '...done')
    return dataWC

##SHOWS HOW IT RETRIEVES RUSSIA WC INFORMATION
RussiaScrapper("https://www.fifa.com/worldcup/matches/?#groupphase")
               
##APPLY FUNCTION TO A LIST OF WORLDCUPS

wc_list=pd.DataFrame(['uruguay1930','italy1934','france1938','brazil1950','switzerland1954','sweden1958','chile1962','england1966','mexico1970','germany1974','argentina1978','spain1982','mexico1986','italy1990','usa1994','france1998','koreajapan2002','germany2006','southafrica2010','brazil2014'],columns=['WC'])

dataWC_ALL=pd.DataFrame()

for i in range(len(wc_list)):
   if i==0:
       dataWC_ALL=WCscrapper(wc_list['WC'][i])
   else:
       dataaux=WCscrapper(wc_list['WC'][i])
       dataWC_ALL=dataWC_ALL.append(dataaux)

###ADDS RUSSIA 2018 INFO  
dataWC_ALL=dataWC_ALL.append(RussiaScrapper("https://www.fifa.com/worldcup/matches/?#groupphase"))

#REPLACE FEDERAL GERMANY FOR GERMANY (GER)
dataWC_ALL['home'] = dataWC_ALL['home'].replace(['FRG'], 'GER')                                            
dataWC_ALL['away'] = dataWC_ALL['away'].replace(['FRG'], 'GER')                                            

###EXPORT DATAFRAME TO CSV    

dataWC_ALL.to_csv("WC_DATA.txt", sep=';', encoding='utf-8')

########################################################QUESTIONS################################################################
########1
###A. What is the probability that more than 3 goals are scored in a single match? 
((dataWC_ALL['goalH']+dataWC_ALL['goalA'])>3).mean()

###B. How true is the saying (take into account that the berlin wall was destroyed in 1989):


#Brazil Probability of winning
dataWC_ALL['brWin']=False
dataWC_ALL.loc[((dataWC_ALL['home']=='BRA') & (dataWC_ALL['winner']=='H')) | ((dataWC_ALL['away']=='BRA') & (dataWC_ALL['winner']=='V')),'brWin']=True

br_array=dataWC_ALL[(dataWC_ALL['home'] == "BRA") | (dataWC_ALL['away'] == "BRA") ]
br_array['brWin'].mean()


#Germany Probability of winning

dataWC_ALL['grWin']=False
dataWC_ALL.loc[((dataWC_ALL['home']=='GER') & (dataWC_ALL['winner']=='H')) | ((dataWC_ALL['away']=='GER') & (dataWC_ALL['winner']=='V')),'grWin']=True

gr_array=dataWC_ALL[(dataWC_ALL['home'] == "GER") | (dataWC_ALL['away'] == "GER")]
gr_array['grWin'].mean()

#Another team facing Brazil or Germany

dataWC_ALL['bgWin']=False
dataWC_ALL.loc[((dataWC_ALL['home']=='BRA') & (dataWC_ALL['winner']=='H')) | ((dataWC_ALL['away']=='BRA') & (dataWC_ALL['winner']=='V')) | ((dataWC_ALL['home']=='GER') & (dataWC_ALL['winner']=='H')) | ((dataWC_ALL['away']=='GER') & (dataWC_ALL['winner']=='V')),'bgWin']=True

#remove matches when Brazil faces Germany or viceversa
gr_array=dataWC_ALL[((dataWC_ALL['home'] == "BRA") | (dataWC_ALL['away'] == "BRA") | (dataWC_ALL['home'] == "GER") | (dataWC_ALL['away'] == "GER")) & (((dataWC_ALL['home'] == "GER") & (dataWC_ALL['away'] != "BRA")) | ((dataWC_ALL['home'] == "BRA") & (dataWC_ALL['away'] != "GER")))]
1-gr_array['bgWin'].mean()

#######2. in matches between teams from America and Europe:

# A. Who is more likely to win? 

#remove matches where Asia/Africa/Oceania countries stack-up
#we add a file that contains all FIFA abbreviations and its continent, so we can filter easily
 