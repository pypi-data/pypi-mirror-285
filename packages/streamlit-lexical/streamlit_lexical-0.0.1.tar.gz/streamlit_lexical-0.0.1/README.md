# streamlit_lexical

Streamlit component that allows you to use Lexical's rich text plugin. 

## Installation instructions

```sh
cd streamlit_lexical/frontend
npm install (or yarn install)
npm run build
cd ../..
pip install -e ./
```

## Usage instructions

```python
import streamlit as st

from streamlit_lexical import streamlit_lexical

rich_text_dict = streamlit_lexical("name")

st.markdown(rich_text_dict)
```