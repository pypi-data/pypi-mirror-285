try:
    from pydantic.v1 import *  # noqa: F403
    from pydantic.v1 import utils  # noqa: F401
except ImportError:
    from pydantic import *  # noqa: F403
