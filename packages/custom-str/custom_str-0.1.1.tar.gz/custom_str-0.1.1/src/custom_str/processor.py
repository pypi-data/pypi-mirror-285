import re
from typing import Set

def get_unique_words(input_string: str) -> Set[str]:
    """
    Process an input string and return a set of unique words.
    
    Args:
        input_string (str): The input string to process.
    
    Returns:
        Set[str]: A set of unique words from the input string.
    """
    # Convert to lowercase and split into words
    words = re.findall(r'\b\w+\b', input_string.lower())
    
    # Return a set of unique words
    return set(words)