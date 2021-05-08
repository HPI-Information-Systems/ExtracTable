from typing import Dict


class PipelineComponent(object):

    def __init__(self):
        self.__next__ = None

    def handle(self, message: Dict):
        pass

    def call_next(self, message: Dict):
        if self.__next__:
            self.__next__.handle(message)

    def reached_end(self):
        pass

    def set_next(self, pipeline_component) -> any:
        self.__next__ = pipeline_component
        return pipeline_component
