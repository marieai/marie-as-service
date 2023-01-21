from typing import TYPE_CHECKING

from marie.api import extract_payload, value_from_payload_or_args
from marie.types.request.data import DataRequest
from marie.utils.docs import docs_from_file

if TYPE_CHECKING:  # pragma: no cover
    from fastapi import FastAPI, Request


def extend_rest_interface(app: 'FastAPI') -> 'FastAPI':
    """Register executors REST endpoints that do not depend on DocumentArray
    :param app:
    :return:
    """

    from .executors.extract.mserve_torch import (
        extend_rest_interface_extract,
    )
    from .executors.ner.mserve_torch import (
        extend_rest_interface_ner,
    )
    from .executors.overlay.mserve_torch import (
        extend_rest_interface_overlay,
    )

    extend_rest_interface_extract(app)
    extend_rest_interface_ner(app)
    extend_rest_interface_overlay(app)

    return app


def parse_response_to_payload(resp: DataRequest):
    """
    We get raw response `marie.types.request.data.DataRequest`
    and we will extract the returned payload (Dictionary object)

    :param resp:
    :return:
    """
    if "__results__" in resp.parameters:
        results = resp.parameters["__results__"]
        payload = list(results.values())[0]
        print(payload)
        return payload

    return {
        "status": "FAILED",
        "message": "are you calling valid endpoint, __results__ missing in params",
    }


async def parse_request_to_docs(request: 'Request'):
    payload = await request.json()
    # every request should contain queue_id if not present it will default to '0000-0000-0000-0000'
    queue_id = value_from_payload_or_args(
        payload, "queue_id", default="0000-0000-0000-0000"
    )
    tmp_file, checksum, file_type = extract_payload(payload, queue_id)
    input_docs = docs_from_file(tmp_file)
    payload["data"] = None

    doc_id = value_from_payload_or_args(payload, "doc_id", default=checksum)
    doc_type = value_from_payload_or_args(payload, "doc_type", default="")

    parameters = {
        "queue_id": queue_id,
        "ref_id": doc_id,
        "ref_type": doc_type,
    }
    return parameters, input_docs
