import numpy as np
from skimage.color import lab2rgb
from matplotlib.colors import LinearSegmentedColormap


def create_ndvi_colormap() -> LinearSegmentedColormap:
    """Create NDVI colormap

    ### color map postions
        0 %: L:55 , A:76 , B:66
        50 %: L:94 , A:-20 , B:85
        100 %: L:83 , A:-89 , B:72

    Returns:
        LinearSegmentedColormap: Class for creating a colormap
    """

    # Define NDVI colors and their positions
    ndvi_colors = {
        0.0: [55, 75, 66],  # Position 0%
        0.25: [74, 28, 76],  # Position 25%
        0.5: [94, -20, 85],  # Position 50%
        0.75: [89, -55, 79],  # Position 75%
        1.0: [83, -89, 72],  # Position 100%
    }

    # Convert NDVI colors to RGB
    rgb_colors = {
        pos: lab2rgb(np.array([[color]], dtype=np.float32))[0, 0]
        for pos, color in ndvi_colors.items()
    }

    # Extract positions and corresponding RGB colors
    positions = sorted(rgb_colors.keys())
    colors = [rgb_colors[pos] for pos in positions]

    # Create a custom colormap
    cmap = LinearSegmentedColormap.from_list(
        "ndvi_colormap", list(zip(positions, colors))
    )

    return cmap


def create_ndwi_colormap() -> LinearSegmentedColormap:
    """
    # Summary:
        Define NDWI colors and their positions

    # Colors
        0 %: R:255 , G:255 , B:217
        12 %: R:237 , G:248 , B:117
        25 %: R:199 , G:233 , B:180
        38 %: R:127 , G:205 , B:187
        50 %: R:65 , G:182 , B:196
        62 %: R:29 , G:145 , B:192
        75 %: R:34 , G:94 , B:168
        88 %: R:37 , G:52 , B:148
        100 %: R:8 , G:29 , B:88

    # Returns:
        LinearSegmentedColormap: Class for creating a colormap
    """

    # Define NDWI colors and their positions

    ndwi_colors = {
        0.0: [255, 255, 217],  # Position 0%
        # 0.12: [237, 248, 117],  # Position 12%
        0.25: [199, 233, 180],  # Position 25%
        # 0.38: [127, 205, 187],  # Position 38%
        0.5: [65, 182, 196],  # Position 50%
        # 0.62: [29, 145, 192],  # Position 62%
        0.75: [34, 94, 168],  # Position 75%
        # 0.88: [37, 52, 148],  # Posi    tion 88%
        1.0: [8, 29, 88],  # Position 100%
    }

    # Convert colors to normalized [0, 1] range
    rgb_colors = {pos: np.array(color) / 255.0 for pos, color in ndwi_colors.items()}

    # Extract positions and corresponding RGB colors
    positions = sorted(rgb_colors.keys())
    colors = [rgb_colors[pos] for pos in positions]

    # Create a custom colormap
    cmap = LinearSegmentedColormap.from_list(
        "ndwi_colormap", list(zip(positions, colors))
    )

    return cmap


def create_gndvi_colormap() -> LinearSegmentedColormap:
    """
    # Summary:
        Define NDWI colors and their positions

    # Colors
        0 %: R:255 , G:255 , B:229
        25 %: R:217 , G:240 , B:163
        50 %: R:120 , G:198 , B:121
        75 %: R:35 , G:132 , B:67
        100 %: R:0 , G:69 , B:41

    # Returns:
        LinearSegmentedColormap: Class for creating a colormap

    """
    gndvi_colors = {
        0.0: [255, 255, 229],  # Position 0%
        0.25: [217, 240, 163],  # Position 25%
        0.5: [120, 198, 121],  # Position 50%
        0.75: [35, 132, 67],  # Position 75%
        1.0: [0, 69, 41],  # Position 100%
    }

    # Convert colors to normalized [0, 1] range
    rgb_colors = {pos: np.array(color) / 255.0 for pos, color in gndvi_colors.items()}

    # Extract positions and corresponding RGB colors
    positions = sorted(rgb_colors.keys())
    colors = [rgb_colors[pos] for pos in positions]

    # Create a custom colormap
    cmap = LinearSegmentedColormap.from_list(
        "ndwi_colormap", list(zip(positions, colors))
    )

    return cmap


def create_cgi_colormap() -> LinearSegmentedColormap:
    """
    # Summary:
        Define NDWI colors and their positions

    # Colors
        0 %: R:247 , G:252 , B:245
        25 %: R:199 , G:233 , B:192
        50 %: R:116 , G:196 , B:118
        75 %: R:35 , G:139 , B:69
        100 %: R:0 , G:68 , B:27

    # Returns:
        LinearSegmentedColormap: Class for creating a colormap
    """

    cgi_colors = {
        0.0: [247, 252, 245],  # Position 0%
        0.25: [199, 233, 192],  # Position 25%
        0.5: [116, 196, 118],  # Position 50%
        0.75: [35, 139, 69],  # Position 75%
        1.0: [0, 68, 27],  # Position 100%
    }

    # Convert colors to normalized [0, 1] range
    rgb_colors = {pos: np.array(color) / 255.0 for pos, color in cgi_colors.items()}

    # Extract positions and corresponding RGB colors
    positions = sorted(rgb_colors.keys())
    colors = [rgb_colors[pos] for pos in positions]

    # Create a custom colormap
    cmap = LinearSegmentedColormap.from_list(
        "ndwi_colormap", list(zip(positions, colors))
    )

    return cmap


def create_ndre_colormap() -> LinearSegmentedColormap:
    """
    # Summary:
        Define  colors and their positions

    # Colors
        0 %: R:165 , G:0 , B:38
        25 %: R:249 , G:142 , B:82  
        50 %: R:255 , G:255 , B:191 
        75 %: R: 104 , G:233 , B:103
        100 %: R:0 , G:104 , B:55

    # Returns:
        LinearSegmentedColormap: Class for creating a colormap
    """
    ndre_colors = {
        0.0: [165, 0, 38],  # Position 0%
        0.25: [249, 142, 82],  # Position 25%
        0.5: [255, 255, 191],  # Position 50%
        0.75: [104, 233, 103],  # Position 75%
        1.0: [0, 104, 55],  # Position 100%
    }

    # Convert colors to normalized [0, 1] range
    rgb_colors = {pos: np.array(color) / 255.0 for pos, color in ndre_colors.items()}

    # Extract positions and corresponding RGB colors
    positions = sorted(rgb_colors.keys())
    colors = [rgb_colors[pos] for pos in positions]

    # Create a custom colormap
    cmap = LinearSegmentedColormap.from_list(
        "ndre_colormap", list(zip(positions, colors))
    )

    return cmap
