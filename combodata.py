#!/usr/bin/env python3

import os
import glob
import pandas as pd
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
import math


# paths

onedrive_path = 'C:/Users/tuq67942/OneDrive - Temple University/Documents/'
onedrive_datapath = onedrive_path+'Data/'
desktop = 'C:/Users/tuq67942/Desktop/'
factorpath = desktop+'Factor analysis/'
csvpath = factorpath+'Analysis/csvs/'
PSPCpath = desktop+'R01_PSPC/Analysis/csvs/'
AIpath = desktop+'AI coding code/Storytelling Study data/'

# I need to calculate averages for Q's and stories!
Mausdf = pd.read_csv(factorpath+'MausMemoryY1.csv')

Qlist = ['Hose: Why doesn\'t the hose work?',
       'Hose: What does Ellie do to fix the hose?',
       'Beach: What does Maus do to be able to sit?',
       'Sled: Why doesn\'t Maus want to go up the hill to sled again?',
       'Sled: What does Ellie do to help Maus?',
       'Car: Why can\'t Maus get in the car?',
       'Car: What does Ellie do to help Maus?',
       'Chair: Why can\'t both Maus and Ellie sit?',
       'Chair: What does Ellie do to make the chair fit both of them?',
       'Groceries: Why can\'t Maus and Ellie carry the groceries?',
       'Groceries: What do they do to make the bag lighter?']
FRlist = ['Hose', 'Beach', 'Sled','Car', 'Chair', 'Groceries']
Mausdf['MausQs'] = Mausdf[Qlist].mean(axis=1)
Mausdf['MausFR'] = Mausdf[FRlist].mean(axis=1)
Mausdf = Mausdf[['MDEM ID','MausQs','MausFR']]
Mausdf = Mausdf.rename(columns={'MDEM ID': 'Subject'})

AIdf = pd.read_csv(AIpath+'combodata.csv')
AIdf = AIdf[['Subject','AM','AM_parent','AM_exp']]

KBITdf = pd.read_csv(AIpath+'R01_KBIT_Age_df.csv')
KBITdf = KBITdf[['participant_id','Raw KBIT','KBit_Score','Age (months)','demo_child_gender']]
KBITdf = KBITdf.rename(columns={'participant_id': 'Subject'})

PSdf = pd.read_csv(PSPCpath+'PS_cat_Year_1.csv')
PSdf = PSdf[['Subject','Target','Lure','Foil','object target selection rate', 'object lure selection rate',
       'object foil selection rate', 'location target selection rate',
       'location lure selection rate', 'location foil selection rate',
       'animal target selection rate', 'animal lure selection rate',
       'animal foil selection rate']]
PSdf = PSdf.rename(columns={'object target selection rate':'PSObjTarget', 'object lure selection rate':'PSObjLure',
       'object foil selection rate':'PSObjFoil', 'location target selection rate':'PSLocTarget',
       'location lure selection rate':'PSLocLure', 'location foil selection rate':'PSLocFoil',
       'animal target selection rate':'PSAniTarget', 'animal lure selection rate':'PSAniLure',
       'animal foil selection rate':'PSAniFoil'})
PCdfdet = pd.read_csv(PSPCpath+'PC_pairs_col.csv')
PCdfdet = PCdfdet.rename(columns={'Place->Animal Accuracy':'LocAniLink',
       'Animal->Object Accuracy':'AniObjLink', 'Animal->Place Accuracy':'AniLocLink',
       'Object->Animal Accuracy':'ObjAniLink', 'Place->Object Accuracy':'LocObjLink',
       'Object->Place Accuracy':'ObjLocLink'})
PCdfdet = PCdfdet[['Subject','LocAniLink','AniObjLink','AniLocLink','ObjAniLink','LocObjLink','ObjLocLink']]
PCdf = pd.read_csv(PSPCpath+'Dependency_Year_1.csv')
PCdf = PCdf[['Subject','Dependency','Accuracy']]
PCdf = PCdf.rename(columns={'Accuracy': 'PCAccuracy'})
PCdf = pd.merge(PCdfdet, PCdf, on='Subject',how='outer')

combodf = pd.merge(Mausdf, AIdf, on='Subject',how='outer',indicator=True)
combodf = combodf[combodf['_merge'] != 'right_only'] # removing storytelling kids
combodf = combodf.drop('_merge', axis=1)

combodf = pd.merge(combodf,KBITdf,on='Subject',how='outer',indicator=True)
combodf = combodf.rename(columns={'_merge': 'mergekbit'})

combodf = pd.merge(combodf, PSdf, on='Subject',how='outer', indicator=True)
combodf = combodf.rename(columns={'_merge': 'merge1'})

combodf = pd.merge(combodf, PCdf, on='Subject',how='outer', indicator=True)

