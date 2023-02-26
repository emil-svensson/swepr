import streamlit as st
import pandas as pd
import numpy as np
import random

import re
from collections import Counter
import math



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


language_mode_dict = {'English':0, 'Swedish':1}
language_mode = st.radio('Translate from...', language_mode_dict.keys(), horizontal=True)


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


def answer_score(w_true, w_answer):
    true_w_vec = Counter(re.compile(r"\w").findall(w_true))
    answer_w_vec = Counter(re.compile(r"\w").findall(w_answer))

    intersection = set(true_w_vec.keys()) & set(answer_w_vec.keys())
    numerator = sum([true_w_vec[x] * answer_w_vec[x] for x in intersection])

    sum1 = sum([true_w_vec[x] ** 2 for x in list(true_w_vec.keys())])
    sum2 = sum([answer_w_vec[x] ** 2 for x in list(answer_w_vec.keys())])
    denominator = math.sqrt(sum1) * math.sqrt(sum2)


    if not denominator:
        return '0'
    else:
        score = str(100*round((float(numerator)/denominator), 2))
        return score
    

def answer_clue(w_true, w_answer):
    # print(f"true: {w_true}")
    # print(f"uinput: {w_answer}")

    if (w_answer == "Awaiting answer") or (w_answer == ""):
        return "You gotta take a shot first. Type something."

    w_out = []
    wt_letter_idx = 0
    wa_letter_idxs_list = [list(range(len(w_answer))) for i in range(len(w_answer))]

    while True:
        if wt_letter_idx == len(w_true):
            break # all output slots should be filled
        
        try: # if w_true has more letters than w_answer we'll get an index error
            wa_letter_idxs = wa_letter_idxs_list[wt_letter_idx]

        except IndexError:
            wa_letter_idxs = wa_letter_idxs_list[0]
            wa_letter_idxs = [] # don't match more stuff if the user input (w_answer) is longer than w_true
            # letter = None
            # pass

        try:
            if match:
                wa_letter_idxs = [wa_letter_idx + 1] # if the last letter was a match, only check the next letter
        except NameError:
            match = False


        for wa_letter_idx in wa_letter_idxs:
            
            try:
                # print(f"a:{wa_letter_idx}, t:{wt_letter_idx}")
                if w_answer[wa_letter_idx] == w_true[wt_letter_idx]:

                    letter = w_true[wt_letter_idx]

                    # special case to make sure the last letter of the words, in fact, match
                    if (wt_letter_idx == len(w_true)-1) and (w_true[-1] != w_answer[-1]):
                        letter = None
                    break
                else:
                    letter = None

            except IndexError:
                pass

            if wt_letter_idx == 0: # this clause is only used if the first letters don't match
                letter = None
                # the list of indices is sliced so that the first letter in w_answer can't be referenced again
                wa_letter_idxs_list = [wa_letter_idxs_list[i][1::] for i in range(len(wa_letter_idxs_list))] # the list of indices is sliv
                break # break if the first letters don't match


        if letter is not None:
            w_out.append(letter)
            match = True
            letter = None
        else:
            match = False
            if wt_letter_idx > 0:
                try:
                    w_out[-1].rstrip()
                except IndexError:
                    pass
                w_out.append(" _ ")
            else:
                w_out.append("_ ")
            
        wt_letter_idx += 1
        # print(w_out)


    if (" _ " not in w_out) and ("_ " not in w_out):
        ind = np.random.choice(np.arange(len(w_out)))
        if ind == 0:
            w_out[0] = "_ "
        else:
            w_out[ind] = " _ "
    

    w_out = "".join(map(str, w_out))

    return w_out



col1, col2 = st.columns(2)

with col1:
    


    if (st.button('Start/reset')) | (st.session_state.counter == 0):
        used_words, smessage = initialize_reset_app()
    if st.session_state.counter > 0:
        used_words = st.session_state.used_words


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



try:
    st.write(smessage)
except NameError:
    pass




if st.session_state.active_q | (st.session_state.user_text_inp1_temp == 'Awaiting answer'):
    
    temp_string = st.session_state.next_word[col_from].iloc[0]
    st.markdown(f"## {temp_string}")
    # st.markdown(f"Translate **{temp_string}** {to_language}")
    st.text_input(f"translate the word above {to_language}:", key='user_text_inp1', on_change=check_clear_answer_update_q)


    if st.session_state.user_text_inp1_temp != 'Awaiting answer':
        st.write(f'Your answer: {st.session_state.user_text_inp1_temp}')
    else:
        st.write(f'Your answer:')


    w_true = st.session_state.next_word[col_to].iloc[0]
    w_answer = st.session_state.user_text_inp1_temp

    if w_answer.lower() == st.session_state.current_word[col_to].iloc[0].lower():
        st.markdown(f"**{success_message()}**")
        initialize_reset_app(type='soft')
    
    elif w_answer != 'Awaiting answer':
        st.write(f"Nope, try again. Attempt score: {answer_score(w_true.lower(), w_answer.lower())}%")


    with st.expander("click me for a clue", expanded=False):
        st.write(f"{answer_clue(st.session_state.next_word[col_to].iloc[0], st.session_state.user_text_inp1_temp)}")

    with st.expander("click me to see the correct answer", expanded=False):
        st.write(st.session_state.next_word[col_to].iloc[0].lower())




st.session_state.counter += 1
