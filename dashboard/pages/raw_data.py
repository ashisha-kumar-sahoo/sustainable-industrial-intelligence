"""Raw Data Explorer with search, column selection, sorting, and CSV export."""

import streamlit as st

import config
from components.filters import RAW
from components.header import page_header
from components.tables import raw_data_table


def rawdata(dark: bool) -> None:
    """Render the filtered raw data table."""
    del dark  # The global theme stylesheet already styles this page.
    page_header("📁 Raw Data Explorer")
    st.caption(
        "Evidence behind dashboard/AI results. Use the global sidebar filters "
        "for facility, zone, and date range."
    )

    dataset_options = [
        dataset for dataset in config.DS if dataset in config.active_domains()
    ]
    if not dataset_options:
        st.info("No datasets are enabled for this facility profile.")
        return

    dataset_column, search_column, page_size_column = st.columns(3)
    dataset = dataset_column.selectbox(
        "Dataset", dataset_options, key="rx_ds"
    )
    search_text = search_column.text_input("Search")
    page_size = page_size_column.selectbox(
        "Rows per page", [25, 50, 100], index=1
    )

    data = RAW(dataset)
    if search_text and not data.empty:
        matching_rows = data.astype(str).apply(
            lambda row: row.str.contains(
                search_text, case=False, regex=False, na=False
            ).any(),
            axis=1,
        )
        data = data.loc[matching_rows]

    if data.empty:
        st.info("No records match the selected filters.")
        return

    selected_columns = st.multiselect(
        "Columns", list(data.columns), default=list(data.columns)
    )
    if not selected_columns:
        st.info("Select at least one column to display or export data.")
        return

    sort_column, ascending_column = st.columns(2)
    sort_by = sort_column.selectbox("Sort by", selected_columns)
    ascending = ascending_column.toggle("Ascending")
    data = data.sort_values(sort_by, ascending=ascending)

    page_count = max(1, (len(data) + page_size - 1) // page_size)
    page_number = st.number_input(
        f"Page (1–{page_count})",
        min_value=1,
        max_value=page_count,
        value=1,
    )
    st.caption(f"{len(data):,} records · showing {page_size} per page")
    raw_data_table(data, selected_columns, int(page_number), page_size, dataset)
