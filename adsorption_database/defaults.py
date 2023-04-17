from pathlib import Path
from os.path import dirname, abspath


EXPERIMENTS_FOLDER = Path(dirname(abspath(__file__))) / "temp"
MONO_ISOTHERMS = "Pure"
MIXTURE_ISOTHERMS = "Mixture"
EXPERIMENTS = "Experiments"
ADSORBATES = "Adsorbates"
ADSORBENTS = "Adsorbents"
SEPARATOR = "\--\\"
