import streamlit as st
from __init__ import streamlit_lexical
# Add some test code to play with the component while it's in development.
# During development, we can run this just as we would any other Streamlit
# app: `$ streamlit run my_component/example.py`
def update_val():
    new_content = "# New Heading\n\nThis is updated content in **Markdown**."
    st.session_state['key'] = new_content

st.write("#") # if this isnt here, for some reason, if you change the heading prior to entering any text, the page jumps to the bottom
st.header("Lexical Rich Text Editor")

if st.session_state.get('key') is None:
    st.session_state['key'] = 'initial value'

# Create an instance of our component with a constant `name` arg, and
markdown = streamlit_lexical(value=st.session_state.get('key'), placeholder="Enter some rich text", key='1234', height=800)


# Button to update content
st.button("Update Editor Content", on_click=update_val)

    #markdown = streamlit_lexical(value=new_content, placeholder="Enter some rich text", height=800)

#st.markdown(markdown)
#markdown = streamlit_lexical(value="", placeholder="Enter some rich text", height=800, on_change=None)

st.markdown(markdown)
st.markdown("---")