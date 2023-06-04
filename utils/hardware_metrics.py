import os


def get_available_cpu_count():
    """
    Returns the number of available CPUs on the system.
    """
    return os.cpu_count()
