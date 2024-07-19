import time
from typing import Callable
import asyncio
import inspect
from functools import update_wrapper


def log_elapsed_time(log_func: Callable):
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = func(*args, **kwargs)
            elapsed_time = time.perf_counter() - start_time
            log_func(f"{func.__name__} : {elapsed_time*1e3:.1f} ms")
            return result

        update_wrapper(wrapper, func)
        return wrapper

    return decorator


def log_elapsed_time_async(log_func: Callable):
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            result = await func(*args, **kwargs)
            elapsed_time = time.perf_counter() - start_time
            log_func(f"{func.__name__} : {elapsed_time*1e3:.1f} ms")
            return result

        update_wrapper(wrapper, func)
        return wrapper

    return decorator


@log_elapsed_time(print)
def test_check_time(n):
    for _ in range(n):
        time.sleep(0.01)


@log_elapsed_time_async(print)
async def test_check_time_async(n):
    for _ in range(n):
        await asyncio.sleep(0.01)


def get_args_dict(func: Callable, *args, **kwargs):
    sig = inspect.signature(func)
    try:  # sypark 여기 try문을 다른 걸로 대체할 수 없을까?
        bound = sig.bind(*args, **kwargs)
    except:
        bound = sig.bind(None, *args, **kwargs)
    # if "self" in sig.parameters:
    #     bound = sig.bind(None, *args, **kwargs)
    # else:
    #     bound = sig.bind(*args, **kwargs)
    bound.apply_defaults()
    result = dict(bound.arguments)
    if "self" in result and result["self"] is None:
        del result["self"]
    return result


def get_dict_str(value: dict):
    args_strs = []
    for key, value in value.items():
        if isinstance(value, list):
            value_str = [str(v) for v in value]
            args_strs.append(f"{key}=[{', '.join(value_str)}]")
        else:
            args_strs.append(f"{key}={value}")
    result = f"{' '.join(args_strs)}"
    return result


def get_func_args_str(func: Callable, args_dict: dict):
    # args_strs = [f"{k}={v}" for k, v in args_dict.items() if k != "self"]
    args_strs = []
    for key, value in args_dict.items():
        if key == "self":
            continue
        if isinstance(value, list):
            value_str = [str(v) for v in value]
            args_strs.append(f"{key}=[{', '.join(value_str)}]")
        elif inspect.iscoroutine(value):
            args_strs.append(f"{key}={value.__qualname__}")
        elif isinstance(value, asyncio.Task):
            args_strs.append(f"{key}={value.get_coro().__qualname__}")
        else:
            args_strs.append(f"{key}={value}")
    result = f"{func.__name__}({' '.join(args_strs)})"
    return result


def log_func_args(
    log_before_func: Callable = None,
    log_after_func: Callable = None,
):
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            args_dict = get_args_dict(func, *args, **kwargs)
            func_args_strs = get_func_args_str(func, args_dict)
            if log_before_func:
                log_before_func(f"{func_args_strs}")
            result = func(*args, **kwargs)
            if log_after_func:
                log_after_func(f"{func_args_strs} -> {result}")
            return result

        update_wrapper(wrapper, func)
        return wrapper

    return decorator


def log_func_args_async(
    log_before_func: Callable = None,
    log_after_func: Callable = None,
):
    def decorator(func: Callable):
        async def wrapper(*args, **kwargs):
            args_dict = get_args_dict(func, *args, **kwargs)
            func_args_strs = get_func_args_str(func, args_dict)
            if log_before_func:
                log_before_func(f"{func_args_strs}")
            result = await func(*args, **kwargs)
            if log_after_func:
                log_after_func(f"{func_args_strs} -> {result}")
            return result

        update_wrapper(wrapper, func)
        return wrapper

    return decorator


# @log_elapsed_time_async(print)
@log_func_args_async(log_before_func=print, log_after_func=print)
async def test_log_func_args_async(a: int, b: float, c: str):
    await asyncio.sleep(0.01)


def skip_func_async(skip_func: Callable[[], bool], return_value=None):
    def decorator(func):
        async def wrapper(*args, **kwargs):
            if skip_func():
                return return_value
            return await func(*args, **kwargs)

        update_wrapper(wrapper, func)
        return wrapper

    return decorator


@skip_func_async(skip_func=lambda: True, return_value="return_sample")
async def test_skip_func_async_do_skip():
    print(f"{test_skip_func_async_do_skip.__name__}")


@skip_func_async(skip_func=lambda: False, return_value="return_sample")
async def test_skip_func_async_donot_skip():
    print(f"{test_skip_func_async_donot_skip.__name__}")


async def main():
    # test_check_time(1)
    # test_check_time(2)
    # test_check_time(3)

    # await test_check_time_async(1)
    # await test_check_time_async(2)
    # await test_check_time_async(3)

    # await test_log_func_args_async(a=1, b=2.3, c="abc")
    # await test_log_func_args_async(a=0, b=0, c="")
    # await test_log_func_args_async(1, 2.3, "abc")

    print(await test_skip_func_async_do_skip())
    print(await test_skip_func_async_donot_skip())


if __name__ == "__main__":
    asyncio.run(main())
