import os


class File:
    def __init__(self, path : str, create : bool = False):
        if (File.isAbsPath(path)):
            self.path = path
        else:
            self.path = File.toAbsPath(path)
        self.directory = File.directoryName(self.path)
        temp = File.baseName(self.path).split(".")
        self.name = temp[0]
        self.extension = temp[1]
        
    
    
    @classmethod
    def baseName(cls, path : str):
        return os.path.basename(path)
    @classmethod
    def directoryName(cls, path : str):
        return os.path.dirname(path) 
    @classmethod
    def toAbsPath(cls, path : str):
        return os.path.abspath(path)
    @classmethod
    def isAbsPath(cls, path : str):
        return os.path.isabs(path)