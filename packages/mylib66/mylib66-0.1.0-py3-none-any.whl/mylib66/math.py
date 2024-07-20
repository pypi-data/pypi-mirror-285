# encoding: utf-8
import math


def _gcd_Euclidean_2(a: int, b: int) -> int:
    while a != 0:
        a, b = b % a, a

    return b


def _gcd_decrease_technique_2(a: int, b: int) -> int:
    reduction = 1
    while True:
        if a % 2 == 0 and b % 2 == 0:
            a //= 2
            b //= 2
            reduction *= 2
        else:
            break

    while True:
        big = max(a, b)
        small = min(a, b)
        if small * 2 == big:
            return small * reduction
        else:
            a, b = small, big - small


def _gcd_Stein_2(a: int, b: int) -> int:
    record = 1
    while True:
        if a < b:
            a, b = b, a
        if b == 0:
            return a * record

        if a % 2 == 0 and b % 2 == 0:
            record *= 2
            a, b = a / 2, b / 2
        elif a % 2 == 0:
            a /= 2
        elif b % 2 == 0:
            b /= 2

        else:
            a, b = (a + b) / 2, (a - b) / 2


def _gcd_prime_factorize_2(a: int, b: int) -> int:
    result = 1
    a = prime_factor(a)
    b = prime_factor(b)
    for num in a:
        if num in b:
            b.remove(num)
            result *= num
    return result


def _gcd_factorize_2(a: int, b: int) -> int:
    a = factor(a)
    b = factor(b)
    for i in a[::-1]:
        if i in b:
            return i


def gcd_2(a: int, b: int, algorithm: str = 'Euclidean') -> int:
    """
    Calculates the Greatest Common Denominator (GCD) of two numbers a and b.

    Notes:
        So far, this function only supports 'Euclidean', 'decrease technique' (更相减损法), 'Stein',
        'prime factorize', and 'factorize' as its algorithms.

    Args:
        a (int): first number
        b (int): second number
        algorithm (str): the algorithm to use for finding GCD

    Returns:
        int: GCD of two numbers
    """

    if a < 0:
        raise ValueError('{0} is negative'.format(a))
    if b < 0:
        raise ValueError('{0} is negative'.format(b))

    if algorithm not in ['Euclidean', 'decrease technique', 'Stein',
                         'prime factorize', 'factorize']:
        raise ValueError('{0} is not a valid value for algorithm'.format(repr(algorithm)))

    if algorithm == 'Euclidean':
        return _gcd_Euclidean_2(a, b)

    elif algorithm == 'decrease technique':
        return _gcd_decrease_technique_2(a, b)

    elif algorithm == 'Stein':
        return _gcd_Stein_2()

    elif algorithm == 'prime factorize':
        return _gcd_prime_factorize_2()

    elif algorithm == 'factorize':
        return _gcd_factorize_2()


