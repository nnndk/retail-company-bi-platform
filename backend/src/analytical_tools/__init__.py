from transliterate import translit


def custom_translit(text: str) -> str:
    """
    Transliterate Russian text into Latin characters.

    :param text: Russian text to transliterate.
    :return: Transliterated text.
    """
    translit_text = translit(text, 'ru', reversed=True)

    return translit_text.replace("'", '').replace(' ', '_')