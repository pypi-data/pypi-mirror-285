"""Memory pool."""

import logging

import torch

logger = logging.getLogger(__name__)


class ReqToTokenPool:
    """A memory pool that maps a request to its token locations."""

    def __init__(self, size: int, max_context_len: int):
        self.mem_state = torch.ones((size,), dtype=torch.bool, device="cuda")
        self.req_to_token = torch.empty(
            (size, max_context_len), dtype=torch.int32, device="cuda"
        )
        self.can_use_mem_size = size

    def alloc(self, need_size: int):
        if need_size > self.can_use_mem_size:
            return None

        select_index = torch.nonzero(self.mem_state).squeeze(1)[:need_size].to(torch.int32)
        self.mem_state[select_index] = False
        self.can_use_mem_size -= need_size

        return select_index

    def free(self, free_index: int):
        self.mem_state[free_index] = True
        if isinstance(free_index, (int,)):
            self.can_use_mem_size += 1
        else:
            self.can_use_mem_size += free_index.shape[0]

    def clear(self):
        self.mem_state.fill_(True)
        self.can_use_mem_size = len(self.mem_state)


class TokenToKVPool:
    """A memory pool that maps a token to its kv cache locations"""

    def __init__(self, size, dtype, head_num, head_dim, layer_num):
        self.size = size

        # We also add one slot. This slot is used for writing dummy output from padded tokens.
        self.mem_state = torch.ones((self.size + 1,), dtype=torch.bool, device="cuda")

        # [size, key/value, head_num, head_dim] for each layer
        self.kv_data = [
            torch.empty((size + 1, 2, head_num, head_dim), dtype=dtype, device="cuda")
            for _ in range(layer_num)
        ]

        # Prefetch buffer
        self.prefetch_buffer = torch.empty(0, device="cuda", dtype=torch.int32)
        self.prefetch_chunk_size = 512

        self.can_use_mem_size = self.size
        self.clear()

    def get_key_buffer(self, layer_id):
        return self.kv_data[layer_id][:, 0]

    def get_value_buffer(self, layer_id):
        return self.kv_data[layer_id][:, 1]

    def available_size(self):
        return self.can_use_mem_size + len(self.prefetch_buffer)

    def alloc(self, need_size):
        buffer_len = len(self.prefetch_buffer)
        if need_size <= buffer_len:
            select_index = self.prefetch_buffer[:need_size]
            self.prefetch_buffer = self.prefetch_buffer[need_size:]
            return select_index

        addition_size = need_size - buffer_len
        alloc_size = max(addition_size, self.prefetch_chunk_size)
        select_index = torch.nonzero(self.mem_state).squeeze(1)[:alloc_size].to(torch.int32)

        if select_index.shape[0] < addition_size:
            return None

        self.mem_state[select_index] = False
        self.can_use_mem_size -= len(select_index)

        self.prefetch_buffer = torch.cat((self.prefetch_buffer, select_index))
        ret_index = self.prefetch_buffer[:need_size]
        self.prefetch_buffer = self.prefetch_buffer[need_size:]

        return ret_index

    def free(self, free_index: torch.Tensor):
        self.mem_state[free_index] = True
        self.can_use_mem_size += len(free_index)

    def clear(self):
        self.mem_state.fill_(True)
        self.can_use_mem_size = self.size

        # We also add one slot. This slot is used for writing dummy output from padded tokens.
        self.mem_state[0] = False
