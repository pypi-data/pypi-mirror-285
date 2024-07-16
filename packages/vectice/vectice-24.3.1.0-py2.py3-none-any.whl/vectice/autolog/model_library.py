from enum import Enum


class ModelLibrary(Enum):
    """Enumeration that defines what the model library."""

    SKLEARN = "SKLEARN"
    SKLEARN_PIPELINE = "SKLEARN_PIPELINE"
    LIGHTGBM = "LIGHTGBM"
    CATBOOST = "CATBOOST"
    KERAS = "KERAS"
    STATSMODEL = "STATSMODEL"
    PYTORCH = "PYTORCH"
    NONE = "NONE"
