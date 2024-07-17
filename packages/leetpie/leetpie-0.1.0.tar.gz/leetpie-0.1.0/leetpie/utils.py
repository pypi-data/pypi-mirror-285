def print_iterable(iterable, n=1):
    """Print an object supporting iteration.

    iterable: An object supporting iteration
    n: An integer representing the number of elements per row (The default value is 1)
    """
    values = [v for v in iterable]
    if n != 1:
        max_length = 0
        for i, v in enumerate(values):
            values[i] = v if isinstance(v, str) else str(v)
            max_length = len(values[i]) if len(values[i]) > max_length else max_length
        width = max_length + 2
        for i, v in enumerate(values):
            if i % n == n - 1:
                print(v.ljust(width))
            else:
                print(v.ljust(width), end='')
        if len(values) % n:
            print()
    else:
        for v in values:
            print(v)
