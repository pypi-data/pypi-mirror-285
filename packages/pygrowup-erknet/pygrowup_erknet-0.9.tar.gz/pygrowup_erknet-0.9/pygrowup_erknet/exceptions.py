class PyGrowUpError(RuntimeError):
    pass

class DataNotFound(PyGrowUpError):
    pass


class DataError(PyGrowUpError):
    pass


class InvalidAge(PyGrowUpError):
    pass


class InvalidMeasurement(PyGrowUpError):
    pass
