import logging
from .wrappers import stock, stocks
from .backends.nasdaq import metadata


logger = logging.getLogger(__name__)


try:
    from .visualization import template
except ModuleNotFoundError as e:
    logger.warning(e)

try:
    # from .visualization import plot_history as plot
    from .visualization.altairplotter import plot_history as plot
except ModuleNotFoundError as e:
    logger.warning(e)

    def plot(*args, **kwargs):
        raise ImportError(
            "Missing optional dependency 'altair'. Use pip or conda to install it."
        )
