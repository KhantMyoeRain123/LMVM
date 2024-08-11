def add(a:float,b:float)->list[dict]:
    """
    Adds two numbers a and b.
    add(a,b)->a+b
    """
    return [{
        "sum":a+b
    }]
def subtract(a:float,b:float)->list[dict]:
    """
    Subtracts two numbers, b from a.
    subtract(a,b)->a-b
    """
    return [{
        "difference":a-b
    }]
def multiply(a:float,b:float)->list[dict]:
    """
    Multiplies two numbers a and b.
    multiply(a,b)->a*b
    """
    return [{
        "product":a*b
    }]
def divide(a:float,b:float)->list[dict]:
    """
    Multiplies two numbers a and b.
    divide(a,b)->a/b
    """
    return [{
        "product":a/b
    }]
