from pathlib import Path
from pyoload import Cast
from pyoload import Union
from pyoload import type_match
from time import perf_counter_ns as nanos


N = 10000
NS = 10
src = Path(__file__).resolve().parent


def test_speed():
    f = open(src / "logs.yaml", "w")
    speedtype_match(f)
    speedCast(f)
    f.close()


def speedtype_match(f):
    begin = nanos()
    for _ in range(N):
        type_match(3, int)
    end = nanos()
    begin2 = nanos()
    for _ in range(N):
        isinstance(3, int)
    end2 = nanos()
    dt = (end - begin) - (end2 - begin2)
    dt = dt / 1000 / N
    print(f"type_match vs isinstance on int:True  {dt}ms", file=f)

    begin = nanos()
    for _ in range(N):
        type_match(3, str)
    end = nanos()
    begin2 = nanos()
    for _ in range(N):
        isinstance(3, int)
    end2 = nanos()
    dt = (end - begin) - (end2 - begin2)
    dt = dt / 1000 / N
    print(f"type_match vs isinstance on int:False  {dt}ms", file=f)

    obj = {str(x): x for x in range(50)}
    t = dict[str, int]
    begin = nanos()
    for _ in range(N):
        type_match(obj, t)
    end = nanos()
    dt = end - begin
    dt = dt / 1000 / N
    print(f"type_match on dict[str, int]*50:True  {dt}ms", file=f)

    obj = {complex(x): float(x) for x in range(50)}
    t = dict[str, int]
    begin = nanos()
    for _ in range(N):
        type_match(obj, t)
    end = nanos()
    dt = end - begin
    dt = dt / 1000 / N
    print(f"type_match on dict[str, int]*50:False  {dt}ms", file=f)


def speedCast(f):
    ct = Cast(int)

    begin = nanos()
    for x in range(N):
        ct("3")
    end = nanos()
    dt = (end - begin) / N / 1000
    print(f"Cast str->int: {dt}ms", file=f)

    ct = Cast(Union[int, str])
    begin = nanos()
    for x in range(N // NS):
        ct(3j)
    end = nanos()
    dt = (end - begin) / N / NS / 1000
    print(f"Cast complex->int | str: {dt}ms", file=f)

    v = {x: [str(x)] * NS for x in range(NS)}
    ct = Cast(dict[str, tuple[float]])
    begin = nanos()
    for x in range(N // NS):
        ct(v)
    end = nanos()
    dt = (end - begin) / N / NS / 1000
    print(
        f"Cast dict[int,list[str]*{NS}]*{NS}->dict[str,tuple[float]]: {dt}ms",
        file=f,
    )
