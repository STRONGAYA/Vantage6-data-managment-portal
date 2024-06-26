import copy
import io


import numpy as np
import pandas as pd
import plotly.graph_objects as go

from collections import defaultdict
from dash import dash_table
from dash import html
from datetime import datetime


def fetch_field_count(descriptive_data, field_name="country", text='countr'):
    """
    Function to fetch the count of unique fields from the descriptive data.

    This function takes in a dictionary of descriptive data, finds the latest data entry based on the keys
    (assumed to be timestamps), and returns a list containing the count of unique fields in the latest data, a line break,
    and the provided text (default is "countr") with 'ies' added if the count is more than 1, else 'y' is added.

    Parameters:
    descriptive_data (dict): The descriptive data to fetch the count of unique fields from. Each key is a timestamp,
                             and each value is a dictionary containing the data fetched at that timestamp.
    field_name (str, optional): The field name to count unique values for. Defaults to "country".
    text (str, optional): The text to return along with the count of unique fields. Defaults to "countr".

    Returns:
    list: A list containing the count of unique fields in the latest data, a line break, and the provided text with 'ies'
          added if the count is more than 1, else 'y' is added.
    """
    if descriptive_data:
        latest_data = descriptive_data[max(descriptive_data.keys())]
        num_countries = len({data[f"{field_name}"] for data in latest_data.values()})
        return [f"{num_countries}", html.Br(), f"{text}{'ies' if num_countries > 1 else 'y'}"]


def fetch_number_of_keys(descriptive_data, text='organisation'):
    """
    Function to fetch the number of keys from the descriptive data.

    This function takes in a dictionary of descriptive data, finds the latest data entry based on the keys
    (assumed to be timestamps), and returns a list containing the number of keys in the latest data, a line break,
    and the provided text (default is "organisation") with an 's' added if the number of keys is more than 1.

    Parameters:
    descriptive_data (dict): The descriptive data to fetch the number of keys from. Each key is a timestamp,
                             and each value is a dictionary containing the data fetched at that timestamp.
    text (str, optional): The text to return along with the number of keys. Defaults to "organisation".

    Returns:
    list: A list containing the number of keys in the latest data, a line break, and the provided text with an 's'
          added if the number of keys is more than 1.
    """
    if descriptive_data:
        latest_data = descriptive_data[max(descriptive_data.keys())]
        return [f"{len(latest_data)}", html.Br(), f"{text}{'s' if len(latest_data) > 1 else ''}"]


def fetch_total_sample_size(descriptive_data, text="AYA"):
    """
    Function to fetch the total sample size from the descriptive data.

    This function takes in a dictionary of descriptive data,
    finds the latest data entry based on the keys (assumed to be timestamps),
    and sums up the "sample_size" field from each data entry in the latest data.
    It then returns a list containing the total sample size, a line break,
    and the provided text (default is "AYA") with an 's' added if the total sample size is more than 1.

    Parameters:
    descriptive_data (dict): The descriptive data to fetch the sample size from. Each key is a timestamp,
    and each value is a dictionary containing the data fetched at that timestamp.
    text (str, optional): The text to return along with the total sample size. Defaults to "AYA".

    Returns:
    list: A list containing the total sample size, a line break, and the provided text with an 's' added
            if the total sample size is more than 1.
    """
    if descriptive_data:
        latest_data = descriptive_data[max(descriptive_data.keys())]
        num_patients = sum(int(data["sample_size"]) for data in latest_data.values())
        return [f"{num_patients}", html.Br(), f"{text}{'s' if num_patients > 1 else ''}"]


