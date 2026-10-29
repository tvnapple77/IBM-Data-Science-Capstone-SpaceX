"""SpaceX Launch Records Dashboard — IBM Data Science Capstone."""

from pathlib import Path

import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.express as px


# Load the dataset from the same folder as this application.
DATA_FILE = Path(__file__).resolve().parent / "spacex_launch_dash.csv"
spacex_df = pd.read_csv(DATA_FILE)
min_payload = float(spacex_df["Payload Mass (kg)"].min())
max_payload = float(spacex_df["Payload Mass (kg)"].max())

site_options = [{"label": "All Sites", "value": "ALL"}] + [
    {"label": site, "value": site}
    for site in sorted(spacex_df["Launch Site"].dropna().unique())
]

app = dash.Dash(__name__)
app.title = "SpaceX Launch Records Dashboard"

# TASK 1: dropdown; TASK 2: pie chart; TASK 3: range slider; TASK 4: scatter chart.
app.layout = html.Div(
    children=[
        html.H1(
            "SpaceX Launch Records Dashboard",
            style={"textAlign": "center", "color": "#503D36", "fontSize": "40px"},
        ),
        dcc.Dropdown(
            id="site-dropdown",
            options=site_options,
            value="ALL",
            placeholder="Select a Launch Site",
            clearable=False,
            searchable=True,
        ),
        html.Br(),
        dcc.Graph(id="success-pie-chart"),
        html.Br(),
        html.P("Payload range (Kg):"),
        dcc.RangeSlider(
            id="payload-slider",
            min=min_payload,
            max=max_payload,
            step=100,
            value=[min_payload, max_payload],
            marks={int(x): str(int(x)) for x in range(0, 10001, 2500)},
            tooltip={"placement": "bottom", "always_visible": False},
        ),
        html.Br(),
        dcc.Graph(id="success-payload-scatter-chart"),
    ],
    style={"margin": "24px"},
)


@app.callback(
    Output("success-pie-chart", "figure"),
    Input("site-dropdown", "value"),
)
def get_pie_chart(entered_site):
    if entered_site == "ALL":
        successful = spacex_df[spacex_df["class"] == 1]
        return px.pie(
            successful,
            names="Launch Site",
            title="Total Successful Launches by Site",
        )

    site_df = spacex_df[spacex_df["Launch Site"] == entered_site]
    counts = site_df["class"].value_counts().reindex([0, 1], fill_value=0)
    return px.pie(
        values=counts.values,
        names=["Failure", "Success"],
        title=f"Launch Outcomes for {entered_site}",
        color=["Failure", "Success"],
        color_discrete_map={"Failure": "#d65f5f", "Success": "#4b88d0"},
    )


@app.callback(
    Output("success-payload-scatter-chart", "figure"),
    Input("site-dropdown", "value"),
    Input("payload-slider", "value"),
)
def get_scatter_chart(entered_site, payload_range):
    if payload_range is None:
        payload_range = [min_payload, max_payload]
    low, high = payload_range
    filtered = spacex_df[
        spacex_df["Payload Mass (kg)"].between(low, high)
    ]
    if entered_site != "ALL":
        filtered = filtered[filtered["Launch Site"] == entered_site]

    fig = px.scatter(
        filtered,
        x="Payload Mass (kg)",
        y="class",
        color="Booster Version Category",
        hover_data=["Launch Site", "Flight Number"],
        title=("Payload vs. Launch Outcome — All Sites" if entered_site == "ALL"
               else f"Payload vs. Launch Outcome — {entered_site}"),
        labels={"class": "Launch Outcome (0=Failure, 1=Success)"},
    )
    fig.update_yaxes(tickmode="array", tickvals=[0, 1], ticktext=["Failure", "Success"])
    return fig


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8050)
