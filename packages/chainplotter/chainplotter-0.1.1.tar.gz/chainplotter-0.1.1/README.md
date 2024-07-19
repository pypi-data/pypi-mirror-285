## Chainplotter

Cosmosis chains are incompatible with plotting tool getdist. Chainplotter takes cosmosis output chains and returns a getdist.MCSamples object that can be plotted using getdist. Chainplotter currently may only work with the Dark Energy Survey (DES) year 3 (Y3) cosmosis chains.

# How to Install: 

```
pip install chainplotter 
pip install -r requirements.txt

```

# How to Use: 

Input cosmosis chain file into loadCosmosisMCSamples(filename) (Note: Must be done without '.txt')
loadCosmosisMCSamples.mc_samples is an object of type getdist.MCSamples that then can be plotted with getdist.

```
import cosmosis_getdist
from getdist import plots

samples = cosmosis_getdist.loadCosmosisMCSamples("../example_data/chain_3x2pt_wcdm_SR_maglim")
g = plots.get_subplot_plotter()
g.triangle_plot(samples.mc_samples)

```

