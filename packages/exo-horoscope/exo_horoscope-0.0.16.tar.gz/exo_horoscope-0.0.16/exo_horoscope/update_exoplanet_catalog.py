"""
This python script updates the exoplanet catalog by querying the NASA Exoplanet Archive.
The script reduces the table to include only the columns of interest and saves the table in the ECSV format.
"""
from astroquery.ipac.nexsci.nasa_exoplanet_archive import NasaExoplanetArchive
import importlib.resources
import os

with importlib.resources.path('exo_horoscope', 'update_exoplanet_catalog.py') as package_root_path:
    package_root = package_root_path.parent

output_file_path = os.path.join(package_root, 'confirmed_exoplanets_table.ecsv')

# load the current catalog of confirmed exoplanets
exoplanets_table = NasaExoplanetArchive.query_criteria(table="pscomppars", select="*")

exoplanets_table_selected_columns = exoplanets_table['ra','dec','pl_name', 'hostname','pl_orbeccen', 'pl_orbsmax','pl_orbper','st_mass',
                                                    'pl_bmassj', 'pl_radj', 'pl_dens', 'pl_eqt', 'st_rad', 'st_teff', 'sy_gaiamag']

exoplanets_table_selected_columns.write(output_file_path, format="ascii.ecsv", overwrite=True)