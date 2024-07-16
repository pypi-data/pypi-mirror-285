""" Network DAG Processing

Docs::

  https://www.timlrx.com/blog/benchmark-of-popular-graph-network-packages

   benchmark was carried out using a Google Compute n1-standard-16 instance (16vCPU Haswell 2.3GHz, 60 GB memory). I compare 5 different packages:

  graph-tool
  igraph
  networkit
  networkx
  snap

  Full results can be seen from  table below:


  dataset	Algorithm	graph-tool	igraph	networkit	networkx	snap
  Google	connected components	0.32	2.23	0.65	21.71	2.02
  Google	k-core	0.57	1.68	0.06	153.21	1.57
  Google	loading	67.27	5.51	17.94	39.69	9.03
  Google	page rank	0.76	5.24	0.12	106.49	4.16
  Google	shortest path	0.20	0.69	0.98	12.33	0.30

  Pokec	connected components	1.35	17.75	4.69	108.07	15.28
  Pokec	k-core	5.73	10.87	0.34	649.81	8.87
  Pokec	loading	119.57	34.53	157.61	237.72	59.75
  Pokec	page rank	1.74	59.55	0.20	611.24	19.52
  Pokec	shortest path	0.86	0.87	6.87	67.15	3.09

    https://networkit.github.io/


    https://pyvis.readdocs.io/en/latest/index.html#


    https://deepgraph.readdocs.io/en/latest/what_is_deepgraph.html


    https://towardsdatascience.com/pyviz-simplifying--data-visualisation-process-in-python-1b6d2cb728f1


    https://graphviz.org/





"""
import os, glob, sys, math, time, json, functools, random, yaml, gc, copy, pandas as pd, numpy as np
from itertools import combinations
import datetime
from box import Box
from typing import Union
from warnings import simplefilter  ; simplefilter(action='ignore', category=FutureWarning)
import warnings
with warnings.catch_warnings():
    pass


from utilmy import pd_read_file, os_makedirs, pd_to_file, glob_glob, json_load


#############################################################################################
from utilmy import log, log2, os_module_name

def help():
    """function help        """
    from utilmy import help_create
    print( help_create(__file__) )



#############################################################################################
def test_all() -> None:
    """ python  $utilmy/deeplearning/util_topk.py test_all         """
    log(os_module_name(__file__))
    test1()


def test1():
    pass


def test_get_amazon():
    # https://drive.google.com/file/d/1WuLFU595Bh2kd9lEWX_Tv43FYWW5BUW2/view?usp=sharing
    file_id = '1WuLFU595Bh2kd9lEWX_Tv43FYWW5BUW2' #<-- You add in here  id from you google drive file, you can find it

    from utilmy.util_download import google_download
    google_download(url_or_id= file_id , fielout='amazon0302.txt')




def test_pd_create_dag(nrows=1000, n_nodes=100):
    aval = np.random.choice([ str(i) for i in range(n_nodes)], nrows )
    bval = np.random.choice([ str(i) for i in range(n_nodes)], nrows )

    w    = np.random.random(nrows )

    d = {'a': aval, 'b': bval, 'w': w }
    df = pd.DataFrame(d )
    return df



