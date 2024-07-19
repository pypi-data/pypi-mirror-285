import numpy as np
import getdist
from getdist import MCSamples
from getdist import loadMCSamples
import re

class loadCosmosisMCSamples:
    """Loads cosmosis output chains and returns a getdist.MCSamples object that can be plotted using getdist.

    Attributes:
        chainfile (str): File name of cosmosis output chains.
        metadata (:obj:`list` of :obj:`str`): Metadata from cosmosis file.
        columnnames (:obj:`np.array` of :obj:`str`): List of columns names (first line in cosmosis metadata)
        sampler_type (str): Sampler used to generate chains. Currently only supports nested sampling.
        chains (:obj:`np.array`): Array with the chains from cosmosis file
        indices (:obj:`np.array`): Indices of the columns that correspond to the loglikelihood, weights and sampled variables.
        paramnames (:obj:`np.array of :obj:`str`): Array of the parameter names.
        samples (:obj:`np.array`): Array with the sampled parameters from the chains.
        loglikes (:obj:`np.array`): Array with the log likelihood from the chains.
        weights (:obj:`np.array`): Array with the weights.
        labels (:obj:`list`): List of the labels for the parameters.
        ranges (:obj: `dict`): Dictionary for each parameters and its corresponding minimum and maximum values.
    """
    def __init__(self,filename):
        """ Initializes the loadCosmosisMCSamples class

        Args:
            filename (str): File name of cosmosis chains (must not contain`.txt`).

        """
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
        self.get_ranges()
        self.make_MC_samples()


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
        self.weights = np.array(self.chains[:,self.index_weight]).flatten()
    
    def get_loglikes(self):
        self.log = np.array(self.chains[:,self.index_log]).flatten()
        
    def get_paramnames(self):
        self.paramnames = self.colnames[self.index_samples]
    
    def get_labels(self):
        labels = []
        names = []
        param_cat_dict = {}
        for i,p in enumerate(self.paramnames):
            c_new = str.lower(re.sub(r"--.*","",p))
            p_new = re.sub(r".*--","",p)
            if "prior" in p_new:
                labels.append(p_new)
                names.append(p)
            elif "like" in p_new:
                labels.append(p_new)
                names.append(p)
            else:
                labels.append(p_new)
                names.append(p)
                if c_new in param_cat_dict.keys():
                    param_cat_dict[c_new].append(p_new)
                else:
                    param_cat_dict[c_new] = []
                    param_cat_dict[c_new].append(p_new)
        self.labels = labels
        self.param_cat_dict = param_cat_dict
        self.names = names 
        return self.labels,self.param_cat_dict,self.names 

    def _get_ranges_chunk(self):
        for i,s in enumerate(self.metadata):
            if "START_OF_VALUES_INI" in s:
                start_of_ranges = i
            if "END_OF_VALUES_INI" in s:
                end_of_ranges = i
        ranges_chunk = self.metadata[start_of_ranges+1:end_of_ranges]
        return ranges_chunk
    
    def _get_cat_chunks(self):
        ranges_chunk = self._get_ranges_chunk()
        unique_cats = self.param_cat_dict.keys()
        cat_sec = []
        ind_chunks = []
        for i,r in enumerate(ranges_chunk):
            for c in unique_cats:
                if c in r:
                    ind_chunks.append(i)
                    cat_sec.append(c)
        ind_chunks.append(len(ranges_chunk)-1)
        cat_chunks = {}
        for i,s in enumerate(cat_sec):
            cat_chunks[s] = ranges_chunk[ind_chunks[i]:ind_chunks[i+1]-1]
        return cat_chunks

    def get_ranges(self):
        cat_chunks = self._get_cat_chunks()
        ranges_dict = {}
        for i in cat_chunks.keys():
            this_chunk = cat_chunks[i]
            these_labels = self.param_cat_dict[i]
            for l in these_labels:
                name = self.names[self.labels.index(l)]
                res = list(filter(lambda x: l in x,this_chunk))
                if len(res)>0:
                    to_delete = l+" = "
                    numbers = re.sub(to_delete,"", res[0])
                    numbers = numbers.split()
                    numbers = np.array(numbers).astype(float)
                    if len(numbers)==1:
                        min_val = None
                        max_val = np.max(numbers)
                    elif len(numbers)==3:
                        min_val = np.min(numbers)
                        max_val = np.max(numbers)
                    ranges_dict[name] = [min_val,max_val]
                else:
                    ranges_dict[name] = [None,None]
            for x in self.names:
                if x not in ranges_dict.keys():
                    ranges_dict[x] = [None,None]
        self.ranges = ranges_dict
        return self.ranges

    def make_MC_samples(self):
        self.mc_samples = MCSamples(samples=self.samples, weights=self.weights,
                           loglikes=-2.*self.log,
                           sampler=self.sampler_type, names=self.paramnames,
                           ranges=self.ranges, labels=self.labels,
                           ignore_rows=0)
                           #settings=settings)
        return self.mc_samples


    #samples = MCSamples
    #return #samples
