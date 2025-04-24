#!/usr/bin/env python3

# Compare Histograms between subjects included in factor analysis and those with missing data:

import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

desktop = 'C:/Users/tuq67942/Desktop/'
factorpath = desktop+'Factor analysis/'
csvpath = factorpath+'Analysis/csvs/'
combodf = pd.read_csv(csvpath+'df_withnan.csv')

combodf = combodf.rename(columns={'Dependency': 'Holistic\nRecollection',
                        'PCAccuracy':'Relational\nBinding',
                        'Target':'Mnemonic\ndiscrimination\n(Target)',
                        'MausQs':'Probed\nQuestion\nAccuracy',
                        'MausFR':'Free\nRecall\nAccuracy',
                        'AM':'Autobiographical\nMemory',
                        'Foil':'Mnemonic\ndiscrimination\n(Foil)',
                        'Lure':'Mnemonic\ndiscrimination\n(Lure)',
                        'KBit_Score': 'IQ',
                        'Delay (Days)': 'Delay','has_nan':'Missing Data'})
cols = ['Age (months)','Relational\nBinding','Mnemonic\ndiscrimination\n(Target)',
                   'Probed\nQuestion\nAccuracy',
                   'Free\nRecall\nAccuracy','Autobiographical\nMemory','IQ',
                   'Holistic\nRecollection']
f, axes = plt.subplots(2, 4, figsize=(13, 12))
for i,c in enumerate(cols):
	row = i // 4
	col = i % 4
	sns.set_theme(style="ticks",font_scale=1)
	#f, ax = plt.subplots(figsize=(7, 5))
	sns.despine(f)
	palette = sns.hls_palette(2)
	g = sns.histplot(combodf,x=c,hue='Missing Data', multiple="stack",palette=palette,ax=axes[row,col])
	if i ==7:
		sns.move_legend(axes[row,col], "upper left", bbox_to_anchor=(1, 1))
	else:
		g.legend([],[], frameon=False)
f.savefig('Figures/Supp_missinghists.png', dpi=300,bbox_inches="tight",format='png')