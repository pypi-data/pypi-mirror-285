"""Utils module."""

from typing import Generator, List, Any, Tuple


def generate_batches(iterable: List[Any], batch_size_limit: int) -> Generator[Any, Any, Any]:
    """Generate lists of length size batch_size_limit containing objects yielded by the iterable."""
    batch: List[Any] = []

    for item in iterable:
        if len(batch) == batch_size_limit:
            yield batch
            batch = []
        batch.append(item)

    if len(batch):
        yield batch


def get_time_periods(hods: List[int]) -> List[Tuple[int, int]]:
    """Group list of periods per continious groups.

    Args:
    ----
        hods (List[int]): list of hours, e.g. [0,1,5,6,2].

    Returns:
    -------
        List[Tuple[int, int]]: continious groups, e.g. [(0,2),(5,6)].

    """
    hods = sorted(set([v for v in hods if v is not None]))
    time_periods = []
    if hods:
        period_start = hods[0]
        for i in range(0, len(hods) - 1):
            if hods[i] + 1 < hods[i + 1]:
                time_periods.append((period_start, hods[i] + 1))
                period_start = hods[i + 1]
        time_periods.append((period_start, hods[-1] + 1))
    return time_periods


def closest_index(list_a: List[Any], k: Any) -> int:
    """Find closest index for value from list.

    Args:
    ----
        list_a (List[Any]): list of values.
        k (Any): value.

    Returns:
    -------
        int: closest index for value from list.

    """
    return min(range(len(list_a)), key=lambda i: abs(list_a[i] - k))


def flatten_concatenation(matrix: List[List[Any]]) -> List[Any]:
    """Flatten list.

    Args:
    ----
        matrix (List[List[Any]]): list of lists

    Returns:
    -------
        List[Any]: flattened list

    """
    flat_list = []
    for row in matrix:
        flat_list += row
    return flat_list
