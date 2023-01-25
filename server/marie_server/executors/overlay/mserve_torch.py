from typing import TYPE_CHECKING

from fastapi import FastAPI, Request
from marie import Client
from marie.logging.predefined import default_logger
from marie_server.rest_extension import (
    parse_response_to_payload,
    parse_payload_to_docs,
    handle_request,
)

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

    @app.post('/api/overlayXXXS', tags=['overlay', 'rest-api'])
    async def overlay_postXXX(request: Request):
        default_logger.info("Executing overlay_post")
        try:
            payload = await request.json()
            parameters, input_docs = await parse_payload_to_docs(payload)
            payload = {}

            async for resp in c.post(
                '/overlay/segment',
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

    async def __process(client: Client, input_docs, parameters):
        payload = {}
        async for resp in client.post(
            '/overlay/segment',
            input_docs,
            request_size=-1,
            parameters=parameters,
            return_responses=True,
        ):
            payload = parse_response_to_payload(resp)
        return payload

    @app.post('/api/overlay', tags=['overlay', 'rest-api'])
    async def overlay_post(request: Request):
        """
        Handle API Overlay endpoint
        :param request:
        :return:
        """
        return await handle_request(request, c, __process)

    @app.get('/api/overlay/status', tags=['overlay', 'rest-api'])
    async def overlay_status():
        default_logger.info("Executing overlay_status")

        return {"status": "OK"}
