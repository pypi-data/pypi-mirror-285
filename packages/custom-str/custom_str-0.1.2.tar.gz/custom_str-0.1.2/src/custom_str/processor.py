import re
from typing import Set, Dict
from collections import Counter

def get_unique_words(input_string: str) -> Set[str]:
    """
    Process an input string and return a set of unique words.
    
    Args:
        input_string (str): The input string to process.
    
    Returns:
        Set[str]: A set of unique words from the input string.
    """
    words = re.findall(r'\b\w+\b', input_string.lower())

    return set(words)

def get_word_frequency(input_string: str) -> Dict[str, int]:
    """
    Process an input string and return a dictionary of word frequencies.
    
    Args:
        input_string (str): The input string to process.
    
    Returns:
        Dict[str, int]: A dictionary with words as keys and their frequencies as values.
    """
    words = re.findall(r'\b\w+\b', input_string.lower())
    return dict(Counter(words))
