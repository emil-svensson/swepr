import streamlit as st
import pandas as pd
from app_fncs import *

## layout stuff
st.set_page_config(layout="wide")
colwidths = [0.6, 0.4]

## more stuff at the bottom




## Print the title at the tippy-top of the page
st.title("🌈 SWEPR 🐢")
st.write(' ')
st.write(' ')
st.write(' ')

df = load_data()

## Initialize the session state object only once and create the variable st_ss as a short-hand
if 'dummy' not in st.session_state:
    st.session_state.dummy = 1
    st_ss = st.session_state
    initialize_reset_app(st_ss, type='initial')
else:
    st_ss = st.session_state
    st_ss.current_user_input = ''




## Global setting for english -> swedish, or swedish -> english
language_mode_dict = {'English':0, 'Swedish':1}

col1, col2 = st.columns(colwidths)
with col1:
    language_mode = st.radio('Translate from...', language_mode_dict.keys(), horizontal=True, key="sel_language")
with col2:
    st.write(' ')
    st.write(' ')
    if st.button('Reset'):
        initialize_reset_app(st_ss)


st.write(' ')
st.write(' ')
st.write(' ')



global col_from, col_to, to_language
if language_mode_dict[language_mode] == 0:
    language_keys = ('e_word', 's_word')
    col_from = 'e_word'
    col_to = 's_word'
    to_language = 'to Swedish'
elif language_mode_dict[language_mode] == 1:
    language_keys = ('s_word', 'e_word')
    col_from = 's_word'
    col_to = 'e_word'
    to_language = 'to English'




def process_user_input():

    user_input_temp = ''

    ## Store input both in st_ss and a function-local temp-variable (if it's not an empty string)
    ## Reset the st_ss user input (clear the textbox)
    if st_ss.user_input_noun != '':
        st_ss.current_word_class = 'noun'
        user_input_temp = st_ss.user_input_noun.strip()
        st_ss.user_input_noun = ''
    elif st_ss.user_input_verb != '':
        st_ss.current_word_class = 'verb'
        user_input_temp = st_ss.user_input_verb.strip()
        st_ss.user_input_verb = ''
    elif st_ss.user_input_prep != '':
        st_ss.current_word_class = 'preposition'
        user_input_temp = st_ss.user_input_prep.strip()
        st_ss.user_input_prep = ''
    elif st_ss.user_input_adj != '':
        st_ss.current_word_class = 'adjective'
        user_input_temp = st_ss.user_input_adj.strip()
        st_ss.user_input_adj = ''

    word_class = st_ss.current_word_class

    ## IF there was actual input...
    if user_input_temp != '':
        st_ss.stored_user_input[word_class] = user_input_temp
        st_ss.user_input_status[word_class] = 'Answer provided'
        if user_input_temp.lower() == df.loc[st_ss.current_word_idx[word_class], language_keys[1]].lower():
            # Set status to "Correct answer and generate a new word"
            st_ss.user_input_status[word_class] = 'Correct answer'
            new_word(df, st_ss, word_class)
        else:
            st_ss.user_input_status[word_class] = 'Wrong answer'




def user_facing_stuff(word_class):

    col_a, col_b = st.columns(colwidths)

    with col_b:
        
        ## After the button has been pressed once, show the remaining number of words
        if st_ss.number_of_words_left[word_class] < 0:
            button_text = f'New word'
        else:
            button_text = f'Next! ({st_ss.number_of_words_left[word_class]})'

        st.write(' ')
        if st.button(button_text ,key=f'button_{word_class}'):
            new_word(df, st_ss, word_class)
            st_ss.user_input_status[word_class] = 'Awaiting answer'
            st.rerun()
    
    with col_a:
        if st_ss.current_word_idx[word_class] is not None:
            current_word = df.loc[st_ss.current_word_idx[word_class], language_keys[0]]
            st.markdown(f"## {current_word}")
        else:
            st.markdown(f" {'___'}")
    
    ## User input text box
    if st_ss.current_word_idx[word_class] is not None:
        st.text_input(f"Translate the word above {to_language}:",
                                                key=f'user_input_{word_class}',
                                                on_change=process_user_input)

        ## Do stuff if the answer is wrong..
        if st_ss.user_input_status[word_class] == 'Wrong answer':

            w_answer = st_ss.stored_user_input[word_class].lower()
            w_true = df.loc[st_ss.current_word_idx[word_class], language_keys[1]].lower()
            st.write(f"Nope, try again. (Your answer was '{w_answer}' and scored {answer_score(w_true, w_answer)})")
            
            with st.expander("Show correct letters", expanded=False):
                st.write(f"{get_correct_letters(w_true, w_answer)}")
            with st.expander("Show desired answer", expanded=False):
                st.write(w_true.lower())

        ## Print success message if answer is correct
        elif st_ss.user_input_status[word_class] == 'Correct answer':
            st.markdown(f"**{success_message()}**")
    return



## Create tabs
tab1, tab2, tab3, tab4 = st.tabs(["Nouns", "Verbs", "Prepositions", "Adjectives"])

# Nouns
with tab1:
    word_class='noun'
    user_facing_stuff(word_class)

# Verbs
with tab2:
    word_class='verb'
    user_facing_stuff(word_class)



st.divider()




## more layout stuff
st.markdown("""<style> .block-container {padding-top: 2rem !important;
                                         padding-left: 0.5rem !important;
                                         padding-right: 0.5rem !important;} </style> """,
            unsafe_allow_html=True)

st.markdown(""" <style> [data-testid="stVerticalBlock"] {gap: 0.5rem !important} </style>""",
            unsafe_allow_html=True)

st.write('''<style>
            [data-testid="column"] {
                min-width: calc(30% - 0.5rem) !important;} </style>''',
        unsafe_allow_html=True)

st.markdown("""<style> [data-testid="baseButton-secondary"] {width: 7rem  !important;} </style> """,
            unsafe_allow_html=True)


st_ss.counter += 1