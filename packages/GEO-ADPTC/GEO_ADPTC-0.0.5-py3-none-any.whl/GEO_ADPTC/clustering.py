 
#%%
from turtle import shape
import numpy as np
from .auxiliary import *
from sklearn.neighbors import KDTree,BallTree,DistanceMetric
from sklearn.utils import check_array
from .DPTree import *

from memory_profiler import profile

@profile(precision=4,stream=open('memory_profiler4000.log','w+'))
def clustering(data,eps, density_metric='cutoff', dist_metric='euclidean',knn_method="kd_tree", knn_num=20, leaf_size=300, connect_eps=1,fast=False):
    '''
    description: spatial clustering without other attribute involved in.
    return {*}
    data:
        A matrix whose columns are feature vectors
    eps：
        cutoff distance used to find the local density of points
    density_metric:
        methord to calculate local density, support: "cutoff", "gauss"
    dist_metric：
        methord to calculate distance matrix，default: "euclidean"，support['euclidean','braycurtis', 'canberra', 'chebyshev', 'cityblock',
        'correlation', 'cosine', 'dice',  'hamming','jaccard', 'jensenshannon', 'kulsinski', 'mahalanobis', 'matching',
        'minkowski', 'rogerstanimoto', 'russellrao', 'seuclidean',
        'sokalmichener', 'sokalsneath', 'sqeuclidean', 'yule']
    knn_num:
        number of the nearest neighbors
    leaf_size:
        leaf nodes number used for knn function. will influence the speed of calculation and query.
    connect_eps:
        specific argument for points connectivity control.
    fast:
        True: use knn methods speed up the calculation of repulsive_force
    '''
    cluster = Cluster(data)
    density,matrix_dist,near_matrix = cluster.get_density(eps,density_metric,dist_metric,leaf_size,knn_num)
    
    # matrix_dist = cluster.get_dist_matrix(data,dist_metric)
    # todo 通过距离矩阵计算邻近矩阵。
    # near_matrix = get_near_matrix(eps,matrix_dist)
    # density = cluster.get_density_old(eps,density_metric,matrix_dist)
    denser_pos,denser_dist = cluster.get_repulsive_force(density,matrix_dist,fast,knn_num,leaf_size,dist_metric,knn_method)
    gamma = cluster._calc_gamma(density,denser_dist)
    labels, core_points = cluster.extract_cluster_auto(data,density,connect_eps,denser_dist,denser_pos,gamma,near_matrix)
    res={'data':data,'labels':labels,'core_points':core_points, 'gamma':gamma,'density':density,'denser_dist':denser_dist,'denser_pos':denser_pos}
    return res


def spacial_clustering(xr_data, spatial_eps,attr_eps,density_metric='cutoff',dist_metric='euclidean',knn_method="kd_tree",knn_num = 20, leaf_size = 300, connect_eps=1):
    '''
        description: Cluster analysis of geospatial raster data; 
        return {*}
        data:
            a two-dimensional xarray.Dataset, and the rows and columns are the latitude and longitude of the geospatial respectively。
        spatial_eps：
            Spatial threshold
        attr_eps：
            Attribute threshold
        density_metric:
            methord to calculate local density, support: "cutoff", "gauss"
        dist_metric：
            methord to calculate distance matrix，default: "euclidean"，support['euclidean','braycurtis', 'canberra', 'chebyshev', 'cityblock',
            'correlation', 'cosine', 'dice',  'hamming','jaccard', 'jensenshannon', 'kulsinski', 'mahalanobis', 'matching',
            'minkowski', 'rogerstanimoto', 'russellrao', 'seuclidean','sokalmichener', 'sokalsneath', 'sqeuclidean', 'yule'.]
        knn_num:
            number of the nearest neighbors
        leaf_size:
            leaf nodes number used for knn function. will influence the speed of calculation and query.
        connect_eps:
            specific argument for points connectivity control.
    '''
    data = np.array(xr_data)
    cluster = STCluster(data)
    sample_array,sample_pos = rasterArray_to_sampleArray(data)
    near_matrix = cluster.calc_homo_near_grid(data,spatial_eps,attr_eps,sample_pos)
    if(density_metric=='cutoff'):
        density = cluster.calc_cutoff_density(near_matrix)
    else:
        density = cluster.calc_gaus_density_grid(data,spatial_eps,attr_eps)
    denser_pos,denser_dist = cluster._calc_repulsive_force_fast(sample_array,knn_num,density,leaf_size,dist_metric,knn_method)
    gamma = cluster._calc_gamma(density,denser_dist)
    labels, core_points = cluster.extract_cluster_auto(sample_array,density,connect_eps,denser_dist,denser_pos,gamma,near_matrix)
    label_nc = labeled_res_to_netcdf(xr_data,sample_array,labels)
    res={'data':data,'labels':labels,'core_points':core_points,'sample_array':sample_array,'label_nc':label_nc,'gamma':gamma,'density':density,'denser_dist':denser_dist,'denser_pos':denser_pos}
    return res

