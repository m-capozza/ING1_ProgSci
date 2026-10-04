# Analyse des vitesses de plaques tectoniques par GNSS

Projet Python dans le cadre du cours de programmation scientifique de première année à Géodata Paris. 
Traitement et visualisation des données de stations GNSS (Global Navigation Satellite System) mondiales dans le cadre de la cinématique des plaques tectoniques. Le pipeline assigne les stations aux plaques tectoniques, identifie celles situées dans des zones de déformation active, calcule les vitesses rigides prédites et produit des sorties cartographiques.

> **Auteurs :** Matteo CAPOZZA, Paloma PIRES-GODART

---

## Table des matières

- [Présentation du projet](#présentation-du-projet)
- [Structure du projet](#structure-du-projet)
- [Sources de données](#sources-de-données)
- [Installation](#installation)
- [Utilisation](#utilisation)
- [Description des modules](#description-des-modules)
- [Résumé du pipeline](#résumé-du-pipeline)
- [Sorties](#sorties)

---

## Présentation du projet

Ce projet implémente un pipeline complet de traitement de données géophysiques :

1. **Lecture** des coordonnées et vitesses des stations GNSS depuis le jeu de données ITRF2020, des géométries de plaques tectoniques depuis un fichier GeoJSON, d'un modèle de mouvement de plaques (PMM) et d'un modèle de taux de déformation (GEM).
2. **Attribution** de chaque station GNSS à une plaque tectonique via un algorithme de point-dans-polygone par ray casting.
3. **Marquage** des stations situées dans des zones de déformation crustale active, avec un seuil de proximité de 50 km vis-à-vis du modèle GEM.
4. **Prédiction** de la vitesse rigide de plaque pour les stations stables, à partir du vecteur de vitesse angulaire issu du PMM.
5. **Conversion** des vitesses cartésiennes en composantes angulaires (longitude/latitude) pour l'affichage cartographique.
6. **Visualisation** des résultats sur des cartes mondiales avec Cartopy.

---

## Structure du projet

```
.
├── ProgSci_CAPOZZA_PIRESGODART.pdf   # Rapport de projet
└── src/
    ├── main.py          # Point d'entrée — exécute le pipeline complet
    ├── partie_1.py      # Lecture des données et conversion de coordonnées
    ├── partie_2.py      # Attribution des plaques (ray casting)
    ├── partie_3.py      # Détection des zones de déformation (distance de Haversine)
    ├── partie_4.py      # Calcul des vitesses prédites et conversion de vitesses
    ├── partie_5.py      # Visualisations cartographiques avec Cartopy
    └── data/
        ├── ITRF2020_GNSS.SSC.txt     # Coordonnées et vitesses des stations GNSS
        ├── GEM_filtered.csv          # Points GEM pré-filtrés
        ├── GSRM_strain.txt           # Modèle brut GEM Global Strain Rate
        ├── pmm_itrf.txt              # Modèle de mouvement de plaques (vitesses angulaires)
        └── Tectonic_Plates.geojson   # Polygones des limites de plaques tectoniques
```

---

## Sources de données

| Jeu de données | Fichier | Description |
|---|---|---|
| **ITRF2020 GNSS** | `ITRF2020_GNSS.SSC.txt` | Référentiel Terrestre International 2020 — positions XYZ et vitesses XYZ des stations |
| **GEM Taux de déformation** | `GSRM_strain.txt` / `GEM_filtered.csv` | Modèle mondial de taux de déformation — composantes du tenseur de déformation horizontale sur une grille globale |
| **Modèle de mouvement de plaques** | `pmm_itrf.txt` | Vecteurs de vitesse angulaire (wx, wy, wz) pour chaque grande plaque tectonique dans le référentiel ITRF |
| **Limites de plaques** | `Tectonic_Plates.geojson` | Géométries polygonales GeoJSON des plaques tectoniques |

---

## Installation

### Prérequis

- Python 3.9+
- numpy
- pandas
- matplotlib
- cartopy

### Installer les dépendances

```bash
pip install numpy pandas matplotlib cartopy
```

> **Note sur Cartopy :** Cartopy nécessite des dépendances système (GEOS, PROJ). Sous Linux : `sudo apt install libgeos-dev libproj-dev`. Sous macOS avec Homebrew : `brew install geos proj`. Voir le [guide d'installation Cartopy](https://scitools.org.uk/cartopy/docs/latest/installing.html) pour plus de détails.

---

## Utilisation

Lancer le pipeline complet depuis le répertoire `src/` :

```bash
cd src
python main.py
```

Cela va :
- Charger et parser tous les jeux de données
- Assigner chaque station GNSS à sa plaque tectonique
- Identifier les stations en zone de déformation
- Calculer les vitesses rigides prédites
- Convertir les vitesses en composantes angulaires
- Afficher un résumé du DataFrame traité

Pour générer et sauvegarder les cartes, décommenter le bloc de visualisation en bas de `main.py`.

Il est également possible d'exécuter chaque module individuellement pour des tests :

```bash
python partie_1.py   # Tester la lecture des données
python partie_4.py   # Tester le calcul des vitesses
python partie_5.py   # Tester la génération des cartes
```

---

## Description des modules

### `partie_1.py` — Lecture des données

Gère la lecture de tous les fichiers et la conversion des coordonnées.

- `xyz_to_llh(X, Y, Z)` — Convertit les coordonnées cartésiennes géocentriques (X, Y, Z) en coordonnées géographiques (λ, φ) en radians, en utilisant les paramètres de l'ellipsoïde GRS80.
- `strain_magnitude(exx, eyy, exy)` — Calcule la magnitude scalaire de déformation à partir des composantes du tenseur de taux de déformation horizontale (en nanostrain/an).
- `read_gnss()` — Parse `ITRF2020_GNSS.SSC.txt` en deux DataFrames : un pour les coordonnées des stations (`df_gnss_c`) et un pour leurs vitesses (`df_gnss_s`). Filtre pour ne conserver que les stations actuellement actives.
- `create_gem_file()` — Lit `GSRM_strain.txt`, calcule les magnitudes de déformation, filtre les points avec une déformation ≥ 50 nanostrain/an et écrit le résultat dans `GEM_filtered.csv`.
- `read_gem()` — Lit le fichier pré-filtré `GEM_filtered.csv`.
- `read_pmm()` — Lit `pmm_itrf.txt` dans un DataFrame des vitesses angulaires de plaques.
- `read_plates()` — Lit `Tectonic_Plates.geojson` et retourne un dictionnaire associant les noms de plaques à des listes de DataFrames de polygones, filtré aux seules plaques présentes dans le PMM.

---

### `partie_2.py` — Attribution des plaques

Détermine à quelle plaque tectonique appartient chaque station GNSS.

- `ray_casting(point, polygon)` — Implémente l'algorithme de lancer de rayon pour tester si un point est à l'intérieur d'un polygone. Inclut une vérification rapide par boîte englobante pour l'efficacité.
- `find_plate_for_row(row, plates_data)` — Applique le ray casting sur tous les polygones de plaques pour une ligne de station donnée.
- `which_plate(df_stations, dict_plates)` — Applique `find_plate_for_row` sur l'ensemble du DataFrame. Pré-calcule les boîtes englobantes de chaque polygone. Ajoute une colonne `plate` au DataFrame. Les stations n'appartenant à aucune plaque sont étiquetées `"Unknown"`.

---

### `partie_3.py` — Détection des zones de déformation

Identifie les stations situées à proximité de zones de déformation crustale active.

- `haversine(φ1, λ1, φ2, λ2)` — Calcule la distance orthodromique (en km) entre deux points exprimés en radians, via la formule de Haversine avec un rayon terrestre de 6378 km.
- `check_station(row, gem_lats, gem_lons)` — Vérification vectorisée : retourne `True` si la station est à moins de 50 km d'un point du modèle GEM.
- `calculate_in_deformation(df_gnss_c, df_gem)` — Applique `check_station` à chaque station et ajoute une colonne booléenne `in_deformation` au DataFrame.

---

### `partie_4.py` — Calcul des vitesses

Calcule les vitesses rigides prédites et convertit les vitesses cartésiennes en composantes angulaires.

- `v_predite(omega, r, T)` — Calcule le vecteur vitesse prédit à la position `r` pour une plaque de vitesse angulaire `omega` et de translation `T`, selon la formule : **v** = **ω** × **r** + **T**.
- `calculate_v_pred(df_gnss, df_pmm)` — Pour chaque station stable (hors zone de déformation, plaque connue), récupère la vitesse angulaire de la plaque dans le PMM et stocke la norme de la vitesse prédite dans une colonne `v_pred`.
- `cartesian_to_angular_velocities(df_gnss, df_gnss_s)` — Convertit les composantes de vitesse cartésiennes (Vx, Vy, Vz) en composantes Est-Nord-Haut (ENU) via une matrice de rotation, puis en composantes de vitesse angulaire (Vλ, Vφ) en degrés/an. Ajoute les colonnes `Vlamb_deg` et `Vphi_deg`.

---

### `partie_5.py` — Visualisation

Produit des cartes mondiales avec Cartopy en projection de Robinson.

- `plot_plates_cartopy(plates, ax, ...)` — Trace les limites des plaques tectoniques sur un axe Cartopy.
- `plot_gnss_stations_cartopy(df_gnss, ax, ...)` — Représente les stations GNSS sous forme de nuage de points sur un axe Cartopy.
- `plot_simple_map(plates, df_gnss, ...)` — Carte mondiale affichant toutes les stations GNSS sur les limites de plaques.
- `plot_gnss_by_plate_cartopy(plates, df_gnss, ...)` — Stations colorées par plaque tectonique assignée (palette tab20).
- `plot_gnss_by_deformation_cartopy(plates, df_gnss, ...)` — Stations colorées en vert (stables) ou en rouge (en zone de déformation).
- `plot_velocity_vectors_cartopy(plates, df_gnss, ...)` — Vecteurs vitesse globaux tracés avec `quiver`.
- `plot_velocity_vectors_by_plate_cartopy(plates, df_gnss, ...)` — Vecteurs vitesse colorés par plaque.
- `save_figure(fig, filename, dpi, ...)` — Sauvegarde une figure matplotlib sur le disque.

---

## Résumé du pipeline

```
ITRF2020_GNSS.SSC.txt
        │
        ▼
  partie_1.read_gnss()
  ┌─────────────────────┐
  │  df_gnss_c          │  coords XYZ → (λ, φ) en deg/rad
  │  df_gnss_s          │  vitesses XYZ
  └─────────────────────┘
        │
        ▼
  partie_2.which_plate()               ← Tectonic_Plates.geojson
        │  ajoute : plate
        ▼
  partie_3.calculate_in_deformation()  ← GEM_filtered.csv
        │  ajoute : in_deformation
        ▼
  partie_4.calculate_v_pred()          ← pmm_itrf.txt
        │  ajoute : v_pred
        ▼
  partie_4.cartesian_to_angular_velocities()
        │  ajoute : Vlamb_deg, Vphi_deg
        ▼
  partie_5.plot_*()
        │
        ▼
   Sorties PNG
```

---

## Sorties

Lorsque le bloc de visualisation de `main.py` est activé, trois fichiers PNG sont générés :

| Fichier | Description |
|---|---|
| `map_simple.png` | Toutes les stations GNSS sur les limites de plaques tectoniques |
| `map_by_plate.png` | Stations colorées par plaque assignée |
| `map_by_deformation.png` | Stations colorées selon leur statut de déformation |

Des cartes de vecteurs vitesse supplémentaires peuvent être produites en appelant `plot_velocity_vectors_cartopy` ou `plot_velocity_vectors_by_plate_cartopy` depuis `partie_5.py`.