############################################################################################################################
def generate_click_data(cfg: str, name='simul', T=None, dirout='data_simulation.csv'):
    """
    Generate a dataframe with sampled items and locations with binomial sampling

    Returns:
    - dataframe: A pandas DataFrame with  following columns:
        - ts: Timestamp (int)
        - userid: ID (int)
        - itemid: Item ID (int)
        - is_clk: Binary reward (1 for click, 0 for no click) sampled from  given probabilities. (int)


    """
    # cfg0 = config_load(cfg) if isinstance(cfg, str) else cfg
    # cfg1 = cfg0[name]
    # T    = cfg1['T']  if T is None else T
    T = 100
    item_probas = np.arange(1, 50 ) / 100.0
    item_cats   = { i:np.random.randint(10) for i in range(0, len(item_probas))   }
    nuser       = 5

 
    ### Generate Simulated Click  ###############################################
    data = []
    for userid in range(0, nuser):
        for ts in range(T):
            #### Check if each itemis was clicked or not : indepdantn bernoulli.
            for itemid, pi in  enumerate(item_probas): 
                is_clk    = binomial_sample(pi)[0]
                data.append([ts, int(userid), int(itemid), is_clk])

    df = pd.DataFrame(data, columns=['ts', 'userid', 'itemid', 'is_clk'])
    df['item_cat1'] = df['itemid'].apply(lambda x : item_cats[x] ) 


    ### Stats Check
    dfg = df.groupby(['itemid']).agg({'is_clk': 'sum', 'ts': 'count'}).reset_index()
    dfg.columns = ['itemid', 'n_clk', 'n_imp']
    dfg['ctr'] = dfg['n_clk'] / dfg['n_imp']


    dfg2 = df.groupby(['itemid', 'userid']).agg({'is_clk': 'sum', 'ts': 'count'}).reset_index()
    dfg2.columns = ['itemid', 'userid', 'n_clk', 'n_imp']


    if dirout is not None:
        pd_to_file(df, dirout, index=False, show=1)
        pd_to_file(dfg,  dirout.replace(".csv", "_stats.csv"), index=False, show=1)        
        pd_to_file(dfg2, dirout.replace(".csv", "_stats2.csv"), index=False, show=1)        
        
    return df


def binomial_sample(p: float, size: int = 1, n: int = 1):
    return np.random.binomial(n=n, p=p, size=size)


def create_graph_df(df=None, dirin=None, dirout=None):
    """
    Goal : tabular data --> Graph format.

            python util_graph.py create_graph_df

            python util_graph.py create_graph_df --dirout ztmp/

            python util_graph.py create_graph_df --dirin myfile.csv 


    ### Generate those dataframes:
            df_nodes:
            id, name, cat1,

            df_edges_item_item:
            id1, id2, edge_type
                            1

            df_edges_item_cat1:
            id1, id2, edge_type
                            2

            df_edges_cat1_cat1:
            id1, id2, edge_type
                            3

    """

    if isinstance(dirin,str):
        df = pd_read_file(dirin) 

    elif isinstance(df, pd.DataFrame):    
        pass 

    else:    
        df = generate_click_data(cfg='config', name='simul', T=None, dirout='data_simulation.csv')
    # assert df[[ 'userid', 'itemid', 'item_cat1', 'is_clk' ]]


    ######### *create Node dataframes for graph
    # Extract unique user IDs, item IDs
    unique_user_ids = df['userid'].unique()
    df_user = pd.DataFrame({'userid': unique_user_ids})
    df_item = df[['itemid','item_cat1']].drop_duplicates()
    df_cat = df[['item_cat1']].drop_duplicates()


    ######### *Create edges DataFrames for graph
    # a. for user-item interactions -->  user cliked on  item and  number of times he/she clicked
    df_user_item = df[df['is_clk'] == 1][['userid', 'itemid']]
    df_user_item = df_user_item.groupby(['userid', 'itemid']).size().reset_index(name='n_clk')

    #b. for item-category relationships -->  item belongs to which category
    df_item_cat = df[['itemid', 'item_cat1']].drop_duplicates()


    # c. for item item relationships --> if  item is cliked by  same user along with  number of times users clicked,cooccurence 
    df_item_item = df[df['is_clk'] == 1][['userid', 'itemid']]
    # Create a merge/join operation to find item-item relationships
    df_item_item = df_item_item.merge(df_item_item, on='userid', suffixes=('_1', '_2'))
    df_item_item = df_item_item[df_item_item['itemid_1'] != df_item_item['itemid_2']]
    df_item_item = df_item_item[['itemid_1', 'itemid_2']]
    # Create a filter to select rows where 'itemid_1' is greater than 'itemid_2'
    dfc_item = df_item_item[df_item_item['itemid_1'] > df_item_item['itemid_2']]
    # Group  filtered DataFrame by  pair of items and count occurrences
    df_item_item = dfc_item.groupby(['itemid_1', 'itemid_2']).size().reset_index(name='n_clk')


    # d. for category category relationships, if  category is cliked by  same user along with  number of times he/she clicked,
    df_cat_cat = df[df['is_clk'] == 1][['userid', 'item_cat1']]
    # Create a merge/join operation to find category-category relationships
    df_cat_cat = df_cat_cat.merge(df_cat_cat, on='userid', suffixes=('_1', '_2'))
    df_cat_cat = df_cat_cat[df_cat_cat['item_cat1_1'] != df_cat_cat['item_cat1_2']]
    df_cat_cat = df_cat_cat[['item_cat1_1', 'item_cat1_2']]
    # Create a filter to select rows where 'item_cat1_1' is greater than 'item_cat1_2'
    dfc = df_cat_cat[df_cat_cat['item_cat1_1'] > df_cat_cat['item_cat1_2']]
    # Group  filtered DataFrame by  pair of categories and count occurrences
    df_cat_cat = dfc.groupby(['item_cat1_1', 'item_cat1_2']).size().reset_index(name='n_clk')


    #### Save nodes #########################################################
    from box import Box
    from utilmy import pd_to_file
    ll = [ 'df_user', 'df_item', 'df_cat', 'df_item_item', 'df_item_cat', 'df_cat_cat', 'df_user_item'
         ]

    dd = Box({})
    for namei in ll :
        dfi = locals()[namei]
        if len(namei.split("_")) > 2:
             x2 = namei.replace("df", 'edge')
             if dirout:
                 pd_to_file(dfi,  dirout + f"/edges/{x2}.parquet", show=1)
        else:
             x2 = namei.replace("df", 'node')
             if dirout:
                 pd_to_file(dfi,  dirout + f"/nodes/{x2}.parquet", show=1)

        dd[namei] = dfi 
    #for ci in ll:
    #    log(ci)
    #    log(locals()[ci].head(5))
    # return df_user, df_item, df_cat, df_item_item, df_item_cat, df_cat_cat, df_user_item
    return dd




