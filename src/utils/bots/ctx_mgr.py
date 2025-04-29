from collections import deque
from typing import Any

import streamlit as st


class CtxMgr:
    def __init__(self, name: str, maxlen: int | None = 20) -> None:
        self.session_state_name = f"{name}_ctx"
        if self.session_state_name not in st.session_state:
            st.session_state[self.session_state_name] = deque(maxlen=maxlen)

    def add_context(self, content: Any) -> None:
        """
        Append a content item to st.session_state[self.session_state_name], initializing it as a deque of max
        length 20 if needed.
        """
        st.session_state[self.session_state_name].append(content)

    def clear_context(self) -> None:
        """
        Clear the context in st.session_state[self.session_state_name].
        """
        st.session_state[self.session_state_name].clear()

    def get_context(self) -> Any:
        """
        Retrieve the current context from st.session_state[self.session_state_name].
        """
        return list(st.session_state[self.session_state_name])
