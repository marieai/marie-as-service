from typing import TYPE_CHECKING

from fastapi import FastAPI, Request
from marie import Client
from marie.api import extract_payload, value_from_payload_or_args
from marie.logging.predefined import default_logger
from marie.utils.docs import docs_from_file, array_from_docs

if TYPE_CHECKING:  # pragma: no cover
    from fastapi import FastAPI


def extend_rest_interface_overlay(app: FastAPI) -> None:
    """
    Extends HTTP Rest endpoint to provide compatibility with existing REST endpoints
    :param app:
    :return:
    """
    c = Client(
        host='0.0.0.0', port=52000, protocol='grpc', request_size=1, asyncio=True
    )

    @app.post('/api/overlay', tags=['overlay', 'rest-api'])
    async def overlay_post(request: Request):
        default_logger.info("Executing overlay_post")
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

            doc_id = value_from_payload_or_args(payload, "doc_id", default=checksum)
            doc_type = value_from_payload_or_args(payload, "doc_type", default="")

            args = {
                "queue_id": queue_id,
                "ref_id": doc_id,
                "ref_type": doc_type,
            }
            payload = {}

            async for resp in c.post(
                '/overlay/segment',
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

    @app.get('/api/overlay/status', tags=['overlay', 'rest-api'])
    async def overlay_status():
        default_logger.info("Executing overlay_status")

        return {"status": "OK"}
