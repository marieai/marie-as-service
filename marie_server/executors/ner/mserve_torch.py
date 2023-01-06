import numpy as np
import torch
import marie
import marie.helper

from typing import Dict, Union, Optional, TYPE_CHECKING
from marie import DocumentArray, Executor, requests
from marie.logging.predefined import default_logger

if TYPE_CHECKING:  # pragma: no cover
    from fastapi import FastAPI


class NerExecutor(Executor):
    def __init__(
        self,
        name: str = '',
        device: Optional[str] = None,
        num_worker_preprocess: int = 4,
        dtype: Optional[Union[str, torch.dtype]] = None,
        **kwargs,
    ):
        """
        :param device: 'cpu' or 'cuda'. Default is None, which auto-detects the device.
        :param num_worker_preprocess: The number of CPU workers to preprocess images and texts. Default is 4.
        :param minibatch_size: The size of the minibatch for preprocessing and encoding. Default is 32. Reduce this
            number if you encounter OOM errors.
        :param dtype: inference data type, if None defaults to torch.float32 if device == 'cpu' else torch.float16.
        """
        super().__init__(**kwargs)

    @requests(on="/ner")
    def extract(self, docs: DocumentArray, **kwargs):
        default_logger.info("Executing NER")
        default_logger.info(kwargs)
        docs[0].text = 'AA - hello, world!'
        docs[1].text = 'AA - goodbye, world!'

    @requests(on='/ner-work')
    def work(self, parameters, **kwargs):
        default_logger.info("Executing NER work")
        print(parameters)
        default_logger.info(kwargs)


def extend_rest_interface_ner_mixin(app: 'FastAPI') -> 'FastAPI':
    @app.get('/extension-b', tags=['Extract - REST API', 'ner-rest'])
    async def extension_A():
        default_logger.info("Executing NER extension")
        return {"message": "XYZ"}
