import pandas as pd

# import functools

# import requests_cache
# from requests_cache.session import CachedSession
import fastf1

from jupyterlite_simple_cors_proxy.fastf1_proxy import (
    enable_cors_proxy as fastf1_cors_proxy,
)

_ = fastf1_cors_proxy(
    domains=["api.formula1.com", "livetiming.formula1.com"],
    # debug=True,
    # By default, the proxy path is:
    # https://api.allorigins.win/raw?url=
    # Or we can specify our own:
    proxy_url="https://corsproxy.io/",
)

from shiny import render, reactive
from shiny.express import ui, input

from matplotlib import pyplot as plt
import fastf1
import fastf1.plotting

fastf1.plotting.setup_mpl(misc_mpl_mods=False, color_scheme="fastf1")

# Create dropdown widget
ui.input_select(
    "season",
    "Season:",
    list(range(2023, 2025)),
)

ui.input_action_button("refresh", "Refresh Plot"),

session = fastf1.get_session(2025, "Bahrain", "Q")
session.load(telemetry=False, laps=True, weather=False)

@reactive.event(input.refresh)
def refresh_plot():
    # Any logic you want to trigger on button click can go here
    return None


# Server logic
@render.text
def result():
    try:
        # Example FastF1 data fetch
        season = fastf1.get_event_schedule(int(input.season()))
        return (
            f"Successfully loaded {len(season)} races from the {input.season()} season"
        )
    except Exception as e:
        return f"Error loading data: {str(e)}"


@render.ui
def styled_table():
    session = fastf1.get_session(int(input.season()), "Bahrain", "Q")
    session.load(telemetry=False, laps=True, weather=False)

    data = session.laps.pick_driver("LEC")
    

    # Assuming df is your styled dataframe
    styled_html = data.head(3).style.to_html()
    return ui.HTML(styled_html)

# TO DO - how can we know when the data has loaded?
@render.plot(alt="A Seaborn histogram on penguin body mass in grams.")
def plot():
    session = fastf1.get_session(int(input.season()), "Bahrain", "Q")
    session.load(telemetry=False, laps=True, weather=False)

    fast_leclerc = session.laps.pick_driver("LEC").pick_fastest()

    lec_car_data = fast_leclerc.get_car_data()

    t = lec_car_data["Time"]
    vCar = lec_car_data["Speed"]

    # The rest is just plotting
    fig, ax = plt.subplots()
    ax.plot(t, vCar, label="Fast")
    ax.set_xlabel("Time")
    ax.set_ylabel("Speed [Km/h]")
    ax.set_title("Leclerc is")
    ax.legend()
    # plt.show()
    return ax