@profile(precision=4,stream=open('memory_profiler22.log','w+'))
def st_clustering(xr_data,spatial_eps,time_eps,attr_eps,density_metric='gauss',dist_metric='euclidean',knn_method="kd_tree",knn_num=20, leaf_size=300, connect_eps=1):
    '''
        description: Cluster analysis of geographical spatio-temporal raster data; 
        return {*}
        xr_data:
            a three-dimensional xarray.Dataset: latitude ,longitude and time。
        spatial_eps：
            Spatial threshold
        time_eps:
            time threshold
        attr_eps:
            Attribute threshold
        density_metric:
            methord to calculate local density, support: "cutoff", "gauss"
        dist_metric:
            methord to calculate distance matrix，default: "euclidean"，support['euclidean','braycurtis', 'canberra', 'chebyshev', 'cityblock',
            'correlation', 'cosine', 'dice',  'hamming','jaccard', 'jensenshannon', 'kulsinski', 'mahalanobis', 'matching',
            'minkowski', 'rogerstanimoto', 'russellrao', 'seuclidean','sokalmichener', 'sokalsneath', 'sqeuclidean', 'yule'.]
        knn_num:
            number of the nearest neighbors
        leaf_size:
            leaf nodes number used for knn function. will influence the speed of calculation and query.
        connect_eps:
            specific argument for points connectivity control.
    '''
    data = np.array(xr_data)
    cluster = STCluster(data)
    sample_array,sample_pos = rasterCube_to_sampleArray(data)
    near_matrix = cluster.calc_homo_near_cube(data,spatial_eps,time_eps,attr_eps,sample_pos)
    if(density_metric=='cutoff'):
        density = cluster.calc_cutoff_density(near_matrix)
    else:
        density = cluster.calc_gaus_density_cube(data,spatial_eps,time_eps,attr_eps)
    denser_pos,denser_dist = cluster._calc_repulsive_force_fast(sample_array,knn_num,density,leaf_size,dist_metric,knn_method)
    gamma = cluster._calc_gamma(density,denser_dist)
    labels, core_points = cluster.extract_cluster_auto(sample_array,density,connect_eps,denser_dist,denser_pos,gamma,near_matrix)
    label_nc = labeled_res_to_netcdf(xr_data,sample_array,labels)
    res={'data':data,'labels':labels,'core_points':core_points,'sample_array':sample_array,'label_nc':label_nc,'gamma':gamma,'density':density,'denser_dist':denser_dist,'denser_pos':denser_pos}
    return res



