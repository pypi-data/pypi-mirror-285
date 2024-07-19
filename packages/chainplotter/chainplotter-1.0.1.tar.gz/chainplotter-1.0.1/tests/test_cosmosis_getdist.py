from chainplotter import cosmosis_getdist
import numpy as np
import getdist
from getdist import plots
import pytest


def test_get_metadata():
    '''
    Unit Test
    '''
    tester = cosmosis_getdist.loadCosmosisMCSamples("../example_data/chain_3x2pt_wcdm_SR_maglim")
    assert tester.metadata != None
    assert len(tester.metadata) > 1 

def test_get_columnnames():
    tester = cosmosis_getdist.loadCosmosisMCSamples("../example_data/chain_3x2pt_wcdm_SR_maglim")
    expected_colnames = ['cosmological_parameters--omega_m',	'cosmological_parameters--h0',	'cosmological_parameters--omega_b',	'cosmological_parameters--n_s',	'cosmological_parameters--a_s',	'cosmological_parameters--omnuh2',	'cosmological_parameters--w',	'shear_calibration_parameters--m1',	'shear_calibration_parameters--m2',	'shear_calibration_parameters--m3',	'shear_calibration_parameters--m4',	'wl_photoz_errors--bias_1',	'wl_photoz_errors--bias_2',	'wl_photoz_errors--bias_3',	'wl_photoz_errors--bias_4',	'lens_photoz_errors--bias_1',	'lens_photoz_errors--bias_2',	'lens_photoz_errors--bias_3',	'lens_photoz_errors--bias_4',	'lens_photoz_errors--width_1',	'lens_photoz_errors--width_2',	'lens_photoz_errors--width_3',	'lens_photoz_errors--width_4',	'bias_lens--b1',	'bias_lens--b2',	'bias_lens--b3',	'bias_lens--b4',	'intrinsic_alignment_parameters--a1',	'intrinsic_alignment_parameters--a2',	'intrinsic_alignment_parameters--alpha1',	'intrinsic_alignment_parameters--alpha2',	'intrinsic_alignment_parameters--bias_ta',	'COSMOLOGICAL_PARAMETERS--SIGMA_8',	'COSMOLOGICAL_PARAMETERS--SIGMA_12',	'DATA_VECTOR--2PT_CHI2',	'prior',	'like',	'post',	'weight\n']
    expected_colnames=np.array(expected_colnames)
    
    assert np.all(tester.colnames == expected_colnames)

def test_get_indices():
    tester = cosmosis_getdist.loadCosmosisMCSamples("../example_data/chain_3x2pt_wcdm_SR_maglim")

    assert tester.index_log != None
    assert type(tester.index_log) == np.ndarray
    assert tester.index_weight != None
    assert type(tester.index_weight) == np.ndarray
    assert len(tester.index_samples) > 0
    assert type(tester.index_samples) == np.ndarray

def test_get_samples():
    tester = cosmosis_getdist.loadCosmosisMCSamples("../example_data/chain_3x2pt_wcdm_SR_maglim")
    
    assert len(tester.samples) > 0
    assert type(tester.samples) == np.ndarray

def test_get_chains():
    tester = cosmosis_getdist.loadCosmosisMCSamples("../example_data/chain_3x2pt_wcdm_SR_maglim")
    
    assert len(tester.chains) > 0
    assert type(tester.chains) == np.ndarray

def test_get_weights():
    tester = cosmosis_getdist.loadCosmosisMCSamples("../example_data/chain_3x2pt_wcdm_SR_maglim")
    
    assert len(tester.weights) > 0
    assert type(tester.weights) == np.ndarray

def test_get_loglikes():
    tester = cosmosis_getdist.loadCosmosisMCSamples("../example_data/chain_3x2pt_wcdm_SR_maglim")

    assert len(tester.log) > 0
    assert type(tester.log) == np.ndarray

def test_lengths():
    tester = cosmosis_getdist.loadCosmosisMCSamples("../example_data/chain_3x2pt_wcdm_SR_maglim")

    assert len(tester.chains) == len(tester.weights)
    assert len(tester.weights) == len(tester.log)

def test_get_paramnames():
    tester = cosmosis_getdist.loadCosmosisMCSamples("../example_data/chain_3x2pt_wcdm_SR_maglim")
    
    assert len(tester.colnames) == len(tester.paramnames) + 2

def test_get_labels():
    tester = cosmosis_getdist.loadCosmosisMCSamples("../example_data/chain_3x2pt_wcdm_SR_maglim")

    assert len(tester.labels) == len(tester.paramnames)
    assert len(tester.names) == len(tester.paramnames)

def test_get_ranges_chunk():
    tester = cosmosis_getdist.loadCosmosisMCSamples("../example_data/chain_3x2pt_wcdm_SR_maglim")
    ranges_chunk = tester._get_ranges_chunk()
    assert len(ranges_chunk) > 0

def test_get_cat_chunks():
    tester = cosmosis_getdist.loadCosmosisMCSamples("../example_data/chain_3x2pt_wcdm_SR_maglim")
    cat_chunks = tester._get_cat_chunks()

    assert len(cat_chunks.keys()) > 0

def test_get_ranges():
    tester = cosmosis_getdist.loadCosmosisMCSamples("../example_data/chain_3x2pt_wcdm_SR_maglim")

    assert len(tester.ranges.keys()) == len(tester.paramnames)

def test_make_MC_samples():
    tester = cosmosis_getdist.loadCosmosisMCSamples("../example_data/chain_3x2pt_wcdm_SR_maglim")

    assert type(tester.mc_samples == getdist.mcsamples.MCSamples)

'''def test_make_plot():
    tester = cosmosis_getdist.loadCosmosisMCSamples("../example_data/chain_3x2pt_wcdm_SR_maglim")

    g = plots.get_subplot_plotter()
    g.triangle_plot([tester.mc_samples], names = ['cosmological_parameters--omega_m', 'COSMOLOGICAL_PARAMETERS--SIGMA_8'])
    g.export('test_plot.png')
    Done == True
    assert Done'''

test_get_metadata()
test_get_columnnames()
test_get_indices()
test_get_samples()
test_get_chains()
test_get_weights()
test_get_loglikes()
test_lengths()
test_get_paramnames()
test_get_labels()
test_get_ranges_chunk()
test_get_cat_chunks()
test_get_ranges()
test_make_MC_samples()

print('DONE WITH TESTS')