def create_graphstorm_config(dirin):
        """ Create graphStorm json config.

        https://graphstorm.readthedocs.io/en/latest/tutorials/own-data.html#the-acm-graph-data-example


        Example of output fro graphStorm




        {
            "nodes": [
                {
                    "node_type": "user",
                    "format": {
                        "name": "parquet"
                    },
                    "files": [
                        "ztmp/graph_raw/nodes/node_user.parquet"
                    ],
                    "node_id_col": "node_id",
                    "features": [
                    ]
                },


                {
                    "node_type": "item",
                    "format": {
                        "name": "parquet"
                    },
                    "files": [
                        "ztmp/graph_raw/nodes/node_item.parquet"
                    ],
                    "node_id_col": "node_id",
                    "features": [
                        {
                            "feature_col": "feat",
                            "feature_name": "feat"
                        },
                        {
                            "feature_col": "item_cat1",
                            "feature_name": "item_cat1",
                            "transform": {
                                "name": "tokenize_hf",
                                "bert_model": "bert-base-uncased",
                                "max_seq_length": 16
                            }
                        }
                    ],


                    "labels": [
                        {
                            "label_col": "item_label",
                            "task_type": "classification",
                            "split_pct": [
                                0.8,
                                0.1,
                                0.1
                            ]
                        }
                    ]
                },


                {
                    "node_type": "itemcat",
                    "format": {
                        "name": "parquet"
                    },
                    "files": [
                        "ztmp/graph_raw/nodes/node_itemcat.parquet"
                    ],
                    "node_id_col": "node_id",
                    "features": [
                        {
                            "feature_col": "feat",
                            "feature_name": "feat"
                        },
                        {
                            "feature_col": "text",
                            "feature_name": "text",
                            "transform": {
                                "name": "tokenize_hf",
                                "bert_model": "bert-base-uncased",
                                "max_seq_length": 16
                            }
                        }
                    ]
                }
            ],







            "edges": [
                {
                    "relation": [ "user", "click", "item" ],
                    "format":   { "name": "parquet" },
                    "files":   [ "ztmp/graph_raw/edges/edge_user_item.parquet" ], 
                    "source_id_col": "userid",
                    "dest_id_col":   "itemid"
                },


                {
                    "relation": [ "item", "linked", "item" ],
                    "format": { "name": "parquet" },
                    "files": [ "ztmp/graph_raw/edges/edge_item_item.parquet" ],
                    "source_id_col": "itemid1",
                    "dest_id_col":   "itemid2"
                },


                {
                    "relation": [ "paper", "citing", "paper" ],
                    "format": { "name": "parquet" }, "files": [ "ztmp/graph_raw/edges/paper_citing_paper.parquet" ],
                    "source_id_col": "source_id",
                    "dest_id_col": "dest_id"
                }

            ]
        }


        """
        
        # Edit the config file manually to provide basic information about the graph
        # for each node mention the id column, ramining will be considered as features
        # for each edge mention the source and destination id column, remaining will be considered as features
        nodes_info_dict = {
            "node_user": {"id_col": "userid"},
            "node_item": {"id_col": "itemid"},
            "node_cat": {"id_col": "item_cat1"},
        }
        edges_info_dict = {
            "edge_user_item": {"source_id_col": "userid", "dest_id_col": "itemid", "relation": [ "user", "click", "item" ]},
            "edge_item_cat": {"source_id_col": "itemid", "dest_id_col": "item_cat1", "relation": [ "item", "linked", "category" ]},
            "edge_item_item": {"source_id_col": "itemid_1", "dest_id_col": "itemid_2", "relation": [ "item", "linked", "item" ]},
            "edge_cat_cat": {"source_id_col": "item_cat1_1", "dest_id_col": "item_cat1_2", "relation": [ "category", "linked", "category" ]},
        }
        # node dict template to be used for each node
        base_node_dict = {
                "node_type": "",
                "format": {
                    "name": "parquet"
                },
                "files": [
                ],
                "node_id_col": "",
                "features": [
                ]
            }
        
        # edge dict template to be used for each edge
        base_edge_dict = {
                    "relation":"",
                    "format":   { "name": "parquet" },
                    "files":   [

                    ], 
                    "source_id_col": "",
                    "dest_id_col":   ""
                }
        # put here the information about the transformation to be applied on which feature
        transform_feature_list = ["item_cat1"]
        transform = {
                        "name": "tokenize_hf",
                        "bert_model": "bert-base-uncased",
                        "max_seq_length": 16
                    }
         
        # put here the information about the node you want label for and the lable column and the task type
        lable_node_info = {"node_item": [
                        {
                            "label_col": "item_cat1",
                            "task_type": "classification",
                            "split_pct": [
                                0.8,
                                0.1,
                                0.1
                            ]
                        }
                    ]
        }


        ######  Automate the creation of the config file
        # dictionary to store the nodes and edges information
        DGL_dict = {}
        DGL_dict["nodes"] = []
        DGL_dict["edges"] = []

        ######  Nodes
        nodes_path_list = [x for x in glob.glob(dirin + "/nodes/*.parquet")]
        for node_path in nodes_path_list:
            print(node_path)
            node_name = node_path.split("/")[-1].split(".")[0]
            id_name = nodes_info_dict[node_name]["id_col"]
            df_node = pd_read_file(node_path)
            feature_names = [x for x in df_node.columns if x != id_name]
            node_dict = base_node_dict.copy()
            
            # add node information to the dictionary
            node_dict["node_type"] = node_name.split("_")[1]
            node_dict["files"] = [node_path]
            node_dict["node_id_col"] = id_name

            # add features information to the dictionary
            feature_list = []
            for feature in feature_names:
                feature_dict = {}
                feature_dict["feature_col"] = feature
                feature_dict["feature_name"] = feature
                if feature in transform_feature_list:
                    feature_dict["transform"] = transform
                feature_list.append(feature_dict)
            node_dict["features"] = feature_list

            # add label information to the dictionary
            if node_name in lable_node_info.keys():
                node_dict["labels"] = lable_node_info[node_name]
                
            # add node information to the main dictionary
            DGL_dict["nodes"].append(node_dict)


        ######  Edges
        edges_path_list = [x for x in glob.glob(dirin + "/edges/*.parquet")]
        for edge_path in edges_path_list:
            print(edge_path)
            edge_name = edge_path.split("/")[-1].split(".")[0]
            df_edge = pd_read_file(edge_path)
            source_id_col = edges_info_dict[edge_name]["source_id_col"]
            dest_id_col = edges_info_dict[edge_name]["dest_id_col"]
            feature_names = [x for x in df_edge.columns if x not in [source_id_col, dest_id_col]]
            edge_dict = base_edge_dict.copy()

            # add edge information to the dictionary
            edge_dict["relation"] = edges_info_dict[edge_name]["relation"]
            edge_dict["files"] = [edge_path]
            edge_dict["source_id_col"] = source_id_col
            edge_dict["dest_id_col"] = dest_id_col

            # add features information to the dictionary
            feature_list = []
            for feature in feature_names:
                feature_dict = {}
                feature_dict["feature_col"] = feature
                feature_dict["feature_name"] = feature
                feature_list.append(feature_dict)
            edge_dict["features"] = feature_list

            # add edge information to the main dictionary
            DGL_dict["edges"].append(edge_dict)

        
        # save the dictionary as a json file
        with open("dgl_config.json", "w") as outfile:
            json.dump(DGL_dict, outfile, indent=4)

        return DGL_dict


                









