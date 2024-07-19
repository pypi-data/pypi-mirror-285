import cosmosis_getdist
import numpy as np
import os 

samples = cosmosis_getdist.loadCosmosisMCSamples("../example_data/chain_3x2pt_wcdm_SR_maglim")
#print(samples.paramnames)
#print(samples.labels)
#print(samples.categories)
print(samples.ranges)

