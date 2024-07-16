from xurpas_data_quality.data.typeset import Numeric
from xurpas_data_quality.render.handler import Handler
from xurpas_data_quality.render.renderer import HTMLBase, HTMLContainer, HTMLTable, HTMLVariable, HTMLPlot, HTMLToggle, HTMLCollapse, HTMLDropdown
from xurpas_data_quality.visuals import plot_to_base64, create_tiny_histogram, create_histogram, create_distribution_plot, create_heatmap, create_interaction_plot


@Handler.register(Numeric)
def render_bottom_numerical(data, col_name:str,*args, **kwargs):
    variable_bottom = [
        HTMLContainer(
            type="default",
            name="Statistics",
            id="stats",
            container_items=[
                HTMLContainer(
                    type = "column",
                    container_items = HTMLTable(
                        data = data['quantile_stats'],
                        name = 'Quantile Statistics')
                ),
                HTMLContainer(
                    type = "column",
                    container_items = HTMLTable(
                        data = data['descriptive_stats'],
                        name = 'Descriptive Statistics'
                    )
                )
            ]
        ),
        HTMLPlot(
            name="Histogram",
            type="large",
            id="histo",
            plot=plot_to_base64(create_histogram(data['histogram']))
        )
    ]

    return HTMLContainer(
        type="tabs",
        col=col_name,
        container_items=variable_bottom
    )