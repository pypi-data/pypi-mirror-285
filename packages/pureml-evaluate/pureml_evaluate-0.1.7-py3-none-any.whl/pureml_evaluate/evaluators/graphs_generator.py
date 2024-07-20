import io

import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Image, Paragraph, SimpleDocTemplate, Spacer


class CustomStyle(ParagraphStyle):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.fontName = "Arial"
        self.fontSize = 6
        self.textColor = "blue"


class GraphsGenerator:
    def get_graphs_as_pdf(
        self, values_all, values_subset_all, pdf_file_name="metrics_graphs.pdf"
    ):
        # Create a PDF document
        pdf_file = pdf_file_name
        doc = SimpleDocTemplate(pdf_file, pagesize=letter)
        elements = []
        # Generate performance graphs if data is available
        if "performance" in values_all and values_subset_all is not None:
            performance_metrics = values_all["performance"]
            keys_in_subset_all = list(values_subset_all.keys())

            style_sheet = ParagraphStyle(name=CustomStyle)
            for metric_name, metric_values in performance_metrics.items():
                fig = go.Figure()
                if metric_name == "confusion_matrix":
                    generate_confusion_matrix_for_pdf(
                        fig=fig,
                        metric_values=metric_values,
                        elements=elements,
                        keys_in_subset_all=keys_in_subset_all,
                        values_subset_all=values_subset_all,
                        metric_name=metric_name,
                    )

                else:
                    data_for_description = {"Complete Data": metric_values}
                    generate_graphs_for_performance(
                        fig,
                        data_for_description,
                        metric_values,
                        keys_in_subset_all,
                        values_subset_all,
                        metric_name,
                        elements=elements,
                    )

                    # Save the Plotly figure as an image in memory
                    image_data = fig.to_image(format="png")

                    # Create an Image object from the image data
                    img = Image(io.BytesIO(image_data))

                    # Set the image dimensions and add it to the elements list
                    img.drawHeight = 400
                    img.drawWidth = 600
                    elements.append(img)

                    description_paragraph = to_generate_description(
                        metric_name=metric_name,
                        data_for_description=data_for_description,
                        style_sheet=style_sheet,
                    )

                    elements.extend((description_paragraph, Spacer(1, 12)))

        # Generate fairness graphs if data is available
        if "fairness" in values_all and values_subset_all is not None:
            fairness_metrics = values_all["fairness"]
            keys_in_subset_all = list(values_subset_all.keys())
            style_sheet = ParagraphStyle(name=CustomStyle)
            for metric_name, metric_values in fairness_metrics.items():
                fig = go.Figure()
                data_for_description = {"Complete Data": metric_values}
                generate_fairness_graphs(
                    fig=fig,
                    metric_values=metric_values,
                    keys_in_subset_all=keys_in_subset_all,
                    values_subset_all=values_subset_all,
                    metric_name=metric_name,
                    data_for_description=data_for_description,
                )
                # Save the Plotly figure as an image in memory
                image_data = fig.to_image(format="png")

                # Create an Image object from the image data
                img = Image(io.BytesIO(image_data))

                # Set the image dimensions and add it to the elements list
                img.drawHeight = 400
                img.drawWidth = 600
                elements.append(img)
                description_paragraph = to_generate_description(
                    metric_name=metric_name,
                    data_for_description=data_for_description,
                    style_sheet=style_sheet,
                )

                elements.extend((description_paragraph, Spacer(1, 12)))

        # Build the PDF document with the elements
        doc.build(elements)

        if values_subset_all is None:
            generate_only_for_values_all(values_all=values_all, elements=elements)
            doc.build(elements)

    def get_graphs_as_html(self, values_all, values_subset_all):

        if "performance" in values_all and values_subset_all != None:
            performance_metrics = values_all["performance"]
            keys_in_subset_all = list(values_subset_all.keys())

            # Generate performance graphs
            for metric_name, metric_values in performance_metrics.items():
                fig = go.Figure()

                if metric_name == "confusion_matrix":
                    generate_confusion_matrix_for_html(
                        fig=fig,
                        metric_values=metric_values,
                        keys_in_subset_all=keys_in_subset_all,
                        values_subset_all=values_subset_all,
                        metric_name=metric_name,
                    )
                else:
                    generate_graph_for_performance_for_html(
                        fig=fig,
                        metric_values=metric_values,
                        keys_in_subset_all=keys_in_subset_all,
                        values_subset_all=values_subset_all,
                        metric_name=metric_name,
                    )

        # Generate fairness graphs
        if "fairness" in values_all and values_subset_all != None:
            fig = go.Figure()
            fairness_metrics = values_all["fairness"]
            for metric_name, metric_values in fairness_metrics.items():
                generate_graphs_for_fairness_for_html(
                    fig=fig,
                    metric_values=metric_values,
                    keys_in_subset_all=keys_in_subset_all,
                    values_subset_all=values_subset_all,
                    metric_name=metric_name,
                )

        if values_subset_all is None:
            fig = go.Figure()
            generate_only_for_values_all_for_html(values_all=values_all)