class BaseCluster(object):
    def __init__(self,data=None) -> None:
        super().__init__()
        self.data = data 
        self.knn_tree = None
    pass

    @fn_timer("_calc_repulsive_force_fast_new")
    def _calc_repulsive_force_fast_new(self,data, k_num, density, leaf_size,dist_metric="euclidean",knn_method="kd_tree"):
        '''
        find the nearest neighbor of higher density based on knn-methods 
        return: 
            denser_dist: the distance to the nearest neighbor of higher density.
            denser_pos: the nearest neighbor of higher density. 
        '''
        # 1. 按照密度大小排序
        sorted_density = np.sort(density)


        if(self.knn_tree is None):
            if(knn_method=="ball_tree"):
                self.knn_tree = BallTree(data,leaf_size=leaf_size,metric=DistanceMetric.get_metric(dist_metric))
            else:
                self.knn_tree = KDTree(data, leaf_size=leaf_size,metric=DistanceMetric.get_metric(dist_metric)) 
        dist, ind = self.knn_tree.query(data, k=k_num)
        # distance of higher density
        denser_dist = np.full(ind.shape[0], -1,dtype=np.float32)
        denser_pos = np.full(ind.shape[0],-1,dtype=np.int32)
        for i in range(len(sorted_density)):
            # 密度最大点
            if i==len(sorted_density)-1:
                denser_dist[sorted_density[i]] = np.max(denser_dist)+1
                denser_pos[sorted_density[i]] = sorted_density[i]
                pass
            else:
                sorted_density[i]
            pass

        for i in range(ind.shape[0]):
            denser_list = np.where(density[ind[i]]>density[i])[0]
            if(len(denser_list)>0):
                denser_dist[i] = dist[i][denser_list[0]]
                denser_pos[i] = ind[i][denser_list[0]] 
                pass
        not_found_data = list(np.where(denser_pos==-1)[0])
        max_density_idx = not_found_data[np.argmax(density[not_found_data])]
        density[max_density_idx] = density[max_density_idx]+1
        not_found_data.pop(np.argmax(density[not_found_data])) 
        num = 1
        # cur_k = k_num
        while(len(not_found_data)>0):
            cur_k = k_num
            cur_data_id = not_found_data.pop()
            if(cur_data_id==610):
                print(cur_data_id)
            cur_k = cur_k+k_num
            if(cur_k>=data.shape[0]):
                cur_k = data.shape[0]
            cur_dist, cur_ind= self.knn_tree.query(data[cur_data_id:cur_data_id+1], k=cur_k)
            cur_dist, cur_ind = cur_dist[0], cur_ind[0]
            denser_list = np.where(density[cur_ind]>density[cur_data_id])
            while(len(denser_list[0])==0):
                cur_k = cur_k + k_num
                # print("cur_k:",cur_k)
                if(cur_k>=data.shape[0]):
                    cur_k = data.shape[0]
                cur_dist, cur_ind= self.knn_tree.query(data[cur_data_id:cur_data_id+1], k=cur_k)
                cur_dist, cur_ind = cur_dist[0], cur_ind[0]
                denser_list = np.where(density[cur_ind]>density[cur_data_id])
                pass
            if(len(denser_list[0])>0):
                # print(num)
                num = num+1
                denser_pos[cur_data_id] = cur_ind[denser_list[0][0]]
                denser_dist[cur_data_id] = cur_dist[denser_list[0][0]]
            else:
                print("Not found:",cur_data_id)
            pass
        denser_dist[max_density_idx] = np.max(denser_dist)+1
        denser_pos[max_density_idx] =max_density_idx
        self.denser_pos = denser_pos
        self.denser_dist = denser_dist
        return denser_pos,denser_dist

    @fn_timer("calc_repulsive_force_fast")
    def _calc_repulsive_force_fast(self,data, k_num, density, leaf_size,dist_metric="euclidean",knn_method="kd_tree"):
        '''
        find the nearest neighbor of higher density based on knn-methods 
        return: 
            denser_dist: the distance to the nearest neighbor of higher density.
            denser_pos: the nearest neighbor of higher density. 
        '''
        if(self.knn_tree is None):
            t0 = time.time()
            if(knn_method=="ball_tree"):
                self.knn_tree = BallTree(data,leaf_size=leaf_size,metric=DistanceMetric.get_metric(dist_metric))
            else:
                self.knn_tree = KDTree(data, leaf_size=leaf_size,metric=DistanceMetric.get_metric(dist_metric)) 
            t1 = time.time()
            print (" %s: %s seconds" % ("build knn_tree", str(t1-t0)) )
        t0 = time.time()
        dist, ind = self.knn_tree.query(data, k=k_num)
        t1 = time.time()
        print (" %s: %s seconds" % ("knn_tree query 500", str(t1-t0)) )
        
        # distance of higher density
        denser_dist = np.full(ind.shape[0], -1,dtype=np.float32)
        denser_pos = np.full(ind.shape[0],-1,dtype=np.int32)
        for i in range(ind.shape[0]):
            denser_list = np.where(density[ind[i]]>density[i])[0]
            if(len(denser_list)>0):
                denser_dist[i] = dist[i][denser_list[0]]
                denser_pos[i] = ind[i][denser_list[0]] 
                pass
        not_found_data = list(np.where(denser_pos==-1)[0])
        max_density_idx = not_found_data[np.argmax(density[not_found_data])]
        density[max_density_idx] = density[max_density_idx]+1
        not_found_data.pop(np.argmax(density[not_found_data])) 
        num = 1
        # cur_k = k_num
        while(len(not_found_data)>0):
            cur_k = k_num
            cur_data_id = not_found_data.pop()
            if(cur_data_id==610):
                print(cur_data_id)
            cur_k = cur_k+k_num
            if(cur_k>=data.shape[0]):
                cur_k = data.shape[0]
            cur_dist, cur_ind= self.knn_tree.query(data[cur_data_id:cur_data_id+1], k=cur_k)
            cur_dist, cur_ind = cur_dist[0], cur_ind[0]
            denser_list = np.where(density[cur_ind]>density[cur_data_id])
            while(len(denser_list[0])==0):
                cur_k = cur_k + k_num
                # print("cur_k:",cur_k)
                if(cur_k>=data.shape[0]):
                    cur_k = data.shape[0]
                cur_dist, cur_ind= self.knn_tree.query(data[cur_data_id:cur_data_id+1], k=cur_k)
                cur_dist, cur_ind = cur_dist[0], cur_ind[0]
                denser_list = np.where(density[cur_ind]>density[cur_data_id])
                pass
            if(len(denser_list[0])>0):
                # print(num)
                num = num+1
                denser_pos[cur_data_id] = cur_ind[denser_list[0][0]]
                denser_dist[cur_data_id] = cur_dist[denser_list[0][0]]
            else:
                print("Not found:",cur_data_id)
            pass
        denser_dist[max_density_idx] = np.max(denser_dist)+1
        denser_pos[max_density_idx] =max_density_idx
        self.denser_pos = denser_pos
        self.denser_dist = denser_dist
        return denser_pos,denser_dist


    @fn_timer("calc_repulsive_force_classical")
    def _calc_repulsive_force_classical(self,data,density,dist_matrix):
        '''
        find the nearest neighbor of higher density based on distance matrix. 
        return: 
            denser_dist: the distance to the nearest neighbor of higher density.
            denser_pos: the nearest neighbor of higher density. 
        '''
        rows = len(data)
        sorted_density = np.argsort(density)
        denser_dist = np.zeros((rows,))
        denser_pos = np.zeros((rows,), dtype=np.int32)
        for index,nodeId in enumerate(sorted_density):
            nodeIdArr_denser = sorted_density[index+1:]
            if nodeIdArr_denser.size != 0:
                over_density_sim = dist_matrix[nodeId][nodeIdArr_denser]
                denser_dist[nodeId] = np.min(over_density_sim)
                min_distance_index = np.argwhere(over_density_sim == denser_dist[nodeId])[0][0]
                # 获得整个数据中的索引值
                denser_pos[nodeId] = nodeIdArr_denser[min_distance_index]
            else:
                denser_dist[nodeId] = np.max(denser_dist)+1
                denser_pos[nodeId] = nodeId
        return denser_pos,denser_dist


    def _calc_gamma(self,density,denser_dist):
        '''
        calculate the decision values, local_density *　denser_distance
        '''
        normal_den = density / np.max(density)
        normal_dis = denser_dist / np.max(denser_dist)
        gamma = normal_den * normal_dis
        self.gamma = gamma
        return gamma
    
    @fn_timer("split_cluster")
    def split_cluster(self,dptree,local_density,connect_eps,closest_denser_nodes_id,near_matrix):
        '''
            Subtree division according to the connectivity of the parent and child nodes.
            dptree: 
                Density peak tree.
            local_density: 
                The local density of all nodes.
            connect_eps: 
                Specific argument for points connectivity control.
            closest_denser_nodes_id: 
                Closest near nodes with higher local density.
            near_matrix: 
                Neighbor matrix within the cutoff distance.
            
        '''
        mean_density = np.mean(local_density)
        outlier_forest = {}
        cluster_forest = {}
        uncertain_forest = {}
        not_direct_reach = []
        #* find not directly reachable nodes(NDRN) ：
        for k in range(len(closest_denser_nodes_id)):
            near_nodes = near_matrix[k]
            if closest_denser_nodes_id[k] not in near_nodes:
                not_direct_reach.append(k)
            pass
        not_direct_reach = np.array(not_direct_reach)
        #* Arrange NDRN by the hierarchy of tree structure:
        depth_list_not_direct_reach= np.zeros(len(not_direct_reach),dtype=np.int16)
        for i in range(len(not_direct_reach)):
            depth_list_not_direct_reach[i] = dptree.calcu_depth(not_direct_reach[i],0)
            pass
        not_direct_reach = list(not_direct_reach[np.argsort(depth_list_not_direct_reach)])
        while(len(not_direct_reach)>0):
            node_id = not_direct_reach.pop()
            node = dptree.node_dir[node_id]
            parent_id = node.getParentId()
            parent_node = dptree.node_dir[parent_id]
            children = parent_node.getChildren()
            siblings_reliable = [ i for i in children if i not in not_direct_reach]
            not_reliable_nodes = [i for i in children if i not in siblings_reliable]
            if node_id in not_reliable_nodes:
                not_reliable_nodes.remove(node_id)
            if node_id in siblings_reliable:
                siblings_reliable.remove(node_id)
            pairs_nodes = self.is_connected(dptree,local_density,connect_eps,node_id,siblings_reliable,not_reliable_nodes,near_matrix)
            if len(pairs_nodes)==0:
                if(node_id==dptree.root_node.node_id):
                    continue
                if(local_density[node_id]-mean_density*connect_eps)>=0:
                    offspring_id = dptree.get_subtree_offspring_id(node_id,[node_id])
                    if(len(offspring_id)<local_density[node_id]):
                        uncertain_forest[node_id] = dptree.remove_subtree(node_id)
                        pass
                    else:
                        cluster_forest[node_id] = dptree.remove_subtree(node_id)
                        pass
                    pass
                else:
                    outlier_forest[node_id] = dptree.remove_subtree(node_id)
                    pass
                pass
            pass
        cluster_forest[dptree.root_node.node_id] = dptree
        return outlier_forest, cluster_forest, uncertain_forest
    

    # @fn_timer("is_connected")
    def is_connected(self,dptree,local_density,connect_eps,cur_node_id,reliable_nodes,not_reliable_nodes,near_matrix):
        '''
            Judging whether the child node is connected to the parent node.
            dptree: ...
            local_density: ...
            connect_eps: ...
            cur_node_id: 
                The current point to confirm connectivity with the parent node.
            reliable_nodes：
                Directly connected to the parent node in the brothers node.
            not_reliable_nodes：
                Not directly connected to the parent node in the brothers node, but may be connected indirectly.
        '''
        #* 1. Determine whether cur_node_id and reliable_nodes are reachable, if so, return; if not, execute 2.
        if(len(reliable_nodes)==0):
            return []
        for reliable_node_id in reliable_nodes:
            pairs_nodes, connected_nodes = dptree.calcu_neighbor_btw_subtree(cur_node_id,reliable_node_id,near_matrix)
            if(len(pairs_nodes)==0):
                continue
            # return pairs_nodes
            cur_node_offspring = dptree.get_subtree_offspring_id(cur_node_id,[cur_node_id])
            local_density_cur_offspring = np.mean(local_density[cur_node_offspring])
            local_density_connected_nodes = np.mean(local_density[connected_nodes])
            if(local_density_connected_nodes>local_density_cur_offspring*connect_eps):
                return pairs_nodes
            pass
        #* 2. Determine whether cur_node_id and not_reliable_nodes(Suppose it is[a,b,c,d,e]) are reachable, if it is reachable with [a,b,c] and unreachable with [d,e], execute this method recursively.
        for i in range(len(not_reliable_nodes)):
            pairs_nodes, connected_nodes = dptree.calcu_neighbor_btw_subtree(cur_node_id,not_reliable_nodes[i],near_matrix)
            if(len(pairs_nodes)==0):
                pairs_nodes = self.is_connected(dptree,local_density,connect_eps,not_reliable_nodes[i],reliable_nodes,not_reliable_nodes[i+1:],near_matrix)
                if(len(pairs_nodes)>0):
                    return pairs_nodes
            else:
                cur_node_offspring = dptree.get_subtree_offspring_id(cur_node_id,[cur_node_id])
                local_density_cur_offspring = np.mean(local_density[cur_node_offspring])
                local_density_connected_nodes = np.mean(local_density[connected_nodes])
                if(local_density_connected_nodes>local_density_cur_offspring*connect_eps):
                    return pairs_nodes
                
            cur_node_offspring = dptree.get_subtree_offspring_id(cur_node_id,[cur_node_id])
            local_density_cur_offspring = np.mean(local_density[cur_node_offspring])
            local_density_connected_nodes = np.mean(local_density[connected_nodes])
            if(local_density_connected_nodes>local_density_cur_offspring*connect_eps):
                return pairs_nodes
            if(len(pairs_nodes)==0):
                pairs_nodes = self.is_connected(dptree,local_density,connect_eps,not_reliable_nodes[i],reliable_nodes,not_reliable_nodes[i+1:],near_matrix)
                if(len(pairs_nodes)>0):
                    return pairs_nodes
        return []


    @fn_timer("label_these_node")
    def label_these_node(self,outlier_forest,cluster_forest,node_num,uncertain_forest,near_matrix):
        '''
            Label the sample points in the forest.
        '''
        labels = np.full((node_num),-1,dtype=np.int32)
        for outlier_id in outlier_forest:
            outlier_tree = outlier_forest[outlier_id]
            outlier_idlist = outlier_tree.get_subtree_offspring_id(outlier_id,[outlier_id])
            labels[outlier_idlist] = -1
            pass
        
        label = 0
        for tree_id in cluster_forest:
            cluster_tree = cluster_forest[tree_id]
            cluster_idlist = cluster_tree.get_subtree_offspring_id(tree_id,[tree_id])
            labels[cluster_idlist] = label
            label = label + 1
            pass

        for uncertain_tree_id in uncertain_forest:
            uncertain_tree = uncertain_forest[uncertain_tree_id]
            uncertain_nodes_id = uncertain_tree.get_subtree_offspring_id(uncertain_tree_id,[uncertain_tree_id])
            all_near_nodes = np.array([],dtype=np.int32)
            for node_id in uncertain_nodes_id:
                all_near_nodes = np.append(all_near_nodes,near_matrix[node_id])
                pass
            all_near_nodes = np.unique(all_near_nodes)
            all_near_nodes = all_near_nodes[np.where(labels[all_near_nodes]!=-1)]
            unique_labels,counts=np.unique(labels[all_near_nodes],return_counts=True)
            if(len(counts)==0):
                cur_label = -1
            else:
                cur_label = unique_labels[np.argmax(counts)]
            labels[uncertain_nodes_id]=cur_label
            pass

        core_points = cluster_forest.keys()
        return labels,core_points


    @fn_timer("auto extract cluster")
    def extract_cluster_auto(self,data,density,connect_eps,denser_dist,denser_pos,gamma,near_matrix):
        '''
            Automatic clustering of points using density peak tree.
        '''
        sorted_gamma_index = np.argsort(-gamma)
        tree = DPTree()
        tree.createTree(data,sorted_gamma_index,denser_pos,denser_dist,density,gamma)
        outlier_forest, cluster_forest, uncertain_forest=self.split_cluster(tree,density,connect_eps,denser_pos,near_matrix)
        labels,core_points = self.label_these_node(outlier_forest,cluster_forest,len(data),uncertain_forest,near_matrix)
        core_points = np.array(list(core_points))
        labels = labels
        self.labels = labels
        self.core_points = core_points
        return labels, core_points



