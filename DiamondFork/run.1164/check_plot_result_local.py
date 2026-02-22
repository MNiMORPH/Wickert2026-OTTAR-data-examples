#! /usr/bin/env python

import dakota.interfacing as di
import ottar
import numpy as np
import pandas as pd

params, results = di.read_parameters_file(parameters_file='params.in', results_file='results.out')

################
# Observations #
################
obs = pd.read_csv('DFk_Motherlode_width_JJ.tsv',
                  sep=None, engine='python')

###############
# Predictions #
###############
rw = ottar.RiverWidth.from_yaml('config_for_output.yaml')

rw.initialize()

# Update values
rw.set_initial_width( params['b0'] )
rw.set_tau_crit_cohesive( params['tau_crit'] )
rw.set_cohesive_detachment_coefficient( 10**params['log__k_d'] )
rw.set_noncohesive_entrainment_coefficient( 10**params['log__k_E'] )
rw.set_coehsive_bank_stickiness( 10**params['log__f_stickiness'] )
rw.set_noncohesive_narrowing_coefficient( 10**params['log__k_n_noncohesive'] )

rw.run()
rw.finalize()



# Predicted values in observed years
# Since we don't have a known date of observation, let's use the annual mean.
# Modeled width by year
modeled_width_by_year = rw.df.groupby(rw.df['Timestamp'].dt.year).mean()['Channel width [m]']

# Compare with data
comp = obs.copy()
# Empty data column
comp['Width modeled [m]'] = np.nan

for _yr in comp['Year']:
    comp.loc[ comp['Year'] == _yr, 'Width modeled [m]' ] = \
        modeled_width_by_year[_yr]

comp['Width error [m]'] = comp['Width modeled [m]'] - comp['Width [m]']

rmse = ( (comp['Width error [m]']**2).sum() / len(comp) )**.5