def generate_confusion_matrix_for_pdf(
    fig, metric_values, elements, keys_in_subset_all, values_subset_all, metric_name
):
    fig = go.Figure(
        data=go.Heatmap(
            z=np.array(metric_values),
            x=["True", "False"],
            y=["Positive", "Negative"],
            colorscale="Viridis",
        )
    )
    fig.update_layout(
        title="Confusion Matrix for Complete Data",
        xaxis_title="Predicted",
        yaxis_title="Actual",
        showlegend=False,
    )

    # Save the figure as a PNG image
    img_bytes = fig.to_image(format="png")
    img = Image(io.BytesIO(img_bytes))

    img.drawHeight = 300
    img.drawWidth = 500
    elements.append(img)

    for subset_key in keys_in_subset_all:
        generate_subsets_for_confusion_matrix(
            fig, metric_name, subset_key, values_subset_all, elements
        )


def generate_subsets_for_confusion_matrix(
    fig, metric_name, subset_key, values_subset_all, elements
):
    subset_values = values_subset_all[subset_key]["performance"][metric_name]
    fig = go.Figure(
        data=go.Heatmap(
            z=np.array(subset_values),
            x=["True", "False"],
            y=["Positive", "Negative"],
            colorscale="Viridis",
        )
    )
    fig.update_layout(
        title=f"Confusion Matrix for {subset_key.capitalize()} Data",
        xaxis_title="Predicted",
        yaxis_title="Actual",
        showlegend=False,
    )

    # Save the figure as a PNG image
    img_bytes = fig.to_image(format="png")
    img = Image(io.BytesIO(img_bytes))

    img.drawHeight = 300
    img.drawWidth = 500
    elements.append(img)


def to_generate_description(data_for_description, metric_name, style_sheet):
    description = " "
    data_str = " "
    for key, value in data_for_description.items():
        data_str += f"{key}: {value},\n "
    description += f" The values for each category are: {data_str[:-2]}\n"

    return Paragraph(description)


def generate_fairness_graphs(
    fig,
    metric_values,
    keys_in_subset_all,
    values_subset_all,
    metric_name,
    data_for_description,
):
    color = get_color(metric_values["severity"])
    fig.add_trace(
        go.Bar(
            x=["Complete"],
            y=[metric_values["value"]],
            name="All",
            marker=dict(color=color),
        )
    )
    # data_for_description = {'Complete Data' : metric_values['value']}
    for subset_key in keys_in_subset_all:
        subset_values = values_subset_all[subset_key]["fairness"][metric_name]
        color = get_color(subset_values["severity"])
        data_for_description[subset_key.capitalize()] = subset_values
        fig.add_trace(
            go.Bar(x=[subset_key], y=[subset_values["value"]], marker=dict(color=color))
        )
    keyname = format_keyname(metric_name)
    fig.update_layout(
        title=f"Fairness - {keyname}",
        xaxis_title="Category",
        yaxis_title="Value",
        showlegend=False,
    )
    # return fig,data_for_description


def generate_graphs_for_performance(
    fig,
    data_for_description,
    metric_values,
    keys_in_subset_all,
    values_subset_all,
    metric_name,
    elements,
):
    color = get_color(metric_values["severity"])
    metric_values = metric_values["value"]
    fig.add_trace(
        go.Bar(x=["Complete Data"], y=[metric_values], marker=dict(color=color))
    )
    for subset_key in keys_in_subset_all:
        subset_values = values_subset_all[subset_key]["performance"][metric_name]
        data_for_description[subset_key.capitalize()] = subset_values
        # data = get_description(type_of_metric='performance',metric_name=metric_name)
        # if data != None:
        #     description = data['description']
        #     whyitmatters = data['why it matters']
        #     configuration = data['configuration']
        #     data_for_description['description'] = description
        #     data_for_description['why it matters'] = whyitmatters
        #     data_for_description['configuration'] = configuration
        color = get_color(subset_values["severity"])
        fig.add_trace(
            go.Bar(x=[subset_key], y=[subset_values["value"]], marker=dict(color=color))
        )

    keyname = format_keyname(metric_name=metric_name)
    fig.update_layout(
        title=f"Performance - {keyname}",
        xaxis_title="Category",
        yaxis_title="Value",
        showlegend=False,
    )


