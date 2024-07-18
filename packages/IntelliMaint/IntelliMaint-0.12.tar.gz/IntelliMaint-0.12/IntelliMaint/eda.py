#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#%% Import Libraries
import os
import numpy as np 
import pandas as pd
import matplotlib.pyplot as plt
#plt.rcParams['figure.figsize'] = (10.0, 8.0)
import seaborn as sns
from scipy import stats
from scipy.stats import norm
from fpdf import FPDF
import IntelliMaint

package_dir_path = os.path.dirname(IntelliMaint.__file__)

#%% Exploratory Analysis Class
class ExploratoryAnalysis:
    
    @classmethod
    def perform_eda(cls, data):
        """
        Perform Exploratory Data Analysis.
        Parameters
        ----------
            data (pandas.DataFrame): input data in dataframe format
        Returns
        -------
            basic_stats_df (pandas.DataFrame): basic statistical info
            skewness_df (pandas.DataFrame): skewness values
            kurt_df (pandas.DataFrame): kurtosis values
        """
        pdf = FPDF()

        # Add a page
        pdf.add_page()
        pdf.set_font("Arial", size = 8)

        pdf.cell(200, 10, txt = "------------------------------------", 
        ln = 1, align = 'C')
        pdf.cell(200, 10, txt = "Performing Exploratory Data Analysis", 
        ln = 1, align = 'C')
        pdf.cell(200, 10, txt = "------------------------------------", 
        ln = 1, align = 'C')
        pdf.cell(200, 10, txt = "The train data has "+str(data.shape[0])+" rows and "+str(data.shape[1])+" columns", 
        ln = 1, align = 'C')
        
        print('------------------------------------')
        print("Performing Exploratory Data Analysis")
        print('------------------------------------')
        print("")
        #print("")
        print ('The train data has {0} rows and {1} columns'.format(data.shape[0], data.shape[1]))
        print("")

        
        def basic_stats():
            global basic_stats_df
            pdf.cell(200, 10, txt = "Descriptive Statistics", 
            ln = 1, align = 'C')
            pdf.cell(200, 10, txt = '----------------------', 
            ln = 1, align = 'C')
            print("Descriptive Statistics")
            print('----------------------')
            bs = data.describe()
            basic_stats_df = bs
            print(bs)
            pdf.cell(200, 10, txt = str(bs), 
            ln = 1, align = 'C')
            #print("")
            #return(bsf)
        
        def missing_value_plot():
            print("Missing Value Analysis")
            print('----------------------')
            pdf.cell(200, 10, txt = "Missing Value Analysis", 
            ln = 1, align = 'C')
            pdf.cell(200, 10, txt = '----------------------', 
            ln = 1, align = 'C')
            k = data.columns[data.isnull().any()]
            
            
            #visualising missing values
            if len(k) == 0:
                print("Hurray !!! No Missing Values")
                pdf.cell(200, 10, txt = "Hurray !!! No Missing Values", 
                ln = 1, align = 'C')
            else:
                print("Oops!! Some Values are missing, checkout the plot")
                pdf.cell(200, 10, txt = "Oops!! Some Values are missing, checkout the plot", 
                ln = 1, align = 'C')
                plt.figure()
                miss = data.isnull().sum()/len(data)
                miss = miss[miss > 0]
                miss.sort_values(inplace=True)
                miss = miss.to_frame()
                miss.columns = ['count']
                miss.index.names = ['Name']
                miss['Name'] = miss.index
    
                #plot the missing value count
                sns.set(style="whitegrid", color_codes=True)
                sns.barplot(x = 'Name', y = 'count', data=miss)
                plt.xticks(rotation = 90)
                #plt.show()
                
                
        def skewness_calc():
            global skewness_df
            print("")
            print('Skewness Analysis')
            print('-----------------')

            pdf.cell(200, 10, txt = 'Skewness Analysis', 
            ln = 1, align = 'C')
            pdf.cell(200, 10, txt = '----------------------', 
            ln = 1, align = 'C')

            sk = data.skew(axis = 0, skipna = True)
            sk = sk.to_frame()
            sk.columns = ["Skewness_Value"]
            skewness_df = sk
            print(sk)
            pdf.cell(200, 10, txt = str(sk), 
            ln = 1, align = 'C')
        def kurtosis_calc():
            global kurt_df
            print("")
            print('Kurtosis Analysis')
            print('-----------------')

            pdf.cell(200, 10, txt = 'Kurtosis Analysis', 
            ln = 1, align = 'C')
            pdf.cell(200, 10, txt = '----------------------', 
            ln = 1, align = 'C')

            kr = data.skew(axis = 0, skipna = True)
            kr = kr.to_frame()
            kr.columns = ["Kurtosis_Value"]
            kurt_df = kr
            print(kr)
            pdf.cell(200, 10, txt = str(kr), 
            ln = 1, align = 'C')

        def distribution_check():#assuming last column is the target variable
            #plt.figure()
            num = [f for f in data.columns if data.dtypes[f] != 'object']
            nd = pd.melt(data, value_vars = num)
            sns.set(font_scale=1)

            def dist_meanplot(x, **kwargs):
                sns.distplot(x, hist_kws=dict(alpha=0.3))
                plt.axvline(x.mean(),  color = 'red', label = str("mean: {:.2f}".format(x.mean())))
                plt.axvline(x.median(),linestyle ='--' , color = 'g',label = str("median: {:.2f}".format(x.median())))
                #plt.axvline(x.mode(),  color = 'o', label = str("mode: {:.2f}".format(x.mode())))

            g = sns.FacetGrid(nd, col="variable" ,col_wrap=2, sharex=False, sharey = False)
            g.map(dist_meanplot, "value").set_titles("{col_name}")
            for ax in g.axes.ravel():
                ax.legend(loc='best', fontsize = 'x-small')
            plt.tight_layout()
            plt.savefig('dist.png')
            # plt.show()    
            
        def correlation_check():
            plt.figure()
            corr = data.corr()
            mask = np.zeros_like(corr)
            mask[np.triu_indices_from(mask)] = True
            with sns.axes_style("white"):
                ax = sns.heatmap(corr,linewidths=.5, mask=mask, cmap="YlGnBu",annot=True)
                bottom, top = ax.get_ylim()
                ax.set_ylim(bottom + 0.5, top - 0.5)
                #ax.set_xlim(xmin=0.0, xmax=1000)

            plt.title('Correlation Graph')
            plt.tight_layout()
            # plt.show()
            plt.savefig('corr.png')
        

#        missing_values()
        #return(basic_stats()) 
        basic_stats()
        missing_value_plot()
        skewness_calc()
        kurtosis_calc()
        distribution_check()
        correlation_check()
        pdf.image('dist.png')
        pdf.image('corr.png')
        pdf.output("test.pdf") 
        return(basic_stats_df,skewness_df,kurt_df)