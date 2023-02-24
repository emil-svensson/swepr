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

if 'user_text_inp' not in st.session_state:
    st.session_state.user_text_inp = ''

if 'user_text_inp_temp' not in st.session_state:
    st.session_state.user_text_inp_temp = ''

if 'current_word' not in st.session_state:
    st.session_state.current_word = ''





st.set_page_config(layout="wide")
st.title("Swepr 🍄")
df = pd.read_excel('swedish_words_practice.xlsx')



def initialize_reset_app(type='hard'):
    if type == 'hard':
        used_words = []
        st.session_state.used_words = []
        st.session_state.counter = 0
        st.session_state.active_q = False
        st.session_state.user_text_inp = ''
        st.session_state.user_text_inp_temp = ''
        st.session_state.current_word = ''

        smessage ='The session has just been started or reset'
        return used_words, smessage

    elif type=='soft':
        st.session_state.active_q = False
        st.session_state.user_text_inp = ''
        st.session_state.user_text_inp_temp = ''
        st.session_state.current_word = ''

        return





if (st.button('Start/reset')) | (st.session_state.counter == 0):
    used_words, smessage = initialize_reset_app()
if st.session_state.counter > 0:
    used_words = st.session_state.used_words

try:
    st.write(smessage)
except NameError:
     pass


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
    st.session_state.user_text_inp_temp = st.session_state.userinputtext1
    st.session_state.userinputtext1 = ""

    st.session_state.active_q = True




def success_message():
    list = ["You got it chief. That's correct.",
            "Yup, that's right",
            "Correct.",
            "Yep, that's the right answer",
            "Nailed it!",
            "Well done, try another word"]
    return random.choice(list)




if st.button('Randomize word'):
    initialize_reset_app(type='soft')

    word, used_words = new_word(used_words)
    st.session_state.current_word = word
    st.session_state.used_words = used_words
    

    st.session_state.user_text_inp_temp = 'Awaiting answer'


else:
    word = st.session_state.current_word






if st.session_state.active_q | (st.session_state.user_text_inp_temp == 'Awaiting answer'):
    
    st.markdown(f"Translate **{word['e_word'].iloc[0]}** to swedish")
    st.session_state.user_text_inp = st.text_input('Type here:', key='userinputtext1', on_change=clear_uinput)

    if st.session_state.user_text_inp_temp != 'Awaiting answer':
        st.write(f'Your answer: {st.session_state.user_text_inp_temp}')
    else:
        st.write(f'Your answer:')


    if st.session_state.user_text_inp_temp == word['s_word'].iloc[0]:
        st.write(success_message())
        initialize_reset_app(type='soft')

    elif st.session_state.user_text_inp_temp != 'Awaiting answer':
        st.write('Nope, try again')




try:
    st.session_state.used_words = used_words
except NameError:
    pass

st.session_state.counter += 1
