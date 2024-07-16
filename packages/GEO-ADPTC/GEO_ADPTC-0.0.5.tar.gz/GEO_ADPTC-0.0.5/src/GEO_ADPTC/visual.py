import cartopy.crs as ccrs
from .auxiliary import *
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from cartopy.mpl.gridliner import LATITUDE_FORMATTER, LONGITUDE_FORMATTER
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.pyplot import MultipleLocator
from mpl_toolkits.basemap import Basemap



def show_data_label(data, labels, corePoints=[],font_show=True, path=""):
    '''
        Show clustering results for 2-dimensional point data.
        
        data: A matrix whose columns are feature vectors.
        lables: Label array of point data.
        corePoints: Core points.
        font_show: Control whether to display text messages.
        path: Image output address.
    '''
    clusterNum = np.unique(labels.astype(int))
    scatterColors =[
        '#337d56','#7d7d00','#c66f35','#0b2d64','#777bce','#eddd9e','#f52443','#874521','#85795e','#326787',
        '#161d21','#744d57','#477066','#9fa0d7','#3c374a','#efe7ab','#c0d6cb','#381801','#6f9388','#ff9b58',
        '#f9e459','#2d5131','#dcb183','#a0d878','#e9c61f','#41627c','#c9b481','#1c2859','#576d93','#b1470e',
        '#502e3e' 
    ]
    plt.figure(num=3, figsize=(10, 8))
    if font_show == False:
        for i in clusterNum:
            if(i < 0):
                colorSytle = '#510101'
                subCluster_id = np.where(labels == i)[0]
                plt.scatter(x=data[subCluster_id, 0], y=data[subCluster_id, 1], c=colorSytle, s=100, marker='*', alpha=1)
                continue
            colorSytle = scatterColors[i % len(scatterColors)]
            subCluster_id = np.where(labels == i)[0]
            plt.scatter(x=data[subCluster_id, 0], y=data[subCluster_id, 1], c=colorSytle, s=100, marker='o', alpha=1)
        pass
    else:
        for i in clusterNum:
            if(i == -1 or i == -2):
                colorSytle = '#510101'
                subCluster_id = np.where(labels == i)[0]
                plt.scatter(x=data[subCluster_id, 0], y=data[subCluster_id, 1],
                            edgecolors=colorSytle, c='', s=800, marker='o', alpha=1)
                continue
            colorSytle = scatterColors[i % len(scatterColors)]
            subCluster_id = np.where(labels == i)[0]
            plt.scatter(x=data[subCluster_id, 0], y=data[subCluster_id, 1],
                        edgecolors=colorSytle, c='', s=800, marker='o', alpha=1)

        for i in range(len(data)):
            plt.text(data[i, 0], data[i, 1], i, fontdict={
                     'fontsize': 18}, family="fantasy", ha='center', va='center', wrap=True)
    if(len(corePoints)>0):
        plt.scatter(x=data[corePoints, 0], y=data[corePoints, 1], marker='+', s=100, c='k', alpha=1)    
    plt.tick_params(labelsize=20)
    if(path != ""):
        plt.savefig(path)
    else:
        plt.show()
    plt.clf()
    pass


def show_decision_graph_by_gamma(clus_res,num=0,font_show=False,path=""):
    '''
        Show the value of gamma(γ = ρ*δ) in decreasing order.
        
        clus_res: The object returned by clustering methods;
        num: The first n numbers to be displayed;
    '''
    gamma = clus_res['gamma']
    data = clus_res['data']
    plt.rcParams['axes.unicode_minus']=False   
    plt.figure(num=2, figsize=(8, 10))
    ax = plt.gca()
    ax.spines['top'].set_visible(False)   
    ax.spines['right'].set_visible(False)  
    y=-np.sort(-gamma)
    if(num!=0):
        y = y[0:num]
    indx = np.argsort(-gamma)
    if(font_show==False):
        plt.scatter(x=range(len(y)), y=y,c='k', s=200*y, marker='o', alpha=1)
    else:
        plt.scatter(x=range(len(y)), y=y,edgecolors="#337d56", c='', s=800, marker='o', alpha=1)
        for i in range(len(y)):
            plt.text(i, y[i], indx[i], fontdict={
                     'fontsize': 18}, family="fantasy", ha='center', va='center', wrap=True)
    plt.xlabel('Sample Counts',fontsize=20)
    plt.ylabel('Decision value: γ',fontsize=20)
    plt.tick_params(labelsize=20)
    if(path != ""):
        plt.savefig(path)
    plt.show()

