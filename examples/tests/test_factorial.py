# Auto-generated test for factorial
import sys
sys.path.insert(0, 'examples')
from sample import *

# tests/test_sample.py
import pytest
from sample import factorial

def test_factorial_normal_cases():
    assert factorial(0) == 1
    assert factorial(1) == 1
    assert factorial(2) == 2
    assert factorial(3) == 6
    assert factorial(4) == 24
    assert factorial(5) == 120

def test_factorial_edge_cases():
    assert factorial(0) == 1  # base case
    assert factorial(1) == 1  # base case

def test_factorial_error_conditions():
    with pytest.raises(ValueError):
        factorial(-1)
    with pytest.raises(ValueError):
        factorial(-5)
    with pytest.raises(ValueError):
        factorial(-10)

def test_factorial_large_input():
    assert factorial(10) == 3628800

def test_factorial_invalid_input_type():
    with pytest.raises(TypeError):
        factorial("10")
    with pytest.raises(TypeError):
        factorial(10.5)
    with pytest.raises(TypeError):
        factorial([10])

def test_factorial_recursive_depth():
    assert factorial(20) == 2432902008176640000

def test_factorial_max_value():
    with pytest.raises(RecursionError):
        factorial(1000)