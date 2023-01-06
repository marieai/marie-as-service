from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from fastapi import FastAPI


def extend_rest_interface(app: 'FastAPI') -> 'FastAPI':
    """Register executors REST endpoints that do not depend on DocumentArray
    :param app:
    :return:
    """

    from .executors.extract.mserve_torch import (
        extend_rest_interface_extract_mixin,
    )
    from .executors.ner.mserve_torch import (
        extend_rest_interface_ner_mixin,
    )

    extend_rest_interface_extract_mixin(app)
    extend_rest_interface_ner_mixin(app)

    return app
