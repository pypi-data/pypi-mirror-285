import numpy as np
import getdist
from getdist import MCSamples
from getdist import loadMCSamples
import re

class loadCosmosisMCSamples:
    #load filename
    #do some stuff to the filename like the getdist.loadMCSamples function does
    #package everything into a getdist MCSamples object
    def __init__(self,filename):
        if filename == None:
            raise ValueError("chainplotter needs a filename")
        self.chainfile = filename+".txt"
        self.get_metadata()
        self.get_columnnames()
        self.get_sampler_type()
        self.get_chains()
        self.index_log,self.index_weight,self.index_samples = self.get_indices()
        self.get_paramnames()
        self.get_samples()
        self.get_loglikes()
        self.get_weights()
        self.get_labels()


    def get_metadata(self):
        metadata = []
        with open(self.chainfile, 'r') as chainfile:
            for line in chainfile:
                if line.startswith("#"):
                    clean_line = line.strip("#")
                    metadata.append(clean_line)
        self.metadata = metadata   

    def get_columnnames(self):
        if self.metadata == None:
            self.metadata = self.get_metadata(self)
        colnames = self.metadata[0].split("\t")
        self.colnames = np.array(colnames)
    
    def get_indices(self):
        index_log = np.where(np.array(self.colnames) == "post")[0]
        index_all = np.arange(len(self.colnames))
        index_weight = np.where(np.array(self.colnames) == "weight\n")[0]
        index_samples = np.array(np.delete(index_all,[index_log,index_weight]).astype(int))
        return index_log,index_weight,index_samples
    
    def get_samples(self):
        self.samples = self.chains[:, self.index_samples]

    def get_chains(self):
        chains = np.loadtxt(self.chainfile,comments="#")
        self.chains = chains

    def get_sampler_type(self):
        for i in self.metadata:
            if "polychord" in i:
                self.sampler_type = "nested"

    def get_weights(self):
        self.weights = self.chains[:,self.index_weight]
    
    def get_loglikes(self):
        self.log = self.chains[:,self.index_log]
        
    def get_paramnames(self):
        self.paramnames = self.colnames[self.index_samples]
    
    def get_labels(self):
        labels = []
        for i,p in enumerate(self.paramnames):
            p_new = re.sub(r".*--","",p)
            labels.append(p_new)
        self.labels = labels
        return self.labels

    def get_ranges(self):
        for i,s in enumerate(self.metadata):
            if "START_OF_VALUES_INI" in s:
                start_of_ranges = i
            if "END_OF_VALUES_INI" in s:
                end_of_ranges = i
        ranges_chunk = self.metadata[start_of_ranges+1:end_of_ranges]
        ranges = {}

        for n in self.labels:
            for m in ranges_chunk:
                if n in m:
                    to_delete = n+" = "
                    numbers = re.sub(to_delete,"",m)
                    numbers = numbers.split()
                    numbers = np.array(numbers).astype(float)
                    print(numbers)
        
            

        return ranges
    
    def make_sampler(self):
        self.mc_samples = MCSamples(samples=self.samples, weights=self.weights,
                           loglikes=-2.*self.log,
                           sampler=self.sampler_type, names=self.paramnames,
                           labels=param_labels, ranges=ranges,
                           ignore_rows=0)
                           #settings=settings)
        return 0


    #samples = MCSamples
    #return #samples
