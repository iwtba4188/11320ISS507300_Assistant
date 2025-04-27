import pandas as pd
import streamlit as st
from gensim.models import Word2Vec
from gensim.parsing.preprocessing import remove_stopwords
from gensim.utils import simple_preprocess

from utils.helpers import st_spinner
from utils.i18n import i18n
from utils.week10 import build_corpus, df_input


def page_init() -> None:
    st.title(i18n("week10.skip_gram.doc_title"))


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
        "sg": 1,
    }

    # Train a skip-gram Word2Vec model
    model = Word2Vec(tokenized_sentences, **word2vec_config)

    spinner.end()

    return model


def most_similar_words(options: list) -> str:
    return st.selectbox(
        i18n("week10.most_similar_words"),
        label_visibility="collapsed",
        options=options,
        index=None,
        placeholder=i18n("week10.most_similar_words.placeholder"),
    )


def show_results(subheader: str, model: Word2Vec, word: str) -> None:
    st.subheader(subheader)
    try:
        similar_words = model.wv.most_similar(word)

        df_similar_words = pd.DataFrame(similar_words, columns=["Word", "Similarity"])
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
    except KeyError:
        st.warning(i18n("week10.no_keyword"))


def train_and_show(df: pd.DataFrame) -> None:
    if (training_corpus := build_corpus(df)) == []:
        st.warning(i18n("week10.no_sentences"))
        return

    model_original = train(training_corpus, is_remove_stopwords=False)
    model_remove_stopwords = train(training_corpus, is_remove_stopwords=True)

    st.subheader(i18n("week10.most_similar_words"))

    if word := most_similar_words(model_original.wv.index_to_key):
        col1, col2 = st.columns(2)

        with col1:
            show_results(i18n("week10.original_model"), model_original, word)

        with col2:
            show_results(
                i18n("week10.remove_stopwords_model"), model_remove_stopwords, word
            )


if __name__ == "__main__":
    page_init()

    df = df_input()
    st.divider()
    train_and_show(df)
