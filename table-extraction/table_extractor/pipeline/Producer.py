from typing import Dict

from pipeline.PipelineComponent import PipelineComponent


class Producer(PipelineComponent):

    def handle(self, message: Dict = None):
        message = self.produce()
        self.call_next(message)

    def produce(self) -> Dict:
        pass

    def has_next(self) -> bool:
        pass
