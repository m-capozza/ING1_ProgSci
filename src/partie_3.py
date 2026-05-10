import numpy as np
import pandas as pd

####### Fonctions #######

def haversine(phi_1, lamb_1, phi_2, lamb_2):
    """
    Calculates the haversine distance between 2 points
    :param phi_1: en rad
    :param phi_2: en rad
    :param lamb_1: en rad
    :param lamb_2: en rad
    """
    dphi = phi_2 - phi_1
    dlamb = lamb_2 - lamb_1
    a = np.sin(dphi/2)**2 + np.cos(phi_1) * np.cos(phi_2) * np.sin(dlamb/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return 6378 * c


def calculate_in_deformation(df_gnss_c, df_gem):
    """
    Sets 'in_deformation' to True if a GNSS station is < 50km from ANY GEM point.
    """
    gem_lats = df_gem['lat'].to_numpy() * np.pi / 180
    gem_lons = df_gem['long'].to_numpy() * np.pi / 180

    # Apply the function to each row of the df
    for idx, row in df_gnss_c.iterrows():
        df_gnss_c.loc[idx,'in_deformation'] = check_station(row, gem_lats, gem_lons)

    return df_gnss_c

def check_station(row, gem_lats, gem_lons):
    """
    Check if a station is within 50km of a GEM point.
    :param row: a row of the df_gnss dataframe
    :param gem_lats: np.array of all the gem points latitudes in rads
    :param gem_lons: np.array of all the gem points longitudes in rads
    """
    # 1. Get station coordinates
    st_lat = row['phi_rad']
    st_lon = row['lamb_rad']

    # 2. Calculate distance to ALL GEM points at once (vectorized)
    distances = haversine(st_lat, st_lon, gem_lats, gem_lons)

    # 3. Return True if any GEM point is within 50km
    return np.any(distances < 50)


if __name__ == "__main__":
    pd.set_option('display.max_rows', None)
    calculate_in_deformation(df_gnss, df_gem)
    print(df_gnss)
