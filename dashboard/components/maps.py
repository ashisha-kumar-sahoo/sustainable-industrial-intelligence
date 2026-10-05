"""3D estate map (pydeck). Moved unchanged from charts.estate_map; render_estate_map is the pydeck call + caption from pages.overview()."""
import pydeck as pdk
import streamlit as st
COL = {"HIGH": [239, 68, 68, 230], "MEDIUM": [250, 204, 21, 225], "NORMAL": [52, 211, 153, 215]}


def estate_map(fac, dark):
    s = .0005; fac = fac.assign(color=fac["severity"].map(COL), polygon=[[[x - s, y - s], [x + s, y - s], [x + s, y + s], [x - s, y + s]] for x, y in zip(fac["lon"], fac["lat"])])
    hot = fac[fac["severity"] == "HIGH"].assign(lon2=lambda d: d["lon"] + .0009, tower=150)
    L = [pdk.Layer("PolygonLayer", fac, get_polygon="polygon", extruded=True, get_elevation="height", get_fill_color="color", get_line_color=[255, 255, 255, 120], pickable=True, auto_highlight=True),
         pdk.Layer("TextLayer", fac, get_position="[lon, lat, height + 25]", get_text="name", get_size=15, get_color=[255, 255, 255, 255] if dark else [15, 23, 42, 255])]
    if len(hot): L.append(pdk.Layer("ColumnLayer", hot, get_position="[lon2, lat]", get_elevation="tower", radius=28, get_fill_color="color", extruded=True))
    return pdk.Deck(layers=L, initial_view_state=pdk.ViewState(latitude=fac["lat"].mean(), longitude=fac["lon"].mean(), zoom=15, pitch=58, bearing=25), map_provider="carto",
                    map_style=pdk.map_styles.CARTO_DARK if dark else pdk.map_styles.CARTO_LIGHT, tooltip={"text": "{name}\n{tip}"})


def render_estate_map(fac, dark):
    st.pydeck_chart(estate_map(fac, dark), use_container_width=True, height=520); st.caption("3D map of facilities. Colours show model/sample severity for the selected domain. Simulated layout, not a live physical sensor map.")
