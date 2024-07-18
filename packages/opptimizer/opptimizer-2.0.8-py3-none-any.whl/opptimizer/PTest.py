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

import sys
from socket import *
import time
import os
from .opp import *
from .pcons import *
from .PLog import *
from .PObject import *

MEDTEST_VER = 1

class PTest(PObject):
	def __init__(self, testName = None, params = None):
		PObject.__init__(self, testName)
		self.params = params
		#self.modules = []
		self.testExecDir = None # this test excution dir (usually sibdir of self.execDir)
		self.execDir = None # main execution dir (uses by executor.execute())
		self.log = None
		self.tokenData = None
		return

	def version(self):
		return 't' + str(MEDTEST_VER)
	
	#def addModule(self, module):
	#	self.modules.append(module)
		
	#def getModules(self):
	#	return self.modules
	
	def setTestExecDir(self, directory):
		self.testExecDir = directory
	
	def getTestExecDir(self):
		return self.testExecDir

	def setExecDir(self, directory):
		self.execDir = directory
	
	def getExecDir(self):
		return self.execDir

	def setTokenData(self, tokenData):
		self.tokenData = tokenData
	
	def getTokenData(self):
		return self.tokenData
		



def connectToServiceITK(self):
	print('connectToServiceITK')
	itkServiceSocket = socket(AF_INET, SOCK_STREAM)
	itkServiceSocket.connect(('localhost', 3355))
	return itkServiceSocket
	
	

		