# def get_description(type_of_metric,metric_name):
#     file_name  = pkg_resources.resource_filename(__name__, 'description.json')
#     with open(f'{file_name}','r') as f:
#         data = json.load(f)

#     if type_of_metric in data and metric_name in data[type_of_metric]:
#         return {
#              'description' : data[type_of_metric][metric_name]['description'],
#              'why it matters' : data[type_of_metric][metric_name]['why it matters'],
#              'configuration' : data[type_of_metric][metric_name]['configuration']
#         }
#     else:
#         return None


def generate_confusion_matrix_for_html(
    fig, metric_values, keys_in_subset_all, values_subset_all, metric_name
):
    fig.add_trace(go.Heatmap(z=np.array(metric_values)))

    # Set layout properties
    fig.update_layout(
        title="Confusion Matrix",
        xaxis=dict(title="Predicted"),
        yaxis=dict(title="Actual"),
    )

    # Save the figure as an HTML file
    pio.write_html(fig, file="confusion_matrix.html")

    for subset_key in keys_in_subset_all:
        subset_values = values_subset_all[subset_key]["performance"][metric_name]
        fig.add_trace(go.Heatmap(z=np.array(subset_values)))

        fig.update_layout(
            title=f"Confusion Matrix - {subset_key.capitalize()}",
            xaxis=dict(title="Predicted"),
            yaxis=dict(title="Actual"),
        )

        # Save the figure as an HTML file
        pio.write_html(fig, file=f"confusion_matrix_{subset_key}.html")


def format_keyname(metric_name):
    metricname = metric_name.split("_")
    return (
        metricname[0].capitalize()
        if len(metricname) == 1
        else " ".join(word.capitalize() for word in metricname)
    )


def generate_graph_for_performance_for_html(
    fig, metric_values, keys_in_subset_all, values_subset_all, metric_name
):
    color = get_color(metric_values["severity"])
    metric_values = metric_values["value"]
    print(f"From Complete Data: {metric_values}")
    fig.add_trace(
        go.Bar(x=["Complete"], y=[metric_values], name="All", marker=dict(color=color))
    )

    # Add subset values
    for subset_key in keys_in_subset_all:
        subset_values = values_subset_all[subset_key]["performance"][metric_name]

        color = "#52BD94" if subset_values["status"] == "Pass" else "#D14343"
        print(f"From SubsetValue: {subset_values['value']}")
        fig.add_trace(
            go.Bar(
                x=[subset_key], y=[subset_values["value"]], name=subset_key.capitalize()
            )
        )

    metric_name = format_keyname(metric_name=metric_name)
    # Set layout properties
    fig.update_layout(
        title=f"Performance - {metric_name}",
        xaxis=dict(title="Category"),
        yaxis=dict(title="Value"),
        showlegend=False,
    )
    # Save the figure as an HTML file
    pio.write_html(fig, file=f"performance_{metric_name}.html")


def generate_graphs_for_fairness_for_html(
    fig, metric_values, keys_in_subset_all, values_subset_all, metric_name
):
    fig = go.Figure()
    # Add complete value
    color = "#52BD94" if metric_values["status"] == "Pass" else "#D14343"
    fig.add_trace(go.Bar(x=["Complete"], y=[metric_values["value"]], name="All"))
    # Add subset values
    for subset_key in keys_in_subset_all:
        subset_values = values_subset_all[subset_key]["fairness"][metric_name]
        color = "#52BD94" if subset_values["status"] == "Pass" else "#D14343"
        fig.add_trace(
            go.Bar(
                x=[subset_key],
                y=[subset_values["value"]],
                name=subset_key.capitalize(),
                marker=dict(color=color),
            )
        )

    # Set layout properties
    metric_name = format_keyname(metric_name=metric_name)
    fig.update_layout(
        title=f"Fairness - {metric_name}",
        xaxis=dict(title="Category"),
        yaxis=dict(title="Value"),
        showlegend=False,
    )
    # Save the figure as an HTML file
    pio.write_html(fig, file=f"fairness_{metric_name}.html")


