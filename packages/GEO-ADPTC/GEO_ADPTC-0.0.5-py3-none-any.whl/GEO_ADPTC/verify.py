import numpy as np
import pandas as pd
from pyclustertend import hopkins, ivat, vat
from .auxiliary import *
from sklearn.metrics import calinski_harabasz_score, davies_bouldin_score, silhouette_score
 
def create_statistic_table(clus_res,filePath=''):
    '''
        Information on the attributes of the elements in each category is counted according to the clustering results:
            total number of elements,  minimum,mean, median, maximum, and standard deviation.
    '''
    labels = clus_res['labels']
    sample_array = clus_res['sample_array']
    statistic_table=pd.DataFrame(columns=['label_id','sum','min','mean','mid','max','std'])
    label_num = np.unique(labels)
    for inx, val in enumerate(label_num):
        attr = sample_array[np.where(labels==val)][:,3]
        sum = len(attr)
        mean = np.mean(attr)
        mid = np.median(attr)
        std = np.std(attr)
        min = np.min(attr)
        max = np.max(attr)
        statistic_table.loc[inx] = [val,sum,min,mean,mid,max,std]
        pass
    if(filePath!=''):
        statistic_table.to_excel(filePath)
        pass
    return statistic_table


def CH_index(clus_res):
    '''
        Compute the Calinski and Harabasz score.
        https://scikit-learn.org/stable/modules/clustering.html#calinski-harabasz-index
    '''
    X = clus_res['data']
    labels = clus_res['labels']
    if "sample_array" in clus_res.keys():
        X = clus_res['sample_array']
    return calinski_harabasz_score(X,labels)

def DB_index(clus_res):
    '''
        Compute the Davies-Bouldin score.
    '''
    X = clus_res['data']
    labels = clus_res['labels']
    if "sample_array" in clus_res.keys():
        X = clus_res['sample_array']
    return davies_bouldin_score(X,labels)    

def Silhouette_Score(clus_res):
    '''
        Compute the mean Silhouette Coefficient of all samples.
    '''
    X = clus_res['data']
    labels = clus_res['labels']
    if "sample_array" in clus_res.keys():
        X = clus_res['sample_array']
    return silhouette_score(X,labels)