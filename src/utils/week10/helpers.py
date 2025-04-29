import numpy as np
import pandas as pd
import streamlit as st

from utils.i18n import i18n


def df_input() -> pd.DataFrame:
    st.subheader("Input Data")

    df = st.data_editor(
        pd.DataFrame(columns=["selected", "sentence"]),
        num_rows="dynamic",
        column_order=("selected", "sentence"),
        column_config={
            "selected": st.column_config.CheckboxColumn(
                i18n("df_input.col_name.selected"),
                help="Select this sentence to train the model",
                default=True,
                width="medium",
                pinned=True,
            ),
            "sentence": st.column_config.TextColumn(
                i18n("df_input.col_name.sentence"),
                help="Enter sentences here",
                required=True,
            ),
        },
        key="df_input",
    )

    return df


def build_corpus(df: pd.DataFrame) -> list[str]:
    # Track: https://github.com/astral-sh/ruff/issues/1852
    df = df[df["selected"] == True]  # noqa: E712
    df = df.replace(regex=r"^\s*$", value=np.nan).dropna()

    corpus = df["sentence"].tolist()
    return corpus
