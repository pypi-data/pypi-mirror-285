from .PModulePy import *

class Mod(PModulePy):
    def __init__(self, func_exec=None, name=None, func_init=None):

        if name is None:
            name = str(self.__str__)

        PModulePy.__init__(self,name, func_exec, func_init)
        
        return