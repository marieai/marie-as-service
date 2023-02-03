import asyncio
import time
import uuid
from functools import partial
from typing import TYPE_CHECKING, Any, Optional

from fastapi import Request
from marie import Client
from marie.api import extract_payload
from marie.api import value_from_payload_or_args
from marie.logging.predefined import default_logger
from marie.types.request.data import DataRequest
from marie.utils.docs import docs_from_file
from marie.utils.types import strtobool

from marie.messaging import (
    mark_request_as_complete,
    mark_request_as_started,
    mark_request_as_failed,
)

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

    client = Client(
        host='0.0.0.0', port=52000, protocol='grpc', request_size=1, asyncio=True
    )

    extend_rest_interface_extract(app, client)
    extend_rest_interface_ner(app, client)
    extend_rest_interface_overlay(app, client)

    return app


def generate_job_id() -> str:
    return str(uuid.uuid4())


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
        return payload

    return {
        "status": "FAILED",
        "message": "are you calling valid endpoint, __results__ missing in params",
    }


async def parse_payload_to_docs(payload: Any, clear_payload: Optional[bool] = True):
    """
    Parse payload request

    :param payload:
    :param clear_payload:
    :return:
    """
    # every request should contain queue_id if not present it will default to '0000-0000-0000-0000'
    queue_id = value_from_payload_or_args(
        payload, "queue_id", default="0000-0000-0000-0000"
    )
    tmp_file, checksum, file_type = extract_payload(payload, queue_id)
    input_docs = docs_from_file(tmp_file)

    if clear_payload:
        key = "data"
        if "data" in payload:
            key = "data"
        elif "srcData" in payload:
            key = "srcData"
        elif "srcBase64" in payload:
            key = "srcBase64"
        elif "srcFile" in payload:
            key = "srcFile"

        payload[key] = None

    doc_id = value_from_payload_or_args(payload, "doc_id", default=checksum)
    doc_type = value_from_payload_or_args(payload, "doc_type", default="")

    parameters = {
        "queue_id": queue_id,
        "ref_id": doc_id,
        "ref_type": doc_type,
    }
    return parameters, input_docs


async def handle_request(
    api_tag: str, request: Request, client: Client, handler: callable
):
    payload = await request.json()
    job_id = generate_job_id()
    default_logger.info(f"handle_request[{api_tag}] : {job_id}")
    sync = strtobool(value_from_payload_or_args(payload, "sync", default=False))

    task = asyncio.ensure_future(
        process_request(api_tag, job_id, payload, partial(handler, client))
    )
    # run the task synchronously
    if sync:
        results = await asyncio.gather(task)
        return results[0]

    return {"jobid": job_id, "status": "ok"}


async def process_request(api_tag: str, job_id: str, payload: Any, handler: callable):
    status = "OK"
    job_tag = ""
    results = None
    try:
        default_logger.info(f"Starting request: {job_id}")
        parameters, input_docs = await parse_payload_to_docs(payload)
        job_tag = parameters["ref_type"] if "ref_type" in parameters else ""
        parameters["payload"] = payload  # THIS IS TEMPORARY HERE

        # payload data attribute should be stripped at this time
        await mark_request_as_started(
            job_id, api_tag, job_tag, status, int(time.time()), payload
        )

        async def run(op, _docs, _param):
            return await op(_docs, _param)

        results = await run(handler, input_docs, parameters)
        return results
    except BaseException as error:
        default_logger.error("processing error", error)
        status = "ERROR"

        await mark_request_as_failed(
            job_id, api_tag, job_tag, status, int(time.time(), error)
        )

        return {"jobid": job_id, "status": status, "error": error}
    finally:
        await mark_request_as_complete(
            job_id, api_tag, job_tag, status, int(time.time()), results
        )
