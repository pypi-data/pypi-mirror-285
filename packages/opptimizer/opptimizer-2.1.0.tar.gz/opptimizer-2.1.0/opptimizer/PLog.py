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

from .PPath import *
from .putils import *

DBG_NODEBUG_LEVEL = 0
DBG_LOW_LEVEL = 1
DBG_MEDIUM_LEVEL = 2
DBG_HIGH_LEVEL = 3

class PLog(PPath):
    def __init__(self, name = "", path = None):
        PPath.__init__(self, path, name)
        self.active = False
        self.LEVEL = DBG_LOW_LEVEL
        self.flush = False
        self.addPrefix = True  #flag if prefix ([self.name]) should be added to log
        
        
        self.setActive(True)
        if (path != None):
            self.setPath(path)
        return
    
    def openLog(self, append = True, onlyRead = False):
        mode = 'a'
        if not append:
            if not onlyRead:
                mode = 'w'
            else:
                mode='r'
            
        return self.open(mode)

    
    def setFlush(self, flush=True):
        self.flush = flush
    
    def getFlush(self):
        return self.flush
    
    def setActive(self, active):
        self.active = active
    
    def isActive(self):
        return self.active
    
    def getPrefix(self):
        if self.addPrefix:
            return '[' + self.name + ']'
    
    # Prints regular log
    def dbg(self, object_to_write, dbgLevel=DBG_LOW_LEVEL):
        if self.isActive() and dbgLevel >= self.LEVEL:
            textToWrite = self.getPrefix() + object_to_write
            oppdbg(textToWrite)
            if self.isOpened():
                self.write(textToWrite, self.flush)
                
    def dbgl(self, object_to_write, dbgLevel=DBG_LOW_LEVEL):
        object_to_write += '\n'
        self.dbg(object_to_write, dbgLevel)

    # Prints WARNING log (as string)
    def wrn(self, object_to_write, dbgLevel=DBG_LOW_LEVEL):
        if self.isActive() and dbgLevel >= self.LEVEL:
            textToWrite = WARN_KEY + self.getPrefix() + ':' + object_to_write 
            oppdbg(textToWrite)
            if self.isOpened():
                self.write(textToWrite, self.flush)
                
    def wrnl(self, object_to_write, dbgLevel=DBG_LOW_LEVEL):
        object_to_write += '\n'
        self.wrn(object_to_write, dbgLevel)
    
    # Prints ERROR log (as string)
    def err(self, object_to_write, dbgLevel=DBG_LOW_LEVEL):
        if self.isActive() and dbgLevel >= self.LEVEL:
            textToWrite = ERROR_KEY + self.getPrefix() + ':' + object_to_write 
            oppdbg(textToWrite)
            if self.isOpened():
                self.write(textToWrite, self.flush)
                
    def errl(self, object_to_write, dbgLevel=DBG_LOW_LEVEL):
        object_to_write += '\n'
        self.err(object_to_write, dbgLevel)
           