def generate_only_for_values_all(values_all, elements):
    style_sheet = getSampleStyleSheet()
    if "performance" in values_all:
        performance_metrics = values_all["performance"]
        for metric_name, metric_values in performance_metrics.items():
            fig = go.Figure()
            data_for_description = {"Complete Data": metric_values}
            if metric_name == "confusion_matrix":
                fig = go.Figure(
                    data=go.Heatmap(
                        z=np.array(metric_values),
                        x=["True", "False"],
                        y=["Positive", "Negative"],
                        colorscale="Viridis",
                    )
                )
                fig.update_layout(
                    title="Confusion Matrix for Complete Data",
                    xaxis_title="Predicted",
                    yaxis_title="Actual",
                    showlegend=False,
                )
            else:
                color = get_color(metric_values["severity"])
                fig.add_trace(
                    go.Bar(
                        x=["Complete Data"],
                        y=[metric_values["value"]],
                        name="All",
                        marker=dict(color=color),
                    )
                )
                keyname = format_keyname(metric_name)
                fig.update_layout(
                    title=f"{keyname}",
                    xaxis_title="Data",
                    yaxis_title="value",
                    showlegend=False,
                )
            image_data = fig.to_image(format="png")
            img = Image(io.BytesIO(image_data))
            img.drawHeight = 400
            img.drawWidth = 600
            elements.append(img)
            description_paragraph = to_generate_description(
                metric_name=metric_name,
                data_for_description=data_for_description,
                style_sheet=style_sheet,
            )
            elements.extend((description_paragraph, Spacer(1, 12)))

    if "fairness" in values_all:
        fairness_metrics = values_all["fairness"]
        for metric_name, metric_values in fairness_metrics.items():
            fig = go.Figure()
            color = get_color(metric_values["severity"])
            metric_values = metric_values["value"]
            data_for_description = {"Complete Data": metric_values}
            keyname = format_keyname(metric_name)
            fig.add_trace(go.Bar(x=["Complete Data"], y=[metric_values], name="All"))
            fig.update_layout(
                title=f"{keyname}",
                xaxis_title="Data",
                yaxis_title="value",
                showlegend=False,
            )
            image_data = fig.to_image(format="png")
            img = Image(io.BytesIO(image_data))
            img.drawHeight = 400
            img.drawWidth = 600
            elements.append(img)
            description_paragraph = to_generate_description(
                metric_name=metric_name,
                data_for_description=data_for_description,
                style_sheet=style_sheet,
            )
            elements.extend((description_paragraph, Spacer(1, 12)))


def generate_only_for_values_all_for_html(values_all):
    if "performance" in values_all:
        performance_metrics = values_all["performance"]
        for metric_name, metric_values in performance_metrics.items():
            fig = go.Figure()
            if metric_name == "confusion_matrix":
                fig = go.Figure(
                    data=go.Heatmap(
                        z=np.array(metric_values),
                        x=["True", "False"],
                        y=["Positive", "Negative"],
                        colorscale="Viridis",
                    )
                )
                fig.update_layout(
                    title="Confusion Matrix for Complete Data",
                    xaxis_title="Predicted",
                    yaxis_title="Actual",
                    showlegend=False,
                )
            else:
                # color = get_color(metric_values['severity'])
                color = get_color(metric_values["severity"])
                fig.add_trace(
                    go.Bar(
                        x=["Complete Data"],
                        y=[metric_values["value"]],
                        name="All",
                        marker=dict(color=color),
                    )
                )
                keyname = format_keyname(metric_name)
                fig.update_layout(
                    title=f"{keyname}",
                    xaxis_title="Data",
                    yaxis_title="value",
                    showlegend=False,
                )
            # Save the figure as an HTML file
            pio.write_html(fig, file=f"performance_{metric_name}.html")

    if "fairness" in values_all:
        fairness_metrics = values_all["fairness"]
        for metric_name, metric_values in fairness_metrics.items():
            fig = go.Figure()
            keyname = format_keyname(metric_name)
            color = "#52BD94" if metric_values["status"] == "Pass" else "#D14343"
            fig.add_trace(
                go.Bar(
                    x=["Complete Data"],
                    y=[metric_values["value"]],
                    name="All",
                    marker=dict(color=color),
                )
            )
            fig.update_layout(
                title=f"{keyname}",
                xaxis_title="Data",
                yaxis_title="value",
                showlegend=False,
            )
            # Save the figure as an HTML file
            pio.write_html(fig, file=f"fairness_{metric_name}.html")


# Function to get color
def get_color(severity):
    if severity == "high":
        return "#D14343"
    elif severity == "moderate":
        return "#FFB020"
    elif severity == "pass":
        return "#52BD94"
    else:
        return "#3366FF"
