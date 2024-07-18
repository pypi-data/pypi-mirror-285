from pathlib import Path

from sorting_vis.algorithms import Algorithms

MINIMUM_ARRAY_VALUE = 10
MAXIMUM_ARRAY_VALUE = 1000
MINIMUM_ARRAY_SAMPLES = 10
MAXIMUM_ARRAY_SAMPLES = 1000
DIR_PATH = Path(__file__).resolve().parents[0]
ASSETS_PATH = DIR_PATH / "assets"
CONFIG_PATH = DIR_PATH / "config.ini"
SMARTFILL_PATH = DIR_PATH / "smartfill.json"
LOWER_SAMPLE_BOUND_PLACEHOLDER = f"< upper, >= {MINIMUM_ARRAY_VALUE}"
UPPER_SAMPLE_BOUND_PLACEHOLDER = f"> lower, <= {MAXIMUM_ARRAY_VALUE}"
SAMPLE_COUNT_PLACEHOLDER = (
    f">= {MINIMUM_ARRAY_SAMPLES}, <= {MAXIMUM_ARRAY_SAMPLES}"
)
AVAILABLE_SORTING_FUNCTIONS = [
    attr for attr in dir(Algorithms) if not attr.startswith("_")
]
