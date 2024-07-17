from funcnodes import Shelf, NodeDecorator
from typing import Union, Optional, Iterator, Tuple, Callable
from enum import Enum
import numpy as np
from keras.layers import Layer

class Method(Enum):
    sigmoid = "sigmoid"
    isotonic = "isotonic"

    @classmethod
    def default(cls):
        return cls.isotonic.value


@NodeDecorator(
    node_id="sklearn.calibration.CalibratedClassifierCV",
    name="CalibratedClassifierCV",
)




CALIBRATION_NODE_SHELFE = Shelf(
    nodes=[calibrated_classifier_cv, calibrationcurve],
    subshelves=[],
    name="Calibration",
    description="Calibration of predicted probabilities.",
)
