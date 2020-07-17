from __future__ import division

import sys
from os import path

#sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))

import pandas as pd;
import numpy as np;
from scipy import spatial;
import json

from mipframework import Algorithm, AlgorithmResult
from mipframework import TabularDataResource
from mipframework import create_runner
from mipframework.highcharts.user_defined import BubbleGridPlot

from utils.algorithm_utils import ExaremeError

# import sys;
# sys.stdout = sys.__stdout__
# import pdb; pdb.set_trace()

def initialize_centroids_localpart(y, y_name, n_clusters, random_state = 123 ):
    np.random.RandomState(random_state)
    random_idx = np.random.permutation(y.shape[0])
    clsize = int( y.shape[0] / n_clusters )
    clcentercount = [ y.loc[random_idx[clsize*clid + 1*clid : min(clsize*(clid+1) + 1*clid, y.shape[0]-1 )]].shape[0] for clid in range(n_clusters) ]
    clcentersum = [ y.loc[random_idx[clsize*clid + 1*clid : min(clsize*(clid+1) + 1*clid, y.shape[0]-1 )]].sum() for clid in range(n_clusters) ]
    clcentersumDict = dict()
    for var_name in y_name:
        clcentersumDict[var_name] = [clcentersum[clid][var_name] for clid in range(n_clusters)]
    return clcentersumDict, clcentercount

def compute_centroids_globalpart(y_name, n_clusters, clcentersumDict, clcentercount):
    clcentroidsDict = dict()
    for var_name in y_name:
        clcentroidsDict[var_name] = [clcentersumDict[var_name][clid]/ clcentercount[clid] for clid in range(n_clusters)]
    return clcentroidsDict

def compute_distance(y, centroids, n_clusters):
    centroidsDataframe = pd.DataFrame.from_dict(centroids) # Auto isws to kanw apo thn arxh!!!
    distance = np.zeros((y.shape[0], n_clusters))
    for id in xrange(y.shape[0]):
        distance[id] = [spatial.distance.euclidean(y.iloc[id],centroidsDataframe.iloc[clid]) for clid in range(n_clusters)]
    return distance

def find_closest_cluster(distance):
    return np.argmin(distance, axis=1)

def compute_centroids_localpart(y, y_name, n_clusters, labels):
    clcentercount = [ y[labels == clid].shape[0] for clid in range(n_clusters) ]
    clcentersum = [ y[labels == clid].sum() for clid in range(n_clusters) ]
    clcentersumDict = dict()
    for var_name in y_name:
        clcentersumDict[var_name] = [clcentersum[clid][var_name] for clid in range(n_clusters)]
    return clcentersumDict, clcentercount

def compute_cluster_size(labels, n_clusters):
    clsize = np.zeros(n_clusters)
    for clid in xrange(n_clusters):
        clsize[clid] = labels[ labels == clid ].shape[0]
    return clsize

