"""
Utilities for working with text (string)
"""
import re


def camel_case_to_snake_case(text: str, to_lower: bool = True) -> str:
    """
    Convert a text from CamelCase to snake_case

    :param text: text to transform
    :type text: str
    :param to_lower: If you want the result to be lowercase, defaults to True
    :type to_lower: bool, optional
    :return: transformed text
    :rtype: str
    """
    regex = "(?<!^)(?=[A-Z])"
    result = re.sub(regex, "_", text)
    # Handle to fix the __{} exception
    result = re.sub(r"^__", "_", result)

    if to_lower:
        return result.lower()
    return result


def remove_special_charachters(
    text: str, regex_remove: str = "[^a-zA-Z0-9_]+", replace_char: str = "_"
) -> str:
    """
    Remove Special Charachters from text and replaces with _

    :param text: text to modify
    :type text: str
    :param regex_remove: regex pattern, defaults to '[^a-zA-Z0-9_]+'
    :type regex_remove: str, optional
    :param replace_char: string to replace it with, defaults to '_'
    :type replace_char: str, optional
    :return: transformed text
    :rtype: str
    """

    pattern = re.compile(regex_remove)

    return pattern.sub(replace_char, text)


def cols_text_to_standard(text: str, upper: bool = True, *args, **kwargs) -> str:
    """
    Convert text to the standard naming convention (for dataframes)

    :param text: text to transform
    :type text: str
    :return: transformed text
    :rtype: str
    """
    text = remove_special_charachters(text, *args, **kwargs)
    text = camel_case_to_snake_case(text, *args, **kwargs)
    if upper:
        text = text.upper()
    return text
