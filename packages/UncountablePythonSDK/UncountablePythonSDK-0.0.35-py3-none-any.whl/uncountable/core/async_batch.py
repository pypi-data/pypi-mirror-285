from uncountable.core.client import Client
from uncountable.types import async_batch_t, base_t
from uncountable.types.async_batch import AsyncBatchRequest
from uncountable.types.async_batch_processor import AsyncBatchProcessorBase


class AsyncBatchProcessor(AsyncBatchProcessorBase):
    _client: Client
    _queue: list[AsyncBatchRequest]

    def __init__(self, *, client: Client) -> None:
        super().__init__()
        self._client = client
        self._queue = []

    def _enqueue(self, req: async_batch_t.AsyncBatchRequest) -> None:
        self._queue.append(req)

    def send(self) -> base_t.ObjectId:
        job_id = self._client.execute_batch_load_async(requests=self._queue).job_id
        self._queue = []
        return job_id
