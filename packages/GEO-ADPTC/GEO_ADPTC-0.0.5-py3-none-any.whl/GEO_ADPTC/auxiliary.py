__package__='GEO_ADPTC'
import time

import numpy as np
import xarray as xr
from scipy.spatial.distance import pdist, squareform
from pyclustertend import hopkins, ivat, vat

def fn_timer(*args,**kwargs):
    '''
        used to calculate the running time of a function.
    '''
    def mid_fn(function):
        def function_timer(*in_args, **kwargs):
            t0 = time.time()
            result = function(*in_args, **kwargs)
            t1 = time.time()
            print (" %s: %s seconds" %
                (args[0], str(t1-t0))
                )
            return result
        return function_timer
    return mid_fn


 
def calc_hopkins(X,sampling_size):
    '''
        Evaluation of data clustering trends by calculating hopkins statistic.
    '''
    tend = hopkins(X,sampling_size)
    return 1-tend

def draw_vat(X):
    '''
        VAT means Visual assesement of tendency. basically, it allow to asses cluster tendency
        through a map based on the dissimiliraty matrix.
    '''
    vat(X)
    pass

def _draw_ivat(X):
    ivat(X)
    pass




def calc_dist_matrix(data,metric='euclidean'):
    '''
        Similarity/Distance metric function
    '''
    dist_mat = squareform(pdist(data, metric=metric))
    return dist_mat


def get_near_matrix(eps,matrix_dist):
    '''
        Get proximity matrix.
    '''
    near_matrix = {}
    rows = matrix_dist.shape[0]
    for i in range(rows):
        near_matrix[i] = np.where(matrix_dist[i]<eps)[0]
    return near_matrix


def rasterArray_to_sampleArray(data):
    '''
        Convert two-dimensional grid data to sample point table, each grid as a sample point
    '''
    rows,cols = data.shape
    data_all = np.zeros((rows*cols,3))
    num = 0
    for i in range(rows):
        for j in range(cols):
            data_all[num,:] = [i,j,data[i,j]]
            num+=1
            pass
        pass
    data_all[:,[0,1]]=data_all[:,[1,0]]
    # not_none_pos = np.where(data_all[:,2]!=0)[0] #* 去除零值后的数据，在全局的位置 [638,629,1004,……] 值为 data_all数据下标
    not_none_pos = np.where(~np.isnan(data_all[:,2]))[0] #* 获取 值为 nan 的下标
    
    # not_none_pos = np.setdiff1d(not_none_pos,nan_pos)
    data_not_none = data_all[not_none_pos]
    pos_not_none = np.full((rows*cols),-1,dtype=np.int64) #* 全局数据中，不为零的下标[-1,-1,0,-1,1,-1,2,3,4,……] 值为 data_not_none 下标
    pos_not_none[not_none_pos] = np.array(range(len(not_none_pos)))
    return data_not_none,pos_not_none



def rasterCube_to_sampleArray(data):
    '''
        Convert three-dimensional space-time cube to sample point table, each cell as a sample point
    '''
    times,rows,cols = data.shape
    data_not_none = np.zeros((times*rows*cols,4))
    data_all = np.zeros((times*rows*cols,4))
    num = 0
    for i in range(rows):
        for j in range(cols):
            for k in range(times):
                data_all[num,:] = [i,j,k,data[k,i,j]]
                num+=1
            pass
        pass
    # data[:,[0,1]]=data[:,[1,0]]
    # not_none_pos = np.where(data_all[:,3]!=0)[0] #* 去除零值后的数据，在全局的位置 [638,629,1004,……] 值为 data_all数据下标
    not_none_pos = np.where(~np.isnan(data_all[:,3]))[0] #* 获取 值为 nan 的下标
    # not_none_pos = np.setdiff1d(not_none_pos,nan_pos)
    data_not_none = data_all[not_none_pos]
    pos_not_none = np.full((times*rows*cols),-1,dtype=np.int64) #* 全局数据中，不为零的下标[-1,-1,0,-1,1,-1,2,3,4,……] 值为 data_not_none 下标
    pos_not_none[not_none_pos] = np.array(range(len(not_none_pos)))
    return data_not_none,pos_not_none


def _check_netcdf(X):
    if type(X)!=xr.DataArray:
        raise ValueError("Only support datatype DataArray of xarray, please handle netcdf data by the library xarray.")


def labeled_res_to_netcdf(ori_nc,data_table,labels):
    '''
        writing cluste label results to netcdf data.
    '''
    ori_ndarray = np.array(ori_nc)
    dr_labels = np.full(ori_ndarray.shape,-2)
    for i in range(len(data_table)):
        if(ori_ndarray.ndim==2):
            dr_labels[int(data_table[i][1])][int(data_table[i][0])] = labels[i]
        elif(ori_ndarray.ndim==3):
            dr_labels[int(data_table[i][2])][int(data_table[i][0])][int(data_table[i][1])] = labels[i]
        else:
            raise ValueError("Two or Three-dimensional matrix is needed")
        pass
    labeled_res= xr.DataArray(
        dr_labels,
        coords=ori_nc.coords,
        dims=ori_nc.dims
    )
    ds = xr.Dataset(data_vars = dict(label=labeled_res,attr=ori_nc))
    return ds


def trans_lon_str(lon_extents):
    lon_str = []
    for i in lon_extents:
        if(i<=180):
            cur_lon_str = str(i) + "°E"
        if(i>180):
            cur_lon_str = str(360-i)+"°W"
        lon_str.append(cur_lon_str)
    return lon_str

def trans_lat_str(lat_extents):
    lat_str = []
    for i in lat_extents:
        if(i<0):
            cur_lat_str = str(i)+"°S"
        elif(i>0):
            cur_lat_str = str(i)+"°N"
        else:
            cur_lat_str = str(i)
        lat_str.append(cur_lat_str)
    return lat_str