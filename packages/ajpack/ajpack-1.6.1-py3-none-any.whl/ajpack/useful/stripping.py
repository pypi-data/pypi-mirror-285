def rma_str(string: str, word: str, part: int = 1) -> str:
    """
    Removes the part before or after the specific word.
    
    part:
        0 = after, 1 = before
    """

    index: int = string.find(word)

    # If the word is not found, return the original string
    if index == -1: return string

    # Return the string including the word
    if part == 0:   return string[:index + len(word)]
    elif part == 1: return string[index + len(word):]
    else: raise ValueError("The part provided is not valid!")