from custom_str.processor import get_unique_words, get_word_frequency

def test_get_unique_words():
    input_string = "The quick brown fox jumps over the lazy dog"
    expected = {"the", "quick", "brown", "fox", "jumps", "over", "lazy", "dog"}
    assert get_unique_words(input_string) == expected

def test_get_unique_words_case_insensitive():
    input_string = "The THE the tHe"
    expected = {"the"}
    assert get_unique_words(input_string) == expected

def test_get_unique_words_empty_string():
    input_string = ""
    expected = set()
    assert get_unique_words(input_string) == expected

def test_get_word_frequency():
    input_string = "The quick brown fox jumps over the lazy dog"
    expected = {
        "the": 2,
        "quick": 1,
        "brown": 1,
        "fox": 1,
        "jumps": 1,
        "over": 1,
        "lazy": 1,
        "dog": 1
    }
    assert get_word_frequency(input_string) == expected
