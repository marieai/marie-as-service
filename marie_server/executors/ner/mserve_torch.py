import numpy as np
import torch
import marie
import marie.helper

from typing import Dict, Union, Optional, TYPE_CHECKING
from marie import DocumentArray, Executor, requests
from marie.logging.predefined import default_logger
from fastapi import FastAPI, Request
from marie import Client, DocumentArray
from marie import Document
from marie.api import extract_payload
from marie.logging.predefined import default_logger
from marie.utils.docs import docs_from_file, array_from_docs

if TYPE_CHECKING:  # pragma: no cover
    from fastapi import FastAPI


def extend_rest_interface_ner(app: FastAPI) -> None:
    """
    Extends HTTP Rest endpoint to provide compatibility with existing REST endpoints
    :param app:
    :return:
    """
    c = Client(
        host='0.0.0.0', port=52000, protocol='grpc', request_size=1, asyncio=True
    )

    @app.post('/api/ner', tags=['ner', 'rest-api'])
    async def text_ner_post(request: Request):
        default_logger.info("Executing text_ner_post")
        try:
            payload = await request.json()
            # every request should contain queue_id if not present it will default to '0000-0000-0000-0000'
            queue_id = (
                payload["queue_id"] if "queue_id" in payload else "0000-0000-0000-0000"
            )

            tmp_file, checksum, file_type = extract_payload(payload, queue_id)
            input_docs = docs_from_file(tmp_file)
            out_docs = array_from_docs(input_docs)
            payload["data"] = None

            args = {
                "queue_id": queue_id,
                "payload": payload,
            }
            payload = {}

            async for resp in c.post(
                '/ner/extract',
                input_docs,
                request_size=-1,
                parameters=args,
                return_responses=True,
            ):
                # We get raw response `marie.types.request.data.DataRequest`
                # and we will extract the returned payload (Dictionary object)
                docs = resp.data.docs
                results = resp.parameters["__results__"]
                payload = list(results.values())[0]
                print(payload)

            return payload
        except BaseException as error:
            default_logger.error("Extract error", error)
            return {"error": error}

    @app.get('/api/ner/status', tags=['ner', 'rest-api'])
    async def text_status():
        default_logger.info("Executing text_status")

        return {"status": "OK"}
