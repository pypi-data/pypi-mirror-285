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

from .opp import *
from .pcons import *
from .PLog import *
from .PExecutable import *
from opptimizer.opp import oppmodify

class PScript(PExecutable):
    def __init__(self, name=""):
        PExecutable.__init__(self, name)
    
    def init(self, argv):
        context = self.parseArgsForContext(argv) 
        self.setContext(oppmodify(self.getContext(), context))
        
        scriptName = oppval('script', self.context)
        if scriptName != None:
            self.setName(scriptName)
        
        print('script.init, context:' + self.getContext())

        outDir = oppval('dout', self.context)
        if outDir == None:
            outDir = '.'  #current directory is default for output
        PPath(outDir).createDirIfNone()
        self.setLogFileName(outDir + P_DIR_SEP + P_SUMMARY_FILENAME)

    # Should be overriden
    def execute(self, argv):    
        return 
    
    def parseArgsForContext(self, argv):
        context = ''   
        
        if len(argv) > 1:
            for arg in argv:
                if oppkey(arg) != None:
                    context = oppmodify(context, arg)

        
        cfgFile = oppval('dcfg', context)
        if cfgFile != None:
            cfgContext = self.parseCfgFile(cfgFile)
            if (cfgContext != ''):
                context = oppsum(context, cfgContext) 
            
        return context
    
    def parseCfgFile(self, cfgFile):
        context = ''
        
        print("parseCfgFile:" + cfgFile)
    
        if (cfgFile != None):
            
            cfg = PPath(cfgFile)
            
            if cfg.exists():
                
                cfg.open()
                content = cfg.readLines()
                
                for item in content:
                    print('item'+item)
                    item = item.split('\n')[0]
                    #TODO: add check if line is correct OPP string
                    context = oppsum(context, item)
                    
                cfg.close()
            else:
                print('WARN parseCfgFile: path not exists:' + cfg.getPath())
        else:
            print('WARN parseCfgFile: path not exists:' + cfg.getPath())
            
        print("context from cfg:" + context)   
        
        return context 
        