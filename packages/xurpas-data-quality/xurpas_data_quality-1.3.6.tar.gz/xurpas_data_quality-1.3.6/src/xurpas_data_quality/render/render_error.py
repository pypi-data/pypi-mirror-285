import pandas as pd
from xurpas_data_quality.render.renderer import HTMLBase, HTMLContainer, HTMLTable, HTMLPlot
from xurpas_data_quality.data.descriptions import TableDescription
from xurpas_data_quality.render.render_sections import render_variables_section, render_correlation_section, render_interactions_section, render_dropdown_section
from xurpas_data_quality.visuals import plot_to_base64, create_missing_bar_plot

def render_error(data:pd.DataFrame, data_invalid:pd.DataFrame, errors:list , name:str, is_empty:bool, minimal:bool):
    content = []
    dataset_statistics = {
        'Number of Variables': data.dataset_statistics['num_variables'],
        'Missing Cells': data.dataset_statistics['missing_cells'],
        'Missing Cells (%)': "{:0.2f}%".format(data.dataset_statistics['missing_cells_perc']),
        'Duplicate Rows': data.dataset_statistics['duplicate_rows'],
        'Duplicate Rows (%)': "{:0.2f}%".format(data.dataset_statistics['duplicate_rows_perc'])
    }

    total_rows = data.dataset_statistics['dataset_length'] + data_invalid.dataset_statistics['dataset_length']
    errors_info = {
        'Valid Data Ingested (# of Rows)': data.dataset_statistics['dataset_length'],
        'Valid Data Ingested (% Percentage)': "{:0.2f}%".format((data.dataset_statistics['dataset_length']/total_rows)*100),
        'Invalid Data Ingested (# of Rows)': data_invalid.dataset_statistics['dataset_length'],
        'Invalid Data Ingested (% Percentage)': "{:0.2f}%".format((data_invalid.dataset_statistics['dataset_length']/total_rows)*100),
        'Total Rows for Dataset': total_rows
    }

    overview_section = HTMLContainer(
        type="box",
        name="Overview",
        container_items = [
            HTMLContainer(
                type="column",
                container_items = HTMLTable(
                    data = dataset_statistics,
                    name="Dataset Statistics"
                )),
            HTMLContainer(
                type="column",
                container_items =  HTMLTable(
                    data= data.variable_types,
                    name="Variable Types"
                )
            )
        ]
    )

    variables_section = HTMLContainer(
        type = "box",
        name = "Variables",
        container_items = render_dropdown_section(items=render_variables_section(data), names=list(data.df))
    )

    missing_section = HTMLContainer(
        type="box",
        name="Missing",
        container_items=[
            HTMLPlot(plot=plot_to_base64(create_missing_bar_plot(data.df), minimal=minimal),
            type="large",
            id="missingplot",
            name="Missing Bar Plot")]
    )

    correlation_section = render_correlation_section(data.correlation, minimal)


    samples_section = HTMLContainer(
        type="box",
        name="Sample",
        container_items=[
            HTMLTable(
                id = "sample",
                data=data.df.head(10).to_html(classes="table table-sm", border=0, index=False, justify='left')
            )
        ]
    )

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
        name="Errors Overview",
        id = "info-errors",
        container_items=[
            HTMLTable(
                data = errors_info
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

    content.extend([
            errors_section,
            overview_section,
            samples_section,
            correlation_section,
            missing_section,
            variables_section,
            ])

    if not minimal:
        interactions_section = HTMLContainer(
        type="box",
        name="Interactions",
        container_items=[
            HTMLContainer(
                type="tabs",
                container_items= render_interactions_section(data.df, minimal)
            )
        ]
        )
    
        content.extend([interactions_section])
    

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