




from pathlib import Path
from typing import List, Optional, Tuple
import numpy as np

import h5py

from data_types import Adsorbate, AdsorbateType, Adsorbent, AdsorbentType, ExperimentType, IsothermType, MixIsothermFileData, MonoIsothermFileData
from isotherms import MixIsotherm, MonoIsotherm 
from os.path import abspath, dirname

from experiment import Experiment

EXPERIMENTS_FOLDER = Path(dirname(abspath(__file__))) / "temp"

def get_mono_isotherm_data_from_txt_file(
        file_data:MonoIsothermFileData
    ) -> Tuple[List[float], List[float]]:
    file_path = EXPERIMENTS_FOLDER / file_data.file_name

    file = np.loadtxt(file_path)
    pressures = file[:, file_data.pressures_col]
    loadings = file[:, file_data.loadings_col]

    if file_data.pressure_conversion_factor_to_Pa is not None:
        pressures = pressures[:]*file_data.pressure_conversion_factor_to_Pa
    
    if file_data.loadings_conversion_factor_to_mol_per_kg is not None:
        loadings = loadings[:]*file_data.loadings_conversion_factor_to_mol_per_kg

    assert pressures.shape == loadings.shape

    return pressures, loadings

def get_mix_isotherm_data_from_txt_file(
        file_data:MixIsothermFileData
    ) -> Tuple[List[float], List[float]]:
    file_path = EXPERIMENTS_FOLDER / file_data.file_name

    file = np.loadtxt(file_path)
    pressures = file[:, file_data.pressures_col]

    loadings = []
    compositions = []
    for index in range(len(file_data.adsorbates)):
        loadings.append(file[:, file_data.loadings_cols[index]])

        try:
            component_compositions = file[:, file_data.composition_cols[index]]
        except IndexError:
            if file_data.load_missing_composition_from_equilibrium:
                component_compositions = []
                for index in range(len(compositions)):
                    index_compositions = [x[index] for x in compositions]
                    component_compositions.append(1-sum(index_compositions))
            else:
                raise
        compositions.append(component_compositions)

    if file_data.pressure_conversion_factor_to_Pa is not None:
        pressures = pressures[:]*file_data.pressure_conversion_factor_to_Pa
    
    if file_data.loadings_conversion_factor_to_mol_per_kg is not None:

        for component_loadings in loadings:
            component_loadings = component_loadings[:]*file_data.loadings_conversion_factor_to_mol_per_kg

    for component_loadings in loadings:
        assert pressures.shape == component_loadings.shape

    return pressures, loadings, compositions

def create_mono_isotherm(name:str, isotherm_type:IsothermType, file_data:MonoIsothermFileData,heats_of_adsorption:Optional[str]=None, comments:Optional[str]=None) -> MonoIsotherm:
    
    pressures, loadings = get_mono_isotherm_data_from_txt_file(file_data)

    return MonoIsotherm(
        name=name,
        isotherm_type=isotherm_type,
        adsorbate=file_data.adsorbate,
        pressures=pressures,
        heats_of_adsorption=heats_of_adsorption,
        loadings=loadings,
        comments=comments
    )

def create_mix_isotherm(name:str, isotherm_type:IsothermType, file_data:MixIsothermFileData, comments:Optional[str]=None) -> MonoIsotherm:
    
    pressures, loadings, bulk_composition = get_mix_isotherm_data_from_txt_file(file_data)

    return MixIsotherm(
        name=name,
        isotherm_type=isotherm_type,
        adsorbates=file_data.adsorbates,
        pressures=pressures,
        loadings=loadings,
        bulk_composition=bulk_composition,
        comments=comments
    )

def get_storage_file() -> h5py.File:
    return h5py.File('storage.hdf5', 'a')

def get_group(group_name:str, parent_group:Optional[h5py.Group]=None) -> h5py.Group:

    if parent_group is None:
        parent_group = get_storage_file()
    
    group = parent_group.get(group_name)

    if group is None:
        group = parent_group.create_group(group_name)

    return group

def register_adsorbate(adsorbate:Adsorbate):
    adsorbates_group = get_group('adsorbates')

    adsorbate_group = get_group(adsorbate.name, adsorbates_group)
    adsorbate_group.attrs.create('type', adsorbate.type.value)
    adsorbate_group.attrs.create('name', adsorbate.name)
    adsorbate_group.attrs.create('chemical_formula', adsorbate.chemical_formula)

def upsert_dataset(group:h5py.Group, dataset_name:str, values:np.ndarray):

    dataset = group.get(dataset_name)

    if dataset is not None:
        del group[dataset_name]

    group.create_dataset(dataset_name, data=values)

