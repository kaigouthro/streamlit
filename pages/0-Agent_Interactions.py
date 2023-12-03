import streamlit as st
import os
from components.selectors import (
    agent_selection,
    conversation_selection,
    chain_selection,
    prompt_options,
    prompt_selection,
)
from ApiClient import ApiClient, DEV_MODE
from components.docs import agixt_docs, predefined_injection_variables
import time

st.set_page_config(
    page_title="Agent Interactions",
    page_icon=":speech_balloon:",
    layout="wide",
)


agixt_docs()

st.header("Agent Interactions")
if show_injection_var_docs := st.checkbox(
    "Show Prompt Injection Variable Documentation"
):
    predefined_injection_variables()
try:
    with open(os.path.join("session.txt"), "r") as f:
        agent_name = f.read().strip()
except:
    agent_name = "OpenAI"
st.session_state["conversation"] = conversation_selection(agent_name=agent_name)
mode = st.selectbox(
    "Select Agent Interaction Mode", ["Chat", "Chains", "Prompt", "Instruct"]
)

agent_name = agent_selection() if mode != "Chains" else ""

if mode in ["Chat", "Instruct"]:
    args = prompt_options()
    args["user_input"] = st.text_area("User Input")
    args["prompt_name"] = "Chat" if mode != "Instruct" else "instruct"
if mode == "Prompt":
    args = prompt_selection()

if mode != "Chains":
    if st.button("Send"):
        args["conversation_name"] = st.session_state["conversation"]
        with st.spinner("Thinking, please wait..."):
            if response := ApiClient.prompt_agent(
                agent_name=agent_name,
                prompt_name=args["prompt_name"],
                prompt_args=args,
            ):
                st.experimental_rerun()

if mode == "Chains":
    chain_names = ApiClient.get_chains()
    if agent_override := st.checkbox("Override Agent"):
        agent_name = agent_selection()
    else:
        agent_name = ""
    if advanced_options := st.checkbox("Show Advanced Options"):
        single_step = st.checkbox("Run a Single Step")
        if single_step:
            from_step = st.number_input("Step Number to Run", min_value=1, value=1)
            all_responses = False
        else:
            from_step = st.number_input("Start from Step", min_value=1, value=1)
            all_responses = st.checkbox(
                "Show All Responses (If not checked, you will only be shown the last step's response in the chain when done.)"
            )
    else:
        single_step = False
        from_step = 1
        all_responses = False
    args = chain_selection()
    args["conversation_name"] = st.session_state["conversation"]
    chain_name = args["chain"] if "chain" in args else ""
    user_input = args["input"] if "input" in args else ""
    if single_step and st.button("Run Chain Step") and chain_name:
        responses = ApiClient.run_chain_step(
            chain_name=chain_name,
            user_input=user_input,
            agent_name=agent_name,
            step_number=from_step,
            chain_args=args,
        )
        st.success(f"Chain '{chain_name}' executed.")
        st.write(responses)
    elif (
        single_step
        and st.button("Run Chain Step")
        and not chain_name
        or not single_step
        and st.button("Run Chain")
        and not chain_name
    ):
        st.error("Chain name is required.")
    elif (not single_step or st.button("Run Chain Step")) and (
        single_step or st.button("Run Chain")
    ):
        responses = ApiClient.run_chain(
            chain_name=chain_name,
            user_input=user_input,
            agent_name=agent_name,
            all_responses=all_responses,
            from_step=from_step,
            chain_args=args,
        )
        st.success(f"Chain '{chain_name}' executed.")
        st.write(responses)

