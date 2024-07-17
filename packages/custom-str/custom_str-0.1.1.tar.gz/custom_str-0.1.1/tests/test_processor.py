from custom_str.processor import get_unique_words

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