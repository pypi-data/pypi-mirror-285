def factorial(n: int) -> int:
    """
    Calculates the factorial of a number

    #### Arguments:
        n (int): A natural number

    #### Returns:
        int: The factorial of n
    """
    out: int = 1
    for i in range(1, n + 1):
        out *= i
    return out

def isPrime(n: int) -> bool:
    """
    Checks if a number is a prime

    #### Arguments:
        n (int): A natural number

    #### Returns:
        bool: Whether n is a prime number or not
    """
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True