def show_decision_graph_by_density_distance(clus_res,font_show=False,path=""):
    '''
        Show the decision graph. 
        The greater the distance and density, the more likely the center point of the cluster.
        The value of gamma(γ = ρ*δ) in decreasing order;
        
        clus_res: The object returned by clustering methods;
    '''    
    plt.rcParams['axes.unicode_minus']=False  
    plt.figure(num=2, figsize=(8, 10))
    ax = plt.gca()
    ax.spines['top'].set_visible(False)  
    ax.spines['right'].set_visible(False) 
    den = clus_res['density']
    dis = clus_res['denser_dist']
    if(font_show==False):
        plt.scatter(x=den, y=dis, c='k', s=30, marker='o', alpha=1)
    else:
        plt.scatter(x=den, y=dis,edgecolors="#337d56", c='', s=800, marker='o', alpha=1)
        for i in range(len(den)):
            plt.text(den[i], dis[i], i, fontdict={
                     'fontsize': 18}, family="fantasy", ha='center', va='center', wrap=True)        
    plt.xlabel('Density: ρ',fontsize=20)
    plt.ylabel('Distance: δ',fontsize=20)
    plt.tick_params(labelsize=20)
    if(path != ""):
        plt.savefig(path)
    plt.show()

def time_heatmap(clus_res):
    '''
        The heatmap of temporal distribution.
        
        clus_res: The object returned by clustering methods;
    '''
    var_t = clus_res['data']
    sample_array = clus_res['sample_array']
    labels = clus_res['labels'] 
    labels_nc = clus_res['label_nc']
    time_len = len(labels_nc.time)
    nodes_num_one_month = np.zeros((np.max(labels)+1,time_len))
    label1_num = np.zeros((time_len))
    for j in range(time_len):
        label_num,node_sum = np.unique(labels_nc.sel(time = labels_nc.time[j]).label,return_counts=True)
        for i in range(len(label_num)):
            if(label_num[i]>=0):
                nodes_num_one_month[label_num[i]][j] = node_sum[i]
            elif(label_num[i]==-1):
                label1_num[j] = node_sum[i]
            pass 
    df = pd.DataFrame(nodes_num_one_month, 
                  index=range(0, np.max(labels)+1), 
                  columns=range(1,time_len+1)) 
    hm = sns.heatmap(data=df,cmap=plt.get_cmap('YlGn'))
    xtickvals=np.arange(len(labels_nc.time))[::12]
    if(len(xtickvals)>2):
        plt.gca().set_xticks(xtickvals)  
        time_index = pd.to_datetime(labels_nc.time.values)
        xtickvals = [ str(y) for y in time_index.year]
        plt.gca().set_xticklabels(xtickvals[::12],                                       
                            rotation = 60,                                          
                            fontdict = {'horizontalalignment': 'center'})
    hm.figure.axes[-1].yaxis.label.set_size(8) 
    plt.title(' ') 
    pass



def show_result_3d(clus_res,extent,label,time_extent=[],path=''):
    '''
        3D spatiotemporal distribution map of Cluster.
    
        clus_res: The object returned by clustering methods;
        extent:[lon_w,lon_e,lat_s,lat_n]
        time_extent:[time1,time2]
        label：the label specified to display
    '''
    res = clus_res['label_nc']
    label_nc = res['label']
    data_nc = np.array(label_nc)
    times,rows,cols = data_nc.shape
    data_all = np.zeros((times*rows*cols,4))
    num = 0
    for i in range(rows):
        for j in range(cols):
            for k in range(times):
                data_all[num,:] = [i,j,k,data_nc[k,i,j]]
                num+=1
            pass
        pass
    data = data_all[np.where(data_all[:,3]==label)[0]]
    lons = []
    lats = []
    times = []
    times_obj = []
    for i in range(len(data)):
        lons.append(float(label_nc.lon[int(data[i,1])].values))
        lats.append(float(label_nc.lat[int(data[i,0])].values))
        times.append(int(data[i,2]))
        times_obj.append(label_nc.time[int(data[i,2])].values)
        pass
    times_obj = np.unique(times_obj)
    colors = [
    '#337d56','#7d7d00','#c66f35','#0b2d64','#777bce','#eddd9e','#f52443','#874521','#85795e','#326787',
    '#161d21','#744d57','#477066','#9fa0d7','#3c374a','#efe7ab','#c0d6cb','#381801','#6f9388','#ff9b58',
    '#f9e459','#2d5131','#dcb183','#a0d878','#e9c61f','#41627c','#c9b481','#1c2859','#576d93','#b1470e',
    '#502e3e' 
]
    _draw_geo3dscatter(lons,lats,times,times_obj,colors[i%len(colors)],extent,time_extent,path)
    pass

