from .PExecutor import *

class Executor(PExecutor):
    def __init__(self, context = None, params = None, modules = None):
        PExecutor.__init__(self, context, params, modules)
        
        return