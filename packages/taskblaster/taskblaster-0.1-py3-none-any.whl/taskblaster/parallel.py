class ParallelizationError(Exception):
    pass


def choose_subworkers(size, subworker_size, subworker_count):
    if subworker_size is None:
        if subworker_count is None:
            subworker_count = 1

        if size % subworker_count != 0:
            raise ParallelizationError(
                f'Number of cores {size} not divisible by subworker count '
                f'{subworker_count}'
            )

        subworker_size = size // subworker_count

    if size % subworker_size != 0:
        raise ParallelizationError(
            f'Number of cores {size} not divisible by subworker size '
            f'{subworker_size}'
        )

    if subworker_count is None:
        subworker_count = size // subworker_size

    if subworker_size * subworker_count != size:
        raise ParallelizationError(
            f'Subworker size and count ({subworker_size}, {subworker_count}) '
            f'must multiply to communicator size {size}'
        )

    return subworker_size, subworker_count


class SerialCommunicator:
    rank = 0
    size = 1

    def broadcast_object(self, obj):
        return obj

    def split(self, size):
        assert size == 1
        return self

    def usercomm(self):
        return self
