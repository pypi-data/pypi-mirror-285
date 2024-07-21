NBSP = "\N{NO-BREAK SPACE}"


def remove_unwanted_whitespaces(contaminated_data: str | None) -> str | None:
    """
    Remove trailing spaces and replace non-breaking spaces
    :param contaminated_data: The string to clean
    :return: The sanitized string
    """
    if contaminated_data is None:
        return None

    return contaminated_data.replace(NBSP, " ").strip(f"\t {NBSP}")
