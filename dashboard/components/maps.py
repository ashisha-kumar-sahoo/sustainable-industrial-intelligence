"""3D estate map built with PyDeck."""

import pydeck as pdk
import streamlit as st

SEVERITY_COLORS = {
    "HIGH": [239, 68, 68, 230],
    "MEDIUM": [250, 204, 21, 225],
    "NORMAL": [52, 211, 153, 215],
}


def estate_map(facilities, dark: bool):
    """Build the extruded facility map and highlight high-severity locations."""
    if facilities.empty:
        return pdk.Deck(layers=[], initial_view_state=pdk.ViewState())

    half_size = 0.0005
    map_data = facilities.copy()
    map_data["color"] = map_data["severity"].map(SEVERITY_COLORS)
    map_data["polygon"] = [
        [
            [longitude - half_size, latitude - half_size],
            [longitude + half_size, latitude - half_size],
            [longitude + half_size, latitude + half_size],
            [longitude - half_size, latitude + half_size],
        ]
        for longitude, latitude in zip(map_data["lon"], map_data["lat"])
    ]

    high_severity = map_data.loc[map_data["severity"] == "HIGH"].copy()
    high_severity["highlight_longitude"] = high_severity["lon"] + 0.0009
    high_severity["tower_height"] = 150

    text_color = [255, 255, 255, 255] if dark else [15, 23, 42, 255]
    layers = [
        pdk.Layer(
            "PolygonLayer",
            map_data,
            get_polygon="polygon",
            extruded=True,
            get_elevation="height",
            get_fill_color="color",
            get_line_color=[255, 255, 255, 120],
            pickable=True,
            auto_highlight=True,
        ),
        pdk.Layer(
            "TextLayer",
            map_data,
            get_position="[lon, lat, height + 25]",
            get_text="name",
            get_size=15,
            get_color=text_color,
        ),
    ]

    if not high_severity.empty:
        layers.append(
            pdk.Layer(
                "ColumnLayer",
                high_severity,
                get_position="[highlight_longitude, lat]",
                get_elevation="tower_height",
                radius=28,
                get_fill_color="color",
                extruded=True,
            )
        )

    view_state = pdk.ViewState(
        latitude=float(map_data["lat"].mean()),
        longitude=float(map_data["lon"].mean()),
        zoom=15,
        pitch=58,
        bearing=25,
    )
    map_style = pdk.map_styles.CARTO_DARK if dark else pdk.map_styles.CARTO_LIGHT

    return pdk.Deck(
        layers=layers,
        initial_view_state=view_state,
        map_provider="carto",
        map_style=map_style,
        tooltip={"text": "{name}\n{tip}"},
    )


def render_estate_map(facilities, dark: bool) -> None:
    """Render the map with a note clarifying the simulated facility layout."""
    st.pydeck_chart(
        estate_map(facilities, dark),
        use_container_width=True,
        height=520,
    )
    st.caption(
        "3D facility map. Colours show model/sample severity for the selected "
        "domain. The layout is simulated, not a live physical sensor map."
    )
