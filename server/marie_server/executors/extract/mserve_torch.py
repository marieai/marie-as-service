import asyncio
import uuid

from fastapi import FastAPI, Request
from marie import Client, DocumentArray
from marie import Document
from marie.api import extract_payload
from marie.logging.predefined import default_logger
from marie.utils.docs import docs_from_file, array_from_docs


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
        print(request)
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

    @app.post('/api/extract', tags=['text', 'rest-api'])
    async def text_extract_post(request: Request):
        default_logger.info("Executing text_extract_post")
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
                '/text/extract',
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

    @app.get('/api/text/status', tags=['text', 'rest-api'])
    async def text_status():
        default_logger.info("Executing text_status")

        return {"status": "OK"}
