"""
This python script updates the exoplanet catalog by querying the NASA Exoplanet Archive.
The script reduces the table to include only the columns of interest and saves the table in the ECSV format.
"""
from astroquery.ipac.nexsci.nasa_exoplanet_archive import NasaExoplanetArchive

# load the current catalog of confirmed exoplanets
exoplanets_table = NasaExoplanetArchive.query_criteria(table="pscomppars", select="*")

exoplanets_table_selected_columns = exoplanets_table['ra','dec','pl_name', 'hostname','pl_orbeccen', 'pl_orbsmax','pl_orbper','st_mass',
                                                    'pl_bmassj', 'pl_radj', 'pl_dens', 'pl_eqt', 'st_rad', 'st_teff', 'sy_gaiamag']

exoplanets_table_selected_columns.write("confirmed_exoplanets_table_test.ecsv", format="ascii.ecsv", overwrite=True)