def generate_sample_size_horizontal_bar(descriptive_data, text="AYA"):
    """
    Function to generate a horizontal bar chart of sample sizes per organisation.

    This function takes in a dictionary of descriptive data, finds the latest data entry based on the keys
    (assumed to be timestamps), and generates a horizontal bar chart showing the sample sizes per organisation.
    The bar chart includes annotations showing the sample size for each organisation and
    the proportion of the total sample size that this represents.

    Parameters:
    descriptive_data (dict): The descriptive data to generate the bar chart from. Each key is a timestamp,
                             and each value is a dictionary containing the data fetched at that timestamp.
    text (str, optional): The text to use in the bar chart title and hovertemplate. Defaults to "AYA".

    Returns:
    dict: A dictionary representing the figure for the bar chart.
    This includes the data for the bars and the layout of the chart.
    """
    if descriptive_data:
        # Get the latest data
        latest_data = descriptive_data[max(descriptive_data.keys())]

        # Calculate the sample sizes and their proportions
        sample_sizes = [int(data["sample_size"]) for data in latest_data.values()]
        total_sample_size = sum(sample_sizes)
        proportions = [round((size / total_sample_size), ndigits=2) for size in sample_sizes]

        # Get the sorted list of organisations
        organisations = sorted(latest_data.keys())

        # Create the data for the bar chart
        data = [
            dict(
                x=[proportions[i]],
                y=[f'Number of {text}s per organisation'],
                name=org,
                type='bar',
                orientation='h',
                marker=dict(line=dict(width=0)),
                hovertemplate=(
                    f"{org} has made data of {sample_sizes[i]} {text}{'s' if sample_sizes[i] > 1 else ''} available, "
                    f"which is {proportions[i] * 100:.2f}% of all available {text} data."
                )
            )
            for i, org in enumerate(organisations)
        ]

        # Create the annotations for the bar chart
        annotations = [
            dict(
                x=(sum(proportions[:i + 1]) - proportions[i] / 2),
                y=0,
                text=str(sample_sizes[i]),
                showarrow=False,
                font=dict(color='white')
            )
            for i in range(len(organisations))
        ]

        # Define the figure
        figure = {
            'data': data,
            'layout': {
                'title': f'Number of {text}s per organisation',
                'barmode': 'stack',
                'yaxis': {'visible': False},
                'xaxis': {
                    'tickformat': ',.0%',
                    'visible': False,
                },
                'legend': {
                    'orientation': 'h',
                    'traceorder': 'normal',
                    'yanchor': 'center',
                    'y': 0,
                    'xanchor': 'center',
                    'x': 0.48,
                },
                'height': 100,
                'margin': dict(l=45, r=0, t=35, b=25),
                'annotations': annotations
            }
        }
        return figure


