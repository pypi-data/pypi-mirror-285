
class TopologicalShape():
    '''TopologicalShape is a class that represents the topological 
    shape of a graph.'''
    def __init__(self, graph):
        '''The constructor of the TopologicalShape class.'''
        self.graph = graph
        self._shape = None
        self._shape = self.get_shape()

    def get_shape(self):
        '''Get the shape of the graph.'''
        return self.graph.get_shape()
    
class TopologicalMapping():
    '''TopologicalMapping is a class that represents the topological
    mapping of a graph, in a low-dimensional space (e.g. 2D).'''
    def __init__(self, graph):
        '''The constructor of the TopologicalMapping class.'''
        self.graph = graph
        self._mapping = None
        self._mapping = self.get_mapping()

    def get_mapping(self):
        '''Get the mapping of the graph.'''
        #TODO implement this method
        pass
    
class TopologicalMetrics():
    '''TopologicalMetrics is a class that represents the topological
    properties in quantifiable numerical values.'''
    def __init__(self, graph):
        '''The constructor of the TopologicalMetrics class.'''
        self.graph = graph
        self._metrics = None
        self._metrics = self.get_metrics()
    
    def get_metrics(self):
        '''Get the metrics of the graph.'''
        #TODO implement this method
        pass

    
