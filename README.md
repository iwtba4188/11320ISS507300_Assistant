> Clone from [GildShen/Gild-chatbot](https://github.com/GildShen/Gild-chatbot).

# 💬 Chatbot template

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://iwtba4188-11320iss507300-assistant.streamlit.app/)
<a href="github.com/iwtba4188/11320ISS507300_Assistant/actions/workflows/tests.yml" target="_blank">
    <img src="https://github.com/iwtba4188/11320ISS507300_Assistant/actions/workflows/tests.yml/badge.svg" alt="Test Action Status">
</a>
<a href="https://coverage-badge.samuelcolvin.workers.dev/redirect/iwtba4188/11320ISS507300_Assistant" target="_blank">
    <img src="https://coverage-badge.samuelcolvin.workers.dev/iwtba4188/11320ISS507300_Assistant.svg" alt="Test Coverage">
</a>

A simple Streamlit app for pet consultancy and adoption matching that shows how to build a chatbot using Google's `gemini-2.5-flash-preview-04-17`.


### How to run it on your own machine

1. Install the requirements

   ```sh
   $ pip install -r requirements.txt
   ```

   or

   ```sh
   $ uv sync
   ```

2. Set your Gemini API key

   You may need to set your Gemini API key in the `secrets.toml` file. You can copy the `secrets.toml.example` file and rename it to `secrets.toml`. Then, set your API key in the file.

   ```sh
   $ cp secrets.toml.example secrets.toml
   ```

   Then, open the `secrets.toml` file and set your API key.

3. Run the app

   ```sh
   $ streamlit run ./src/streamlit_app.py
   ```
