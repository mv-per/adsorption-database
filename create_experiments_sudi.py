from pathlib import Path
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
    CH4 = Adsorbate("Methane", "CH4")
    N2 = Adsorbate("Nitrogen", "N2")
    Calgon = Adsorbent(AdsorbentType.ACTIVATED_CARBON, "Calgon-F400")
    handler.register_adsorbent(Calgon)

    mono_isotherms = []
    for file_name, adsorbate, ix in zip(
        ["SUDI_co2", "SUDI_ch4", "SUDI_n2", "SUDI_ch4_2", "SUDI_n2_2"],
        [CO2, CH4, N2, CH4, N2],
        [1, 1, 1, 2, 2],
    ):
        handler.register_adsorbate(adsorbate)

        pure_data = MonoIsothermTextFileData(
            f"{file_name}.txt", adsorbate, 0, 1, pressure_conversion_factor_to_Pa=1e6
        )
        mono_isotherms.append(
            handler.create_mono_isotherm(
                f"{adsorbate.chemical_formula}-0{ix}", 318.2, IsothermType.EXCESS, pure_data
            )
        )

    mix_isotherms = []

    mix = [
        {"adsorbates": [CH4, CO2], "x": [20, 40, 60, 80]},
        {"adsorbates": [CH4, N2], "x": [20, 40, 60, 81]},
        {"adsorbates": [N2, CO2], "x": [20, 40, 58, 80]},
    ]

    for mixture in mix:
        adsorbates = mixture["adsorbates"]
        compositions = mixture["x"]

        for x in compositions:

            names = [adsorbate.chemical_formula for adsorbate in adsorbates]

            adsorbates_names = ("").join(names)
            file_name = f"SUDI_{adsorbates_names}_{x}"
            print(file_name)

            mix_data = MixIsothermTextFileData(
                f"{file_name}.txt",
                adsorbates,
                0,
                [2, 4],
                [1],
                load_missing_composition_from_equilibrium=True,
                pressure_conversion_factor_to_Pa=1e6,
            )

            name = ("-").join(names)
            mix_isotherms.append(
                handler.create_mix_isotherm(f"{name}-{x}", 318.2, IsothermType.EXCESS, mix_data)
            )

    experiment = Experiment(
        name="Sudi-calgon",
        authors=[
            "Mahmud Sudibandriyo",
            "Zhejun Pan",
            "James E. Fitzgerald",
            "Robert L. Robinson",
            "Khaled A. M. Gasem",
        ],
        adsorbent=Calgon,
        experiment_type=ExperimentType.VOLUMETRIC,
        monocomponent_isotherms=mono_isotherms,
        mixture_isotherms=mix_isotherms,
        paper_url="https://pubs.acs.org/doi/pdf/10.1021/la020976k",
        year="2003",
        paper_doi="10.1021/la020976k",
    )

    handler.register_experiment(experiment)

    handler.gen_regression()
