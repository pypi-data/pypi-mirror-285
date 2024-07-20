
class TabularDataExtractor():
    '''Class to extract tabular data from a file
    and prepare it to point cloud space'''

    def __init__(self, filename):
        self.filename = filename

    def extract(self):
        '''Extract tabular data from a file'''
        pass
    
    def prepare(self):
        '''Prepare tabular data to point cloud space'''
        pass

class PointCloud():
    '''Class to represent a point cloud'''

    def __init__(self, data):
        self.data = data

    def distance_matrix(self):
        '''Compute the distance matrix of the point cloud'''
        pass

    def plot(self):
        '''Plot the point cloud'''
        pass

class TopologicalSpace():
    '''Class to represent a topological space'''

    def __init__(self, data):
        self.data = data

    def persistent_homology(self):
        '''Compute the persistent homology of the topological space'''
        pass

    def plot(self):
        '''Plot the topological space'''
        pass