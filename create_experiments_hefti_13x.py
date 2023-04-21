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
    handler = TextFileHandler(Path("temp"))

    CO2 = Adsorbate("Carbon Dioxide", "CO2")
    N2 = Adsorbate("Nitrogen", "N2")
    z13X = Adsorbent(
        AdsorbentType.ZEOLITE,
        "13X",
        pellet_size=2,
        manufacturer="ZeoChem",
    )

    TEMPERATURES = [25, 45, 65, 100, 140]
    pos = [[0, 1], [2, 3], [4, 5], [6, 7], [8, 9]]

    mono_isotherms = []

    for file_name, adsorbate in zip(
        ["hefti_co2_13x", "hefti_n2_13x"],
        [CO2, N2],
    ):
        for temperature, indexes in zip(TEMPERATURES, pos):
            pure_data = MonoIsothermTextFileData(
                f"{file_name}.txt",
                adsorbate,
                indexes[0],
                indexes[1],
                pressure_conversion_factor_to_Pa=1e5,
                filter_duplicate=True,
            )
            T = temperature + 273.15

            isotherm = handler.create_mono_isotherm(
                f"{adsorbate.chemical_formula}-{T}",
                T,
                IsothermType.EXCESS,
                pure_data,
            )

            print(isotherm.name)
            mono_isotherms.append(isotherm)

    mix_isotherms = []

    TEMPERATURES = [25, 45]
    exps = [1, 2, 3]

    adsorbates = [CO2, N2]

    for temp in TEMPERATURES:
        for exp in exps:
            file_name = f"hefti_co2_n2_{temp}_13x-{exp}"

            mix_data = MixIsothermTextFileData(
                f"{file_name}.txt",
                adsorbates,
                0,
                [2, 3],
                [1],
                load_missing_composition_from_equilibrium=True,
                pressure_conversion_factor_to_Pa=1e5,
            )
            names: List[str] = [
                str(adsorbate.chemical_formula) for adsorbate in adsorbates
            ]
            name = ("-").join(names)

            isotherm = handler.create_mix_isotherm(
                f"{name}-{temp}-{exp}",
                temp + 273.15,
                IsothermType.EXCESS,
                mix_data,
            )

            print(isotherm.name)
            mix_isotherms.append(isotherm)

    experiment = Experiment(
        name="HEFTI-13x",
        authors=[
            "Max Hefti",
            "Dorian Marx",
            "Lisa Joss",
            "Marco Mazzoti",
        ],
        adsorbent=z13X,
        experiment_type=ExperimentType.GRAVIMETRIC,
        monocomponent_isotherms=mono_isotherms,
        mixture_isotherms=mix_isotherms,
        paper_doi=["10.1016/j.micromeso.2015.05.044"],
    )

    handler.register_experiment(experiment)
