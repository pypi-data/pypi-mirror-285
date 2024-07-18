from typing import Optional, Union
import numpy as np
from funcnodes import Shelf, NodeDecorator
from exposedfunctionality import controlled_wrapper
from tensorflow.keras.utils import to_categorical


@NodeDecorator(
    node_id="tensorflow.keras.utils.to_categorical",
    name="to_categorical",
)
@controlled_wrapper(to_categorical, wrapper_attribute="__fnwrapped__")
def _to_categorical(
    x: Union[list, np.ndarray],
    num_classes: Optional[int] = None,
) -> np.ndarray:
    return to_categorical(x, num_classes)


UTILS_NODE_SHELFE = Shelf(
    nodes=[_to_categorical],
    subshelves=[],
    name="Utilities",
    description="Python & NumPy utilities",
)
