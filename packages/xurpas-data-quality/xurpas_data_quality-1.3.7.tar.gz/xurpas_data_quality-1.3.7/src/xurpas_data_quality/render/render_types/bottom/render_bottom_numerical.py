from xurpas_data_quality.data.typeset import Numeric
from xurpas_data_quality.render.handler import Handler
from xurpas_data_quality.render.renderer import HTMLBase, HTMLContainer, HTMLTable, HTMLVariable, HTMLPlot, HTMLToggle, HTMLCollapse, HTMLDropdown
from xurpas_data_quality.visuals import plot_to_base64, create_tiny_histogram, create_histogram, create_distribution_plot, create_heatmap, create_interaction_plot


@Handler.register(Numeric)
def render_bottom_numerical(data, col_name:str,*args, **kwargs):
    quantile_statistics = {
        "Minimum": data['quantile_stats']['minimum'],
        "Fifth (5th) Percentile": data['quantile_stats']['5th_percentile'],
        "First Quartile (Q1)":data['quantile_stats']['Q1'],
        "Median": data['quantile_stats']['median'],
        "Ninety-Fifth (95th) Percentile": data['quantile_stats']["95th_percentile"],
        "Maximum": data['quantile_stats']['maximum'],
        "Range": data['quantile_stats']['range'],
        "Interquartile Range (IQR)": data['quantile_stats']['IQR']
    }

    descriptive_statistics = {
        "Standard Deviation": "{:.2f}".format(data['descriptive_stats']['std_dev']),
        "Mean": "{:.2f}".format(data['descriptive_stats']["mean"]),
        "Coefficient of Variation (CV)": "{:.2f}".format(data['descriptive_stats']["CV"]),
        "Kurtosis": "{:.2f}".format(data['descriptive_stats']['kurtosis']),
        "Mean Absolute Deviation": "{:.2f}".format(data['descriptive_stats']["MAD"]),
        "Skew": "{:.2f}".format(data['descriptive_stats']['skew']),
        "Sum": "{:.2f}".format(data['descriptive_stats']['sum']),
        "Variance": "{:.2f}".format(data['descriptive_stats']['variance']),
        "Monotonicity": data['descriptive_stats']["monotonicity"]
    }


    variable_bottom = [
        HTMLContainer(
            type="box",
            name="Overview",
            container_items=[HTMLContainer(
                type="default",
                name="Statistics",
                id="stats",
                container_items=[
                    HTMLContainer(
                        type = "column",
                        container_items = HTMLTable(
                            data = quantile_statistics,
                            name = 'Quantile Statistics')
                    ),
                    HTMLContainer(
                        type = "column",
                        container_items = HTMLTable(
                            data = descriptive_statistics,
                            name = 'Descriptive Statistics'
                        )
                    )
                ]
            )]
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