combononan = combodf[combodf['_merge'] != 'left_only']
combononan = combononan[combononan['AM'].notna()]
combononan = combononan[combononan['MausQs'].notna()]
combononan = combononan[combononan['KBit_Score'].notna()]
combononan = combononan.drop(['mergekbit','merge1','_merge'], axis=1)
combononannosubj = combononan.drop('Subject', axis=1)

combodf = combodf[combodf['Subject'] != 'TEST']
combodf['has_nan'] = combodf.isnull().any(axis=1)
combodf.to_csv(csvpath+'df_withnan.csv',index=False)
combononan.to_csv(csvpath+'df_withsubj.csv',index=False)
combononannosubj.to_csv(csvpath+'df_nosubj.csv',index=False)

# Download newest demographics spreadsheet from Redcap, and put in this folder
# Add age and sex demographics
demofiles = glob.glob(onedrive_datapath+'R01MarvelousMoments*')
demofile = max(demofiles, key=os.path.getctime)
df = pd.read_csv(demofile).dropna(subset = ['demo_age'])
df = df[['redcap_event_name','session_date','participant_id','demo_age','demo_child_gender','kbit_std_v']]
df = df.dropna(subset = ['session_date'])
df = df[df['redcap_event_name'].str.contains('year1')]
df['Delay'] = df.apply(lambda row: row.session_date > "2023-03-01", axis=1)
df=df.drop(['session_date','redcap_event_name'],axis=1)
df = df.rename({'demo_age': 'Age','participant_id':'Subject'}, axis='columns')

df_all = combononan.merge(df, on=['Subject'],how='left')


# determine delay between session 1 and session 2
df = pd.read_csv(demofile)
df = df[df['redcap_event_name'].str.contains("year1")]
		
delaylist = []
for s in df_all['Subject']:
	dates = list(df[df['participant_id'] == s]['session_date'])
	delay = (datetime.strptime(dates[1], "%Y-%m-%d") - 
			 datetime.strptime(dates[0], "%Y-%m-%d")).days
	delaylist.append({'Subject':s,
					 'Delay (Days)':delay,
					 'Age':math.floor(df_all[df_all['Subject'] == s]['Age'].iloc[0])})
delaydf = pd.DataFrame(delaylist)
combodf = pd.merge(delaydf, combononan, on='Subject',how='outer',indicator=True)
combodf = combodf.drop(['_merge'], axis=1)

sns.set_theme(style="ticks",font_scale=1.5)
f, ax = plt.subplots(figsize=(7, 5))
sns.despine(f)
palette = sns.hls_palette(4)
g = sns.histplot(delaydf,x='Delay (Days)',hue="Age", multiple="stack",binwidth=1,palette=palette)
sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
f.savefig('Figures/Supp3.png', dpi=300,bbox_inches="tight",format='png')

def find_outliers_IQR(df):
	q1=df.quantile(0.25)
	q3=df.quantile(0.75)
	IQR=q3-q1
	outliers = df[((df<(q1-1.5*IQR)) | (df>(q3+1.5*IQR)))]
	return outliers

# determine number of subjects who did each of 3 versions of PSPC
versiondf = pd.read_csv(PSPCpath+'Dependency_Year_1.csv')

versionlist = []
for s in df_all['Subject']:
	delay = versiondf[versiondf['Subject'] == s]['Delay'].iloc[0]
	samed = versiondf[versiondf['Subject'] == s]['Same Day'].iloc[0]
	dates = list(df[df['participant_id'] == s]['session_date'])
	versionlist.append({'Subject':s,
					 'PSPCversion':str(delay)+str(samed)})
pspcversiondf = pd.DataFrame(versionlist)
combodf = pd.merge(pspcversiondf, combodf, on='Subject',how='outer',indicator=True)
combodf = combodf.drop(['Subject','_merge'], axis=1)
combodf['DelayPSPC'] = combodf['Delay (Days)']
filter_ = combodf['PSPCversion'].str.contains('False')
idx = combodf[ filter_ ].index
combodf.loc[idx, "DelayPSPC"] = 0
combodf.to_csv(csvpath+'delaydf.csv',index=False)


combodf = combodf.drop(['Delay (Days)'], axis=1)
combodf = combodf.rename({'DelayPSPC': 'Delay (Days)'}, axis='columns')
# Create a figure displaying all possible delays for PSPC task:
sns.set_theme(style="ticks",font_scale=1.5)
f, ax = plt.subplots(figsize=(7, 5))
sns.despine(f)
palette = sns.hls_palette(4)
g = sns.histplot(combodf,x='Delay (Days)',hue="Age", multiple="stack",binwidth=1,palette=palette)
sns.move_legend(ax, "upper left", bbox_to_anchor=(1, 1))
f.savefig('Figures/Supp4.png', dpi=300,bbox_inches="tight",format='png')




