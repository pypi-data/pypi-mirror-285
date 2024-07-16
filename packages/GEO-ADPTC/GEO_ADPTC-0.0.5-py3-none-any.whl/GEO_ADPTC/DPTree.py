import numpy as np
from .auxiliary import *

class DPTree():
    def __init__(self) -> None:
        self.node_count = 0
        self.node_dir = {}
        self.root_node = None
        self.node_offspring = {}
        self.sorted_gamma_index = None
        pass

    @fn_timer("createTree")
    def createTree(self,X,sorted_gamma_index,closest_node_id,closest_dis_denser,local_density,gamma):
        #* create tree by the sorted gamma
        node_dir = {}
        node_created = np.zeros(len(sorted_gamma_index))
        self.sorted_gamma_index = sorted_gamma_index
        for i in range(len(sorted_gamma_index)):
            node_id = sorted_gamma_index[i]
            parent_id = closest_node_id[node_id]
            attr_list = X[node_id]
            dist_to_parent = closest_dis_denser[node_id]
            density = local_density[node_id]
            if(node_created[node_id]==0):
                node = Node(node_id,attr_list,parent_id,dist_to_parent=dist_to_parent,density=density,gamma=gamma[node_id],children=[])
                node_created[node_id] = 1
                node_dir[node_id] = node
            node_dir[node_id].setParentId(parent_id)
            if(node_created[parent_id]==0):
                parent_node = Node(parent_id,X[parent_id],parent_id=None,dist_to_parent=closest_dis_denser[parent_id],density=local_density[parent_id],gamma=gamma[parent_id],children=[])
                node_created[parent_id] = 1
                node_dir[parent_id] = parent_node
            parent_node = node_dir[parent_id]
            cur_node = node_dir[node_id]
            if(node_id != parent_id):
                parent_node.addChild(node_id)
            
        self.root_node = node_dir[sorted_gamma_index[0]]
        self.node_dir = node_dir
        self.node_count = len(sorted_gamma_index)
        pass
    
    
    def get_subtree_offspring_id(self,node_id,other_idlist):
        '''
            get the offspring id list of the subtree
            node_id : root node id of the subtree.
        '''
        def fn_get_subtree_offspring_id(node_id,offspring_idlist):
            if(node_id in self.node_offspring.keys()):
                return self.node_offspring[node_id]
            else:
                node = self.node_dir[node_id]
                children = node.getChildren()
                child_num = len(children)
                if(child_num==0):
                    self.node_offspring[node_id] = offspring_idlist
                    return offspring_idlist
                offspring_idlist= list(offspring_idlist) + children
                for i in children:
                    child_offspring_idlist = fn_get_subtree_offspring_id(i,[])
                    self.node_offspring[i] = child_offspring_idlist
                    offspring_idlist= list(offspring_idlist) + child_offspring_idlist
                    pass
                self.node_offspring[node_id] = offspring_idlist
                return offspring_idlist             
        offspring_idlist = fn_get_subtree_offspring_id(node_id,[])
        return np.array(list(offspring_idlist) + other_idlist)


    def remove_subtree(self,child_id):
        offspring_id = self.get_subtree_offspring_id(child_id,[child_id])
        offspring_len = len(offspring_id)
        node_id = self.node_dir[child_id].getParentId()
        node = self.node_dir[node_id]
        node.removeChild(child_id)
        self.node_count = self.node_count-offspring_len
        if(node_id in self.node_offspring.keys()):
            for node_to_delete in offspring_id:
                self.node_offspring[node_id].remove(node_to_delete)
                # print("删除子孙节点:",node_to_delete)
                pass
            pass
        #* create new subtree:
        new_tree = DPTree()
        for i in offspring_id:
            removed_node = self.node_dir.pop(i)
            new_tree.node_dir[i] = removed_node
            pass
        new_tree.node_count = offspring_len
        new_tree.root_node = new_tree.node_dir[child_id]
        new_tree.root_node.setParentId(child_id)
        return new_tree
    


    def calcu_neighbor_btw_subtree(self,node_id_one,node_id_two,mixin_near_matrix):
        '''
            get the neighbor nodes between two subtrees
        '''
        connected_nodes = np.array([],dtype=np.int32)
        offspring_one = self.get_subtree_offspring_id(node_id_one,[node_id_one])
        offspring_two = self.get_subtree_offspring_id(node_id_two,[node_id_two])
        pairs_nodes = []
        for i in offspring_two:
            connected_nodes_index = np.intersect1d(mixin_near_matrix[i],offspring_one)
            if len(connected_nodes_index)>0:
                for j in connected_nodes_index:
                    pairs_nodes.append([i,j])
                    pass
                pass
        if(len(pairs_nodes)==0):
            return pairs_nodes,connected_nodes
        return np.array(pairs_nodes), np.unique(np.array(pairs_nodes).flatten())
    
    def calcu_depth(self,node_id, depth):
        node = self.node_dir[node_id]
        parent_id = node.getParentId()
        if(node_id==parent_id):
            return depth
        else:
            return self.calcu_depth(parent_id,depth+1)
        


class Node():
    def __init__(self,node_id,attr_list,parent_id=None,dist_to_parent=None,density=None,gamma=None,children=[]) -> None:
        self.node_id = node_id
        self.attr_list = attr_list
        self.parent_id = parent_id
        self.dist_to_parent = dist_to_parent
        self.density = density
        self.children = children
        self.gamma = gamma
        pass
    
    def addChild(self,child):
        self.children+=[child]

    def removeChild(self,child):
        self.children.remove(child)
    
    def resetChildren(self):
        self.children = []

    def setParentId(self,parent_id):
        self.parent_id = parent_id

    def getAttr(self):
        return self.attr_list

    def getNodeId(self):
        return self.node_id

    def getParentId(self):
        return self.parent_id
    
    def getDistToParent(self):
        return self.dist_to_parent
    
    def getDensity(self):
        return self.density

    def getGamma(self):
        return self.gamma

    def getChildren(self):
        return self.children
    
    def hasChildren(self,child_id):
        if child_id in self.children:
            return True
        else:
            return False
        
        
