import numpy as np
import pandas as pd

def ray_casting(point, polygon):
    """
    Utilise la méthode du ray casting pour savoir si un point appartient à un polygon. Parité du nombre d'intersections.
    :param point: tuple (coord lat, coord long), le point a etudier
    :param polygon: list de tuple [(x1, y1), (x2,y2), ...], le polygon
    :return bool: True si dans le polygon, False sinon
    """

    x_p, y_p = point

    # check if point is outside greater box
    x_min = min(p[0] for p in polygon)
    x_max = max(p[0] for p in polygon)
    y_min = min(p[1] for p in polygon)
    y_max = max(p[1] for p in polygon)
    if x_p < x_min or x_p > x_max or y_p < y_min or y_p > y_max:
        return False

    intersections = 0
    # point is in greater box
    for i in range(0, len(polygon)):
        x_a, y_a = polygon[i]
        x_b, y_b = polygon[(i+1)% len(polygon)]

        if y_p < max(y_a, y_b):
            if y_p >= min(y_a, y_b):
                if x_p <= max(x_a, x_b):
                    x_intersect = (y_p - y_a) * (x_b - x_a) / (y_b - y_a) + x_a
                    if x_p <= x_intersect:
                        intersections += 1
    if intersections % 2 == 0:
        return False
    else:
        return True

def find_plate_for_row(row, plates_data):
    """
    Applies the ray casting function to a row of the df_gnss_c for all plates. Returns the name of the plate.
    """
    # Accessing your specific column names
    lon_val = row['lamb_deg']
    lat_val = row['phi_deg']
    point = (lon_val, lat_val)

    for plate_name, polygons in plates_data.items():
        for poly_info in polygons:
            lon_min, lon_max, lat_min, lat_max = poly_info['bbox']

            # Fast BBox check: is the station even near this plate?
            if lon_min <= lon_val <= lon_max and lat_min <= lat_val <= lat_max:
                # Detailed Ray Casting check
                if ray_casting(point, poly_info['coords']):
                    return plate_name
    return "Unknown"

def which_plate(df_stations, dict_plates):
    """
    Assigns a plate name to each GNSS station using specific coordinate names.
    """
    # 1. Prepare plates (Pre-calculating Bounding Boxes once)
    plates_data = {}
    for plate_name, list_of_dfs in dict_plates.items():
        polygons = []
        for df in list_of_dfs:
            coords = [tuple(row) for row in df[['lon', 'lat']].to_numpy().tolist()]
            lons = [p[0] for p in coords]
            lats = [p[1] for p in coords]
            polygons.append({
                'coords': coords,
                'bbox': (min(lons), max(lons), min(lats), max(lats))
            })
        plates_data[plate_name] = polygons

    # 2. Apply the logic
    df_stations['plate'] = df_stations.apply(lambda row: find_plate_for_row(row, plates_data), axis=1)
    return df_stations

if __name__ == "__main__":
