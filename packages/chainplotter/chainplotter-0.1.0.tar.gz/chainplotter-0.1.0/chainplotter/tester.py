import cosmosis_getdist
from getdist import plots
import getdist
import time

samples = cosmosis_getdist.loadCosmosisMCSamples("../example_data/chain_3x2pt_wcdm_SR_maglim")
print(samples.mc_samples)
print(type(samples.mc_samples))
time_start = time.time()
g = plots.get_subplot_plotter()

g.triangle_plot(samples.mc_samples)
g.export('../example_data/des_y3_triange.png')
time_end = time.time()

delta = time_end - time_start
print(delta)
#print(samples.weights.shape)

#gsamples = getdist.loadMCSamples("../example_data/lcdm_act_baseline_167519500360")
#g = plots.get_subplot_plotter()
#g.triangle_plot(samples.mc_samples)
#g.export('../example_data/cobaya_act.png')
