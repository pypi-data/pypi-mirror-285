import pandas as pd
from xurpas_data_quality.render.renderer import HTMLBase, HTMLContainer, HTMLTable, HTMLPlot
from xurpas_data_quality.data.descriptions import TableDescription
from xurpas_data_quality.render.render_sections import render_variables_section, render_correlation_section, render_interactions_section, render_dropdown_section
from xurpas_data_quality.visuals import plot_to_base64, create_missing_bar_plot

def render_error(data:pd.DataFrame, data_invalid:pd.DataFrame, errors:list , name:str, is_empty:bool, minimal:bool):
    total_rows = data.dataset_statistics['dataset_length'] + data_invalid.dataset_statistics['dataset_length']
    errors_stats = {
        'Valid Data Ingested (# of Rows)': data.dataset_statistics['dataset_length'],
        'Valid Data Ingested (% Percentage)': "{:0.2f}%".format((data.dataset_statistics['dataset_length']/total_rows)*100),
        'Invalid Data Ingested (# of Rows)': data_invalid.dataset_statistics['dataset_length'],
        'Invalid Data Ingested (% Percentage)': "{:0.2f}%".format((data_invalid.dataset_statistics['dataset_length']/total_rows)*100),
        'Total Rows for Dataset': total_rows
    }


    sample_errors_section = HTMLContainer(
        type="default",
        name="Invalid Ingested Data",
        id ="sample-errors",
        container_items=[
            HTMLTable(
                id = "sample",
                data=data_invalid.df.to_html(classes="table table-sm", border=0, index=False, justify='left')
            )
        ]
    )

    errors_list = HTMLContainer(
            type="default",
            name="Errors",
            id = "list-errors",
            container_items=[
                HTMLTable(
                    id = "errors",
                    data = errors
                )
            ]
        )
    
    errors_info = HTMLContainer(
        type="default",
        id = "info-errors",
        name="Error Overview",
        container_items=[
            HTMLContainer(type="default",
                          container_items=[]),
            HTMLTable(
                name="Errors Overview",
                data = errors_stats
            )
        ]
    )

    errors_section = HTMLContainer(
        type="box",
        name="Errors during Ingestion",
        id = "errors_section",
        container_items=[
            HTMLContainer(
                type="tabs",
                container_items=[errors_info,errors_list, sample_errors_section]
            )
        ]
    )

 
    return errors_section
