import random, secrets

def gen_pwd(length:int, possible_digits:str) -> str:
    """Generates a pwd with the length and the digits provided."""
    
    if length > 0:
        return "".join(secrets.choice(possible_digits) for _ in range(length))
    else:
        raise ValueError("The length of the digits in your password must be grater than 0!")