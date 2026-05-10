import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import cartopy.crs as ccrs
import cartopy.feature as cfeature


def plot_plates_cartopy(plates, ax, facecolor='lightgray', edgecolor='black',
                        linewidth=1.5, alpha=0.5, transform=None):
    """
    Plot tectonic plate boundaries on a Cartopy axis.

    :param plates: dict of plate polygons from read_plates()
    :param ax: cartopy GeoAxes object
    :param facecolor: fill color for plates
    :param edgecolor: border color for plates
    :param linewidth: width of plate boundaries
    :param alpha: transparency (0-1)
    :param transform: coordinate transform (default: PlateCarree)
    :return: cartopy GeoAxes object
    """
    if transform is None:
        transform = ccrs.PlateCarree()

    for plate_name, polygons in plates.items():
        for polygon_df in polygons:
            ax.fill(
                polygon_df['lon'],
                polygon_df['lat'],
                facecolor=facecolor,
                edgecolor=edgecolor,
                linewidth=linewidth,
                alpha=alpha,
                transform=transform,
                zorder=1
            )

    return ax


def plot_gnss_stations_cartopy(df_gnss, ax, color='red', marker='o',
                                size=30, alpha=0.8, label='GNSS Stations',
                                transform=None):
    """
    Plot GNSS station locations on a Cartopy axis.

    :param df_gnss: DataFrame with GNSS station data (must have 'lamb_deg' and 'phi_deg')
    :param ax: cartopy GeoAxes object
    :param color: color of station markers
    :param marker: marker style
    :param size: marker size
    :param alpha: transparency (0-1)
    :param label: legend label
    :param transform: coordinate transform (default: PlateCarree)
    :return: cartopy GeoAxes object
    """
    if transform is None:
        transform = ccrs.PlateCarree()

    ax.scatter(
        df_gnss['lamb_deg'],
        df_gnss['phi_deg'],
        s=size,
        c=color,
        marker=marker,
        label=label,
        zorder=5,
        alpha=alpha,
        transform=transform,
        edgecolors='darkred',
        linewidths=0.5
    )

    return ax


def plot_simple_map(plates, df_gnss, figsize=(16, 10)):
    """
    Create a simple map with tectonic plates and GNSS stations using Cartopy.

    :param plates: dict of plate polygons from read_plates()
    :param df_gnss: DataFrame with GNSS station data
    :param figsize: tuple (width, height) for figure size
    :return: figure and axis objects
    """
    # Create figure and axis with Robinson projection
    fig, ax = plt.subplots(figsize=figsize, subplot_kw={'projection': ccrs.Robinson()})

    # Add map features
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue', alpha=0.3, zorder=0)
    ax.add_feature(cfeature.LAND, facecolor='wheat', alpha=0.2, zorder=0)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5, edgecolor='gray', zorder=2)

    # Add gridlines
    gl = ax.gridlines(draw_labels=False, linewidth=0.5, color='gray',
                      alpha=0.5, linestyle='--', zorder=3)

    # Plot tectonic plates
    plot_plates_cartopy(plates, ax, facecolor='none', edgecolor='black',
                       linewidth=2.0, alpha=0.8)

    # Plot GNSS stations
    plot_gnss_stations_cartopy(df_gnss, ax, color='red', size=15, alpha=0.7)

    # Set title
    ax.set_title('Tectonic Plates and GNSS Stations',
                fontsize=16, fontweight='bold', pad=20)

    # Add legend
    ax.legend(loc='lower left', fontsize=10, framealpha=0.9)

    # Set global extent
    ax.set_global()

    plt.tight_layout()

    return fig, ax


