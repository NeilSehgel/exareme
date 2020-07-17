import requests
import unittest
import os
import json
import logging
import math
from decimal import *

import rpy2.robjects as robjects

import sys
from os import path

sys.path.append(path.abspath(__file__))
from tests import vm_url

endpointUrl = vm_url + "KMEANS"
folderPath = "R_scripts"
file = "kMeans.Rmd"


class TestkMeans(unittest.TestCase):
    def setUp(self):
        filePath = os.path.join(os.path.abspath(folderPath), file)
        with open(filePath, "r") as myfile:
            data = myfile.read()
        # Execute R script
        self.Test1Result, self.Test2Result, self.Test3Result = robjects.r(data)

    def test_KMEANS_1(self):
        logging.info(
            "---------- TEST : KMEANS - desd-synthdata   & 2 variables,  2 clusters"
        )
        data = [
            {"name": "iterations_max_number", "value": "50"},
            {"name": "y", "value": "lefthippocampus,righthippocampus"},
            {"name": "k", "value": ""},
            {
                "name": "centers",
                "value": '{"lefthippocampus":[1.7, 2.5],"righthippocampus":[1.5, 2.0]}',
            },
            {"datapoint" : ""},
            {"name": "pathology", "value": "dementia"},
            {"name": "dataset", "value": "desd-synthdata"},
            {"name": "e", "value": "0.0001"},
            {"name": "filter", "value": ""},
        ]
        headers = {"Content-type": "application/json", "Accept": "text/plain"}
        r = requests.post(endpointUrl, data=json.dumps(data), headers=headers)
        result = json.loads(r.text)
        print("EXAREME", result)
        self.Test1Result = json.loads(self.Test1Result)
        print("1", self.Test1Result)
        resultsComparison(result["result"][0]["data"], self.Test1Result)

    def test_KMEANS_2(self):
        logging.info(
            "---------- TEST : KMEANS - desd-synthdata   & 3 variables,  4 clusters"
        )
        data = [
            {"name": "iterations_max_number", "value": "50"},
            {"name": "y", "value": "rightpallidum,leftpallidum,lefthippocampus"},
            {"name": "k", "value": ""},
            {
                "name": "centers",
                "value": '{"rightpallidum": [0.2, 0.6, 1.0, 1.5],"leftpallidum":[0.5, 1.2, 3.9, 2.0],"lefthippocampus":[1.7, 2.0, 2.5, 3.0]}'
            },
            {"datapoint" : ""},
            {"name": "pathology", "value": "dementia"},
            {"name": "dataset", "value": "desd-synthdata"},
            {"name": "e", "value": "0.0001"},
            {"name": "filter", "value": ""},
        ]
        headers = {"Content-type": "application/json", "Accept": "text/plain"}
        r = requests.post(endpointUrl, data=json.dumps(data), headers=headers)
        result = json.loads(r.text)
        print("EXAREME", result)
        self.Test2Result = json.loads(self.Test2Result)
        print("2", self.Test2Result)
        resultsComparison(result["result"][0]["data"], self.Test2Result)

    def test_KMEANS_3(self):
        logging.info(
            "---------- TEST : KMEANS - desd-synthdata  & 4 variables,  5 clusters"
        )
        data = [
            {"name": "iterations_max_number", "value": "50"},
            {
                "name": "y",
                "value": "rightpallidum,leftpallidum,lefthippocampus,righthippocampus",
            },
            {"name": "k", "value": ""},
            {
                "name": "centers",
                "value": '{"rightpallidum":[0.2,0.6,1.0,1.5,2.0],"leftpallidum":[0.5,1.2,1.5,2.0,2.2],"lefthippocampus":[1.7,2.5,3.9,4.0,2.3],"righthippocampus":[1.5,2.0,2.5,3.0,4.0]}'                            
            },
            {"datapoint" : ""},
            {"name": "pathology", "value": "dementia"},
            {"name": "dataset", "value": "desd-synthdata"},
            {"name": "e", "value": "0.0001"},
            {"name": "filter", "value": ""},
        ]
        headers = {"Content-type": "application/json", "Accept": "text/plain"}
        r = requests.post(endpointUrl, data=json.dumps(data), headers=headers)
        result = json.loads(r.text)
        print("EXAREME", result)
        self.Test3Result = json.loads(self.Test3Result)
        print("3", self.Test3Result)
        resultsComparison(result["result"][0]["data"], self.Test3Result)


def resultsComparison(jsonExaremeResult, jsonRResult):
    Rvariables = json.loads(jsonRResult[0][1])
    Rvariables = [v.split(".")[1] for v in Rvariables]
    Rcenters = json.loads(jsonRResult[0][2])
    Rpoints = json.loads(jsonRResult[0][3])
    ii = 0
    for i in range(len(Rcenters)):
        if Rpoints[i] > 0:
            print(Rpoints[i])
            for j in range(len(Rvariables)):
                print("RR", Rvariables[j], Rcenters[i][j])
                print("EX", jsonExaremeResult[ii][Rvariables[j]])
                assert math.isclose(
                    jsonExaremeResult[ii][Rvariables[j]],
                    Rcenters[i][j],
                    rel_tol=0,
                    abs_tol=10
                    ** (-abs(Decimal(str(Rcenters[i][j])).as_tuple().exponent)),
                )
            print(jsonExaremeResult[ii]["clpoints"], Rpoints[i])
            assert jsonExaremeResult[ii]["clpoints"] == Rpoints[i]
            ii = ii + 1
