from collections import deque
from typing import Callable, Dict, List, Tuple, Optional

from Block import Block
from BlockFactory import BlockFactory


class Table(object):

    def __init__(
            self,
            bin_key: Tuple,
            block_factory: BlockFactory,
            on_table_candidate: Callable[[Tuple, Block, Block], None],
            blocks: Optional[List[Block]] = None
    ):
        self.bin_key = bin_key
        self.block_factory = block_factory
        self.on_table_candidate = on_table_candidate
        self.blocks = deque(blocks or (), maxlen=2)  # header, data
        if not blocks:
            self.next_block()

    def add_row(self, interpretations: List[Dict[str, any]]):
        active_block = self.blocks[-1]
        if not active_block.is_compatible(interpretations):
            active_block.close()
            active_block = self.next_block()
        active_block.add(interpretations)

    def next_block(self) -> Block:
        if self.blocks:
            self.create_table_candidate()
        block = self.block_factory.create(self.bin_key[0])
        self.blocks.append(block)
        return block

    def create_table_candidate(self):
        header = self.blocks[0] if len(self.blocks) == 2 else None
        data = self.blocks[-1]
        self.on_table_candidate(self.bin_key, header, data)

    def close(self):
        self.blocks[-1].close()
        self.create_table_candidate()
        self.blocks.clear()
