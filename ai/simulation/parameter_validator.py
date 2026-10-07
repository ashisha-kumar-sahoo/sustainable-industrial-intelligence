def validate_reduction_percentage(
    reduction_pct
):
    """
    Validate a percentage reduction value
    for a simulation scenario.
    """

    try:
        reduction_pct = float(reduction_pct)
    except (TypeError, ValueError):
        return False

    if reduction_pct <= 0:
        return False

    if reduction_pct >= 100:
        return False

    return True

if __name__ == "__main__":

    tests = [
        15,
        10,
        0,
        -5,
        100,
        150
    ]

    for value in tests:

        print(
            value,
            "->",
            validate_reduction_percentage(value)
        )