class Cluster(BaseCluster):
    def __init__(self,data=None) -> None:
        super().__init__(data=data)

    
    def get_dist_matrix(self,data,metric):
        dist_mat = calc_dist_matrix(data,metric)
        self.matrix_dist = dist_mat
        return dist_mat
    
    @fn_timer("get_density")
    def get_density(self,eps,density_metric,dist_mat,leaf_size,k_num):
        # 判断数组长度，如果样本大于1万个，则使用 knn 方法：
        if(len(self.data)<10000):
            matrix_dist = self.get_dist_matrix(self.data,dist_mat) 
            near_matrix = get_near_matrix(eps,matrix_dist)
            if(density_metric=='gauss'):
                return self._calc_gaus_density(matrix_dist,eps),matrix_dist,near_matrix
            else:
                return self._calc_cutoff_density(matrix_dist,eps),matrix_dist,near_matrix  
        else:
            # 使用knn方法求 密度和邻近矩阵
            self.knn_tree = KDTree(self.data, leaf_size=leaf_size,metric=DistanceMetric.get_metric(dist_mat)) 
            matrix_dist, ind = self.knn_tree.query(self.data, k=k_num) 
            density = 1/matrix_dist[:,-1]*10000
            near_matrix = self.knn_tree.query_radius(self.data,eps)
            return density,matrix_dist,near_matrix
        
    def get_density_old(self,eps,metric,dist_mat):
        if(metric=='gauss'):
            return self._calc_gaus_density(dist_mat,eps)
        else:
            return self._calc_cutoff_density(dist_mat,eps)
    
    
    def get_repulsive_force(self,density,dist_matrix=[],fast=True,k_num=8,leaf_size=30,dist_metric='euclidean',knn_method="kd_tree"):
        if(fast):
            denser_pos,denser_dist = self._calc_repulsive_force_fast(self.data,k_num,density,leaf_size,dist_metric,knn_method)
        else:
            denser_pos,denser_dist = self._calc_repulsive_force_classical(self.data,density,dist_matrix)
        self.denser_pos = denser_pos
        self.denser_dist = denser_dist
        return denser_pos,denser_dist
    
    
    
    @fn_timer("calc_gaus_density")
    def _calc_gaus_density(self,dist_mat, eps):
        '''
        calculate the local density of points with gauss kernel density 
        '''
        rows = dist_mat.shape[0]
        local_gaus_density = np.zeros((rows,),dtype=np.float32)
        for i in range(rows):
            local_gaus_density[i] = np.exp(-1 *((dist_mat[i, :])/(eps))**2).sum()
            pass
        self.density = local_gaus_density
        return local_gaus_density
    
    
    @fn_timer("calc_cutoff_density")
    def _calc_cutoff_density(self,dist_mat, eps):
        '''
        calculate the local density of points with cutoff distance as radius 
        '''
        local_cutoff_density = np.where(dist_mat < eps, 1, 0).sum(axis=1)
        self.density = local_cutoff_density
        return local_cutoff_density


