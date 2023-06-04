from pylogger.logger import Logger


@Logger.log_execution_time
def fib(n: int):
    if n <= 1:
        return n

    fib_nums = {0: 0, 1: 1}

    for i in range(2, n + 1):
        fib_nums[i] = fib_nums[i - 1] + fib_nums[i - 2]

    return fib_nums[n]


val = fib(4)

# Logger.info(val)

print(val)