def generate_fair_data_availability(global_schema_data, descriptive_data, text="AYA"):
    """
    Function to generate a DataFrame and a list of tooltips for FAIR data availability.

    This function takes in a dictionary of global schema data, a dictionary of descriptive data, and a string text.
    It processes the data to generate a DataFrame and a list of tooltips, which are then used to create a Dash DataTable.

    Parameters:
    global_schema_data (dict): The global schema data to process. Each key is a variable name,
    and each value is a dictionary containing information about the variable.
    descriptive_data (dict): The descriptive data to process. Each key is a timestamp,
    and each value is a dictionary containing the data fetched at that timestamp.
    text (str, optional): The text to use in the tooltips. Defaults to "AYA".

    Returns:
    dash_table.DataTable: The created Dash DataTable.
    """
    df_rows = []
    tooltips = []  # Initialize tooltips as a list
    # prefixes for replacement purposes; TODO move to global schema json
    prefixes = {"ncit": "http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#",
                "sct": "http://snomed.info/sct"}

    variable_info = global_schema_data.get('variable_info')
    if variable_info is None:
        variable_info = {}

    # Find the most recent timestamp
    most_recent_timestamp = max(descriptive_data.keys(), key=lambda x: datetime.fromisoformat(x))

    # Select the data associated with the most recent timestamp
    descriptive_data_most_recent = descriptive_data[most_recent_timestamp]

    # Get the list of organizations from the descriptive data
    organizations = list(descriptive_data_most_recent.keys())

    _variable_info = copy.deepcopy(variable_info)
    for key, info in _variable_info.items():
        # Replace the prefix in the 'class' field
        for prefix, uri in prefixes.items():
            if prefix + ":" in info['class']:
                info['class'] = info['class'].replace(prefix + ":", uri)
                break

        # Replace the prefix in the 'value_mapping' field
        value_mapping = info.get('value_mapping', {})
        if value_mapping:
            for mapping, target_info in value_mapping.get('terms', {}).items():
                for prefix, uri in prefixes.items():
                    if prefix + ":" in target_info['target_class']:
                        target_info['target_class'] = target_info['target_class'].replace(prefix + ":", uri)
                        break

    # For each key and class in the 'variable_info' field, create a row
    for variable in variable_info.keys():
        org_variable_info = {}

        for organisation in organizations:
            try:
                _org_variable_info = [local_variable_info for local_variable_info in
                                      descriptive_data_most_recent[organisation]['variable_info'] if
                                      local_variable_info.get('main_class') == _variable_info[variable].get("class")]
            except KeyError:
                _org_variable_info = [{'main_class': '', 'main_class_count': 0,
                                       'sub_class': '', 'sub_class_count': 0}]

            org_variable_info[organisation] = _org_variable_info

        # Compute the total count
        total_count = 0
        for info_list in org_variable_info.values():
            for info in info_list:
                if info.get('main_class') == _variable_info[variable].get("class") and info.get('sub_class') == \
                        _variable_info[variable].get("class"):
                    total_count += info.get('main_class_count', 0)

        row = {
            'Variables': variable.replace('_', ' ').title(),
            'Values': '',
            f'Total {text}s': total_count,  # Include the total count in the row
        }

        # Create a tooltip row for each row
        org_data = [f'{org}: __{info_list[0].get("main_class_count", 0)}__' for org, info_list in
                    org_variable_info.items()
                    if
                    any(info.get('main_class') == _variable_info[variable].get("class") and info.get('sub_class') == \
                        _variable_info[variable].get("class") for info in info_list)]

        if org_data:
            org_data = (f'__{variable.replace("_", " ").title()}__  \n'
                        f'Available {text} data per organisation  \n') + '  \n'.join(org_data)
        else:
            org_data = (f'No {text}s with information on __{variable.replace("_", " ")}__ '
                        f'appear to be available.')

        tooltip_row = {
            'Variables': f'__{variable.replace("_", " ").title()}__  \n'
                         f'Associated class: {_variable_info[variable].get("class")}',
            'Values': '',
            f'Total {text}s': org_data
        }

        # Replace the full URI with a prefix in the tooltip
        for prefix, uri in prefixes.items():
            if uri in tooltip_row['Variables']:
                tooltip_row['Variables'] = tooltip_row['Variables'].replace(uri, prefix + ":")
                break

        for organisation, info_list in org_variable_info.items():
            if info_list:
                for info in info_list:
                    if info.get('main_class') == _variable_info[variable].get("class") and info.get('sub_class') == \
                            _variable_info[variable].get("class"):
                        row[organisation] = int(info.get('main_class_count', 0))
                        tooltip_row[
                            organisation] = (f'__{info.get("main_class_count", 0)}__ {text}s in {organisation} '
                                             f'have information on __{variable.replace("_", " ")}__.')
                        break
                    else:
                        row[organisation] = 0
                        tooltip_row[
                            organisation] = (f'Data for __{variable.replace("_", " ")}__ '
                                             f'appears unavailable for {organisation}.')
            else:
                row[organisation] = 0
                tooltip_row[
                    organisation] = f'Data for __{variable.replace("_", " ")}__ appears unavailable for {organisation}.'

        # Append the row and tooltip row to the list of rows and tooltips
        df_rows.append(row)
        tooltips.append(tooltip_row)

        # Replace the prefix in the 'value_mapping' field
        value_mapping = _variable_info[variable].get('value_mapping', {})
        if value_mapping:
            for value, value_info in value_mapping.get('terms', {}).items():
                # Compute the total count
                total_count = 0

                # go through the results
                for info_list in org_variable_info.values():
                    for info in info_list:
                        if info.get('main_class') == _variable_info[variable].get("class") and info.get('sub_class') == \
                                value_info.get("target_class"):
                            total_count += info.get('sub_class_count', 0)

                row = {
                    'Variables': '',
                    'Values': value.replace('_', ' ').title(),
                    f'Total {text}s': total_count,  # Include the total count in the row
                }

                # Create a tooltip row for each row
                org_data = [f'{org}: __{info.get("sub_class_count", 0)}__' for org, info_list in
                            org_variable_info.items()
                            for info in info_list if info.get('main_class') == _variable_info[variable].get("class")
                            and info.get('sub_class') == value_info.get("target_class")]

                if org_data:
                    org_data_str = (f'{variable.replace("_", " ").title()} - __{value.replace("_", " ").title()}__  \n'
                                    f'Available {text} data per organisation  \n') + '  \n'.join(org_data)
                else:
                    org_data_str = (f'No {text}s with __{value.replace("_", " ")}__ for {variable.replace("_", " ")} '
                                    f'appear to be available.')

                tooltip_row = {
                    'Variables': '',
                    'Values': f'{variable.replace("_", " ").title()} - __{value.replace("_", " ").title()}__  \n'
                              f'Associated class: {value_info.get("target_class")}',
                    f'Total {text}s': org_data_str
                }

                # Replace the full URI with a prefix in the tooltip
                for prefix, uri in prefixes.items():
                    if uri in tooltip_row['Values']:
                        tooltip_row['Values'] = tooltip_row['Values'].replace(uri, prefix + ":")
                        break

                for organisation, info_list in org_variable_info.items():
                    if info_list:
                        for info in info_list:
                            if info.get('main_class') == _variable_info[variable].get("class") and info.get(
                                    'sub_class') == value_info.get("target_class"):
                                row[organisation] = int(info.get('sub_class_count', 0))
                                tooltip_row[
                                    organisation] = (f'__{info.get("sub_class_count", 0)}__ {text}s '
                                                     f'in {organisation} have __{value.replace("_", " ")}__ '
                                                     f'as {variable.replace("_", " ")}.')
                                break
                            else:
                                row[organisation] = 0
                                tooltip_row[
                                    organisation] = (f'No {text}s that have __{value.replace("_", " ")}__ '
                                                     f'as {variable.replace("_", " ")} '
                                                     f'appear available in {organisation}.')
                    else:
                        row[organisation] = 0
                        tooltip_row[
                            organisation] = (f'No {text}s that have __{value.replace("_", " ")}__ '
                                             f'as {variable.replace("_", " ")} '
                                             f'appear available in {organisation}.')

                # Append the row and tooltip row to the list of rows and tooltips
                df_rows.append(row)
                tooltips.append(tooltip_row)

    # Convert the list of rows to a DataFrame
    df = pd.DataFrame(df_rows)

    # Create a new DataFrame for display purposes
    display_df = df.copy()
    for col in display_df.columns[3:]:
        display_df[col] = display_df[col].apply(lambda x: '✔' if x > 0 else '✖')

    return df, create_data_table(display_df, tooltips)


