from typing import TYPE_CHECKING

from fastapi import FastAPI, Request
from marie import Client
from marie.logging.predefined import default_logger

from marie_server.rest_extension import parse_request_to_docs, parse_response_to_payload

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
            parameters, input_docs = await parse_request_to_docs(request)
            payload = {}

            async for resp in c.post(
                '/ner/extract',
                input_docs,
                request_size=-1,
                parameters=parameters,
                return_responses=True,
            ):
                print(type(resp))
                payload = parse_response_to_payload(resp)
            return payload
        except BaseException as error:
            default_logger.error("Extract error", error)
            return {"error": error}

    @app.get('/api/ner/status', tags=['ner', 'rest-api'])
    async def text_status():
        default_logger.info("Executing text_status")

        return {"status": "OK"}
