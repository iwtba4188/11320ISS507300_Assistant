import numpy as np
import plotly.graph_objs as go
import streamlit as st
from gensim.models import Word2Vec
from gensim.utils import simple_preprocess
from sklearn.decomposition import PCA

from utils.helpers import color_map, st_spinner
from utils.i18n import i18n
from utils.week10 import build_corpus, df_input


def page_init() -> None:
    st.title(i18n("week10.3d.doc_title"))


def draw_3d(training_corpus: list) -> None:
    spinner = st_spinner()

    tokenized_sentences = [simple_preprocess(sentence) for sentence in training_corpus]
    model = Word2Vec(
        tokenized_sentences, vector_size=100, window=5, min_count=1, workers=4
    )
    word_vectors = np.array([model.wv[word] for word in model.wv.index_to_key])
    pca = PCA(n_components=3)
    reduced_vectors = pca.fit_transform(word_vectors)

    word_colors = []
    for word in model.wv.index_to_key:
        for i, sentence in enumerate(tokenized_sentences):
            if word in sentence:
                word_colors.append(color_map[i % len(color_map)])
                break

    # Create a 3D scatter plot using Plotly
    scatter = go.Scatter3d(
        x=reduced_vectors[:, 0],
        y=reduced_vectors[:, 1],
        z=reduced_vectors[:, 2],
        mode="markers+text",
        text=model.wv.index_to_key,
        textposition="top center",
        marker=dict(color=word_colors, size=2),
    )

    fig = go.Figure(data=[scatter])

    # Set the plot title and axis labels
    fig.update_layout(
        scene=dict(xaxis_title="X", yaxis_title="Y", zaxis_title="Z"),
        title=i18n("week10.3d.fig_title"),
        # width=1000,  # Custom width
        height=700,  # Custom height
    )

    spinner.end()
    st.plotly_chart(fig)


if __name__ == "__main__":
    page_init()

    df = df_input()

    st.divider()

    training_corpus = build_corpus(df)
    if training_corpus == []:
        st.warning(i18n("week10.no_sentences"))
    else:
        draw_3d(training_corpus)
