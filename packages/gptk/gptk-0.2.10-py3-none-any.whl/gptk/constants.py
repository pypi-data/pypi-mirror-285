
from pathlib import Path
from pint import UnitRegistry as UR
from auto_all import start_all, end_all

start_all()

units = UR()
units.load_definitions(Path(__file__).parent.joinpath('data','gptk_units.txt'))
DANNYDEVITO  = 1 * units.DannyDeVito
STANLEYTUCCI = 1 * units.StanleyTucci
end_all()