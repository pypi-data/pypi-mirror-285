from concurrent.futures import ThreadPoolExecutor
from os import cpu_count

def cpuexecutor():
    return ThreadPoolExecutor(cpu_count())
