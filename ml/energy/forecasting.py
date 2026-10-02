import pandas as pd


def forecast_energy(
    data,
    window=3
):
    """
    Short-term energy consumption forecasting
    using the rolling average of previous values.
    """

    data = data.copy()

    # Forecast = average of previous energy values
    data["forecast_energy_kwh"] = (
        data.groupby(
            ["facility_id", "zone_id"]
        )["energy_kwh"]
        .transform(
            lambda x: x.shift(1)
            .rolling(
                window=window,
                min_periods=1
            )
            .mean()
        )
    )

    # First value has no previous value
    data["forecast_energy_kwh"] = (
        data["forecast_energy_kwh"]
        .fillna(data["energy_kwh"])
    )

    return data