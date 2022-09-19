'''
Created on Jun 23, 2021

@author: Andre Granville
'''
class Estacao(object):
    
    def __init__(self, code, X, Y):
        self.site = Site(code, X, Y)
        self.historicalMeasures = HistoricalMeasures()         
            
class Site(object):
    
    def __init__(self, code, X, Y):
        self.code = code
        self.X =  X
        self.Y = Y
                
class HistoricalMeasures(object):

    def __init__(self):
        self.horizon =  Horizon()
        self.measures = {}
        
class Horizon(object):
    
    def __init__(self):
        self.initialDate =  ""
        self.finalDate = ""
        
        
