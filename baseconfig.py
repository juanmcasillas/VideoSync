import sys


import os.path
import os
import argparse
import xml.dom.minidom as xmlp


class BaseConfig(object):
    def __init__(self):
        pass

    def __str__(self):
        s = ""
        for i in self.__dict__.keys():
            s += "%s:\t%s\n" % (i, self.__dict__[i])
        return s

    def CSV(self, header=False):
        s = ""
        if header:
            for i in self.__dict__.keys():
                s += "%s\t" % i
        
        for i in self.__dict__.keys():
            s += "%s\t" % self.__dict__[i]
    
        
        return s
        

    def _xmlgetTEXT(self,nodelist):
        rc = []
        for node in nodelist.childNodes:
            if node.nodeType == node.TEXT_NODE:
                rc.append(node.data)
        return ''.join(rc)


    def __getitem__(self, key): return self.__dict__[key]
    def __setitem__(self, key, value):  self.__dict__[key] = value

    def keys(self):
        return self.__dict__.keys()