class kMeans(Algorithm):

    def __init__(self, cli_args):
        super(kMeans, self).__init__(__file__, cli_args)

    def local_init(self):
        y = self.data.variables
        y_name = list(y.columns)

        if ( self.parameters.k == '' and self.parameters.centers =='' ) or ( self.parameters.k != '' and self.parameters.centers !=''):
            raise ExaremeError("Only one of the following two parameters should be empty/have value: Centers or k")
        elif self.parameters.k != '':
            k = int(self.parameters.k)
            clcentersumDict, clcentercount = initialize_centroids_localpart(y, y_name, k)
            self.push_and_add_dict(clcentersumDict = clcentersumDict)
            self.push_and_add_list(clcentercount = clcentercount)
        self.push_and_agree(y_name=y_name)

    def global_init(self):
        iter_ = 0

        y_name = self.fetch("y_name")

        if self.parameters.k != '':
            k = int(self.parameters.k)
            clcentersumDict = self.fetch("clcentersumDict")
            clcentercount = self.fetch("clcentercount")
            clcentroidsDict = compute_centroids_globalpart(y_name, k, clcentersumDict, clcentercount)
        elif self.parameters.centers != '':
            clcentroidsDict = json.loads(self.parameters.centers)
            k = len(clcentroidsDict[y_name[0]])

        self.store( iter_  = iter_ )
        self.store( y_name  = y_name )
        self.store( k  = k )
        self.store( clcentroidsDict = clcentroidsDict )

        self.push( k = k )
        self.push( clcentroidsDict = clcentroidsDict )

    def local_step(self):
        y = self.data.variables
        y_name = list(y.columns)

        k = self.fetch ("k")
        clcentroidsDict = self.fetch("clcentroidsDict")

        distances = compute_distance(y, clcentroidsDict, k)
        labels = find_closest_cluster(distances)
        clcentersumDict, clcentercount = compute_centroids_localpart(y, y_name, k, labels)

        self.push_and_add_dict(clcentersumDict = clcentersumDict)
        self.push_and_add_list(clcentercount = clcentercount)


    def global_step(self):
        e = float(self.parameters.e)
        max_iter = float(self.parameters.iterations_max_number)
        k = self.load("k")
        iter_ = self.load("iter_")
        y_name = self.load("y_name")
        old_clcentroidsDict = self.load("clcentroidsDict")

        clcentersumDict = self.fetch("clcentersumDict")
        clcentercount = self.fetch("clcentercount")

        clcentroidsDict = compute_centroids_globalpart(y_name, k, clcentersumDict, clcentercount)

        # Verify termination condition
        iter_ += 1
        diff = []
        for var_name in y_name:
            diff = diff + [a-b for a,b in zip(clcentroidsDict[var_name], old_clcentroidsDict[var_name])]
        if max(diff) < e or iter_ >= max_iter:
            self.terminate()
        self.store(k  = k )
        self.store(iter_  = iter_ )
        self.store(y_name  = y_name )
        self.push(clcentroidsDict = clcentroidsDict)

    def local_final(self):
        y = self.data.variables
        y_name = list(y.columns)

        k = self.fetch ("k")
        clcentroidsDict = self.fetch("clcentroidsDict")

        distances = compute_distance(y, clcentroidsDict, k)
        labels = find_closest_cluster(distances)
        clsize = compute_cluster_size(labels, k)

        self.push_and_add_list(clsize = clsize)

        #Prediction
        if self.parameters.datapoint !="":
            subjectcodecolumn =  self.data.full['subjectcode']
            datasetcolumn = self.data.full['dataset']
            datapoint = json.loads(self.parameters.datapoint)
            distances = compute_distance(pd.DataFrame.from_dict(datapoint), clcentroidsDict, k)
            closestclusterid = find_closest_cluster(distances)
            similar_datasetcolumn = datasetcolumn[labels == closestclusterid]
            similar_subjectcodecolumn = subjectcodecolumn[labels == closestclusterid]
            similar_y = y[labels == closestclusterid]

            temp = pd.concat([similar_datasetcolumn,similar_subjectcodecolumn],axis =1)
            similar_data = pd.concat([temp, similar_y],axis =1)

            self.push_and_concat(similar_data = similar_data)


    def global_final(self):
        k = self.fetch("k")
        y_name = self.load("y_name")
        clcentroidsDict = self.fetch("clcentroidsDict")
        clsize = self.fetch("clsize")

        ###########################################################################
        #Kmeans results
        result1_json = [{ "clid" : i+1 , "clpoints" : clsize[i]} for i in xrange(k)]
        from itertools import product
        for i,var in product(range(k), y_name):
            result1_json[i][var] = clcentroidsDict[var][i]
        reult2_json = {}
        result1_table = TabularDataResource (
            fields = ["cluster id"] + y_name + ["cluster size"],
            data =  [[i] + [clcentroidsDict[var][i] for var in y_name] + [clsize[i]] for i in xrange(k)],
            title="k-means Summary",)
        result2_table = TabularDataResource (fields = [], data = [], title="")
        result1_hc_bubble = highchartbubble(" k-means result", y_name, clustercentroids = [[clcentroidsDict[var][i] for var in y_name] + [clsize[i]] for i in xrange(k)] )
        result1_hc_scatter3d = highchartscatter3d(" k-means result", y_name, clustercentroids =  [[clcentroidsDict[var][i] for var in y_name] + [clsize[i]] for i in xrange(k)] )


        ###########################################################################
        #Similarity results
        similar_data_dict = {}
        if self.parameters.datapoint !="":
            similar_data = self.fetch("similar_data")
            similar_data_dict = (similar_data.T).to_dict()
            datapoint = json.loads(self.parameters.datapoint)
        result2_json = []
        for key in similar_data_dict:
            result2_json.append(similar_data_dict[key])
        result2_table = TabularDataResource (
            fields = ["subjectcode", "dataset"] + y_name,
            data = [[result2_json[i]['subjectcode'], result2_json[i]['dataset']]+ [result2_json[i][key] for key in y_name] for i in xrange(len(result2_json))],
            title="Similarity results",)

        result1_hc_bubble = highchartbubble(" k-means result", y_name, clustercentroids = [[clcentroidsDict[var][i] for var in y_name] + [clsize[i]] for i in xrange(k)] ,
                                                        mydatapoint = [[datapoint[key][0] for key in y_name] + [1]] ,
                                                        similardatapoints = [[result2_json[i][key] for key in y_name] + [1] for i in xrange(len(result2_json))])
        result1_hc_scatter3d = highchartscatter3d(" k-means result", y_name, clustercentroids = [[clcentroidsDict[var][i] for var in y_name] + [clsize[i]] for i in xrange(k)] ,
                                                mydatapoint = [[datapoint[key][0] for key in y_name] + [1]] ,
                                                similardatapoints = [[result2_json[i][key] for key in y_name] + [1] for i in xrange(len(result2_json))])

        self.result = AlgorithmResult(
            raw_data=[result1_json,result2_json],
            tables=[result1_table, result2_table],
            highcharts=[result1_hc_bubble, result1_hc_scatter3d],
        )

