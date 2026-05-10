import pandas as pd
import numpy as np
import json

######## Variables #########

# 1/fe = 298.257223563
f_e = 1/298.257223563

# ae
a_e = 6378137.0

# (e_e)**2
e_e2 = f_e*(2-f_e)

######## Functions #########

def xyz_to_llh(X, Y, Z):
    """
    Converti les coordonnees X,Y,Z (cartesiennes geocentriques) en des coordonnes Lamb, Phi, h (geographiques)
    :param X: float
    :param Y: float
    :param Z: float
    :return (lamb, phi) en rad, h ne nous interesse pas pour la suite
    """
    r = np.sqrt(X**2 + Y**2 + Z**2)
    mu = np.arctan(Z/((X**2 + Y**2)**(1/2))*((1-f_e)+(a_e*e_e2)/r))
    lamb = 2*np.arctan(Y/(X + ((X**2 + Y**2)**(1/2))))
    phi = np.arctan((Z*(1-f_e) + e_e2*a_e*np.sin(mu)**3)/((1-f_e)*(np.sqrt(X**2 + Y**2) - e_e2*a_e*np.cos(mu)**3)))
    # h = (X**2 + Y**2)**(1/2)*np.cos(phi)+Z*np.sin(phi)-a_e*(1-e_e2*np.sin(phi)**2)**(1/2)
    return (lamb, phi) # en rad

def strain_magnitude(exx, eyy, exy):
    """
    :param exx: composante en xx du tenseur de taux de deformation horizontale (en nanostrain/an)
    :param eyy: composante en yy du tenseur de taux de deformation horizontale (en nanostrain/an)
    :param exy: composante en xy du tenseur de taux de deformation horizontale (en nanostrain/an)
    :return strain_magnitude: la magnitude de deformation du point (en nanostrain/an)
    """
    strain_magnitude = (exx**2 + eyy**2 + 2*exy**2)**(1/2)
    return strain_magnitude

######## Creation of the DataFrame from GNSS ITR2020 file #########

def read_gnss():
    """
    Cree 2 dataframes a partir du fichier ITRF2020_GNSS.SSC.txt, df_gnss_c le df des coordonnees et df_gnss_s le df des vitesses.
   :return df_gnss_c, df_gnss_s:
    """
    df = pd.read_fwf("data/ITRF2020_GNSS.SSC.txt", skiprows=7,
        colspecs=[
            (0, 9),      # DOMES_NB
            (10, 25),     # SITE_NAME
            (26, 30),     # TECH
            (32, 36),     # ID
            (37, 50),     # X_or_Vx
            (51, 64),     # Y_or_Vy
            (65, 78),     # Z_or_Vz
            (79, 85),     # Sigma1
            (86, 92),     # Sigma2
            (93, 99),    # Sigma3
            (101, 102),   # SOLN
            (103, 157),   # DATA_START
            (116, None)   # DATA_END
            ],
        names=['DOMES_NB', 'SITE_NAME', 'TECH', 'ID', 'X_Vx', 'Y_Vy', 'Z_Vz','Sigma1', 'Sigma2', 'Sigma3', 'SOLN', 'DATA_START', 'DATA_END']
            )

    df_gnss_s = df[(df['ID'].isna())].copy().reset_index(drop=True) # creates a new df with all the rows for which "SITE_NAME" is empty = all of our speeds
    df_gnss_s = df_gnss_s.rename(columns={'X_Vx': 'Vx', 'Y_Vy': 'Vy', 'Z_Vz': 'Vz'})
    df_gnss_c = df[(df['ID'].notna())].copy().reset_index(drop=True) # creates a new df with all the rows for which "SITE_NAME" is not empty = all of our coords
    df_gnss_c = df_gnss_c.rename(columns={'X_Vx': 'X', 'Y_Vy': 'Y', 'Z_Vz': 'Z'})
    df_gnss_s[['SITE_NAME', 'TECH', 'ID']] = df_gnss_c[['SITE_NAME', 'TECH', 'ID']].values
    df_gnss_c = df_gnss_c[(df_gnss_c['DATA_END'].isna()) | df_gnss_c['DATA_END'].str.contains('00:000:00000', na=False)] # only keeps rows for which the station is still active

    # Get indexes of coords rows
    speed_indices = df_gnss_c.index

    # Filter df_speeds using those indices
    df_gnss_s = df_gnss_s.loc[speed_indices].reset_index(drop=True)
    df_gnss_c = df_gnss_c.reset_index(drop=True)

    # Remove 'DATA_START' and 'DATA_END' cols from the speed df
    df_gnss_s = df_gnss_s.drop(columns=['DATA_START', 'DATA_END'])

    # Convert numeric columns to float
    numeric_cols = ['X', 'Y', 'Z']
    for col in numeric_cols:
        df_gnss_c[col] = pd.to_numeric(df_gnss_c[col], errors='coerce')


    # Creation of new cols using vectorized calculations
    lamb_rad, phi_rad = xyz_to_llh(df_gnss_c['X'], df_gnss_c['Y'], df_gnss_c['Z'])
    df_gnss_c['lamb_rad'] = lamb_rad
    df_gnss_c['phi_rad'] = phi_rad
    df_gnss_c['lamb_deg'] = lamb_rad * 180 / np.pi
    df_gnss_c['phi_deg'] = phi_rad * 180 / np.pi

    return df_gnss_c, df_gnss_s


