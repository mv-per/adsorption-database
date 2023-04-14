from pathlib import Path
from adsorption_database.handlers import TextFileHandler
from adsorption_database.handlers.text_file_hander import (
    GetLoadingsFromAdsorbed,
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
    CH4 = Adsorbate("Methane", "CH4")
    N2 = Adsorbate("Nitrogen", "N2")
    adsorbent = Adsorbent(AdsorbentType.ACTIVATED_CARBON, "Norit R1", void_volume=0.3511)
    handler.register_adsorbent(adsorbent)

    mono_isotherms = []
    for file_name, adsorbate, ix in zip(
        ["DRE_99_co2_298K", "DRE_99_ch4_298K", "DRE_99_n2_298K"],
        [CO2, CH4, N2],
        [1, 1, 1],
    ):
        handler.register_adsorbate(adsorbate)

        pure_data = MonoIsothermTextFileData(
            f"{file_name}.txt", adsorbate, 0, 1, pressure_conversion_factor_to_Pa=1e6
        )
        mono_isotherms.append(
            handler.create_mono_isotherm(
                f"{adsorbate.chemical_formula}-0{ix}", 298, IsothermType.EXCESS, pure_data
            )
        )

    mix_isotherms = []

    mix = [
        {"adsorbates": [CH4, CO2], "x": [20, 55, 95], "pos_n": [2, 4], "pos_y": [1], "get": False},
        {"adsorbates": [CH4, N2], "x": [10, 45, 75], "pos_n": [2, 4], "pos_y": [1], "get": False},
        {"adsorbates": [CO2, N2], "x": [20, 50, 90], "pos_n": [2, 4], "pos_y": [1], "get": False},
        {
            "adsorbates": [CH4, CO2, N2],
            "x": [1, 2, 3, 4, 5],
            "pos_n": [3, 6],
            "pos_y": [1, 2],
            "pos_x": [4, 5],
            "pos_nt": 3,
            "get": True,
        },
    ]

    for mixture in mix:
        adsorbates = mixture["adsorbates"]
        compositions = mixture["x"]

        if mixture["get"]:
            get_loadings = GetLoadingsFromAdsorbed(True, mixture["pos_x"], mixture["pos_nt"])
        else:
            get_loadings = None

        for x in compositions:

            names = [adsorbate.chemical_formula for adsorbate in adsorbates]

            adsorbates_names = ("_").join(names)
            file_name = f"DRE_99_{adsorbates_names}_{x}"
            print(file_name)

            mix_data = MixIsothermTextFileData(
                f"{file_name}.txt",
                adsorbates,
                0,
                mixture["pos_n"],
                mixture["pos_y"],
                load_missing_composition_from_equilibrium=True,
                pressure_conversion_factor_to_Pa=1e6,
                get_loadings_from_adsorbed=get_loadings,
            )

            name = ("-").join(names)
            mix_isotherms.append(
                handler.create_mix_isotherm(f"{name}-{x}", 298, IsothermType.EXCESS, mix_data)
            )

    experiment = Experiment(
        name="Dre-norit-R1",
        authors=[
            "Dreisbach", "Staudt", "Keller"
        ],
        adsorbent=adsorbent,
        experiment_type=ExperimentType.GRAVIMETRIC,
        monocomponent_isotherms=mono_isotherms,
        mixture_isotherms=mix_isotherms,
        paper_url="https://link.springer.com/article/10.1023/A:1008914703884",
        year="1999",
        paper_doi="10.1023/A:1008914703884",
    )

    handler.register_experiment(experiment)

    handler.gen_regression()
