import yaml
import matplotlib.pyplot as plt
import time
import numpy as np
from numba import jit
import streamlit as st
import pandas as pd

state = st.session_state
st.set_page_config(page_title="Martingale", layout="wide")


@jit(nopython=True)
def simulation(money_start, money_end, win_chance, start_bet):
    money = money_start
    bet = start_bet
    while money > 0 and money < money_end:
        # roll
        win = np.random.rand() <= win_chance
        
        # if win
        if win:
            money += bet
            bet = start_bet

        # if loss
        if not win:
            money -= bet
            bet *= 2
            # Clamp bet
            bet = bet if bet <= money else money 

    
    return money >= money_end

def run_simulations(goal_money):
    success = 0
    for i in range(state.n_sim):
        success += simulation(state.money_start, goal_money, state.win_chance/100, state.start_bet)
    return success / state.n_sim

        
if not 'init' in state:
    state.init = True

    with open("config.yaml", 'r') as stream:
        state.config = yaml.safe_load(stream)

    state.money_start = state.config["start_money"] 
    state.goal_increase_factor = state.config["goal_increase_factor"] 
    state.goal_increase_money = state.config["goal_increase_money"] 
    state.win_chance = state.config["win_chance"]
    state.start_bet = state.config["start_bet"] 
    state.n_sim = state.config["n_sim"] 

    state.fig, state.ax = plt.subplots()

def update_bar():
    state.fig, state.ax = plt.subplots()
    probs = {}
    # Show a progress bar
    progress_bar = st.progress(0)
    progress_text = st.empty()
    n_sims = len(state.goal_increase_money) + len(state.goal_increase_factor)
    n_sim_done = 0
    progress_text.text(f"Progress: {100*n_sim_done/n_sims:.0f} %")
    progress_bar.progress(n_sim_done/n_sims)

    # Calculate all the probabilities
    for goal_increase_money in state.goal_increase_money:
        goal_money = goal_increase_money + state.money_start
        if goal_money in probs:
            continue
        probs[goal_money] = run_simulations(goal_money)

        # progress bar
        n_sim_done +=1
        progress_text.text(f"Progress: {100*n_sim_done/n_sims:.0f} %")
        progress_bar.progress(n_sim_done/n_sims)


    for goal_increase_factor in state.goal_increase_factor:
        goal_money = goal_increase_factor * state.money_start
        if goal_money in probs:
            continue
        probs[goal_money] = run_simulations(goal_money)

        # progress bar
        n_sim_done +=1
        progress_text.text(f"Progress: {100*n_sim_done/n_sims:.0f} %")
        progress_bar.progress(n_sim_done/n_sims)
    
    progress_bar.empty()
    progress_text.empty()



    x_axis_vals = np.linspace(0, len(probs), num=len(probs))
    x_labels = np.round(list(probs.keys())).astype(int)
    state.ax.bar(x_axis_vals, list(probs.values()), tick_label=x_labels)
    state.ax.set_yticks(np.linspace(0, 1, num=21))


st.markdown("# Martingale simulator")
col1, col2, col3 = st.columns([2, 4, 2])

with col1:
    state.n_sim = int(st.text_input("Number of simulatons", value=state.n_sim))
    state.win_chance = float(st.text_input("Win chance", value=state.win_chance))
    state.money_start = int(st.text_input("Start money", value=state.money_start))
    state.start_bet = int(st.text_input("Start bet", value=state.start_bet))
    
    new_increase_money = int(st.text_input("Add money goal", value=1))
    if not new_increase_money in state.goal_increase_money:
        state.goal_increase_money.append(new_increase_money)

    new_increase_factor = float(st.text_input("Add money factor goal", value=2))
    if not new_increase_factor in state.goal_increase_factor:
        state.goal_increase_factor.append(new_increase_factor)

    # st.write(f"state.goal_increase_money: {state.goal_increase_money}")
    # money = st.selectbox("Remove a goal money increase", state.goal_increase_money)
    # remove = st.button("remove")
    # if remove:
    #     state.goal_increase_money.remove(money)
    # st.write(f"remove:{remove}, money: {money}")
    # st.write(f"money_increase_goal: {state.goal_increase_money}")

    sim = st.button("Simulate")

with col2:
    if sim:
        update_bar()
    st.pyplot(state.fig)












