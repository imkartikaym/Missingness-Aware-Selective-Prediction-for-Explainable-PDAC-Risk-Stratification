import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="PDAC-GUARD | Record Screen",
    page_icon="🧬",
    layout="wide",
)

st.title("Record Screen")
st.caption(
    "Upload, inspect, edit, and export research dataset records."
)

st.info(
    "Research use only. This page does not provide a clinical diagnosis."
)

uploaded_file = st.file_uploader(
    "Upload a dataset",
    type=["csv", "xlsx"],
    help="Supported formats: CSV and Excel (.xlsx).",
)

if uploaded_file is not None:
    try:
        if uploaded_file.name.lower().endswith(".csv"):
            data = pd.read_csv(uploaded_file)
        else:
            data = pd.read_excel(uploaded_file)

        st.session_state["pdac_guard_records"] = data
        st.session_state["pdac_guard_file"] = uploaded_file.name

    except ImportError:
        st.error(
            "Excel support requires openpyxl. Add openpyxl "
            "to requirements.txt and redeploy."
        )
    except Exception as error:
        st.error(f"Could not read the file: {error}")

if "pdac_guard_records" in st.session_state:
    data = st.session_state["pdac_guard_records"]

    st.divider()
    st.subheader("Dataset overview")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total records", len(data))
    col2.metric("Total columns", len(data.columns))
    col3.metric(
        "Missing cells",
        int(data.isna().sum().sum()),
    )

    st.subheader("Edit records")

    st.caption(
        "Edit cells directly in the table. You can also add or "
        "delete rows. Download your changes to save them."
    )

    edited_data = st.data_editor(
        data,
        num_rows="dynamic",
        use_container_width=True,
        key="pdac_guard_record_editor",
        height=450,
    )

    st.session_state["pdac_guard_records"] = edited_data

    st.subheader("Search records")

    search_text = st.text_input(
        "Search across all columns",
        placeholder="Enter a biomarker value, cohort, or keyword...",
    )

    if search_text:
        searchable = edited_data.astype(str)
        matches = searchable.apply(
            lambda column: column.str.contains(
                search_text,
                case=False,
                na=False,
                regex=False,
            )
        ).any(axis=1)

        st.dataframe(
            edited_data.loc[matches],
            use_container_width=True,
            height=300,
        )
        st.caption(f"Matching records: {int(matches.sum())}")
    else:
        st.dataframe(
            edited_data.head(10),
            use_container_width=True,
        )
        st.caption("Showing the first 10 records in the preview.")

    st.download_button(
        label="Download edited records as CSV",
        data=edited_data.to_csv(index=False).encode("utf-8"),
        file_name="pdac_guard_edited_records.csv",
        mime="text/csv",
        use_container_width=True,
    )

else:
    st.markdown("### Get started")
    st.write(
        "Upload a CSV or Excel dataset to explore and edit its records."
    )

    st.write(
        "Your existing app pages remain available through the sidebar."
    )
