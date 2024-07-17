_seed = 2333
def my_rand():
    global _seed
    _seed = _seed * 233 + 23333
    _seed = _seed % 233333333
    return _seed

def my_randint(low: int, high: int):
    if high - low <= 0:
        return low
    r = my_rand()
    return (r % (high - low)) + low