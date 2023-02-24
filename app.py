import streamlit as st
import pandas as pd
import numpy as np
import random



if 'counter' not in st.session_state:
    st.session_state.counter = 0

if 'used_words' not in st.session_state:
    st.session_state.used_words = []

if 'active_q' not in st.session_state:
    st.session_state.active_q = False

if 'user_text_inp1_temp' not in st.session_state:
    st.session_state.user_text_inp1_temp = ''

if 'current_word' not in st.session_state:
    st.session_state.current_word = None

if 'next_word' not in st.session_state:
    st.session_state.next_word = None





st.set_page_config(layout="wide")
st.title("🌈 SWEPR 🐢")
df = pd.read_excel('swedish_words_practice.xlsx')


language_mode_dict = {'from English':0, 'from Swedish':1}
language_mode = st.radio('Translate...', language_mode_dict.keys(), horizontal=True)


if language_mode_dict[language_mode] == 0:
    col_from = 'e_word'
    col_to = 's_word'
    to_language = 'to Swedish'
elif language_mode_dict[language_mode] == 1:
    col_from = 's_word'
    col_to = 'e_word'
    to_language = 'to English'





def initialize_reset_app(type='hard'):
    if type == 'hard':
        used_words = []
        st.session_state.used_words = []
        st.session_state.counter = 0
        st.session_state.active_q = False
        st.session_state.user_text_inp1_temp = ""
        st.session_state.current_word = None
        st.session_state.next_word = None

        smessage ='The session has just been started or reset'
        return used_words, smessage

    elif type=='soft':
        st.session_state.active_q = False
        # st.session_state.user_text_inp = ''
        st.session_state.user_text_inp1_temp = ''
        # st.session_state.current_word = ''

        return




def success_message():
    list = ["You got it chief. That's correct.",
            "Yup, that's right",
            "Correct.",
            "Yep, that's the right answer",
            "Nailed it!",
            "Well done, try another word"]
    return random.choice(list)



def new_word(used_words):

    # making sure that we don't pick a word that has already been used in the session
    df_red_ind = [val for val in df.index if val not in used_words]
    df_reduced = df[df.index.isin(df_red_ind)]

    if len(df_reduced) > 0:
        word = df_reduced.sample(1)    
        used_words.append(word.index[0]) 
        
    else:
        used_words, _ = initialize_reset_app()
        st.write('All words have been used. Resetting.')
        word, used_words = new_word(used_words)

    return word, used_words



def clear_uinput():
    st.session_state.user_text_inp1_temp = st.session_state.user_text_inp1
    st.session_state.user_text_inp1 = ""

    st.session_state.active_q = True




def check_clear_answer_update_q():
    # executes on the next run when submitting the text field input

    if st.session_state.user_text_inp1.lower() == st.session_state.next_word[col_to].iloc[0].lower():
        # answer is correct

        # before next_word is (re-)generated we store it in current_word
        if st.session_state.next_word is not None:
            st.session_state.current_word = st.session_state.next_word

        # generate new word and update used_words
        st.session_state.next_word, st.session_state.used_words = new_word(used_words)
          

    # save the inaccurate answer in st.session_state.user_text_inp1_temp and then reset text input field state variable
    st.session_state.user_text_inp1_temp = st.session_state.user_text_inp1
    st.session_state.user_text_inp1 = ""

    st.session_state.active_q = True



col1, col2 = st.columns(2)

with col1:
    


    if (st.button('Start/reset')) | (st.session_state.counter == 0):
        used_words, smessage = initialize_reset_app()
    if st.session_state.counter > 0:
        used_words = st.session_state.used_words


    try:
        st.write(smessage)
    except NameError:
        pass

    st.write('''<style>

    [data-testid="column"] {
        width: calc(50% - 1rem) !important;
        flex:  1 calc(50% - 1rem) !important;
        min-width: calc(50% - 1rem) !important;
    }
    </style>''', unsafe_allow_html=True)


with col2:

    if st.button('Randomize word'):
        initialize_reset_app(type='soft')
        word, used_words = new_word(used_words)

        # before next_word is (re-)generated we store it in current_word
        if st.session_state.next_word is not None:
            st.session_state.current_word = st.session_state.next_word
        else:
            # in the first iteration current word and next word will be the same
            st.session_state.current_word = word


        st.session_state.next_word = word
        st.session_state.used_words = used_words

        st.session_state.user_text_inp1_temp = 'Awaiting answer'

    st.write('''<style>

    [data-testid="column"] {
        width: calc(50% - 1rem) !important;
        flex:  1 calc(50% - 1rem) !important;
        min-width: calc(50% - 1rem) !important;
    }
    </style>''', unsafe_allow_html=True)



if st.session_state.active_q | (st.session_state.user_text_inp1_temp == 'Awaiting answer'):
    
    temp_string = st.session_state.next_word[col_from].iloc[0]
    st.markdown(f"Translate **{temp_string}** {to_language}")
    st.text_input('Type here:', key='user_text_inp1', on_change=check_clear_answer_update_q)


    if st.session_state.user_text_inp1_temp != 'Awaiting answer':
        st.write(f'Your answer: {st.session_state.user_text_inp1_temp}')
    else:
        st.write(f'Your answer:')


    if st.session_state.user_text_inp1_temp.lower() == st.session_state.current_word[col_to].iloc[0].lower():
        st.markdown(f"**{success_message()}**")
        initialize_reset_app(type='soft')
        
    elif st.session_state.user_text_inp1_temp != 'Awaiting answer':
        st.write('Nope, try again')




st.session_state.counter += 1
