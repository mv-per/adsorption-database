




# from pathlib import Path
# from typing import List, Optional, Tuple
# import numpy as np

# import h5py

# from data_types import Adsorbate, AdsorbateType, Adsorbent, AdsorbentType, ExperimentType, IsothermType, MixIsothermFileData, MonoIsothermFileData
# from isotherms import MixIsotherm, MonoIsotherm 
# from os.path import abspath, dirname

# from experiment import Experiment






# if __name__=='__main__':

#     CO2 = Adsorbate(
#         AdsorbateType.GAS, 'Carbon Dioxide', 'CO2'
#     )

    
#     CH4 = Adsorbate(
#         AdsorbateType.GAS, 'Methane', 'CH4'
#     )

#     N2 = Adsorbate(
#         AdsorbateType.GAS, 'Nitrogen', 'N2'
#     )

#     register_adsorbate(CO2)
#     register_adsorbate(CH4)
#     register_adsorbate(N2)

    

#     co2_data = MonoIsothermFileData(
#         'SUDI_co2.txt', CO2, 0,1, pressure_conversion_factor_to_Pa=1e6
#     )
#     ch4_data = MonoIsothermFileData(
#         'SUDI_ch4.txt', CH4, 0,1, pressure_conversion_factor_to_Pa=1e6
#     )
#     n2_data = MonoIsothermFileData(
#         'SUDI_n2.txt', N2, 0,1, pressure_conversion_factor_to_Pa=1e6
#     )

#     co2_isotherm = create_mono_isotherm('CO2-01', IsothermType.EXCESS, co2_data)
#     ch4_isotherm = create_mono_isotherm('CH4-01', IsothermType.EXCESS, ch4_data)
#     n2_isotherm = create_mono_isotherm('N2-01', IsothermType.EXCESS, n2_data)

    
#     co2_ch4_1_data = MixIsothermFileData(
#         'SUDI_CO2CH4_20.txt', [CO2, CH4], 0, [2,4], [1], load_missing_composition_from_equilibrium=True, pressure_conversion_factor_to_Pa=1e6
#     )
#     co2_ch4_1_isotherm = create_mix_isotherm(
#         'CO2-CH4-1', IsothermType.EXCESS, co2_ch4_1_data
#     )

#     print(co2_ch4_1_isotherm)

#     Calgon = Adsorbent(AdsorbentType.ACTIVATED_CARBON, 'Calgon-F400')
#     experiment = Experiment(name='Sudi',authors=['a', 'b','c'], adsorbent=Calgon, experiment_type=ExperimentType.VOLUMETRIC, temperature=318.2, monocomponent_isotherms=[co2_isotherm, ch4_isotherm, n2_isotherm])

#     register_experiment(experiment)