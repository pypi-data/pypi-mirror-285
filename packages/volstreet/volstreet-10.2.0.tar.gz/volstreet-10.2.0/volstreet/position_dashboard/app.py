from dash import html, dcc, Dash, Input, Output
from volstreet.angel_interface.interface import fetch_book
from volstreet.strategies.monitoring import get_current_state_of_strategy
from volstreet.position_dashboard.formatting import generate_table

# Initialize the app
app = Dash(__name__)

# Define the layout
app.layout = html.Div(
    [
        html.Div(
            children=[
                html.Label("Index"),
                dcc.Dropdown(
                    id="index",
                    options=[
                        {"label": i.capitalize(), "value": i.upper()}
                        for i in [
                            "nifty",
                            "banknifty",
                            "finnifty",
                            "midcpnifty",
                            "sensex",
                        ]
                    ],
                    placeholder="Index",
                ),
                html.Br(),
                html.Label("Strategy"),
                dcc.Dropdown(
                    id="strategy",
                    options=[
                        {"label": i.capitalize(), "value": i}
                        for i in ["delta", "trend"]
                    ],
                    placeholder="Strategy",
                ),
                html.Br(),
                html.Div(id="output_table"),
            ],
        )
    ]
)


@app.callback(
    Output("output_table", "children"),
    Input("index", "value"),
    Input("strategy", "value"),
)
def update_table(index, strategy):
    if not index or not strategy:
        return "Please select both an index and a strategy."
    book = fetch_book("orderbook")
    df = get_current_state_of_strategy(book, index, strategy)
    if df.empty:
        return "No data available for the selected index and strategy."
    return generate_table(df)


if __name__ == "__main__":
    app.run(debug=True)