def create_data_table(df, tooltips):
    """
    Function to create a Dash DataTable.

    This function takes a pandas DataFrame and a list of tooltips as input, and returns a Dash DataTable.
    The DataTable includes several styles for the table, cells, data, and header,
    as well as conditional styles for the data.
    The tooltips are added to the DataTable based on the input list of tooltips.

    Parameters:
    df (pandas.DataFrame): The DataFrame to convert into a DataTable.
    tooltips (list): A list of tooltips to add to the DataTable.
    Each tooltip is a dictionary where the keys are column names and the values are the tooltip texts.

    Returns:
    dash_table.DataTable: The created Dash DataTable.
    """
    _style_table = {'height': '450px', 'overflowY': 'auto', 'max-width': '100%', 'width': '100%', 'overflowX': 'auto'}
    _style_cell = {'fontSize': '14px', 'border': 'none', 'padding': '0px 15px 0px 0px', 'width': '{}%',
                   'textOverflow': 'ellipsis', 'overflow': 'hidden'}
    _style_data = {'border': 'none'}
    _style_header = {'position': 'sticky', 'top': 0, 'backgroundColor': '#ffffff', 'fontWeight': 'bold'}

    data_table = dash_table.DataTable(
        id='table-data-availability',
        columns=[{"name": i, "id": i} for i in df.columns],
        data=df.to_dict('records'),
        style_table=_style_table,
        style_cell={**_style_cell, 'width': '{}%'.format(100 / len(df.columns))},
        style_data=_style_data,
        style_header=_style_header,
        style_data_conditional=[
            {'if': {'column_id': col, 'filter_query': '{' + col + '} eq "' + symbol + '"'}, 'color': color}
            for col in df.columns[3:] for symbol, color in [('✔', 'green'), ('✖', 'red')]
        ],
        tooltip_data=[
            {column: {'value': str(tooltip[column]), 'type': 'markdown'}
            if column in tooltip else None for column in df.columns}
            for tooltip in tooltips
        ],
        fixed_columns={'headers': True, 'data': 2},
        tooltip_duration=None
    )
    return data_table