def gcd(*nums, algorithm='Euclidean'):
    """
    Calculates the Greatest Common Denominator (GCD) of multiple numbers.

    Notes:
        So far, this function only supports 'Euclidean', 'decrease technique' (更相减损法), 'Stein',
        'prime factorize', and 'factorize' as its algorithms.

    Args:
        *nums (int): numbers to find GCD of
        algorithm (str): the algorithm to use for finding GCD

    Returns:
        int: GCD of the numbers
    """

    for num in nums:
        if num < 0:
            raise ValueError('{0} is negative'.format(num))

    if algorithm not in ['Euclidean', 'decrease technique', 'Stein',
                         'prime factorize', 'factorize']:
        raise ValueError('{0} is not a valid value for algorithm'.format(repr(algorithm)))

    nums = list(nums)

    # replace every two numbers by their GCD, repeat until only one number left
    while len(nums) != 1:
        for i in range(len(nums) // 2):
            nums[i] = gcd_2(nums[i], nums[i + 1], algorithm=algorithm)
            del nums[i + 1]

    return nums[0]


def lcm(*nums: int) -> int:
    """
    Calculates the Least Common Multiple (LCM) of the given numbers.

    Args:
        *nums (int): numbers to find LCM of

    Returns:
        int: LCM of the numbers
    """

    for num in nums:
        if num < 0:
            raise ValueError('{0} is negative'.format(num))

    nums = list(nums)
    # replace every two numbers by their LCM, repeat until only one number left
    while len(nums) != 1:
        for i in range(len(nums) // 2):
            nums[i] = nums[i] * nums[i + 1] / gcd_2(nums[i], nums[i + 1])
            del nums[i + 1]

    return nums[0]


def ratio(*nums: int, digits: int = 1) -> list[int]:
    """
    Round the numbers into whole number ratios.

    Args:
        *nums (int): numbers to turn to ratios
        digits (int): digits to retain, determined by smallest number

    Returns:
        list[int]: the ratios of the numbers
    """

    for num in nums:
        if num < 0:
            raise ValueError('{0} is negative'.format(num))

    nums = list(nums)
    least = min(nums)
    place = 0

    # find number of places to round off
    if least < 1:
        while least * 10 ** place < 1:
            place += 1
    else:
        while least * 10 ** place < 1:
            place -= 1

    for i in range(len(nums)):
        nums[i] = round(nums[i] * 10 ** (place + digits - 1))

    # cancel out common factors
    nums_gcd = gcd(*nums)
    for i in range(len(nums)):
        nums[i] = int(nums[i] / nums_gcd)

    return nums


def prime_factor(num: int) -> list:
    """
    Calculates the prime factorization of the given number.

    Args:
        num (int): the number to prime factorize

    Returns:
        list: the prime factors
    """

    # find smaller factor, which must be prime because going from smaller to larger
    # add factors of larger factor, until larger factor is also prime
    for i in range(2, int(math.sqrt(num)) + 1):  # largest number is root of num
        if num % i == 0:
            return [i] + prime_factor(int(num / i))
    return [num]  # must be prime if no factor can be found within the range


def factor(num: int) -> list:
    """
    Finds all factors of the given number.

    Args:
        num (int): the number to factorize

    Returns:
        list: the factors
    """

    # simplest algorithm, go through every smaller number, and test if it's divisible
    factors = []
    for i in range(1, num // 2 + 1):
        if num % i == 0:
            factors.append(i)
    return factors


def polynomial_value(x: int | float,
                     coefficients: list[int | float] | tuple[int | float]) -> int | float:
    """
    Calculate the polynomial with given x and coefficients.

    Notes:
        The remainder of synthetic division is also the value of the polynomial, see the factor
        theorem.
        Remember to include zero coefficients and constant terms.

    Args:
        x (int | float): the x to use to calculate
        coefficients (list[int | float] | tuple[int | float]): coefficients of the polynomial

    Returns:
        int | float: value of the polynomial

    Examples:
        >>> polynomial_value(3, [2, 0, 3])  # y=2x^2+3
        >>> 21
    """

    return synthetic_division(x, coefficients)[-1]


def synthetic_division(a: int | float,
                       coefficients: list[int | float] | tuple[int | float]) -> list[int | float]:
    """
    Use synthetic division to find the quotient of the polynomial with the given coefficients,
    divided by x-a.

    Notes:
        Remember to include zero coefficients and constant terms.

    Args:
        a (int | float): the a in x-a
        coefficients (list[int | float] | tuple[int | float]): coefficients of the base polynomial

    Returns:
        list[int | float]: quotient of the division

    Examples:
        >>> synthetic_division(2, [1, 1, -6])
        >>> [1, 3, 0]
    """

    value = [0]  # must include 0, meaning no last value for first term
    for i in range(len(coefficients)):
        value.append(coefficients[i] + value[-1] * a)
    return value[1:]  # exclude first term 0


def find_a_zeros(coefficients: list[int | float] | tuple[int | float],
                 digits: int = 3, accuracy: int = 8) -> int | float:
    """
    Find a zero of the polynomial with given coefficients.

    Notes:
        Uses the Locational Principle.

    Args:
        coefficients (list[int | float] | tuple[int | float]): coefficients of the polynomial
        digits (int): number of digits after the decimal point to retain in the results
        accuracy (int): how accurate the results need to be, the number means how many digits from 0

    Returns:
        int | float: the zero
    """

    a = 0

    # first find which two integers it is between
    while True:
        # positive side
        a = -a + 1
        b = a - 1
        if polynomial_value(a, coefficients) * polynomial_value(b, coefficients) < 0:
            break

        # negative side
        a = -a
        b = a + 1
        if polynomial_value(a, coefficients) * polynomial_value(b, coefficients) < 0:
            break

    # use binary search to narrow down and get the zero
    while True:
        m = (a + b) / 2

        if round(polynomial_value(m, coefficients), accuracy) == 0:
            return round(m, digits)

        if polynomial_value(a, coefficients) * polynomial_value(m, coefficients) < 0:
            b = m  # zero between a, m
        else:
            a = m  # zero between b, m
