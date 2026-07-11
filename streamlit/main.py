import streamlit as st
from tools import Tools
from agent.loopagent import conversation

tool = Tools()

st.title("Medical Appointment Booking System")

if "current_view" not in st.session_state:
    st.session_state.current_view = "login"

if "is_logged_in" not in st.session_state:
    st.session_state.is_logged_in = False

if "session_id" not in st.session_state:
    st.session_state.session_id = None

if "username" not in st.session_state:
    st.session_state.username = None

if "messages" not in st.session_state:
    st.session_state.messages = []


def login_user():
    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login", use_container_width=True):

        user = tool.get_user(username, password)

        if user["status"]:
            st.session_state.is_logged_in = True
            st.session_state.session_id = user["data"]["session_id"]
            st.session_state.username = user["data"]["username"]
            st.session_state.messages = []

            st.rerun()

        else:
            st.error(user["message"])

def signup_user():
    st.subheader("Sign Up")

    username = st.text_input("New Username")
    password = st.text_input("New Password", type="password")

    if st.button("Sign Up", use_container_width=True):

        result = tool.create_user(username, password)

        if result["status"]:
            st.success("Account created successfully.")

            st.session_state.current_view = "login"

            st.rerun()

        else:
            st.error(result["message"])

def chat_bot():

    st.success(f"Welcome {st.session_state.username}")

    col1, col2 = st.columns([5, 1])

    with col2:
        if st.button("Logout"):

            st.session_state.is_logged_in = False
            st.session_state.session_id = None
            st.session_state.username = None
            st.session_state.messages = []
            st.session_state.current_view = "login"

            st.rerun()

    st.divider()

    # Display previous messages
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # Chat input
    if prompt := st.chat_input("Ask something..."):

        st.session_state.messages.append(
            {
                "role": "user",
                "content": prompt
            }
        )

        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):

            with st.spinner("Thinking..."):

                response = conversation(
                    prompt,
                    thread_id=st.session_state.session_id
                )

            st.markdown(response)

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": response
            }
        )


if st.session_state.is_logged_in:

    chat_bot()

else:

    col1, col2, _ = st.columns([1, 1, 4])

    with col1:
        if st.button(
            "Login",
            type="primary" if st.session_state.current_view == "login" else "secondary",
            use_container_width=True,
        ):
            st.session_state.current_view = "login"
            st.rerun()

    with col2:
        if st.button(
            "Sign Up",
            type="primary" if st.session_state.current_view == "signup" else "secondary",
            use_container_width=True,
        ):
            st.session_state.current_view = "signup"
            st.rerun()

    st.divider()

    if st.session_state.current_view == "login":
        login_user()
    else:
        signup_user()