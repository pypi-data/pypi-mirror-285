import pandas as pd

from xurpas_data_quality.data.descriptions import TableDescription
from xurpas_data_quality.render.renderer import HTMLBase, HTMLContainer, HTMLTable
from xurpas_data_quality.config import Settings

def render_compare(data: TableDescription, name:str):
    
    config = {'color_list': Settings().colors.base_colors}

    headers = [f"Table {i+1}" for i in range(len(data))]
    distinct_count_list = []
    value_count_list = []
    shared_values_list = []
    variable_types_list = []
    num_variables_list = []
    missing_cells_list = []
    missing_cells_perc_list = []
    duplicate_rows_list = []
    duplicate_rows_perc_list = []

    for datum in data:
        distinct_count_list.append(datum.comparison['distinct_count'])
        value_count_list.append(datum.comparison['value_count'])
        shared_values_list.append(datum.shared_values)
        variable_types_list.append(datum.variable_types)
        num_variables_list.append(datum.dataset_statistics['num_variables'])
        missing_cells_list.append(datum.dataset_statistics['missing_cells'])
        missing_cells_perc_list.append("{:0.2f}%".format(datum.dataset_statistics['missing_cells_perc']))
        duplicate_rows_list.append(datum.dataset_statistics['duplicate_rows'])
        duplicate_rows_perc_list.append("{:0.2f}%".format(datum.dataset_statistics['duplicate_rows_perc']))

    combined_data = {
        'Distinct Values (Count)': distinct_count_list,
        'Values (Count)': value_count_list,
        'Values Shared Between Tables': shared_values_list
    }

    dataset_statistics = {
        'Number of Variables': num_variables_list,
        'Missing Cells': missing_cells_list,
        'Missing Cells (%)': missing_cells_perc_list,
        'Duplicate Rows': duplicate_rows_list,
        'Duplicate Rows (%)': duplicate_rows_perc_list 
    }

    variable_types_statistics = {}
    for key in set().union(*variable_types_list):
        variable_types_statistics[key] = [0] * len(variable_types_list)

    for i, d in enumerate(variable_types_list):
        for key, value in d.items():
            variable_types_statistics[key][i] = value

    column_comparison = HTMLContainer(
            type="box",
            name = "Comparison",
            container_items=[
                HTMLTable(
                    id = "comparison",
                    name = 'Comparing the "Volume" Column',
                    data = combined_data,
                    headers = headers,
                    config = config
                )
            ]
        )
    
    overview_section = HTMLContainer(
        type="box",
        name="Overview",
        container_items = [
            HTMLContainer(
                type="column",
                container_items = HTMLTable(
                    id = "comparison",
                    name = "Overview of Data",
                    data = dataset_statistics,
                    headers = headers,
                    config = config
                )
            ),
            HTMLContainer(
                type="column",
                container_items = HTMLTable(
                    id = "comparison",
                    name = "Overview of Variables",
                    data = variable_types_statistics,
                    headers = headers,
                    config = config
                )
            )
        ]
    )

    content = [
        column_comparison,
        overview_section
    ]
    body = HTMLContainer(type="sections",
                         container_items = content)

    if name is not None:
        return HTMLBase(
            body=body,
            name=name
        )
    
    else:
        return HTMLBase(
            body=body
        )