def graphstorm_help():
    """
     
# Setup Environment
        # pyenv global 3.8.13 && python --version
        # python -c 'import os; print(os)'
        # pip3 list 
        pyenv global system ### remove  


#### Setup Conda 
        export CONDA_DIR="/workspace/miniconda"
        export PATH=$CONDA_DIR/bin:$PATH
        echo $PATH
        wget https://repo.anaconda.com/miniconda/Miniconda3-py38_22.11.1-1-Linux-x86_64.sh -O miniconda.sh && \
        chmod a+x miniconda.sh && \
        bash ./miniconda.sh -b -p $CONDA_DIR && \
        rm ./miniconda.sh

        conda init bash 
        which python && which pip 

        echo $PATH

        conda create -n gstorm python==3.8.13
        conda activate gstorm
        which pip 

        ls  
        /workspace/miniconda/envs/gstorm/bin/pip list

        echo $PYTHONPATH



#### Pip install
      python -m  pip install torch==1.13.1+cpu --extra-index-url https://download.pytorch.org/whl/cpu
        pip install dgl==1.0.4 -f https://data.dgl.ai/wheels-internal/repo.html

        ### Check
        pip install graphstorm --dry-run

        pip install graphstorm 
        pip list 


#### Sample test
        export WORKSPACE="$(pwd)/graphstorm"
        cd $WORKSPACE/examples

        python3 acm_data.py --output-path $WORKSPACE/ztmp/acm_raw --output-type raw_w_text



### SSH server install
        sudo apt-get install openssh-server
        sudo /etc/init.d/ssh restart




##### My environment has a GTX 1080 gpu. 
Before installing library below, you should have Nvidia driver and CUDA installed. 

    - Python: 3.10.12
    - OS: Ubuntu-22.04


####  CUDA with the latest version (12.x), 
it may have issues, since dgl may look for cudart.so.11

    pip3 install graphstorm
    pip3 install torch==1.13.1+cu116 --extra-index-url https://download.pytorch.org/whl/cu116
    pip3 install dgl==1.0.4+cu117 -f https://data.dgl.ai/wheels/cu117/repo.html


### SSH server install
        sudo apt-get install openssh-server
        sudo /etc/init.d/ssh restart




#### Then, configure SSH No-password login.
        ssh-keygen -t rsa -f ~/.ssh/id_rsa -N ''
        cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

        https://www.gitpod.io/docs/configure/workspaces/ports


        Test it with ssh 127.0.0.1  
        If it shows ```connection refused```, maybe the ssh server is not installed or started.



#### Fethc Graphstorm Souce Code
        git clone https://github.com/awslabs/graphstorm.git

        [Notice] ```/mnt/h/graphsotrm``` is my workspace. I use ```$WORKSPACE``` to represent it in the following text, you should replace it with your own path.


# Prepare Raw Data
        export WORKSPACE="$(pwd)/graphstorm"
        ls $WORKSPACE
        cd $WORKSPACE/examples

        python3 acm_data.py --output-path $WORKSPACE/ztmp/acm_raw --output-type raw_w_text



The output will look like the screenshot below. It shows the information of author nodes, which indicates that the “text” column contains text feature.

<img src="./raw_data.png" width = "600" height = "400" alt="1" align=center />

##### Construct Graph
        python3 -m graphstorm.gconstruct.construct_graph \
                --conf-file $WORKSPACE/ztmp/acm_raw/config.json \
                --output-dir $WORKSPACE/ztmp/acm_nc \
                --num-parts 1 \
                --graph-name acm



# Launch GraphStorm Trainig without Fine-tuning BERT Models
        rm /tmp/ip_list.txt

### SSH server install
        sudo apt-get install -y openssh-server
        sudo /etc/init.d/ssh restart

        ssh-keygen -t rsa -f ~/.ssh/id_rsa -N ''
        cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

        touch /tmp/ip_list.txt
        echo 127.0.0.1 >  /tmp/ip_list.txt

### kill port
sudo lsof -i :22
sudo kill -9 4535



[Notice] If you only have one GPU, ```--num-trainers``` should be 1, or the trainning can't be launched.

        source activate gstorm

        python -c 'import graphstorm; print(graphstorm)'

        python -m graphstorm.run.gs_node_classification \
                --workspace $WORKSPACE \
                --part-config $WORKSPACE/ztmp/acm_nc/acm.json \
                --ip-config  "/tmp/ip_list.txt" \
                --num-trainers 1 \
                --num-servers 1 \
                --num-samplers 0 \
                --ssh-port 22 \
                --cf $WORKSPACE/examples/use_your_own_data/acm_lm_nc.yaml \
                --save-model-path $WORKSPACE/acm_nc/models \
                --node-feat-name paper:feat author:feat subject:feat




    """











