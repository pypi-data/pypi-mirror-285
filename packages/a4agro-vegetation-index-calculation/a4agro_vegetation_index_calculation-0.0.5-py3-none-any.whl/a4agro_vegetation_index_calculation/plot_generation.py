import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.colors import Normalize


def calculate_class_break_values(
    raster_array: np.ndarray, num_classes: int = 5, decimal_places: int = 4
) -> list[float]:
    """
    # Summary:
        Calculate class break values

    # Parameters:
        raster_array (np.ndarray): Array of values
        num_classes (int): Number of classes
        decimal_places (int): Decimal places

    # Returns:
        list[float]: List of class break values
    """

    valid_data = raster_array[~np.isnan(raster_array)]

    class_break_values = np.percentile(valid_data, np.linspace(0, 100, num_classes + 1))

    class_break_values = np.round(class_break_values, decimal_places)

    return class_break_values.tolist()


def generate_figure_save_and_show(
    index: np.ndarray,
    class_labels: list[str],
    title: str,
    colormap: LinearSegmentedColormap,
    output_path_file_and_name: str,
    show: bool = False,
):
    """
    # Summary:
        Generate figure

    # Arguments:
        index (np.ndarray): Array of values
        class_labels (list[str]): List of class labels : example ["Área sin o Débil vegetación", "Vegetación escasa o Crecimiento inicial", "Vegetación moderada y saludable", "Vegetación densa y vigorosa", "Vegetación sobresaturada o de Alta densidad"]
        title (str): Title of the figure : example "Normalized Difference Vegetation Index (NDVI)"
        colormap (LinearSegmentedColormap): Colormap
        output_path_file_and_name (str): Name of the output file : example "C:/Users/A4agro/Desktop/ndvi-fig.png"
        show (bool): Show the figure
    """
    min_val = np.nanmin(index)
    max_val = np.nanmax(index)

    class_break_values = calculate_class_break_values(
        index, num_classes=4, decimal_places=4
    )
    norm = Normalize(vmin=min_val, vmax=max_val)

    # Create a figure and subplot for the plot
    fig = plt.figure(figsize=(20, 10))
    ax = fig.add_subplot(111)

    # Display index using imshow with colormap and normalization
    cbar_plot = ax.imshow(index, cmap=colormap, norm=norm)

    # Turn off axis labels
    ax.axis("off")

    # Set title for the plot
    ax.set_title(title, fontsize=17, fontweight="bold")

    # Create legend elements with class labels and values
    legend_elements = []
    for i in range(len(class_labels)):
        label = f"{class_labels[i]}\n({class_break_values[i]:.4f})"
        legend_elements.append(
            plt.Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor=colormap(norm(i)),
                markersize=10,
                label=label,
            )
        )

    # Sort legend elements based on class break values
    legend_elements_sorted = sorted(
        legend_elements, key=lambda x: float(x.get_label().split("(")[-1].split(")")[0])
    )

    ax.legend(
        handles=legend_elements_sorted,
        loc="lower center",
        bbox_to_anchor=(0.5, -0.05),
        fontsize=12,
        ncol=5,
    )

    # Save the plot as an image file
    fig.savefig(output_path_file_and_name, dpi=200, bbox_inches="tight", pad_inches=0.7)

    if show == True:
        # Show the plot
        plt.show()