class highchartbubble:
    def __init__(self, title, y_name, **kwargs ):
        self.title = title
        self.y_name = y_name
        self.dataseries = {}
        for key in kwargs:
            self.dataseries[key] = kwargs[key]

    def render(self):
        hc_result =  { "type" : "application/vnd.highcharts+json",
                            "data" : { "chart" : { "type": "bubble",  "plotBorderWidth": 1, "zoomType": "xy"},
                                       "title" : { "text": self.title }
                                     }
                          }
        if len(self.y_name) != 2:
            hc_result["data"]["subtitle"] = {"text":"This plot is empty as there are not two variables "}
        elif max([len(self.dataseries[key]) for key in self.dataseries])==0:
            hc_result["data"]["subtitle"] = {"text":"This plot is empty as there are not enough data points"}
        else:
            hc_result["data"]["xAxis"] = { "gridLineWidth": 1, "title": {"text": self.y_name[0], "align":"middle" }}
            hc_result["data"]["yAxis"] = { "gridLineWidth": 1, "title": {"text": self.y_name[1], "align":"middle" }}
            hc_result["data"]["series"] = []
            for key in self.dataseries:
                hc_result["data"]["series"].append({ "data": self.dataseries[key]})

        hc_result = json.dumps(hc_result)
        return hc_result


class highchartscatter3d:
    def __init__(self, title, y_name, **kwargs):
        self.title = title
        self.y_name = y_name
        self.dataseries = {}
        for key in kwargs:
            self.dataseries[key] = kwargs[key]

    def render(self):
        hc_result =  { "type": "application/vnd.highcharts+json",
                       "data": { "chart": { "renderTo": 'container',
                                "margin": 100,
                                "type": "scatter3d",
                                "animation": "false",
                                "options3d": {  "enabled": "true", "alpha": 10, "beta": 30, "depth": 250,"viewDistance": 5, "fitToPlot": "false",
                                                "frame": { "bottom": { "size": 1, "color": "rgba(0,0,0,0.02)" },
                                                "back": { "size": 1, "color": "rgba(0,0,0,0.04)" },
                                                "side": { "size": 1, "color": "rgba(0,0,0,0.06)" }}}},
                                "title": { "text": self.title}}}

        if len(self.y_name) != 3:
            hc_result["data"]["chart"]["subtitle"] = { "text": "This plot is empty as there are not three variables" }
        elif max([len(self.dataseries[key]) for key in self.dataseries])==0:
            hc_result["data"]["chart"]["subtitle"] = { "text": "This plot is empty as there are not data points" }
        else:
            hc_result["data"]["chart"]["xAxis"] = {"gridLineWidth": 1 , "title": {"text": "x: " + self.y_name[0] + "","align": "middle"}},
            hc_result["data"]["chart"]["yAxis"] = {"gridLineWidth": 1 , "title": {"text": "y: " + self.y_name[1] + "","align": "middle"}},
            hc_result["data"]["chart"]["zAxis"] = {"gridLineWidth": 1 , "title": {"text": "z: " + self.y_name[2] + "","align": "middle"}},
            hc_result["data"]["chart"]["series"] = [{"colorByPoint": "true",
                                                     "data": self.data ,
                                                     "marker": {"radius": 5}}]
        hc_result = json.dumps(hc_result)

        return hc_result






if __name__ == "__main__":
    import time

    algorithm_args = [
        "-y",           "lefthippocampus,righthippocampus",
        "-k",           "",
        "-centers",     """{"lefthippocampus":[1.7, 2.5], "righthippocampus":[1.5, 2.0]}""",
        "-datapoint",   """{"lefthippocampus":[1.2], "righthippocampus":[1.5]}""",
        "-e",           "0.0001",
        "-iterations_max_number",    "50",
        "-pathology",   "dementia",
        "-dataset",     "desd-synthdata",
        "-filter",      ""
    ]

    runner = create_runner(
        kMeans, num_workers=2, algorithm_args=algorithm_args,
    )
    start = time.time()
    runner.run()
    end = time.time()
    print("Completed in ", end - start)
