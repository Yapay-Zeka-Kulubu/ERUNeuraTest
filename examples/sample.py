# Sample Python file for testing
def factorial(n: int) -> int:
    """Calculate factorial of n."""
    if n < 0:
        raise ValueError("n must be non-negative")
    if n == 0 or n == 1:
        return 1
    return n * factorial(n - 1)


def fibonacci(n: int) -> int:
    """Calculate nth Fibonacci number."""
    if not isinstance(n, int):
        raise TypeError("n must be an integer")
    if n < 0:
        raise ValueError("n must be non-negative")
    if n <= 1:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


class Calculator:
    """Simple calculator class."""
    
    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        return a + b
    
    def divide(self, a: float, b: float) -> float:
        """Divide a by b."""
        if b == 0:
            raise ZeroDivisionError("Cannot divide by zero")
        return a / b

