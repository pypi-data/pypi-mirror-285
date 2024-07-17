import pickle


def validate_name(string: str):
    if string is None:
        raise ValueError("string must be informed!")
    if len(string) < 5:
        raise ValueError("string must have at least 5 characters!")
    if len(string) > 30:
        raise ValueError("string cannot be longer than 30 characters!")
    # special characters not allowed
    special_characters = "\"'!@#$%¨&*()+=§`[]{}ªº;.,~^/?\\|áéíóúâêîôûãõäëïöüñç "
    string = string.lower()
    if any(c in special_characters for c in string):
        raise ValueError("string has invalid characters. Only '-' and '_' are allowed!")
    # start and end
    if string.startswith("_"):
        raise ValueError("string can't start with _!")
    if string.startswith("-"):
        raise ValueError("string can't start with -!")
    if string.endswith("_"):
        raise ValueError("string can't end with _!")
    if string.endswith("-"):
        raise ValueError("string can't end with -!")

    return string


def load_pickle_model(pickle_path):
    with open(pickle_path, "rb") as f:
        model = pickle.load(f)
    return model
