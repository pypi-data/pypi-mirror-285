def assert_failure(method, *args):
    try:
        method(*args)
        assert False
    except TypeError:
        pass
