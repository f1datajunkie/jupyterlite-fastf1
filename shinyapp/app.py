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

ui.input_checkbox_group(
    "data_options",
    "Data channels",
    {
        "laps": "laps",
        "telemetry": "telemetry",
        "weather": "weather",
        "messages": "messages",
    },
)
# ui.input_action_button("relad_data", "Reload data")
# ui.input_action_button("refresh_session", "Refresh session")


@reactive.calc
def season_data():
    # Example FastF1 data fetch
    season = fastf1.get_event_schedule(int(input.season()))
    return season


@reactive.calc
def session_data():
    data_options = input.data_options()
    session = fastf1.get_session(int(input.season()), "Bahrain", "Q")
    session.load(
        telemetry="telemetry" in data_options,
        laps="laps" in data_options,
        weather="weather" in data_options,
        messages="messages" in data_options,
    )
    # session.load()
    return session


@reactive.effect
def _():
    print(f"Data options have changed to {input.data_options()}")


with ui.navset_card_underline():

    with ui.nav_panel("season"):

        @render.ui  
        def season_frame():
            season = season_data()
            styled_html = season.head(3).style.to_html()
            return ui.HTML(styled_html)

    with ui.nav_panel("session"):

        @render.ui
        def laps_frame():
            if "laps" not in input.data_options():
                return ui.HTML("<div><em>You must load <tt>laps</tt> data for this view.</em></div>")
            else:
                session = session_data()
                data = session.laps.pick_driver("LEC")
                styled_html = data.head(3).style.to_html()
                return ui.HTML(styled_html)

    with ui.nav_panel("fastlap"):

        @render.plot(alt="A fast lap...")
        def fast_laps():
            if "telemetry" not in input.data_options():
                return ui.HTML("<div><em>You must load <tt>laps<.<tt>telemetry</tt> data for this view.</em></div>")
            else:
                session = session_data()
                fast_driver = session.laps.pick_driver("LEC").pick_fastest()

                # data = fast_driver.get_car_data()
                # styled_html = data.head(3).style.to_html()
                # return ui.HTML(styled_html)
                fast_data = fast_driver.get_car_data()
                t = fast_data["Time"]
                vCar = fast_data["Speed"]

                # The rest is just plotting
                fig, ax = plt.subplots()
                ax.plot(t, vCar, label="Fast")
                ax.set_xlabel("Time")
                ax.set_ylabel("Speed [Km/h]")
                ax.set_title("Leclerc")
                ax.legend()
                return ax
