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

# Create season selector
ui.input_select(
    "season",
    "Season:",
    list(range(2023, 2025)),
)

# Create event selector
ui.input_select("event", "Events", {})

# Create a session selector
ui.input_select("session", "Sessions", {})

ui.input_checkbox_group(
    "data_options",
    "Data channels",
    {
        "session": "session",
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
@reactive.event(input.season, input.event, input.session, input.data_options)
def session_data():
    data_options = input.data_options()
    session = fastf1.get_session(int(input.season()), input.event(), input.session())
    session.load(
        telemetry="telemetry" in data_options,
        laps="laps" in data_options,
        weather="weather" in data_options,
        messages="messages" in data_options,
    )
    # session.load()
    return session


@reactive.effect
@reactive.event(input.season)
def update_events_select():
    season = season_data()
    season_events = season[season["EventFormat"]!="testing"]
    events = season_events["EventName"].to_list()
    #    ( season_events[["Country", "EventName"]]
    #    .set_index("Country")["EventName"]
    #    .to_dict() )

    ui.update_select("event", choices=events)


@reactive.effect
@reactive.event(input.event)
def update_sessions_select():
    event = fastf1.get_event(int(input.season()), input.event())
    session_names = [
        event[key]
        for key in event.index
        if key.startswith("Session")
        and not key.endswith("Date")
        and not key.endswith("DateUtc")
    ]
    ui.update_select("session", choices=session_names)


@reactive.effect
@reactive.event(input.session)
def update_laps_driver_select():
    session = session_data()
    laps_drivers = session.results["Abbreviation"].to_list()
    ui.update_select("laps_driver", choices=laps_drivers)


@reactive.effect
@reactive.event(input.session)
def update_fast_driver_select():
    session = session_data()
    fast_drivers = session.results["Abbreviation"].to_list()
    ui.update_select("fast_driver", choices=fast_drivers)


@reactive.effect
def _():
    print(f"Data options have changed to {input.data_options()}")


with ui.navset_card_underline():

    with ui.nav_panel("season"):

        @render.data_frame
        def season_frame():
            season = season_data()
            return render.DataGrid(season)

    with ui.nav_panel("event"):
        @render.ui
        def event_info():
            session = session_data()
            html = pd.DataFrame(session.event).to_html()
            return ui.HTML(html)

    with ui.nav_panel("session"):

        @render.ui
        def session_info():
            if "session" not in input.data_options():
                m = ui.modal(
                    "You must load 'session' data for this view.",
                    title="Data required",
                    easy_close=True,
                )
                ui.modal_show(m)
            else:
                session = session_data()
                html = pd.json_normalize(session.session_info).T.to_html()
                return ui.HTML(html)

    with ui.nav_panel("session_laps"):
        # Create driver selector
        ui.input_select(
            "laps_driver",
            "Driver:",
            {},
        )

        @render.data_frame
        def laps_frame():
            if "laps" not in input.data_options():
                m = ui.modal(
                    "You must load 'session' and 'laps' data for this view.",
                    title="Data required",
                    easy_close=True,
                )
                ui.modal_show(m)
            else:
                session = session_data()
                data = session.laps.pick_driver(input.laps_driver())
                return render.DataGrid(data)

    with ui.nav_panel("fastlap"):

        # Create fast driver selector
        ui.input_select(
            "fast_driver",
            "Driver:",
            {},
        )

        @render.plot(alt="A fast lap...")
        def fast_laps():
            if "telemetry" not in input.data_options():
                m = ui.modal(
                    "You must load 'session', 'laps' and 'telemetry' data for this view.",
                    title="Data required",
                    easy_close=True,
                )
                ui.modal_show(m)

            else:
                session = session_data()
                fast_driver = session.laps.pick_driver(input.fast_driver()).pick_fastest()

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
                ax.set_title(input.fast_driver())
                ax.legend()
                return ax
