#!/usr/bin/env python

# opPtimizer: optimization framework for AI  
# Copyright (c) 2019 Artur Bak. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

#from opp import *

from .opp import *

MED_VER = 5

def medversion():
    return 'm' + str(MED_VER)

WARN_KEY = 'WARN:'
ERROR_KEY = 'ERR:'

P_DIR_SEP = '/'
P_UP_DIR = '..' + P_DIR_SEP
P_NEW_LINE = '\n'

P_PARAM_SEP = ';'

P_DROOT_DEFAULT = '.'
P_DIN_DEFAULT = '_in'
P_DOUT_DEFAULT = '_out'
P_DTRAIN_DEFAULT = '_train'
P_DRAW_DEFAULT = '_raw'

P_SET_DEFAULT_FILENAME = 'inputset'
P_SET_DEFAULT_FILFORMAT = 'csv'

P_TRAINSET_DEFAULT_FILENAME = 'traindata'
P_TESTSET_DEFAULT_FILENAME = 'testdata'
P_VALIDATESET_DEFAULT_FILENAME = 'validatedata'

P_SUMMARY_FILENAME = 'summary-log.txt'
P_EXEC_FILENAME = 'exec-log.txt'
P_RESULT_FILENAME = 'result.txt'
P_TESTLIST_FILENAME = 'testlist.txt'
P_TESTCHAIN_FILENAME = 'testchain-log.txt'

PSERVICE_MAX_PARAMS_MSG_LEN = 1024 * 5
PSERVICE_MAX_REPLY_MSG_LEN = 1024 * 1

P_KEY = 'key'
P_KEY_TESTNAME = 'testName'
P_KEY_TEST = 'test'
P_KEY_ROOTDIR = 'rootDir'
P_KEY_DATADIR = 'dataDir'
P_KEY_TRAINDIR = 'trainDir'
P_KEY_RAWDATADIR = 'rawDataDir'
P_KEY_INPUTDIR = 'inputDir'
P_KEY_OUTPUTDIR = 'outputDir'
P_KEY_MODELDIR = 'modelDir'
P_KEY_IN = 'in'
P_KEY_OUT = 'out'

P_KEY_FILTER = 'filter'

KEY_PREPAREDATA = 'PrepareData'


KEY_WRITE_TESTNAME_TO_RESLT = "testNameInResulfFile"

KEY_PLOT = 'plot'
KEY_PRECISION = 'precision'
KEY_RECALL = 'recall'
KEY_FALLOUT = 'fallout'
KEY_ACCURACY = 'accuracy'
KEY_CLASSIFIER = 'cl'
KEY_RESULTFILE = 'ResultFile'
KEY_DESCRIPTION = 'description'

KEY_COLOR = 'color'
KEY_INVERSE = 'inverse'
VAL_CL_SVM = 'svm' 
VAL_CL_NN = 'nn'
VAL_CL_DT = 'dt'
VAL_CL_GAUSSNB = 'gaussnb'
VAL_CL_RANDFOREST = 'rforest'
VAL_CL_ADABOOST = 'adaboost'
VAL_BEST = 10.0
VAL_BLUE = 'blue'
VAL_RED = 'red'

def oppKey(val):
    return P_KEY + '=' + str(val)

# Sets value for P_KEY_IN
def oppIn(fileName):
    return P_KEY_IN + '=' + str(fileName)

# Returns P_KEY_IN value
# @param default value that will be returned if no key value is found in params
def oppvalIn(params, default=None):
    return oppval(P_KEY_IN, params)

def oppOut(val):
    return P_KEY_OUT + '=' + val

# Returns P_KEY_OUT value
# @param default value that will be returned if no key value is found in params
def oppvalOut(params, default=None):
    return oppval(P_KEY_OUT, params)

#returns output dir with standard name in given path
def oppStdOutputDir(path):
    return opp(P_KEY_OUTPUTDIR,path + '/' + P_DOUT_DEFAULT)

def oppCommand(val):
    return 'command=' + val

def oppRange(val):
    return 'range=' + val

def oppRoot(rootPath):
    return 'RootDir=' + rootPath

# Creates list of param values for executor
def oppMakeOppList(key, valList):
    resultList = [key]
    resultList.extend(valList) 
    return resultList
    
def oppThreshold(key, th):
    return 'key=' + key + ';threshold=' + str(th)

def oppPlot(key,params):
    opp = 'key=' + key
    for par in params:
        opp = oppsum(opp, par)
    return opp
    
def oppLabel(label):
    return 'label=' + label

def oppColor(col):
    return 'color=' + col

def oppPrepareData(val):
    return KEY_PREPAREDATA + '=' + val

def oppTrainDir(val):
    return P_KEY_TRAINDIR + '=' + val

def oppInputDir(val):
    return P_KEY_INPUTDIR + '=' + val

def oppOutputDir(val):
    return P_KEY_OUTPUTDIR + '=' + val

def oppModelDir(val):
    return P_KEY_MODELDIR + '=' + val

def oppRawDataDir(val):
    return P_KEY_RAWDATADIR + '=' + val

def oppResultFile(val):
    return KEY_RESULTFILE + '=' + val

def oppDescription(val):
    return KEY_DESCRIPTION + '=' + val
