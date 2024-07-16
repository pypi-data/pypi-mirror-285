r"""The component that orchestrates model client (Embedding models in particular) and output processors."""

from typing import Optional, Any, Dict, List
import logging
from tqdm import tqdm

from lightrag.core.types import ModelType
from lightrag.core.model_client import ModelClient
from lightrag.core.types import (
    EmbedderOutputType,
    EmbedderInputType,
    BatchEmbedderInputType,
    BatchEmbedderOutputType,
)
from lightrag.core.component import Component
import lightrag.core.functional as F


log = logging.getLogger(__name__)


class Embedder(Component):
    r"""
    A user-facing component that orchestrates an embedder model via the model client and output processors.

    Args:
        model_client (ModelClient): The model client to use for the embedder.
        model_kwargs (Dict[str, Any], optional): The model kwargs to pass to the model client. Defaults to {}.
        output_processors (Optional[Component], optional): The output processors after model call. Defaults to None.
            If you want to add further processing, it should operate on the ``EmbedderOutput`` data type.

    input: a single str or a list of str. When a list is used, the list is processed as a batch of inputs in the model client.

    Note:
        - The ``output_processors`` will be applied only on the data field of ``EmbedderOutput``, which is a list of ``Embedding``.
        - Use ``BatchEmbedder`` for automatically batching input of large size, larger than 100.
    """

    model_type: ModelType = ModelType.EMBEDDER
    model_client: ModelClient
    output_processors: Optional[Component]

    def __init__(
        self,
        *,
        model_client: ModelClient,
        model_kwargs: Dict[str, Any] = {},
        output_processors: Optional[Component] = None,
    ) -> None:

        super().__init__(model_kwargs=model_kwargs)
        if not isinstance(model_kwargs, Dict):
            raise ValueError(
                f"{type(self).__name__} requires a dictionary for model_kwargs, not a string"
            )
        self.model_kwargs = model_kwargs.copy()
        # if "model" not in model_kwargs:
        #     raise ValueError(
        #         f"{type(self).__name__} requires a 'model' to be passed in the model_kwargs"
        #     )
        # ensure the model_client is an instance of ModelClient
        if not isinstance(model_client, ModelClient):
            raise ValueError(
                f"{type(self).__name__} requires a ModelClient instance for model_client, please pass it as OpenAIClient() or GroqAPIClient() for example."
            )
        self.model_client = model_client
        self.output_processors = output_processors

    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> "Embedder":
        """Create an Embedder from a configuration dictionary.

        Example:

        .. code-block:: python

            embedder_config =  {
                "model_client": {
                    "component_name": "OpenAIClient",
                    "component_config": {}
                },
                "model_kwargs": {
                    "model": "text-embedding-3-small",
                    "dimensions": 256,
                    "encoding_format": "float"
                }
            }

            embedder = Embedder.from_config(embedder_config)
        """
        assert "model_client" in config, "model_client is required in the config"
        return super().from_config(config)

    def update_default_model_kwargs(self, **model_kwargs) -> Dict:
        return F.compose_model_kwargs(self.model_kwargs, model_kwargs)

    def _pre_call(self, input: EmbedderInputType, model_kwargs: Dict) -> Dict:
        # step 1: combine the model_kwargs with the default model_kwargs
        composed_model_kwargs = self.update_default_model_kwargs(**model_kwargs)
        # step 2: convert the input to the api_kwargs
        api_kwargs = self.model_client.convert_inputs_to_api_kwargs(
            input=input,
            model_kwargs=composed_model_kwargs,
            model_type=self.model_type,
        )
        log.debug(f"api_kwargs: {api_kwargs}")
        return api_kwargs

    def _post_call(self, response: Any) -> EmbedderOutputType:
        embedding_output: EmbedderOutputType = (
            self.model_client.parse_embedding_response(response)
        )

        data = embedding_output.data
        if self.output_processors:
            if not embedding_output.error and data is not None:
                embedding_output.data = self.output_processors(data)
            else:
                log.debug(
                    f"Skipping output processors due to error: {embedding_output.error}"
                )

        return embedding_output

    def call(
        self,
        input: EmbedderInputType,
        model_kwargs: Optional[Dict] = {},
    ) -> EmbedderOutputType:
        log.debug(f"Calling {self.__class__.__name__} with input: {input}")
        api_kwargs = self._pre_call(input=input, model_kwargs=model_kwargs)
        response = self.model_client.call(
            api_kwargs=api_kwargs, model_type=self.model_type
        )

        output = self._post_call(response)
        # add back the input
        output.input = [input] if isinstance(input, str) else input
        log.debug(f"Output from {self.__class__.__name__}: {output}")
        return output

    async def acall(
        self,
        input: EmbedderInputType,
        model_kwargs: Optional[Dict] = {},
    ) -> EmbedderOutputType:
        log.debug(f"Calling {self.__class__.__name__} with input: {input}")
        composed_model_kwargs = self._pre_call(input=input, model_kwargs=model_kwargs)
        response = await self.model_client.acall(
            input=input, model_kwargs=composed_model_kwargs, model_type=self.model_type
        )
        output = self._post_call(response)
        log.debug(f"Output from {self.__class__.__name__}: {output}")
        return output

    def _extra_repr(self) -> str:
        s = f"model_kwargs={self.model_kwargs}, "
        return s


class BatchEmbedder(Component):
    __doc__ = r"""Adds batching to the embedder component.

    Args:
        embedder (Embedder): The embedder to use for batching.
        batch_size (int, optional): The batch size to use for batching. Defaults to 100.
    """

    def __init__(self, embedder: Embedder, batch_size: int = 100) -> None:
        super().__init__(batch_size=batch_size)
        self.embedder = embedder
        self.batch_size = batch_size

    def call(
        self, input: BatchEmbedderInputType, model_kwargs: Optional[Dict] = {}
    ) -> BatchEmbedderOutputType:
        r"""Call the embedder with batching.

        Args:
            input (BatchEmbedderInputType): The input to the embedder. Use this when you have a large input that needs to be batched. Also ensure
            the output can fit into memory.
            model_kwargs (Optional[Dict], optional): The model kwargs to pass to the embedder. Defaults to {}.

        Returns:
            BatchEmbedderOutputType: The output from the embedder.
        """

        if isinstance(input, str):
            input = [input]
        n = len(input)
        embeddings: List[EmbedderOutputType] = []
        for i in tqdm(
            range(0, n, self.batch_size),
            desc="Batch embedding documents",
        ):
            batch_input = input[i : i + self.batch_size]
            batch_output = self.embedder.call(
                input=batch_input, model_kwargs=model_kwargs
            )
            embeddings.append(batch_output)
        return embeddings