def _draw_geo3dscatter(lons,lats,times,times_obj,label_color,extent,time_extent,path=''):
    # print("times",times)
    fig = plt.figure(figsize=(20,20))
    ax = fig.gca(projection='3d')
    # Create a basemap instance that draws the Earth layer
    bm = Basemap(llcrnrlon=extent[0], llcrnrlat=extent[2],
                urcrnrlon=extent[1], urcrnrlat=extent[3],
                projection='cyl', resolution='l', fix_aspect=False, ax=ax)
    ax.add_collection3d(bm.drawcoastlines(linewidth=0.25))
    ax.view_init(azim=245, elev=30)
    lon_step = 10
    lat_step = 5
    meridians = np.arange(extent[0], extent[1] + lon_step, lon_step)
    parallels = np.arange(extent[2], extent[3] + lat_step, lat_step)
    meridians_str = trans_lon_str(meridians)
    parallels_str = trans_lat_str(parallels)
    ax.set_yticks(parallels)
    ax.set_yticklabels(parallels_str,fontdict = {'horizontalalignment': 'center'})
    ax.set_xticks(meridians)
    ax.set_xticklabels(meridians_str,rotation = 30,fontdict = {'horizontalalignment': 'center'})
    
    if(time_extent==[]):
        ax.set_zlim(np.min(np.unique(times)), np.max(np.unique(times)),1)
        times_str = pd.to_datetime(times_obj)
        xtickvals = [str(m)[:3].upper() + '-' + str(y) for y,m in zip(times_str.year, times_str.month)]
        print(path,":",xtickvals[0],"-",xtickvals[-1])
        locator = 1
        if(len(times_obj)>20):
            locator=4
        elif(len(times_obj)>10):
            locator=2
        elif(len(times_obj)<=10):
            locator=1
        ax.zaxis.set_major_locator(MultipleLocator(locator))
        ax.set_zticklabels(xtickvals[0:len(xtickvals):locator],rotation = 30,fontdict = {'horizontalalignment': 'right'})
    else:
        ax.set_zlim(time_extent[0], time_extent[1])
    ax.scatter(lons, lats, times,c=label_color,alpha=0.5,s=20,marker='s')
    ax.scatter(lons, lats,c='#00000005',alpha=0.5,s=20,marker='o')
    plt.tick_params(labelsize=25)
    if(path!=''):
        plt.savefig(path)
    plt.show()
    pass

def _create_map(ax):
    gl = ax.gridlines(crs=ccrs.PlateCarree(),draw_labels=True,linewidth=1.2,color='k',alpha=0.5,linestyle='--')
    gl.xlabels_top = False
    gl.ylabels_right = False
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER
    gl.xlabel_style = {'fontsize': 30}
    gl.ylabel_style = {'fontsize': 30}
    return ax 

