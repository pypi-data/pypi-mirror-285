from typing import Any
from typing import Any, Collection, Iterable



def items[K, V](data: dict[K, V]) -> list[tuple[K, V]]:
    return list(data.items())


def multi_index(data: Collection, indices: list[int | str]) -> Any:
    """Given a sequence of indices, returns the value from nested index from data."""
    get_code = ''.join([f"['{ind}']" if isinstance(ind, str) else f"[{ind}]" for ind in indices])
    value = eval("data" + get_code)
    return value


def sort_by[T](data: Iterable[T], indices: list[int | str], reverse: bool = False) -> list[T]:
    return type(data)(sorted(data, key=lambda d: multi_index(d, indices), reverse=reverse))




def flatten_nested_dict[K1, K2](nested_dict: dict[K1, dict[K2, Any]]) -> dict[tuple[K1, K2], Any]:
    out = {}
    for k1, d in nested_dict.items():
        for k2, value in d.items():
            out[k1, k2] = value
    return out


def promote_key[T: list[dict] | dict[str, dict]](data: T, key: str, attrs: list[int | str]) -> T:
    if isinstance(data, list):
        new_data = []
        for d in data:
            v = d.copy()
            for attr in attrs:
                v = v[attr]
            d[key] = v
            new_data.append(d)
        return new_data
    elif isinstance(data, dict):
        new_data = {}
        for k1, d in data.items():
            v = d.copy()
            for attr in attrs:
                v = v[attr]
            d[key] = v
            new_data[k1] = d
        return new_data
    else:
        raise NotImplementedError()