############################################################################################################################
class  GraphDataLoader(object):
    def __init__(self,):
        """
        Load/save/convert data into parquet, pandas dataframe

            mygraph242423/
                edges.parquet
                nodes.parquet
                meta.json
                    

        load(dirin,  )
            -->  edges: pd.Dataframe ( 'node_a', 'node_b' 'weight', 'edge_type' ] 
                verteex :  pd.daframe('node_id'  , 'node_int',  'col1', 'col2' ]
                meta : dict of metatada
                            
                
        save(dirout)
            os.makedirs

        convert
            (edget, node, meta) --->   networkit or networkx
        """

        self.edges = pd.DafraFrame()
        self.nodes = pd.datarFrame()
        self.nodes_index = {}  #node_idint --> infos
        self.meta = {'cola':  'cola', 'colb': 'cola', 'colvertex': 'colvertex'}



    def load(self, dirin, from_='networkit/networkx'):
        """ Load from disk

        """
        self.nodes = pd_read_file(dirin +"/nodes.parquet")
        self.edges = pd_read_file(dirin +"/edges.parquet")  ### graph        
        self.meta =  json_load(dirin    +"/meta.json")
        self.nodes_index = {}  #node_idint --> infos


        dd = {}
        for x in self.nodex[ 'node_id' ].values :
           dd[ hash(x) ] = x
        self.nodes_index = dd  #node_idint --> infos


    def convert_from(self, graph, from_='networkit/networkx'):
        """ Get From existing network in Memory

        """
        self.nodes = pd.datarFrame()
        self.edges = pd.DafraFrame()

        self.nodes_index = {}  #node_idint --> infos
        self.meta = {}


    def save(self, dirout):
        pass


    def convert_to(self, target='networkit/networkx'):


       if target == 'networkit':
           graph, index = dag_networkit_convert(df_or_file= self.nodes, 
                                 cola= self.meta['cola'], 
                                 colb= self.meta['cola'], colvertex= self.meta['colvertex'], nrows=1000000000)

       return graph, index












