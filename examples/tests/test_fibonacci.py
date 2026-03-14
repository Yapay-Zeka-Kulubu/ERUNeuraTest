import pytest
from examples.sample import fibonacci

def test_normal_case_fib():
    assert fibonacci(2) == 1
    assert fibonacci(3) == 2
    assert fibonacci(5) == 5
    assert fibonacci(7) == 13

def test_edge_case_fib():
    assert fibonacci(0) == 0
    assert fibonacci(1) == 1

def test_large_case_fib():
    assert fibonacci(12) == 144
    assert fibonacci(20) == 6765

def test_negative_case_fib():
    with pytest.raises(ValueError):
        fibonacci(-1)

    with pytest.raises(ValueError):
        fibonacci(-5)

def test_type_err_case_fib():
    with pytest.raises(TypeError):
        fibonacci("5")

    with pytest.raises(TypeError):
        fibonacci(None)

    with pytest.raises(TypeError):
        fibonacci(3.5)

    with pytest.raises(TypeError):
        fibonacci([5])