class STCluster(BaseCluster):
    def __init__(self, data) -> None:
        super().__init__(data=data)
        
    
    @fn_timer("calc_homo_near_grid")
    def calc_homo_near_grid(self,data,s_eps,attr_eps,pos_not_none):
        mixin_near_matrix = {}
        rows,cols = data.shape
        num = 0
        for i in range(rows):
            for j in range(cols):
                #* 计算每个点的邻域范围:
                left_lon = i-s_eps if i-s_eps>=0 else 0
                rigth_lon = i+s_eps if i+s_eps<rows else rows
                up_lat = j-s_eps if j-s_eps>=0 else 0
                down_lat = j+s_eps if j+s_eps<cols else cols
                s_near = data[left_lon:rigth_lon+1,up_lat:down_lat+1]
                # if(data[i,j]!=0  and (not np.isnan(data[i,j]))):
                if(not np.isnan(data[i,j])):
                    # pos_s_near = np.where((np.abs(s_near-data[i,j])<=attr_eps) & (s_near!=0) &(~np.isnan(s_near)))
                    pos_s_near = np.where((np.abs(s_near-data[i,j])<=attr_eps) &(~np.isnan(s_near)))
                    pos_data = np.vstack(pos_s_near) + np.array([[left_lon],[up_lat]])
                    pos_in_matrix = cols*pos_data[0]+pos_data[1]  #* 获取全局邻域位置（全局包含空值点）
                    pos = pos_not_none[pos_in_matrix]
                    mixin_near_matrix[num] = pos
                    num+=1
                pass
            pass
        self.near_matrix = mixin_near_matrix
        return mixin_near_matrix
    
    
    @fn_timer("calc_homo_near_cube")
    def calc_homo_near_cube(self,data,s_eps,t_eps,attr_eps,pos_not_none):
        mixin_near_matrix = {}
        time_len,rows,cols = data.shape
        num = 0
        for i in range(rows):
            for j in range(cols):
                for k in range(time_len):
                    left_lon = i-s_eps if i-s_eps>=0 else 0
                    rigth_lon = i+s_eps if i+s_eps<rows else rows
                    up_lat = j-s_eps if j-s_eps>=0 else 0
                    down_lat = j+s_eps if j+s_eps<cols else cols
                    early_time = k-t_eps if k-t_eps>=0 else 0
                    lated_time = k+t_eps if k+t_eps<time_len else time_len
                    s_near = data[early_time:lated_time+1,left_lon:rigth_lon+1,up_lat:down_lat+1]
                    # if(data[k,i,j]!=0  and (not np.isnan(data[k,i,j]))):
                    if(not np.isnan(data[k,i,j])):
                        # pos_s_near = np.where((np.abs(s_near-data[k,i,j])<=attr_eps) & (s_near!=0) &(~np.isnan(s_near)))
                        pos_s_near = np.where((np.abs(s_near-data[k,i,j])<=attr_eps)  &(~np.isnan(s_near)))
                        pos_data = np.vstack(pos_s_near) + np.array([[early_time],[left_lon],[up_lat]])
                        pos_in_matrix = time_len*cols*pos_data[1]+time_len*pos_data[2]+pos_data[0]
                        pos = pos_not_none[pos_in_matrix]
                        mixin_near_matrix[num] = pos
                        num+=1
                    pass
                pass
            pass
        self.near_matrix = mixin_near_matrix
        return mixin_near_matrix
    
    
    
    @fn_timer("calc_cutoff_density")
    def calc_cutoff_density(self,near_matrix):
        data_len = len(near_matrix)
        density = np.zeros(data_len,dtype=np.float32)
        for i in range(data_len):
            density[i] = len(near_matrix[i])
        self.density = density
        return density
    
    @fn_timer("calc_gaus_density_grid")
    def calc_gaus_density_grid(self,data,s_eps,attr_eps):
        '''
            data is a Two-dimensional matrix，row：lon; column:lat;
        '''
        rows,cols = data.shape
        # zero_num = np.where(data==0,1,0).sum()
        nan_num = np.where(np.isnan(data),1,0).sum()
        # density_list_len = rows*cols - zero_num - nan_num
        density_list_len = rows*cols - nan_num
        density = np.zeros(density_list_len,dtype=np.float32)
        num = 0
        for i in range(rows):
            for j in range(cols):
                #* 计算每个点的邻域范围:
                left_lon = i-s_eps if i-s_eps>=0 else 0
                rigth_lon = i+s_eps if i+s_eps<rows else rows
                up_lat = j-s_eps if j-s_eps>=0 else 0
                down_lat = j+s_eps if j+s_eps<cols else cols
                s_near = data[left_lon:rigth_lon+1,up_lat:down_lat+1]
                # s_near = s_near[np.where((~np.isnan(s_near)) & (s_near!=0))]
                s_near = s_near[np.where((~np.isnan(s_near)))]
                # if(data[i,j]!=0 and (not np.isnan(data[i,j]))):
                if(not np.isnan(data[i,j])):
                    density[num] = np.exp(-1*((1-(np.abs(s_near-data[i,j])))/attr_eps)**2).sum()
                    num+=1
                pass
            pass
        self.density = density
        return density
    
    
    @fn_timer("calc_gaus_density_cube")
    # @njit
    def calc_gaus_density_cube(self,data,s_eps,t_eps,attr_eps):
        '''
            此处 data 为立方体数据，三个维度：time,lon,lat
        '''
        time_len,rows,cols = data.shape
        # zero_num = np.where(data==0,1,0).sum()
        nan_num = np.where(np.isnan(data),1,0).sum()
        # density_list_len = time_len*rows*cols - zero_num - nan_num
        density_list_len = time_len*rows*cols - nan_num
        density = np.zeros(density_list_len,dtype=np.float32)
        num = 0
        for i in range(rows):
            for j in range(cols):
                for k in range(time_len):
                    #* 计算每个点的邻域范围:
                    left_lon = i-s_eps if i-s_eps>=0 else 0
                    rigth_lon = i+s_eps if i+s_eps<rows else rows
                    up_lat = j-s_eps if j-s_eps>=0 else 0
                    down_lat = j+s_eps if j+s_eps<cols else cols
                    early_time = k-t_eps if k-t_eps>=0 else 0
                    lated_time = k+t_eps if k+t_eps<time_len else time_len
                    s_near = data[early_time:lated_time+1,left_lon:rigth_lon+1,up_lat:down_lat+1]
                    # s_near = s_near[np.where((~np.isnan(s_near)) & (s_near!=0))]
                    s_near = s_near[np.where((~np.isnan(s_near)))]
                    # if(data[k,i,j]!=0 and (not np.isnan(data[k,i,j]))):
                    if(not np.isnan(data[k,i,j])):
                        density[num] = np.exp(-1*((1-(np.abs(s_near-data[k,i,j])))/attr_eps)**2).sum()
                        num+=1
                    pass
                pass
            pass
        
        return density