def register_mono_isotherm(isotherm:MonoIsotherm, experiment_group:h5py.Group):

    stored_isotherm_name= f"MONO-{isotherm.name}-{isotherm.isotherm_type.value}"

    isotherm_group = get_group(stored_isotherm_name, experiment_group)

    isotherm_group.attrs.create('name', isotherm.name)
    isotherm_group.attrs.create('adsorbate', isotherm.adsorbate.name)
    isotherm_group.attrs.create('isotherm_type', isotherm.isotherm_type.value)

    if isotherm.comments is not None:
        isotherm_group.attrs.create('comments', isotherm.comments)

    upsert_dataset(isotherm_group, 'pressures',isotherm.pressures)
    upsert_dataset(isotherm_group, 'loadings',isotherm.loadings)
    upsert_dataset(isotherm_group, 'heats_of_adsorption',isotherm.heats_of_adsorption)

    return stored_isotherm_name

def register_mix_isotherm(isotherm:MonoIsotherm, experiment_group:h5py.Group):

    stored_isotherm_name= f"MIX-{isotherm.name}-{isotherm.isotherm_type.value}"

    isotherm_group = get_group(stored_isotherm_name, experiment_group)

    isotherm_group.attrs.create('name', isotherm.name)
    isotherm_group.attrs.create('isotherm_type', isotherm.isotherm_type.value)

    if isotherm.comments is not None:
        isotherm_group.attrs.create('comments', isotherm.comments)

    adsorbates_names = [adsorbate.name for adsorbate in isotherm.adsorbates]

    upsert_dataset(isotherm_group, 'adsorbates', adsorbates_names)
    upsert_dataset(isotherm_group, 'pressures',isotherm.pressures)
    upsert_dataset(isotherm_group, 'loadings',isotherm.loadings)
    upsert_dataset(isotherm_group, 'heats_of_adsorption',isotherm.heats_of_adsorption)

    return stored_isotherm_name

def register_experiment(experiment:Experiment):
        
        experiment_group = get_group("EXPERIMENT-" + experiment.name)

        experiment_group.attrs.create('name',experiment.name)
        experiment_group.attrs.create('temperature',experiment.temperature)
        experiment_group.attrs.create('adsorbent',experiment.adsorbent.name)
        experiment_group.attrs.create('experiment_type',experiment.experiment_type.value)

        isotherm_names = []
        for isotherm in experiment.monocomponent_isotherms:
            isotherm_names.append(register_mono_isotherm(isotherm, experiment_group))
        experiment_group.attrs.create('monocomponent_isotherms', '|\|'.join(isotherm_names))

        isotherm_names = []
        for isotherm in experiment.mixture_isotherms:
            isotherm_names.append(register_mix_isotherm(isotherm, experiment_group))
        experiment_group.attrs.create('mixture_isotherms', '|\|'.join(isotherm_names))



if __name__=='__main__':

    CO2 = Adsorbate(
        AdsorbateType.GAS, 'Carbon Dioxide', 'CO2'
    )

    
    CH4 = Adsorbate(
        AdsorbateType.GAS, 'Methane', 'CH4'
    )

    N2 = Adsorbate(
        AdsorbateType.GAS, 'Nitrogen', 'N2'
    )

    register_adsorbate(CO2)
    register_adsorbate(CH4)
    register_adsorbate(N2)

    

    co2_data = MonoIsothermFileData(
        'SUDI_co2.txt', CO2, 0,1, pressure_conversion_factor_to_Pa=1e6
    )
    ch4_data = MonoIsothermFileData(
        'SUDI_ch4.txt', CH4, 0,1, pressure_conversion_factor_to_Pa=1e6
    )
    n2_data = MonoIsothermFileData(
        'SUDI_n2.txt', N2, 0,1, pressure_conversion_factor_to_Pa=1e6
    )

    co2_isotherm = create_mono_isotherm('CO2-01', IsothermType.EXCESS, co2_data)
    ch4_isotherm = create_mono_isotherm('CH4-01', IsothermType.EXCESS, ch4_data)
    n2_isotherm = create_mono_isotherm('N2-01', IsothermType.EXCESS, n2_data)

    
    co2_ch4_1_data = MixIsothermFileData(
        'SUDI_CO2CH4_20.txt', [CO2, CH4], 0, [2,4], [1], load_missing_composition_from_equilibrium=True, pressure_conversion_factor_to_Pa=1e6
    )
    co2_ch4_1_isotherm = create_mix_isotherm(
        'CO2-CH4-1', IsothermType.EXCESS, co2_ch4_1_data
    )

    print(co2_ch4_1_isotherm)

    Calgon = Adsorbent(AdsorbentType.ACTIVATED_CARBON, 'Calgon-F400')
    experiment = Experiment(name='Sudi',authors=['a', 'b','c'], adsorbent=Calgon, experiment_type=ExperimentType.VOLUMETRIC, temperature=318.2, monocomponent_isotherms=[co2_isotherm, ch4_isotherm, n2_isotherm])

    register_experiment(experiment)