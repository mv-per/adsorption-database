from pathlib import Path
from typing import List
from adsorption_database.handlers import TextFileHandler
from adsorption_database.handlers.text_file_hander import (
    MixIsothermTextFileData,
    MonoIsothermTextFileData,
)
from adsorption_database.models.adsorbate import Adsorbate
from adsorption_database.models.adsorbent import Adsorbent, AdsorbentType
from adsorption_database.models.experiment import Experiment, ExperimentType
from adsorption_database.models.isotherms import IsothermType

if __name__ == "__main__":

    handler = TextFileHandler(Path("temp").resolve())

    CO2 = Adsorbate("Carbon Dioxide", "CO2")
    CH4 = Adsorbate("Methane", "CH4")
    N2 = Adsorbate("Nitrogen", "N2")
    Zeolite_5A = Adsorbent(AdsorbentType.ZEOLITE, "5A")

    mono_data = {
        '273':[0,1],
        '283':[2,3],
        '303':[4,5],
        '323':[6,7],
        '343':[8,9],
    }

    mono_isotherms = []
    for adsorbate in [CO2,CH4,N2]:
        for temp, indexes in mono_data.items():

            pure_data = MonoIsothermTextFileData(
                f"Mofahari_2014_{adsorbate.chemical_formula}.txt", adsorbate, indexes[0], indexes[1], pressure_conversion_factor_to_Pa=1e5, filter_duplicate=True
            )
            mono_isotherms.append(
                handler.create_mono_isotherm(
                    f"{adsorbate.chemical_formula}-{temp}", float(temp), IsothermType.EXCESS, pure_data
                )
            )

    mix_isotherms = []

    mix = [
        {"adsorbates": [CH4, CO2],'temp':303, "x": [1,2,3]},
        {"adsorbates": [CH4, CO2],'temp':323, "x": [1,2]},
        {"adsorbates": [CH4, N2],'temp':303, "x": [1,2]},
        {"adsorbates": [CH4, N2],'temp':323, "x": [1,2]},
    ]

    for mixture in mix:
        adsorbates: List[Adsorbate] = mixture["adsorbates"]  # type:ignore[assignment]
        compositions: List[int] = mixture["x"]  # type:ignore[assignment]
        temp: int = mixture["temp"]  # type:ignore[assignment]

        for x in compositions:

            names: List[str] = [str(adsorbate.chemical_formula) for adsorbate in adsorbates]

            adsorbates_names = ("_").join(names)
            file_name = f"Mofahari_{adsorbates_names}_{temp}-{x}"
            print(file_name)

            mix_data = MixIsothermTextFileData(
                f"{file_name}.txt",
                adsorbates,
                0,
                [3,4],
                [1],
                load_missing_composition_from_equilibrium=True,
                pressure_conversion_factor_to_Pa=1e5,
            )

            name = ("-").join(names)
            mix_isotherms.append(
                handler.create_mix_isotherm(f"{name}-{x}", 318.2, IsothermType.EXCESS, mix_data)
            )

    experiment = Experiment(
        name="MOFA-5A",
        authors=[
            "Ali Bakhtyari",
            "Masoud Mofarahi",
            "Fatemeh Gholipour",
        ],
        adsorbent=Zeolite_5A,
        experiment_type=ExperimentType.VOLUMETRIC,
        monocomponent_isotherms=mono_isotherms,
        mixture_isotherms=mix_isotherms,
        paper_doi=["10.1016/j.micromeso.2014.08.022", "10.1021/je4005036"],
    )

    handler.register_experiment(experiment)
