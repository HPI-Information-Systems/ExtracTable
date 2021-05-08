from functools import reduce
from typing import List

from pipeline.Consumer import PrintConsumer, Consumer
from pipeline.Producer import Producer
from pipeline.Transformer import Transformer


class Pipeline(object):

    def __init__(
            self,
            producer: Producer,
            transformers: List[Transformer] = None,
            consumer: Consumer = PrintConsumer()
    ):
        if producer is None:
            raise Exception('Producer cannot be None')
        self.producer = producer
        self.pipeline = [
            producer,
            *(transformers or []),
            consumer
        ]
        self.chain_pipeline()

    def run(self):
        while self.producer.has_next():
            self.producer.handle()
        results = [component.reached_end() for component in self.pipeline]
        return results[-1] if results else None

    def chain_pipeline(self):
        reduce(lambda prev_component, component: prev_component.set_next(component), self.pipeline)

