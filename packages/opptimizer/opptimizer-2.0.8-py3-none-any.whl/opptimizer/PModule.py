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

import subprocess
from .opp import *
from .pcons import *
from .PLog import *
from .PExecutable import *

class PModule(PExecutable):
    def __init__(self, name=""):
        PExecutable.__init__(self, name)
        self.name = name
        self.currentTest = None
        self.resultFilePath = None
        self.inputPath = None
        self.exec_result = None
        self.resultFile = None
        self.paramsEx = None
        self.skipExe = False
       # self.writeTestNameToResult = True
        return
    
    def init(self, testName, context):
        self.setContext(context)
        if testName == None:
            testName = 'test'
            
        if self.getCurrentTest() != None:
            testExecDir = self.getCurrentTest().getTestExecDir()
            if testExecDir != None:
                    self.setLogFileName(testExecDir + P_DIR_SEP + testName + '-log.txt')
            else:
                print("PModule.init() ERR: log not initialized due to lack of exec dir")
        else:
            print("PModule.init() ERR: log not initialized due to lack of current test")
        
        resultFilePath = oppval('dresultfile', self.getContext())
        self.setResultFilePath(resultFilePath)
        
        #self.dbgl("Init module " + self.name + ", logFilename:" + self.getLogFileName())
        #self.dbgl("Init module " + self.name + " resultFilePath:" + self.getResultFilePath())

    def getName(self):
        return self.name
    
    def setCurrentTest(self, test):
        self.currentTest = test
    
    def getCurrentTest(self):
        return self.currentTest
    
        # returs all params for current test    
    def getParamsEx(self):
        return self.paramsEx

    def setParamsEx(self, paramsEx):
        self.paramsEx = paramsEx
    
    def setSkipExe(self, val):
        self.skipExe = val

    
    #####  FILES (log/data)  INTERFACE  ################

    def resultFileOpen(self):
        if (self.getResultFilePath() != None):
            self.resultFile = PPath(self.getResultFilePath(), "ResultFile")
            self.resultFile.open('a')
        else:
            print("PModule.resulFiletOpen() ERR: log not initialized due to lack of path")

    def resultFileClose(self):
        if self.resultFile != None:
            self.resultFile.close()

    def writeToResultFile(self, resultStr, semicolon = True, new_line = False):
        if self.resultFile != None:
            semicolon = P_PARAM_SEP if semicolon else ''
            newline = '\n' if new_line else ''
            self.resultFile.write(resultStr + semicolon + newline)


    def setResultFilePath(self, resultFilePath):
        self.resultFilePath = resultFilePath
            
    def getResultFilePath(self):
        return self.resultFilePath
    
    def setInputPath(self, inputPath):
        self.inputPath = inputPath
            
    def getInputPath(self):
        return self.inputPath
            

    
    #####  END of FILES (log/data)  INTERFACE  ################
    
    #Returns a path to result from optimization for given input file
    # @flat defines if test name prefix should be added
    # @noext cuts extension form @inFilePath before processing
    # DEPRECATED: now use the same function from PPath
    def getFileResPath(self, inFilePath, testName='', testExecDir='',
                        noext=True, reskey=None, resext=None, flat=False):
        print("DEPRECATED: PModule.getFileResPath() is deprecated. Use the same function from PPath instead!")
        result = None
        testPrefix=''
        
        if flat:
            testPrefix = testName + '-'
        
        if reskey != None:
            reskey = '-' + reskey
        else:
            reskey = ''
        
        if resext != None:
            resext = '.' + resext
        else:
            resext = ''
            
        result = PPath(inFilePath, basename=True, noext=True, prefix=testPrefix,
                        postfix=reskey+resext, parent=testExecDir)
        return result
    
    
    def setExecresult(self, execResult):
        self.exec_result = execResult
        
    def getExecResult(self):
        return self.exec_result
    
    #checks if input is not special key
    # and if so it resolves for test
    def resolveInputPath(self):
        
        resolvedInputPath = None        
        context = self.getContext()
        testExtecDir = self.getCurrentTest().getTestExecDir()
        if context != None  and testExtecDir != None:
            inputPath = oppval('din', context)
            if (inputPath == '__cap'):
                resolvedInputPath = PPath(testExtecDir + P_DIR_SEP + 'cap')
            else:
                resolvedInputPath = PPath(inputPath)
                
        self.setInputPath(resolvedInputPath)
    
    # Executes module
    # Returns tokenData (custom global data for tests execution) 
    def execute(self, params, tokenData = None):
        
        testName = oppval(P_KEY_TESTNAME, params)
        self.dbgopen()
        
        executionParams = oppmodify(self.getContext(), params)
        if self.getLogFileName() != None:
            logFileParam = self.getLogFileName()
        else:
            logFileParam = "" 
            
        executionParams = oppmodify(executionParams, opp("logFile", logFileParam))
        self.setParamsEx(executionParams)
        #execDir = oppval('testExecDir', self.context)
        #if execDir != None:
        #    executionParams = oppmodify(executionParams, opp("resultFile", execDir + P_DIR_SEP + DP_RESULT_FILENAME))
        
        self.dbgl(self.name + ".execute().context: " + self.getContext())
        self.dbgl(self.name + ".execute().params: " + params)
        
        self.resolveInputPath()
        
        writeTestNameToResult = oppval(KEY_WRITE_TESTNAME_TO_RESLT, params)
        if writeTestNameToResult == '1':
            self.resultFileOpen()
            if (self.resultFile != None and not self.resultFile.isEmpty()):
                self.writeToResultFile('\n')
                
            #self.writeToResultFile(opp('testName', testName) + ';')
            self.resultFileClose();
        
        
        if (not self.skipExe):
            self.dbgclose()
            p = subprocess.Popen(["./runapp.sh", self.name, executionParams], cwd="../../modules/" + self.name)
            print("wait")
            p.wait()
            self.setExecresult(p.returncode)
            self.dbgopen()
        else:
            self.dbgl("Native execution skipped for module " + self.name)
            
        
        
        self.dbgl("module " + self.name +  " finished with return " + str(self.getExecResult()))
        self.dbgclose()
        
        return tokenData
        
    
    
