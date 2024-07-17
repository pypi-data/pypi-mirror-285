def convert_size_to_bytes(size_str: str) -> int:
    '''convert a string that describe size to number of bytes.'''
    units = {"b": 1, "kb": 1024, "mb": 1024**2, "gb": 1024**3, "tb": 1024**4}
    size_str = size_str.strip().lower()

    num  = "".join(filter(lambda x: x.isdigit(), size_str.lower()))
    unit = "".join(filter(lambda x: x.isalpha(), size_str.lower()))

    if unit not in units:
        raise RuntimeError(f"Invalid unit {unit}. Use 'b', 'kb', 'mb', 'gb', or 'tb'.")

    return int(float(num) * units[unit])
