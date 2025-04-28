import pandas as pd
import streamlit as st
from gensim.models import Word2Vec
from gensim.parsing.preprocessing import remove_stopwords
from gensim.utils import simple_preprocess

from utils.helpers import st_spinner
from utils.i18n import i18n
from utils.week10 import build_corpus, df_input


def page_init() -> None:
    st.title(i18n("week10.cbow.doc_title"))


def train(training_corpus: list, is_remove_stopwords: bool) -> None:
    spinner = st_spinner()

    # Preprocess the sentences
    if is_remove_stopwords:
        tokenized_sentences = [
            simple_preprocess(remove_stopwords(sentence))
            for sentence in training_corpus
        ]
    else:
        tokenized_sentences = [
            simple_preprocess(sentence) for sentence in training_corpus
        ]

    word2vec_config = {
        "vector_size": 200,
        "window": 6,
        "min_count": 1,
        "workers": 4,
        "sg": 0,
    }

    # Train a skip-gram Word2Vec model
    model = Word2Vec(tokenized_sentences, **word2vec_config)

    spinner.end()

    return model


def select_similar_word(options: list) -> str:
    return st.selectbox(
        i18n("week10.most_similar_words"),
        label_visibility="collapsed",
        options=options,
        index=None,
        placeholder=i18n("week10.most_similar_words.placeholder"),
    )


def get_similar_words(model: Word2Vec, word: str) -> pd.DataFrame | None:
    try:
        similar_words = model.wv.most_similar(word)
        df_similar_words = pd.DataFrame(similar_words, columns=["Word", "Similarity"])
        return df_similar_words
    except KeyError as e:
        st.warning(i18n("week10.not_keyword"))


def show_results(subheader: str, df_similar_words: pd.DataFrame | None) -> None:
    if df_similar_words is None:
        return

    st.subheader(subheader)

    st.dataframe(
        df_similar_words,
        column_config={
            "Word": st.column_config.TextColumn(),
            "Similarity": st.column_config.ProgressColumn(
                format="%.5f",
                min_value=0,
                max_value=1,
            ),
        },
    )


def train_and_show(df: pd.DataFrame) -> None:
    if (training_corpus := build_corpus(df)) == []:
        st.warning(i18n("week10.no_sentences"))
        return

    models = {
        "original": train(training_corpus, is_remove_stopwords=False),
        "rm_stopwords": train(training_corpus, is_remove_stopwords=True),
    }

    st.subheader(i18n("week10.most_similar_words"))

    if word := select_similar_word(models["original"].wv.index_to_key):
        cols = st.columns(len(models))

        results = []
        for col, model in zip(cols, models.values()):
            with col:
                results.append(get_similar_words(model, word))

        for col, name, result in zip(cols, models.keys(), results):
            with col:
                show_results(i18n(f"week10.{name}_model"), result)


if __name__ == "__main__":
    page_init()

    df = df_input()
    st.divider()
    train_and_show(df)
