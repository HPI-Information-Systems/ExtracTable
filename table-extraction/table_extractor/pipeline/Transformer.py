from typing import Dict

from pipeline.PipelineComponent import PipelineComponent


class Transformer(PipelineComponent):

    def handle(self, message: Dict):
        self.transform(message)

    def transform(self, message: Dict):
        pass