######## Creation of the DataFrame from the GEM Strain Rate Model #########

def create_gem_file():
    """
    Creates a new file called GEM_filtered.csv based on the GSRM_strain.txt file. This new file is a filtered version (much smaller)
    """
    df_gem = pd.read_fwf("data/GSRM_strain.txt",skiprows=24)
    df_gem = df_gem.rename(columns={'#lat': 'lat'})

    # converts the azi_e1 col that was of type object to float64
    numeric_cols = ['azi_e1']
    for col in numeric_cols:
        df_gem[col] = pd.to_numeric(df_gem[col], errors='coerce')

    df_gem['strain_mag'] = strain_magnitude(df_gem['exx'], df_gem['eyy'], df_gem['exy']) # creates a new col with the strain magnitude
    df_gem = df_gem[df_gem['strain_mag']>=50] # only keep points with strain_mag >= 20, others are considered stable.

    # Trier par strain_mag décroissant, puis supprimer les doublons en ne gardant que le plus haut strain_mag
    df_gem = df_gem.sort_values('strain_mag', ascending=False).drop_duplicates(subset=['lat', 'long'], keep='first')

    # Creation of the new file
    df_gem.to_csv('GEM_filtered.csv', index=False)

    return


def read_gem():
    """
    Reads the GEM_filtered.csv file and returns it as a df.

    :return df_gem: pd.df
    """
    df_gem = pd.read_csv("data/GEM_filtered.csv")
    return df_gem


######## Creation of the DataFrame from the pmm_itrf.txt #########

def read_pmm():
    """
    Reads the pmm.itrf.txt file to a df.

    :return df_pmm: the df created
    """
    df_pmm = pd.read_csv(
        "data/pmm_itrf.txt",
        sep=r'\s+',  # Séparer par n'importe quel espace/tab
        skiprows=3,  # Sauter les lignes d'en-tête
        names=['Plate', 'Name', 'NS', 'wx', 'wy', 'wz', 'w', 'T_x', 'T_y', 'swx', 'swy', 'swz', 'sw']
    )
    df_pmm['Name'] = df_pmm['Name'].str.replace('_', ' ') # makes sure that "North_America" and "South_America" ar spelled "North America" and "South America" as in the dict
    return df_pmm

######## Creation of the DataFrame from the Tectonic_Plates.geojson #########

def read_plates():
    df_pmm = read_pmm()
    plates_in_df = df_pmm['Name'].to_list()
    with open("data/Tectonic_Plates.geojson", "r") as f:
        Tectonic_Plates = json.load(f)

    dict_plates = {}

    for feature in Tectonic_Plates['features']:
        # Extraire le nom de la plaque
        plate_name = feature['properties']['PlateName']

        # Extraire le type de geom
        geom_type = feature['geometry']['type']

        # Extraire les coordonnées du polygone
        coordinates = feature['geometry']['coordinates']

        plate_polygons = []  # list of DataFrames for this plate

        if geom_type == 'Polygon':
                # One polygon → one exterior ring
                exterior_ring = coordinates[0]
                lons, lats, hs = zip(*exterior_ring)

                plate_polygons.append(pd.DataFrame({
                    'lon': lons,
                    'lat': lats,
                    'h': hs
                }))

        elif geom_type == 'MultiPolygon':
            # Multiple polygons → multiple exterior rings
            for polygon in coordinates:
                exterior_ring = polygon[0]
                lons, lats, hs = zip(*exterior_ring)

                plate_polygons.append(pd.DataFrame({
                    'lon': lons,
                    'lat': lats,
                    'h': hs
                }))
        dict_plates[plate_name] = plate_polygons

    dict_plates = {plate: df_coords for plate, df_coords in dict_plates.items() if plate in plates_in_df}
    return dict_plates

if __name__ == "__main__":

    # 1.1


    print("DataFrame - df_coords :")
    print(df_gnss_c)
    print("DataFrame - df_speeds :")
    print(df_speeds)


    # 1.2

    """
    print("DataFrame - GEM Strain Rate Model :")
    print(df_GEM)
    """

    # 1.3

    """
    fig, ax = plt.subplots(figsize=(10, 6))

    for plate_name, polygons in dict_plates.items():
        for df in polygons:
            ax.fill(
                df['lon'],
                df['lat'],
                facecolor='lightgray',   # fill color
                edgecolor='black',       # border color
                linewidth=2.0,
                alpha=0.6)
    plt.show()
    """
