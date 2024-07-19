from typing import Any, List

from xurpas_data_quality.data.descriptions import TableDescription
from xurpas_data_quality.render.renderer import BaseRenderer, HTMLBase, HTMLContainer, HTMLTable, HTMLVariable, HTMLPlot, HTMLToggle, HTMLCollapse, HTMLDropdown
from xurpas_data_quality.visuals import plot_to_base64, create_missing_bar_plot
from xurpas_data_quality.render.render_sections import render_variables_section, render_correlation_section, render_interactions_section, render_dropdown_section


def render_report(data: TableDescription, minimal:bool,report_name: str=None) -> List[BaseRenderer]:
    """
    Creates the content of a normal report
    """
    
    content = []
    dataset_statistics = {
        'Number of Variables': data.dataset_statistics['num_variables'],
        'Missing Cells': data.dataset_statistics['missing_cells'],
        'Missing Cells (%)': "{:0.2f}%".format(data.dataset_statistics['missing_cells_perc']),
        'Duplicate Rows': data.dataset_statistics['duplicate_rows'],
        'Duplicate Rows (%)': "{:0.2f}%".format(data.dataset_statistics['duplicate_rows_perc'])
    }

    if data.alerts is not None and "shipment_no_alerts" in data.alerts:
        overview= HTMLContainer(
            type="default",
            name="Overview",
            id="overview-tab",
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
        alerts = HTMLContainer(
            type="default",
            name="Alerts",
            id="alerts-tab",
            flex=True,
            container_items = [
                HTMLTable(
                    id="alerts",
                    data=[f" There are {data.alerts['shipment_no_alerts']['alerts']} rows with no Shipment Numbers"]
                ),
                HTMLTable(
                    id ="alert_sample",
                    data = data.alerts["shipment_no_alerts"]["df"].to_html(classes="table table-sm", border=0, justify='left')
                )
            ])
        
        overview_section = HTMLContainer(
            type="box",
            name="Overview",
            id = "overview_section",
            container_items=[
                HTMLContainer(
                    type="tabs",
                    container_items=[overview, alerts]
                )
            ]
        )

    else:
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
    
    content.extend([overview_section,
                samples_section,
                variables_section,
                missing_section, 
                correlation_section, 
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

    return content