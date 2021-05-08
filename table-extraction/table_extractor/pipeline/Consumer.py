from typing import Dict

from pipeline.PipelineComponent import PipelineComponent


class Consumer(PipelineComponent):

    def handle(self, message: Dict):
        self.consume(message)

    def set_next(self, pipeline_component: PipelineComponent):
        raise Exception("Consumer cannot have next reference")

    def consume(self, message: Dict):
        pass


class PrintConsumer(Consumer):

    def consume(self, message: Dict):
        print(message)
