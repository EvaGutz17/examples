import numpy as np
import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output

from ..data.loader import DataSchema
from . import ids


def render(app: Dash, data: pd.DataFrame) -> html.Div:
    all_years: list[str] = data[DataSchema.YEAR].tolist()
    all_months: list[str] = data[DataSchema.MONTH].tolist()
    unique_categories: list[str] = sorted(set(data[DataSchema.CATEGORY].tolist()))

    @app.callback(
        Output(ids.CATEGORY_DROPDOWN, "value"),
        [
            Input(ids.YEAR_DROPDOWN, "value"),
            Input(ids.MONTH_DROPDOWN, "value"),
            Input(ids.SELECT_ALL_CATEGORIES_BUTTON, "n_clicks"),
        ],
    )
    def select_all_categories(years: list[str], months: list[str], _: int) -> list[str]:
        year_mask = np.isin(all_years, all_years if years is None else years)
        month_mask = np.isin(all_months, all_months if months is None else months)
        mask = year_mask & month_mask
        filtered_data = data.loc[mask]
        return sorted(set(filtered_data[DataSchema.CATEGORY].tolist()))

    return html.Div(
        children=[
            html.H6("Category"),
            dcc.Dropdown(
                id=ids.CATEGORY_DROPDOWN,
                options=[
                    {"label": category, "value": category}
                    for category in unique_categories
                ],
                value=unique_categories,
                multi=True,
                placeholder="Select",
            ),
            html.Button(
                className="dropdown-button",
                children=["Select All"],
                id=ids.SELECT_ALL_CATEGORIES_BUTTON,
                n_clicks=0,
            ),
        ],
    )
