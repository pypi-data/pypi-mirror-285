units = {
    "B": 1,
    "KiB": 1024,
    "MiB": 1024 ** 2,
    "GiB": 1024 ** 3,
    "TiB": 1024 ** 4,
    "PiB": 1024 ** 5,
    "EiB": 1024 ** 6,
}


def human_size_number(byte_size: int, target_unit: str):
    for item in units.items():
        if item[0] == target_unit:
            return float(byte_size / item[1])

    raise ValueError(f"unsupported unit {target_unit}")


def human_size(byte_size: int, target_unit: str = "MiB") -> str:
    if byte_size < 1024:
        return "{} B".format(byte_size)

    for item in sorted(units.items(), reverse=False, key=lambda i: i[1]):
        if byte_size / item[1] < 1024 or (target_unit is not None and item[0] == target_unit):
            v = byte_size / item[1]
            u = item[0]
            if v == int(v):
                return f'{int(v)} {u}'
            else:
                return f'{v:.2f} {u}'


def from_human_size(size: str) -> int:
    fields = size.split()
    if len(fields) != 2:
        raise ValueError(f'invalid human size format, `{size}`')

    v = float(fields[0])
    u = fields[1]

    multiple = units.get(u, None)
    if multiple is None:
        raise ValueError(f'invalid human size format, unknown unit {u}')

    return int(v * multiple)