def plot_gnss_by_plate_cartopy(plates, df_gnss, figsize=(16, 10)):
    """
    Plot GNSS stations colored by their assigned plate.

    :param plates: dict of plate polygons from read_plates()
    :param df_gnss: DataFrame with GNSS station data (must have 'plate' column)
    :param figsize: tuple (width, height) for figure size
    :return: figure and axis objects
    """

    # Create figure and axis with Robinson projection
    fig, ax = plt.subplots(figsize=figsize, subplot_kw={'projection': ccrs.Robinson()})

    # Add map features
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue', alpha=0.3, zorder=0)
    ax.add_feature(cfeature.LAND, facecolor='wheat', alpha=0.2, zorder=0)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5, edgecolor='gray', zorder=2)

    # Add gridlines
    gl = ax.gridlines(draw_labels=False, linewidth=0.5, color='gray',
                      alpha=0.5, linestyle='--', zorder=3)

    # Plot tectonic plates
    plot_plates_cartopy(plates, ax, facecolor='lightgray', edgecolor='black',
                       linewidth=1.5, alpha=0.4)

    # Plot GNSS stations colored by plate
    plate_names = df_gnss['plate'].unique()
    colors = plt.cm.tab20(np.linspace(0, 1, len(plate_names)))

    for plate, color in zip(plate_names, colors):
        plate_data = df_gnss[df_gnss['plate'] == plate]
        ax.scatter(
            plate_data['lamb_deg'],
            plate_data['phi_deg'],
            s=20,
            c=[color],
            marker='o',
            label=plate,
            zorder=5,
            alpha=0.8,
            transform=ccrs.PlateCarree()
        )

    # Set title
    ax.set_title('GNSS Stations Colored by Tectonic Plate',
                fontsize=16, fontweight='bold', pad=20)

    # Add legend (outside plot area)
    ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5),
             fontsize=9, framealpha=0.9)

    # Set global extent
    ax.set_global()

    plt.tight_layout()

    return fig, ax


def plot_gnss_by_deformation_cartopy(plates, df_gnss, figsize=(16, 10)):
    """
    Plot GNSS stations colored by deformation status.

    :param plates: dict of plate polygons from read_plates()
    :param df_gnss: DataFrame with GNSS station data (must have 'in_deformation' column)
    :param figsize: tuple (width, height) for figure size
    :return: figure and axis objects
    """
    if 'in_deformation' not in df_gnss.columns:
        raise ValueError("DataFrame must have 'in_deformation' column. Run calculate_in_deformation() first.")

    # Create figure and axis with Robinson projection
    fig, ax = plt.subplots(figsize=figsize, subplot_kw={'projection': ccrs.Robinson()})

    # Add map features
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue', alpha=0.3, zorder=0)
    ax.add_feature(cfeature.LAND, facecolor='wheat', alpha=0.2, zorder=0)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5, edgecolor='gray', zorder=2)

    # Add gridlines
    gl = ax.gridlines(draw_labels=False, linewidth=0.5, color='gray',
                      alpha=0.5, linestyle='--', zorder=3)

    # Plot tectonic plates
    plot_plates_cartopy(plates, ax, facecolor='lightgray', edgecolor='black',
                       linewidth=1.5, alpha=0.4)

    # Stations NOT in deformation zones (stable)
    stable = df_gnss[df_gnss['in_deformation'] == False]
    ax.scatter(
        stable['lamb_deg'],
        stable['phi_deg'],
        s=25,
        c='green',
        marker='o',
        label='Stable (Not in Deformation Zone)',
        zorder=5,
        alpha=0.7,
        transform=ccrs.PlateCarree(),
        edgecolors='darkgreen',
        linewidths=0.5
    )

    # Stations IN deformation zones
    in_def = df_gnss[df_gnss['in_deformation'] == True]
    ax.scatter(
        in_def['lamb_deg'],
        in_def['phi_deg'],
        s=30,
        c='red',
        marker='o',
        label='In Deformation Zone',
        zorder=6,
        alpha=0.8,
        transform=ccrs.PlateCarree(),
        edgecolors='darkred',
        linewidths=0.5
    )

    # Set title
    ax.set_title('GNSS Stations by Deformation Status',
                fontsize=16, fontweight='bold', pad=20)

    # Add legend
    ax.legend(loc='lower left', fontsize=11, framealpha=0.9)

    # Set global extent
    ax.set_global()

    plt.tight_layout()

    return fig, ax

def plot_velocity_vectors_cartopy(plates, df_gnss, figsize=(16, 10),
                                   scale=0.1, arrow_color='red'):
    """
    Plot GNSS stations with velocity vectors using quiver for better visibility.

    :param plates: dict of plate polygons from read_plates()
    :param df_gnss: DataFrame with GNSS station data
    :param scale: Scale factor for quiver. If arrows are too small, DECREASE this value.
                  If arrows are too large, INCREASE this value.
    :param arrow_color: Color of the velocity vectors
    """
    # Create figure and axis
    fig, ax = plt.subplots(figsize=figsize, subplot_kw={'projection': ccrs.Robinson()})

    # Add standard map features
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue', alpha=0.3, zorder=0)
    ax.add_feature(cfeature.LAND, facecolor='wheat', alpha=0.2, zorder=0)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5, edgecolor='gray', zorder=2)

    # Plot tectonic plate boundaries
    plot_plates_cartopy(plates, ax, facecolor='none', edgecolor='black',
                        linewidth=1.0, alpha=0.5)

    # Extract data
    x = df_gnss['lamb_deg'].values
    y = df_gnss['phi_deg'].values
    u = df_gnss['Vlamb_deg'].values
    v = df_gnss['Vphi_deg'].values

    # Use quiver for vector plotting
    # transform=ccrs.PlateCarree() tells Cartopy the data is in Lat/Lon
    q = ax.quiver(x, y, u, v,
                  color=arrow_color,
                  transform=ccrs.PlateCarree(),
                  scale=scale,
                  zorder=6,
                  width=0.002,      # Thickness of the arrow shaft
                  headwidth=3,      # Width of the head relative to shaft
                  headlength=4)     # Length of the head relative to shaft


    # Plot the station points themselves
    ax.scatter(x, y, s=5, c='blue', alpha=0.5, transform=ccrs.PlateCarree(), zorder=5)

    ax.set_title('Global GNSS Velocity Vectors', fontsize=16, fontweight='bold', pad=20)
    ax.set_global()
    plt.tight_layout()

    return fig, ax

