import streamlit as st
import pandas as pd
import random
import math
import re
import numpy as np
from collections import Counter


@st.cache_data
def load_data():
    df1 = pd.read_excel('swedish_words_practice.xlsx', sheet_name='nouns')
    df2 = pd.read_excel('swedish_words_practice.xlsx', sheet_name='verbs')
    df = pd.concat([pd.concat([pd.Series(['noun']*len(df1), name='type'), df1], axis=1),
                    pd.concat([pd.Series(['verb']*len(df2), name='type'), df2], axis=1)], axis=0).reset_index(drop=True)
    return df



def initialize_reset_app(st_ss, type='hard'):
    word_classes = ['noun', 'verb', 'preposition', 'adjective']

    init_dict = {
        'counter': 0,
        'current_word_class': 'noun',
        'used_word_idxs': [],
        'user_input_noun': '',
        'user_input_verb': '',
        'user_input_prep': '',
        'user_input_adj': '',
        'current_word_idx': dict(zip(word_classes, [None]*len(word_classes))),
        'previous_word_idx': dict(zip(word_classes, [None]*len(word_classes))),
        'number_of_words_left': dict(zip(word_classes, [-1]*len(word_classes))),
        'stored_user_input': dict(zip(word_classes, ['']*len(word_classes))),
        'user_input_status': dict(zip(word_classes, ['']*len(word_classes))),}


    ## Only set a state-value from init_dict if it doesn't exist in st_ss
    if type == 'initial':
        for param, value in init_dict.items():
            if param not in st_ss:
                st_ss[param] = value

    ## Overwrite all state-values from init_dict
    elif type == 'hard':
        for param, value in init_dict.items():
            st_ss[param] = value

    elif type=='soft':
        # st.write('soft reset did nothing!')
        st_ss.used_word_idxs = []

    return 



def new_word(df, st_ss, wclass):
    ## First, filter with word class
    df_temp = df[df['type'] == wclass].copy()

    ## Only pick from indices not used in this session
    remaining_idxs = [val for val in df_temp.index if val not in st_ss.used_word_idxs]
    df_temp = df_temp[df_temp.index.isin(remaining_idxs)]
    st_ss.number_of_words_left[wclass] = len(df_temp)-1

    if len(df_temp) > 0:
        ## Store current_word_idx  in previous_word_idx
        st_ss.previous_word_idx[wclass] = st_ss.current_word_idx[wclass]

        ## Sample a new row with new word-data and extract the index, add it to the used_words_idxs list
        row = df_temp.sample(1)
        st_ss.current_word_idx[wclass] = int(row.index[0]) 
        st_ss.used_word_idxs.append(int(row.index[0]))

        ## Reset the stored usaer input
        st_ss.stored_user_input[wclass] = ""        

    else:
        initialize_reset_app(st_ss, type='soft')
        new_word(df, st_ss, wclass)

    return 
    # return 'All words have been used. Resetting.'



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


def success_message():
    list = ["You got it chief. That's correct.",
            "Yup, that's right",
            "Correct.",
            "Yep, that's the right answer",
            "Nailed it!",
            "Well done, try another word"]
    return random.choice(list)



def answer_clue(w_true, w_answer):
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

    if (" _ " not in w_out) and ("_ " not in w_out):
        ind = np.random.choice(np.arange(len(w_out)))
        if ind == 0:
            w_out[0] = "_ "
        else:
            w_out[ind] = " _ "
    
    w_out = "".join(map(str, w_out))

    return w_out