############################################################################################################################
############################################################################################################################
def test_networkit(net):
    """Compute PageRank as a measure of node centrality by receiving a NetworkKit graph.


    Docs::
        net  :   NetworkKit graph

        https://networkit.github.io/dev-docs/notebooks/Centrality.html


    """
    import networkit as nk

    df = test_pd_create_dag()

    G, imap = dag_networkit_convert(df_or_file=df, cola='a', colb='b')
    dag_networkit_save(G)

    nk.overview(G)

    ### PgeRank
    pr = nk.centrality.PageRank(net)
    pr.run()
    print( pr.ranking())


def dag_networkit_convert(df_or_file: pd.DataFrame, cola='cola', colb='colb', colvertex="", nrows=1000):
    """Convert a panadas dataframe into a NetworKit graph
      and return a NetworKit graph.


    Docs::
                    df   :    dataframe[[ cola, colb, colvertex ]]
      cola='col_node1'  :  column name of node1
      colb='col_node2'  :  column name of node2
      colvertex=""      :  column name of weight

      https://networkit.github.io/dev-docs/notebooks/User-Guide.html#-Graph-Object


    """
    import networkit as nk, gc
    from utilmy import pd_read_file

    if isinstance(df_or_file, str):
      df = pd_read_file(df_or_file)
    else :
      df = df_or_file
      del df_or_file

    #### Init Graph
    # nodes   = set(df[cola].unique()) + set(df[colb].unique())
    nodes   = set(df[cola].unique()).union(set(df[colb].unique()))
    n_nodes = len(nodes)

    graph = nk.Graph(n_nodes, edgesIndexed=False, weighted = True )
    if colvertex != "":
      weights = df[colvertex].values
    else :
      weights = np.ones(len(df))

    #### Add to Graph
    dfGraph = df[[cola, colb]].values

    # print(df[cola])

    #### Map string ---> Integer, save memory
    # print(str(df))
    if 'int' not in str(df[cola].dtypes):
      index_map = { hash(x):x for x in nodes }
      # for i in range(len(df)):

      for i in range(len(df[[cola, colb]].values)):
          ai = df.iloc[i, 0]
          bi = df.iloc[i, 1]
          graph.addEdge( int(index_map.get( ai, ai)), int(index_map.get( bi, bi)), weights[i])
    else :
      index_map = {   }
      for i in range(len(df)):
          ai = df.iloc[i, 0]
          bi = df.iloc[i, 1]
          graph.addEdge( ai, bi, weights[i])

    return graph, index_map