def plot_velocity_vectors_by_plate_cartopy(plates, df_gnss, figsize=(16, 10),
                                            scale=1e-7):
    """
    Plot GNSS stations with velocity vectors colored by tectonic plate.
    Note: scale should be very small (e.g., 1e-7) if velocities are in deg/yr.
    """

    fig, ax = plt.subplots(figsize=figsize, subplot_kw={'projection': ccrs.Robinson()})

    # Add map features
    ax.add_feature(cfeature.OCEAN, facecolor='lightblue', alpha=0.3)
    ax.add_feature(cfeature.LAND, facecolor='wheat', alpha=0.2)
    ax.add_feature(cfeature.COASTLINE, linewidth=0.5, edgecolor='gray')

    plot_plates_cartopy(plates, ax, facecolor='lightgray', edgecolor='black', alpha=0.3)

    # Get colors for each plate
    plate_names = df_gnss['plate'].unique()
    colors = plt.cm.tab20(np.linspace(0, 1, len(plate_names)))
    plate_colors = dict(zip(plate_names, colors))

    # We store the quiver objects to create a legend later
    for plate in plate_names:
        data = df_gnss[df_gnss['plate'] == plate]

        # Plot vectors for this plate
        q = ax.quiver(data['lamb_deg'].values, data['phi_deg'].values,
                      data['Vlamb_deg'].values, data['Vphi_deg'].values,
                      color=plate_colors[plate],
                      transform=ccrs.PlateCarree(),
                      scale=scale,
                      width=0.0015,
                      label=plate,
                      zorder=6)

    ax.set_title('GNSS Velocities by Plate', fontsize=16, fontweight='bold')
    ax.legend(loc='center left', bbox_to_anchor=(1.02, 0.5), ncol=2)
    ax.set_global()
    plt.tight_layout()

    return fig, ax

def save_figure(fig, filename, dpi=300, bbox_inches='tight'):
    """
    Save figure to file.

    :param fig: matplotlib figure object
    :param filename: output filename (with extension)
    :param dpi: resolution in dots per inch
    :param bbox_inches: bounding box setting
    """
    fig.savefig(filename, dpi=dpi, bbox_inches=bbox_inches)
    print(f"Figure saved as {filename}")

if __name__ == "__main__":
    # Example usage
    import partie_1 as p1
    import partie_2 as p2
    import partie_3 as p3

    # Load data
    print("Loading data...")
    plates = p1.read_plates()
    df_gnss_c, df_gnss_s = p1.read_gnss()

    # Simple map with all stations
    print("Creating simple map...")
    fig1, ax1 = plot_simple_map(plates, df_gnss_c)
    save_figure(fig1, 'map_simple.png', dpi=300)
    plt.show()

    # Process data for more advanced plots
    print("Processing data...")
    df_gnss_c = p2.which_plate(df_gnss_c, plates)
    df_gem = p1.read_gem()
    df_gnss_c = p3.calculate_in_deformation(df_gnss_c, df_gem)

    # Map colored by plate
    print("Creating map colored by plate...")
    fig2, ax2 = plot_gnss_by_plate_cartopy(plates, df_gnss_c)
    save_figure(fig2, 'map_by_plate.png', dpi=300)
    plt.show()

    # Map colored by deformation
    print("Creating map colored by deformation...")
    fig3, ax3 = plot_gnss_by_deformation_cartopy(plates, df_gnss_c)
    save_figure(fig3, 'map_by_deformation.png', dpi=300)
    plt.show()

    print("\nAll figures saved!")
