
def add_one(number: int) -> int:
    """
    Retorna seu envio acrescentando +1

    Args:
        number: Inserir algum numero inteiro.

    Returns:
        Um número inteiro somado

    Raises:
        TypeError: Caso não seja um int, por exemplo uma string.

    Examples:
        >>> add_one(0)
        1
    """
    if not isinstance(number, int):
        raise TypeError("Input must be an integer")

    return number + 1
