# streamlit-chat-input-advanced

Streamlit component that allows you catch arrow up keyboard event

it implements ability to 
* clear textarea when user press Escape

  ![Example message cleanup on Escape|200x100](example_msg_cleanup.gif)
* allow go back and forth by message history 

    ![Chat history example](example_chat_history.gif)

## Installation instructions

```sh
pip install streamlit-chat-input-advanced
```

## Usage instructions

```python
import streamlit as st

from chat_input_advanced import chat_input_avd

value = chat_input_avd()

st.write(value)
```