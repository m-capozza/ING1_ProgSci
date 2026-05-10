import pandas as pd
import numpy as np
import partie_1 as p1

def calculate_v_pred(df_gnss, df_pmm):
    """
    Applies the v_predite() function to all rows of the df_gnss for wich the station is not in a deformation zone.
    :param df_gnss: df of all gnss stations
    :param df_pmm: df of a
    :return df_gnss: the df_gnss with an added col called v_pred
    """
    # Apply the function to each row of the df
    for idx, row in df_gnss[(df_gnss['in_deformation'] == False) & (df_gnss['plate'] != 'Unknown')].iterrows():
        plate_name = row['plate']
        plate_data = df_pmm[df_pmm['Name'] == plate_name]

        omega_mas = plate_data[['wx', 'wy', 'wz']].values[0] # in mas/an
        omega_rad = omega_mas * 4.848136811e-9 # in rad/an
        r = df_gnss.loc[idx, ['X', 'Y', 'Z']].values
        T = np.array([0.37,0.35,0.74])/1000
        df_gnss.loc[idx, 'v_pred'] = np.linalg.norm(v_predite(omega_rad,r,T)) # calculates the norm of the vector

    return df_gnss

def v_predite(omega, r, T):
    """
    Calculates the predicted speed given omega, r and T.
    :param omega: np.array [wx,wy,wz] in rad/an
    :param r: np.array [X,Y,Z] in mm
    :param T: np.array [Tx,Ty,Tz] in mm/an
    :return v_predite: np.array [vx, vy, vz] m/an
    """
    v_rotation = np.cross(omega,r)
    return v_rotation + T/1000

def cartesian_to_angular_velocities(df_gnss, df_gnss_s, R=6371000):
    """
    Convert Cartesian velocities (Vx, Vy, Vz) to angular velocities (Vλ, Vφ) and add to dataframe.

    This function performs two transformations:
    1. Cartesian (X,Y,Z) → ENU (East-North-Up) using rotation matrix
    2. ENU → Angular velocities using approximation for graphical representation

    :param df_gnss: DataFrame with coordinates
    :param df_gnss_s: DataFrame with velocities
    :param R: Earth radius in meters (default: 6371 km = 6371000 m)
    :return: df_gnss with added 'Vlamb_deg' and 'Vphi_deg' columns (degrees/year)
    """
    # Extract values from dataframes
    Vx = df_gnss_s['Vx'].values
    Vy = df_gnss_s['Vy'].values
    Vz = df_gnss_s['Vz'].values
    phi_rad = df_gnss['phi_rad'].values
    lamb_rad = df_gnss['lamb_rad'].values

    # Step 1: Convert Cartesian (XYZ) to ENU using rotation matrix
    # VE = -sin(λ)·Vx + cos(λ)·Vy
    VE = -np.sin(lamb_rad) * Vx + np.cos(lamb_rad) * Vy

    # VN = -sin(φ)cos(λ)·Vx - sin(φ)sin(λ)·Vy + cos(φ)·Vz
    VN = (-np.sin(phi_rad) * np.cos(lamb_rad) * Vx
          - np.sin(phi_rad) * np.sin(lamb_rad) * Vy
          + np.cos(phi_rad) * Vz)

    # Step 2: Convert ENU to angular velocities (approximation for map display)
    # Vφ ≈ VN / R (radians/year)
    Vphi_rad = VN / R

    # Vλ ≈ VE / (R·cos(φ)) (radians/year)
    Vlamb_rad = VE / (R * np.cos(phi_rad))

    # Convert to degrees/year
    Vphi_deg = Vphi_rad * 180 / np.pi
    Vlamb_deg = Vlamb_rad * 180 / np.pi

    # Add to dataframe
    df_gnss['Vlamb_deg'] = Vlamb_deg
    df_gnss['Vphi_deg'] = Vphi_deg

    return df_gnss

if __name__ == "__main__":
    df_gnss = p1.read_gnss()[0]
    df_pmm = p1.read_pmm()

    print(df_gnss)
    calculate_v_pred(df_gnss, df_pmm)

    print(df_gnss)

    # TODO
    # import the right df_gnss from part 3
    # finish the calculate_v_pred function !
