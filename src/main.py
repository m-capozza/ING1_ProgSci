import partie_1 as p1
import partie_2 as p2
import partie_3 as p3
import partie_4 as p4
import partie_5 as p5
import pandas as pd
import matplotlib.pyplot as plt


if __name__ == '__main__':
    # Load data
    print("Loading data...")
    df_gem = p1.read_gem()
    df_pmm = p1.read_pmm()
    df_gnss = p1.read_gnss()[0]
    df_gnss_s = p1.read_gnss()[1]
    plates = p1.read_plates()

    # Process data
    print("Processing data...")
    df_gnss_c = p2.which_plate(df_gnss, plates)
    df_gnss_c = p3.calculate_in_deformation(df_gnss_c, df_gem)
    df_gnss_c = p4.calculate_v_pred(df_gnss_c, df_pmm)
    df_gnss_c = p4.cartesian_to_angular_velocities(df_gnss_c, df_gnss_s)

    print(df_gnss_c.head(10))

    """
    # Simple map with plates and all GNSS stations
    print("Creating simple map with plates and GNSS stations...")
    fig1, ax1 = p5.plot_simple_map(plates, df_gnss_c, figsize=(16, 10))
    p5.save_figure(fig1, 'map_simple.png', dpi=300)
    plt.show()

    # Map with stations colored by tectonic plate
    print("Creating map with stations colored by plate...")
    fig2, ax2 = p5.plot_gnss_by_plate_cartopy(plates, df_gnss_c, figsize=(16, 10))
    p5.save_figure(fig2, 'map_by_plate.png', dpi=300)
    plt.show()

    # Map with stations colored by deformation status
    print("Creating map with stations colored by deformation...")
    fig3, ax3 = p5.plot_gnss_by_deformation_cartopy(plates, df_gnss_c, figsize=(16, 10))
    p5.save_figure(fig3, 'map_by_deformation.png', dpi=300)
    plt.show()

    print("\nAll figures saved successfully!")
    """