def dag_networkit_save(net, dirout, format='metis/gml/parquet', tag="", cols= None, index_map=None,n_vertex=1000):
    """Save a NetworkKit graph.


    Docs::
        net     :   NetworkKit graph
        dirout  :   output folder
        format  :   file format 'metis/gml/parquet'
        tag     :   folder suffix

        https://networkit.github.io/dev-docs/notebooks/IONotebook.html


    """
    import json, os, pandas as pd
    dirout = dirout if tag == "" else dirout + "/" + tag + "/"
    os.makedirs(dirout, exist_ok=True)

    ##### Metadata in json  ########################################
    dinfo = {}
    try :
        nodes   = set(df[cola].unique()).union(set(df[colb].unique()))
        n_nodes = len(nodes)
        dinfo = { 'cola':  cola, 'colb': colb, 'colvertex':colvertex, 'n_rows': nrows, 'n_nodes': n_nodes}
    except : pass
    json.dump(dinfo, open(dirout + "/network_meta.json", mode='w'), )


    #####  Main data     ##########################################
    if 'parquet' in format:
          df = np.zeros((n_vertex,2) )
          for i,edge in enumerate(net) :
              df[i,0] = edge[0]
              df[i,1] = edge[1]
              df[i,2] = edge[2]
          cols = cols if cols is not None else ['a', 'b', 'weight']
          df   = pd.DataFrame(df, columns=cols)

          if isinstance(index_map, dict):

            df[cols[0]] = df[cols[0]].apply(lambda x : index_map.get(x, x) )
            df[cols[1]] = df[cols[1]].apply(lambda x : index_map.get(x, x) )
          from utilmy import pd_to_file
          pd_to_file(df, dirout + "/network_data.parquet", show=1)

    else :
        import networkit as nk
        ddict = { 'metis': nk.Format.METIS, 'gml': nk.Format.GML }
        nk.graphio.writeGraph(net, dirout + f'/network_data.{format}' ,  ddict.get(format, 'metis') )

    return dirout


def dag_networkit_load(dirin="", model_target='networkit', nrows=1000, cola='cola', colb='colb', colvertex=''):
    """  Load into network data INTO a framework

    Docs::
            dirin  :   input folder

            https://networkit.github.io/dev-docs/notebooks/IONotebook.html

    """
    import pandas as pd, glob, json
    ddict = { 'metis',  'gml', 'parquet' }

    def is_include(fi, dlist):
        for ext in dlist :
            if ext in fi : return True
        return False
    print(dirin)
    flist0 = glob.glob(dirin, recursive= True)
    print(flist0)
    flist  = [ fi for fi in flist0 if   is_include(fi, ddict )  ]

    if len(flist) == 0 : return None

    if ".parquet" in  flist[0] :
        djson = {}
        try :
           fjson = [fi for fi in flist0 if ".json" in flist0]
           djson = json.load(open(fjson[0], mode='r') )
        except : pass

        cola      = djson.get('cola', cola)
        colb      = djson.get('colb', cola)
        colvertex = djson.get('colvertex', colvertex)


        if model_target == 'networkit':
           net = dag_create_networkit(df_or_file= flist, cola=cola, colb=colb, colvertex=colvertex, nrows=nrows)
        print("return")
        return net

    elif model_target == 'networkit':
        import networkit as nk
        ddict = { 'metis': nk.Format.METIS, 'gml': nk.Format.GML  }
        ext =   flist[0].split("/")[-1].split(".")[-1]
        net = nk.readGraph(dirin, ddict[ext])
        print("return1")
        return net
    else :
      print("return2")
      raise Exception('not supported')