def generate_donut_chart(descriptive_data, text="AYA", chart_type="organisation"):
    """
    Function to generate a donut chart of sample sizes per organisation or AYAs per country.

    This function takes in a dictionary of descriptive data, finds the latest data entry based on the keys
    (assumed to be timestamps), and generates a donut chart showing the sample sizes per organisation or AYAs per country.
    The donut chart includes annotations showing the sample size for each organisation or country and
    the proportion of the total sample size that this represents.

    Parameters:
    descriptive_data (dict): The descriptive data to generate the donut chart from. Each key is a timestamp,
                             and each value is a dictionary containing the data fetched at that timestamp.
    text (str, optional): The text to use in the donut chart title and hovertemplate. Defaults to "AYA".
    chart_type (str, optional): The type of chart to generate.
    Can be "organisation" or "country". Defaults to "organisation".

    Returns:
    dict: A dictionary representing the figure for the donut chart.
    This includes the data for the donut chart and the layout of the chart.
    """
    if descriptive_data:
        latest_data = descriptive_data[max(descriptive_data.keys())]

        if chart_type == "organisation":
            labels = sorted(latest_data.keys())
            sample_sizes = [int(data["sample_size"]) for data in latest_data.values()]
            title = f'{text}s per organisation'
        elif chart_type == "country":
            country_data = defaultdict(int)
            for data in latest_data.values():
                country_data[data["country"]] += int(data["sample_size"])
            labels, sample_sizes = zip(*sorted(country_data.items()))
            title = f'{text}s per country'

        data = [
            dict(
                labels=labels,
                values=sample_sizes,
                type='pie',
                hole=.56,
                name='',
                hovertemplate=(
                    f"<b>%{{label}}</b><br>Available {text} data: <b>%{{value}}</b><br>"
                    f"Proportion of all available {text} data: <b>%{{percent}}</b>"
                )
            )
        ]

        figure = go.Figure(data=data)

        figure.update_layout(
            title=title,
            hoverlabel=dict(font_family='Poppins, sans-serif'),
            font=dict(family='Poppins, sans-serif'),
            legend=dict(
                orientation='h',
                yanchor='top',
                y=0,
                xanchor='center',
                x=0.5,
            ),
        )

        return figure


