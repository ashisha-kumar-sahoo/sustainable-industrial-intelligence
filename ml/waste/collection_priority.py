def calculate_collection_priority(data):

    data = data.copy()

    # Default priority
    data["collection_priority"] = "LOW"

    # HIGH priority
    data.loc[
        data["overflow_risk"] == "HIGH",
        "collection_priority"
    ] = "HIGH"

    # MEDIUM priority
    data.loc[
        (
            data["overflow_risk"] == "MEDIUM"
        ) &
        (
            data["collection_priority"] != "HIGH"
        ),
        "collection_priority"
    ] = "MEDIUM"

    return data