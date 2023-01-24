import asyncio
import uuid
from typing import Any

from fastapi import FastAPI, Request
from marie import Client, DocumentArray
from marie import Document
from marie.api import extract_payload
from marie.logging.predefined import default_logger
from marie.utils.docs import docs_from_file, array_from_docs

from marie_server.rest_extension import parse_response_to_payload


def mark_request_as_complete(request_id: str):
    default_logger.info(f"Executing mark_request_as_complete : {request_id}")


def extend_rest_interface_extract(app: FastAPI) -> None:

    """
    Extends HTTP Rest endpoint to provide compatibility with existing REST endpoints
    :param app:
    :return:
    """
    c = Client(
        host='0.0.0.0', port=52000, protocol='grpc', request_size=1, asyncio=True
    )

    @app.post('/api/text/extract-test', tags=['text', 'rest-api'])
    async def text_extract_post_test(request: Request):
        default_logger.info("Executing text_extract_post")
        payload = await request.json()
        print(payload.keys())
        inputs = DocumentArray.empty(6)

        # async inputs for the client
        async def async_inputs():
            uuid_val = uuid.uuid4()
            for _ in range(2):
                yield Document(text=f'Doc_{uuid_val}#{_}')
                await asyncio.sleep(0.2)

        # {'data': ????, 'mode': 'multiline', 'output': 'json', 'doc_id': 'e8974900-0bee-4a9a-9c91-d8fdc909f446', 'doc_type': 'example_ner'

        print(">> ")
        outputs = DocumentArray()
        out_text = []
        async for resp in c.post('/text/extract', async_inputs, request_size=1):
            print('--' * 100)
            print(resp)
            print(resp.texts)
            out_text.append(resp.texts)
            print('++' * 100)
            outputs.append(resp)

        return {"message": f"ZZZ : {len(outputs)}", "out_text": out_text}

    @app.get('/api/extract', tags=['text', 'rest-api'])
    async def text_extract_get(request: Request):
        default_logger.info("Executing text_extract_get")
        return {"message": "reply"}

    async def process_request(request_id: str, payload: Any):
        try:
            default_logger.info(f"Starting request: {request_id}")
            # every request should contain queue_id if not present it will default to '0000-0000-0000-0000'
            queue_id = (
                payload["queue_id"] if "queue_id" in payload else "0000-0000-0000-0000"
            )

            await asyncio.sleep(4)
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
                '/text/extract',
                input_docs,
                request_size=-1,
                parameters=args,
                return_responses=True,
            ):
                payload = parse_response_to_payload(resp)

            mark_request_as_complete(request_id)
            return payload
        except BaseException as error:
            default_logger.error("Extract error", error)
            return {"error": error}

    @app.post('/api/extract', tags=['text', 'rest-api'])
    async def text_extract_post(request: Request):
        request_id = str(uuid.uuid4())
        default_logger.info(f"Executing text_extract_post : {request_id}")
        payload = await request.json()
        asyncio.ensure_future(process_request(request_id, payload))

        return {"request_id": request_id}

    @app.get('/api/text/status', tags=['text', 'rest-api'])
    async def text_status():
        default_logger.info("Executing text_status")

        return {"status": "OK"}