def show_result_2d(clus_res,time_index,extent,path=""):
    '''
        2D spatial distribution chart.
        
        clus_res: The object returned by clustering methods;
        time_index: Index of time to be displayed
        extent: Range of space to be displayed,[lon_w,lon_e,lat_s,lat_n].
    '''
    
    labels = clus_res['labels']
    label_nc = clus_res['label_nc']
    time_nc = label_nc.sel(time=label_nc.time[time_index])    
    da = time_nc['label'] 
    proj = ccrs.PlateCarree()
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(15,10), subplot_kw={'projection':proj})
    bm = Basemap(llcrnrlon=extent[0], llcrnrlat=extent[2],
                urcrnrlon=extent[1], urcrnrlat=extent[3], resolution='l', fix_aspect=False, ax=ax)
    bm.drawcoastlines(linewidth=0.25)
    cbar_kwargs={
        'label': 'Lables',
        'ticks':np.arange(-1,np.max(labels),1), 
        'orientation':'horizontal'
    }
    levels = np.arange(-1,np.max(labels),1)
    
    ax = _create_map(ax)
    ncolors = 256
    color_array = plt.get_cmap('terrain')(range(ncolors))
    color_array[0] = [0,0,0,0]
    map_object = LinearSegmentedColormap.from_list(name='Paired1',colors=color_array)
    pre_pic = da.plot.contourf(ax=ax,levels=levels, cmap=map_object, extend='both', cbar_kwargs = cbar_kwargs,transform=ccrs.PlateCarree())
    ax.set_title(' ', fontsize=30)
    cb = pre_pic.colorbar
    cb.ax.set_ylabel('labels',fontsize=20)
    cb.ax.tick_params(labelsize=18)
    fig.show()
    if(path != ""):
        plt.savefig(path)
    pass

def showAttr(res,attr_name,time_index,extent):
    '''
        Use 2D maps to display element attribute information.
        
        res: The object returned by clustering methods;
        attr_name:The name of attribute;
        time_index: Index of time to be displayed
        extent: Range of space to be displayed
    '''
    label_nc = res['label_nc']
    time_nc = label_nc.sel(time=label_nc.time[time_index])
    da = time_nc[attr_name]
    proj = ccrs.PlateCarree(central_longitude=180.0)
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(20,10), subplot_kw={'projection':proj})
    cbar_kwargs={
        'label': 'precipitation mm/d',
        'ticks':extent, 
    }
    levels = extent
    
    ax = _create_map(ax)
    ncolors = 256
    color_array = plt.get_cmap('Spectral_r')(range(ncolors))
    color_array[0] = [color_array[0][0],color_array[0][1],color_array[0][2],0]
    map_object = LinearSegmentedColormap.from_list(name='my_spectral_r',colors=color_array)
    pre_pic = da.plot.contourf(ax=ax,levels=levels, cmap=map_object, extend='both', cbar_kwargs = cbar_kwargs,transform=ccrs.PlateCarree())
    ax.set_title(' ', fontsize=30)
    cb = pre_pic.colorbar
    
    cb.ax.set_ylabel('Temperature ℃',fontsize=30)
    cb.ax.tick_params(labelsize=24)

    ax.coastlines()
    fig.show()


def show_box(clus_res,labels_show):
    '''
        Display box diagram.
    
        clus_res: The object returned by clustering methods;
        labels_show:the label specified to display.
    '''
    data = clus_res['sample_array']
    labels = clus_res['labels']
    fig,axes = plt.subplots()
    for i in range(len(labels_show)):
        cur_label_cell_pos = np.where(labels==labels_show[i])
        axes.boxplot(x=data[cur_label_cell_pos,-1][0],sym='rd',positions=[i],showfliers=False,notch=True)
    plt.xlabel('label',fontsize=20)
    plt.ylabel('attr',fontsize=20) 
    plt.xticks(range(len(labels_show)),labels_show)
    plt.tick_params(labelsize=15)
    pass


def show_vlines(clus_res,labels_show):
    '''
        The violin statistics chart of Clusters.
        
        clus_res: The object returned by clustering methods;
        labels_show:the label specified to display.
    '''
    data = clus_res['sample_array']
    labels = clus_res['labels']
    fig,axes = plt.subplots()
    for i in range(len(labels_show)):
        cur_label_cell_pos = np.where(labels==labels_show[i])
        axes.violinplot(data[cur_label_cell_pos,-1][0],positions=[i],showmeans=False,showmedians=True)
    plt.xlabel('label',fontsize=20)
    plt.ylabel('attr',fontsize=20)  
    plt.xticks(range(len(labels_show)),labels_show)
    plt.tick_params(labelsize=15)
    pass