def generate_completeness_chart(availability_data, text="AYA"):
    """
    Function to generate a completeness chart.

    This function takes in a DataFrame of data availability, calculates the completeness of the data,
    and generates a completeness chart showing the completeness of the data.
    The completeness chart includes annotations showing the completeness for each organisation and
    the proportion of the total completeness that this represents.

    Parameters:
    df (pandas.DataFrame): The DataFrame of data availability to generate the completeness chart from.
    text (str, optional): The text to use in the completeness chart title and hovertemplate. Defaults to "AYA".

    Returns:
    dict: A dictionary representing the figure for the completeness chart.
    This includes the data for the completeness chart and the layout of the chart.
    """
    # Convert the input data to a DataFrame
    initial_df = pd.read_json(io.StringIO(availability_data), orient='split')
    _initial_df_copy = initial_df.copy()

    # Create a DataFrame that contains the variable counts per organisation
    available_variable_counts_df = _initial_df_copy[_initial_df_copy['Variables'] != '']
    available_variable_counts_df = available_variable_counts_df.drop('Values', axis=1)

    # Create a DataFrame that contains the sum of the value counts per organisation
    # Fill forward the 'Variables' column in the DataFrame
    initial_df['Variables'] = initial_df['Variables'].replace('', np.nan).ffill()

    unavailable_df = pd.DataFrame()
    for column in initial_df.columns[2:]:
        column_counts = initial_df[initial_df['Values'] != ''].groupby('Variables')[column].sum().reset_index()

        if unavailable_df.empty:
            unavailable_df = column_counts
        else:
            unavailable_df = unavailable_df.join(column_counts.set_index('Variables'), on='Variables', rsuffix='_r')

    # Calculate the difference; i.e. how much missing information is there
    unavailable_df = unavailable_df.set_index('Variables').subtract(available_variable_counts_df.set_index('Variables'),
                                                                    fill_value=0).reset_index()

    # Set positive differences to 0 and make negative differences positive
    unavailable_df[unavailable_df.columns[1:]] = unavailable_df[unavailable_df.columns[1:]].clip(upper=0).abs()

    # Calculate the difference; i.e. how much usable information is there
    available_variable_counts_df = available_variable_counts_df.set_index('Variables').subtract(
        unavailable_df.set_index('Variables'), fill_value=0).reset_index()

    # Rename the columns
    unavailable_df = unavailable_df.rename(
        columns={f'Total {text}s': f'Total unavailable {text}s'})
    available_variable_counts_df = available_variable_counts_df.rename(
        columns={f'Total {text}s': f'Total available {text}s'})

    # Merge the dataframes on 'Variables' column
    visualisation_df = unavailable_df.merge(available_variable_counts_df[['Variables', f'Total available {text}s']],
                                            on='Variables',
                                            how='left')

    # Get the list of columns to drop
    columns_to_drop = visualisation_df.columns.difference(
        ['Variables', f'Total available {text}s', f'Total unavailable {text}s'])

    # Drop the columns
    visualisation_df = visualisation_df.drop(columns=columns_to_drop)

    # Convert 'Total available AYAs' and 'Total unavailable AYAs' columns to integer
    visualisation_df[f'Total available {text}s'] = visualisation_df[f'Total available {text}s'].astype(int)
    visualisation_df[f'Total unavailable {text}s'] = visualisation_df[f'Total unavailable {text}s'].astype(int)

    # Create a dictionary mapping each organisation to its (un)available count
    unavailable_counts = unavailable_df.set_index('Variables').to_dict()
    available_counts = available_variable_counts_df.set_index('Variables').to_dict()

    # Create the figure
    fig = go.Figure(data=[
        go.Bar(
            name='Complete information',
            x=visualisation_df['Variables'],
            y=visualisation_df[f'Total available {text}s'],
            width=0.5,
            hovertemplate=[
                f"<extra></extra><b>{row['Variables']}</b><br>"
                f"Total complete information: <b>{int(row[f'Total available {text}s'])}</b> {text}s<br><br>"
                f"Share per organisation<br>" + "<br>".join(
                    f"{org}: <b>{int(available_counts[org][row['Variables'].title()])}</b>"
                    for org in available_variable_counts_df.columns[2:]  # Iterate over the organisations
                )
                for index, row in visualisation_df.iterrows()
            ]
        ),
        go.Bar(
            name='Incomplete information',
            x=visualisation_df['Variables'],
            y=visualisation_df[f'Total unavailable {text}s'],
            width=0.5,
            # <extra> represents the trace's tag next to the tooltip, which we set to an empty string here
            hovertemplate=[
                f"<extra></extra><b>{row['Variables']}</b><br>"
                f"Total incomplete information: <b>{int(row[f'Total unavailable {text}s'])}</b> {text}s<br><br>"
                f"Share per organisation<br>" + "<br>".join(
                    f"{org}: <b>{int(unavailable_counts[org][row['Variables'].title()])}</b>"
                    for org in unavailable_df.columns[2:]  # Iterate over the organisations
                )
                for index, row in visualisation_df.iterrows()
            ]
        )
    ])

    # Update the layout of the figure
    fig.update_layout(
        hoverlabel=dict(font_family='Poppins, sans-serif'),
        barmode='stack',
        font=dict(family='Poppins, sans-serif'),
        plot_bgcolor='rgba(0,0,0,0)',
        width=1100,
        height=400,
        margin=dict(l=20, r=20, t=20, b=20),
        legend=dict(
            yanchor="top",
            y=-0.3,
            xanchor="center",
            x=0.5,
            orientation="h"
        ),
        yaxis_title=f"Total number of {text}s",
    )

    return fig