############################################################################################################################
def pd_plot_network(df:pd.DataFrame, cola: str='col_node1', 
                    colb: str='col_node2', coledge: str='col_edge',
                    colweight: str="weight",html_code:bool = True):
    """  Function to plot network https://pyviz.org/tools.html
    Docs::

            df                :        dataframe with nodes and edges
            cola='col_node1'  :        column name of node1
            colb='col_node2'  :        column name of node2
            coledge='col_edge':        column name of edge
            colweight="weight":        column name of weight
            html_code=True    :        if True, return html code
    """

    def convert_to_networkx(df:pd.DataFrame, cola: str="", colb: str="", colweight: str=None):
        """
        Convert a panadas dataframe into a networkx graph
        and return a networkx graph
        Docs::

                df                :        dataframe with nodes and edges
        """
        import networkx as nx
        import pandas as pd
        g = nx.Graph()
        for index, row in df.iterrows():
            g.add_edge(row[cola], row[colb], weight=row[colweight],)

        nx.draw(g, with_labels=True)
        return g


    def draw_graph(networkx_graph, notebook:bool =False, output_filename='graph.html',
                   show_buttons:bool =True, only_physics_buttons:bool =False,html_code:bool  = True):
        """  This function accepts a networkx graph object, converts it to a pyvis network object preserving
        its node and edge attributes,
        and both returns and saves a dynamic network visualization.
        Valid node attributes include:
            "size", "value", "title", "x", "y", "label", "color".
            (For more info: https://pyvis.readdocs.io/en/latest/documentation.html#pyvis.network.Network.add_node)

        Docs::

                networkx_graph:  graph to convert and display
                notebook: Display in Jupyter?
                output_filename: Where to save  converted network
                show_buttons: Show buttons in saved version of network?
                only_physics_buttons: Show only buttons controlling physics of network?
        """
        from pyvis import network as net
        import re
        # make a pyvis network
        pyvis_graph = net.Network(notebook=notebook)

        # for each node and its attributes in  networkx graph
        for node, node_attrs in networkx_graph.nodes(data=True):
            pyvis_graph.add_node(str(node), **node_attrs)

        # for each edge and its attributes in  networkx graph
        for source, target, edge_attrs in networkx_graph.edges(data=True):
            # if value/width not specified directly, and weight is specified, set 'value' to 'weight'
            if not 'value' in edge_attrs and not 'width' in edge_attrs and 'weight' in edge_attrs:
                # place at key 'value'  weight of  edge
                edge_attrs['value'] = edge_attrs['weight']
            # add  edge
            pyvis_graph.add_edge(str(source), str(target), **edge_attrs)

        # turn buttons on
        if show_buttons:
            if only_physics_buttons:
                pyvis_graph.show_buttons(filter_=['physics'])
            else:
                pyvis_graph.show_buttons()

        # return and also save
        pyvis_graph.show(output_filename)
        if html_code:

          def extract_text(tag: str,content: str)-> str:
            reg_str = "<" + tag + ">\s*((?:.|\n)*?)</" + tag + ">"
            extracted = re.findall(reg_str, content)[0]
            return extracted
          with open(output_filename) as f:
            content = f.read()
            head = extract_text('head',content)
            body = extract_text('body',content)
            return head, body
    networkx_graph = convert_to_networkx(df, cola, colb, colweight=colweight)
    head, body = draw_graph(networkx_graph, notebook=False, output_filename='graph.html',
               show_buttons=True, only_physics_buttons=False,html_code = True)
    return head, body







###############################################################################################################
if __name__ == "__main__":
    import fire
    fire.Fire()
    # create_graph_df()





