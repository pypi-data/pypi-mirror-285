# -*- coding: utf-8 -*-


import numpy as np
import matplotlib.pyplot as plt
# from .grand import IndividualAnomalyInductive, IndividualAnomalyTransductive, GroupAnomaly
from .grand.individual_anomaly.individual_anomaly_inductive import IndividualAnomalyInductive
from .grand.individual_anomaly.individual_anomaly_transductive import IndividualAnomalyTransductive
from .grand.group_anomaly.group_anomaly import GroupAnomaly
import pandas as pd
from scipy.stats import norm
from fpdf import FPDF

class AnomalyDetection:

    def __init__(self, w_martingale=15,k=50,non_conformity = "knn", ref_group=["hour-of-day"]):
        self.model = IndividualAnomalyTransductive(
                w_martingale = w_martingale,         # Window size for computing the deviation level
                ref_group = ref_group  # Criteria for reference group construction
                )

    def zscore(self, data, mu, sigma):
        return (data - mu) / sigma

    def deviation_detection(self, data, mu, sigma, l1 = 4, l2 = 8, l3 = 12):
        """
        Deviation detection using zscore \n
        Parameters
        ----------------
            data (pandas.DataFrame): input data in the form of dataframe
            mu (scaler): mean\n
            sigma (scaler): standard deviation\n
            l1: TO DO (default=4)
            l2: TO DO (default=8)
            l3: TO DO (default=12)
        Returns
        -------
            z_s (scaler): z-score
            sigma: standard deviation
        """
        z_s = self.zscore(data,mu, sigma)
        if(len(z_s.shape)>1):
            z_s = z_s[:,0]
        t = np.linspace(0,len(z_s)-1,len(z_s))
        thres1 = l1*sigma
        thres2 = l2*sigma
        thres3 = l3*sigma
        plt.scatter(t[np.where(z_s<=thres1)], z_s[np.where(z_s<=thres1)], color='y', label='Normal', alpha=0.3, edgecolors='none')
        plt.scatter(t[np.where((z_s>thres1) & (z_s<=thres2))], z_s[np.where((z_s>thres1) & (z_s<=thres2))], color='b', label='L1 Threshold', alpha=0.3, edgecolors='none')
        plt.scatter(t[np.where((z_s>thres2) & (z_s<=thres3))], z_s[np.where((z_s>thres2) & (z_s<=thres3))], color='g', label='L2 Threshold', alpha=0.3, edgecolors='none')
        plt.scatter(t[np.where(z_s>thres3)], z_s[np.where(z_s>thres3)], color='r', label='Anomalous points', alpha=0.3, edgecolors='none')
        plt.xlabel('Observation Signal (in samples)')
        plt.ylabel('Anomaly Score')
        plt.title('Anomaly Score Estimation')
        plt.legend()
        return z_s, sigma

    def train_cosmo(self,data, threshold=0.6, w_martingale = 15, non_conformity = "knn",k = 20):
        """
        Dummy text is this. Is it really though.\n
        Parameters
        ----------
            data (pandas.DataFrame): TO DO
            w_martingale (int): TO DO
            non_conformity (string): TO DO (default="median")
            k (int): TO DO (default=20)
        Returns
        -------
            model (object): trained model instance
        """
        df = data
        
        self.model = IndividualAnomalyInductive(
            w_martingale = w_martingale,
            non_conformity = non_conformity,
            k = k)

        # Fit the model to a fixed subset of the data
        X_fit = data.to_numpy()
        self.model.fit(X_fit)
        self.model.dev_threshold = threshold

    def test_cosmo(self, data):
        """
        TO DO some text for the time being.\n
        Parameters
        ----------
            data (pandas.DataFrame): TO DO
        Returns
        -------
            strangeness (pandas.DataFrame): TO DO
            P-values (pandas.DataFrame): TO DO
        """
        cols = ['Strangeness', 'P-Values', 'Deviation']
        lst_dict = []
        df = data
        for t, x in zip(df.index, df.values):
            info = self.model.predict(t, x)
            lst_dict.append({'Strangeness': info.strangeness,
                             'P-Values':info.pvalue,
                             'Deviation':info.deviation})
            
        # Plot strangeness and deviation level over time
        # gr = self.model.plot_deviations(figsize=(12, 8), plots=["strangeness", "deviation", "pvalue", "threshold"])
        
        # strangeness=0.0907913513823968, pvalue=0.2, deviation=0.26, is_deviating=False

        figsize=(12, 8)
        plots=["strangeness", "deviation", "pvalue", "threshold"]
        plots, nb_axs, i = list(set(plots)), 0, 0
        if "data" in plots:
            nb_axs += 1
        if "strangeness" in plots:
            nb_axs += 1
        if any(s in ["pvalue", "deviation", "threshold"] for s in plots):
            nb_axs += 1

        fig, axes = plt.subplots(nb_axs, sharex="row", figsize=figsize)
        if not isinstance(axes, (np.ndarray) ):
            axes = np.array([axes])

        if "data" in plots:
            axes[i].set_xlabel("Time")
            axes[i].set_ylabel("Feature 0")
            axes[i].plot(self.df.index, self.df.values[:, 0], label="Data")
            if debug:
                axes[i].plot(self.model.T, np.array(self.model.representatives)[:, 0], label="Reference")
            axes[i].legend()
            i += 1

        if "strangeness" in plots:
            axes[i].set_xlabel("Time")
            axes[i].set_ylabel("Strangeness")
            axes[i].plot(self.model.T, self.model.S, label="Strangeness")
            # if debug:
            #     axes[i].plot(self.model.T, np.array(self.model.diffs)[:, 0], label="Difference")
            axes[i].legend()
            i += 1

        if any(s in ["pvalue", "deviation", "threshold"] for s in plots):
            axes[i].set_xlabel("Time")
            axes[i].set_ylabel("Deviation")
            axes[i].set_ylim(0, 1)
            if "pvalue" in plots:
                axes[i].scatter(self.model.T, self.model.P, alpha=0.25, marker=".", color="green", label="p-value")
            if "deviation" in plots:
                axes[i].plot(self.model.T, self.model.M, label="Deviation")
            if "threshold" in plots:
                axes[i].axhline(y=self.model.dev_threshold, color='r', linestyle='--', label="Threshold")
            axes[i].legend()

        fig.autofmt_xdate()

        plt.savefig('cosmo.png')
        # pdf = FPDF()

        # Add a page
        # pdf.add_page()
        # pdf.image('cosmo.png')
        # pdf.output("test.pdf") 

        df1 = pd.DataFrame(lst_dict, columns=cols)
        
        return df1['Strangeness'].to_numpy(), df1['P-Values'].to_numpy()


    def test_cosmo_streaming(self, data):
        """
        TO DO some text for the time being.\n
        Parameters
        ----------
            data (pandas.DataFrame): TO DO
        Returns
        -------
            strangeness (pandas.DataFrame): TO DO
            P-values (pandas.DataFrame): TO DO
        """
        cols = ['Strangeness', 'P-Values', 'Deviation']
        lst_dict = []
        df = data
        for t, x in zip(df.index, df.values):
            info = self.model.predict(t, x)
            lst_dict.append({'Strangeness': info.strangeness,
                             'P-Values':info.pvalue,
                             'Deviation':info.deviation})
        df1 = pd.DataFrame(lst_dict, columns=cols)
        
        return df1['Strangeness'].to_numpy(), df1['P-Values'].to_numpy(), df1['Deviation'].to_numpy()
    
    def nonstationary_AD_cosmo(self,data,n=1):
        """
        TO DO Some text for the time being. \n
        Parameters
        ----------
        data (pandas.DataFrame): TO DO 
        n (int): TO DO
        w_martingale (int): TO DO 
        k (int): TO DO
        non_conformity (string): TO DO (default="median")
        ref_group (list(string)): TO DO (default=default=["hour-of-day"])

        Returns
        -------
        df1 (pandas.DataFrame): TO DO 
        gr (plot): TO DO
        """
        

        df = data
        cols = ['Strangeness', 'P-Values', 'Deviation']
        lst_dict = []
        
        info = self.model.predict(df.index[0], df.values[0])
    
        # lst_dict.append({'Strangeness': info.strangeness,
        #                      'P-Values':info.pvalue,
        #                      'Deviation':info.deviation})
        return info.strangeness, info.deviation, info.pvalue
        
        # result = []
        
        # for t, x in zip(df.index, df.values):
        #     info = self.model.predict(t, x)
    
        #     lst_dict.append({'Strangeness': info.strangeness,
        #                      'P-Values':info.pvalue,
        #                      'Deviation':info.deviation})
        #     result.append([info.strangeness, info.deviation, info.pvalue])
        # Plot strangeness and deviation level over time
        # gr = model.plot_deviations(figsize=(12, 8), plots=["strangeness", "deviation", "pvalue", "threshold"])
        
        # df1 = pd.DataFrame(lst_dict, columns=cols)
        
        # return df1, gr

        # return result