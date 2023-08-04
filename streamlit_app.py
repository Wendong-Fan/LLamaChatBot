import streamlit as st
import replicate
import os
from time import sleep

st.set_page_config(page_icon="🦙💬", page_title=" LLamaChat")

#Replicate Credentials
with st.sidebar:
    st.title("🦙💬 LlamaChat")
    if 'REPLICATE_API_TOKEN' in st.secrets:
        st.success('API key already provided!', icon='✅')
        replicate_api = st.secrets['REPLICATE_API_TOKEN']
    else:
        replicate_api = st.text_input("Enter Replicate API token: ", type='password')
        if not (replicate_api.startswith('r8_') and len(replicate_api)==40):
            st.warning('Please enter your credentials!', icon='⚠️')
        else:
            st.success('Proceed to entering your prompt message!', icon='👉')
            
    st.markdown("How to get the Replicate API token for free!")
    st.markdown("1. Go to https://replicate.com/signin/")
    st.markdown("2. Sign in with your GitHub account.")
    st.markdown("3. Proceed to the API tokens page and copy your API token.")
    st.markdown("Built by Josiah Adesola")
    st.markdown("🙏Acknowledged the Streamlit Blog ")
    
os.environ['REPLICATE_API_TOKEN'] = replicate_api

#Store LLM generated responses 
if "messages" not in st.session_state.keys():
    st.session_state.messages = [{"role": "assistant", "content": "How may I assist you today?"}]

#Display or clear chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])     
        
def clear_chat_history():
    st.session_state.messages =  [{"role": "assistant", "content": "How may I assist you today?"}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

# Generate Llama2 response

def generate_llama2_response(prompt_input):
    string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
    for dict_message in st.session_state.messages:
        if dict_message["role"] == "user":
            string_dialogue +="User: " + dict_message["content"] + "\\n\\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\\n\\n"
    output = replicate.run('a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5', 
                           input={"prompt": f"{string_dialogue} {prompt_input} Assistant: ",
                                  "temperature":0.01, "top_p":0.9, "max_length":1024, "repetition_penalty":1})
    return output

# User-provided prompt 
if prompt := st.chat_input(disabled=not replicate_api):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
        
# Generate a new response if last message is not from assistant
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = generate_llama2_response(prompt)
            placeholder = st.empty()
            full_response = ''
            for item in response:
                full_response += item + " "
                placeholder.markdown(full_response + "▌")
                sleep(0.1)
            placeholder.markdown(full_response)
            
        message = {"role": "assistant", "content": full_response}
        st.session_state.messages.append(message)
