import os

import streamlit as st
from streamlit_chat import message
from langchain.chains import ConversationChain
from langchain.llms import OpenAI
import openai

from db.db_client import DBIndex
from dotenv import load_dotenv

load_dotenv()


# OPENAPI_API_KEY = "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"

# # From here down is all the StreamLit UI.
st.set_page_config(page_title="Test", page_icon=":robot:")
st.header("My saved linkedin posts chatbot")

openai.api_key = os.environ.get('OPENAI_API_KEY')

# Place this near the top of your script where you define TOP_K
TOP_K = st.slider('Select TOP_K Value', min_value=1, max_value=100, value=5, step=1)


@st.cache_resource
def get_index(class_name):
    print('connecting to linkedin...')
    index = DBIndex(class_name=class_name)
    return index

choice_mapping = {'LinkedIn': get_index('Linkedin'),
                  'OneNote': get_index('Onenote')}

if "generated" not in st.session_state:
    st.session_state["generated"] = []

if "past" not in st.session_state:
    st.session_state["past"] = []


def get_text():
    input_text = st.text_input("You: ", "Ask me anything", key="input")
    choice = st.radio(
        'Choose your source',
        ('OneNote', 'LinkedIn')
    )
    # if input_text == "Ask me anything":
    #     return "", {'matches': [{'metadata': {'text': ""}}]}

    # embed_model = "text-embedding-ada-002"
    # res = openai.Embedding.create(
    #     input=[input_text],
    #     engine=embed_model
    # )
    print(f'user_input: {input_text}')

    # retrieve from Pinecone
    # xq = res['data'][0]['embedding']
    # get relevant contexts (including the questions)
    # res = index.query(xq, top_k=TOP_K, include_metadata=True)


    index = choice_mapping[choice]

    res = index.search(input_text, ['text', 'file_name', 'name', 'date'], limit=TOP_K)

    return input_text, res


user_input, emb_res = get_text()
print(emb_res)

# get list of retrieved text
contexts = [item['text'] for item in emb_res]

augmented_query = "\n\n---\n\nCONTEXTS: ".join(contexts) + "\n\n-----\n\n" + user_input

print(f'augmented_query: {augmented_query}')

output = ""

if user_input:
    # output = chain.run(input=user_input)

    # system message to 'prime' the model
    primer = f"""You're an expert on my linkedin posts. You only provide answers in the following format. Post: ... Link: .... you only provide posts and links from the CONTEXTS"""
    # primer = f"""You are Q&A bot. A highly intelligent system that answers
    # user questions based on the information provided by the user above
    # each question. If the information can not be found in the information
    # provided by the user you truthfully say "I don't know". Summarise and give referecnces from results. Always provide references and they should be linkedin links https://lnkd.in/....
    # """

    print("starting a new conversation. initiating openai chat completion...")

    output = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",  #"gpt-4",
        messages=[
            {"role": "system", "content": primer},
            {"role": "user", "content": augmented_query}
        ]
    )

    print("output: ", output)
    st.session_state.past.append(user_input)
    if 'choices' in output:
        st.session_state.generated.append(output['choices'][0]['message']['content'])
    else:
        st.session_state.generated.append("")

if st.session_state["generated"]:

    for i in range(len(st.session_state["generated"]) - 1, -1, -1):
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state["past"][i], is_user=True, key=str(i) + "_user")

    st.subheader('Retrieved Results')
    for i, match in enumerate(emb_res):
        st.markdown(
            f"<div style='white-space: pre-wrap; color: #ffffff; font-weight: bold;'>date {i + 1}: {match.get('date')}</div>",
            unsafe_allow_html=True)
        st.markdown(
            f"<div style='white-space: pre-wrap; color: #ffffff; font-weight: bold;'>Author name {i + 1}: {match.get('name')}</div>",
            unsafe_allow_html=True)

        st.markdown(
            f"<div style='white-space: pre-wrap; color: #ffffff; font-weight: bold;'>Result file {i + 1}: {match.get('file_name')}</div>",
            unsafe_allow_html=True)
        st.markdown(f"<div style='white-space: pre-wrap; color: #ffffff;'>Result {i + 1}: {match['text'][:1000]}</div>",
                    unsafe_allow_html=True)
        st.markdown("---")  # separator


# run streamilt app from CLI
# streamlit run streamlit_qanoon.py