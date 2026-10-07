import re


def parse_energy_reduction_question(question):
    """
    Extract facility name and reduction percentage
    from an energy-reduction scenario question.
    """

    pattern = re.search(
        r"What if (.+?) reduces energy consumption by (\d+(?:\.\d+)?)%",
        question,
        re.IGNORECASE
    )

    if not pattern:
        return None

    facility_name = pattern.group(1).strip()
    reduction_pct = float(pattern.group(2))

    return {
        "facility_name": facility_name,
        "reduction_pct": reduction_pct
    }


if __name__ == "__main__":

    question = (
        "What if BoxCraft Packaging Unit "
        "reduces energy consumption by 15%?"
    )

    result = parse_energy_reduction_question(question)

    print("=== PARSED SCENARIO ===")
    print(result)