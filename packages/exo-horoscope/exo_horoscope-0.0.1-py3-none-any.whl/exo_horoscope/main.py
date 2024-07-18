from astroquery.ipac.nexsci.nasa_exoplanet_archive import NasaExoplanetArchive
from astropy.time import Time
from astropy.coordinates import EarthLocation, AltAz, SkyCoord
import astropy.units as u
from geopy import geocoders  
from geopy.geocoders import Nominatim
from datetime import datetime
import numpy as np

class User(object):
    """
    User class
    """

    def __init__(self, user, citystate, year, month, day, hour, minute, second):
        """
        Args:
        name (str): Name of User
        citystate (str): City and State of birth in the form: 'City State'
        year (int): Birthyear of User
        month (int): Birthmonth of User
        day (int): Birthday of User
        hour (int): Birthhour of User
        minute (int): Birthminute of User
        second (int): Birthsecond of User
        """
        self.user = user

        self.citystate = citystate

        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        time = Time(datetime(self.year, self.month, self.day, self.hour, self.minute, self.second))
        self.time = time

        self.closest_object_nasa_table = self.get_closest_table()

    def get_closest_table(self):
            
        geolocator = Nominatim(user_agent='moeur')
        location = geolocator.geocode(self.citystate)
        date_time = datetime(self.year, self.month, self.day, self.hour, self.minute, self.second)
        self.birth_lat, self.birth_lon = location[1][0], location[1][1]
        zen_ra, zen_dec = self.get_zenith()
        # need to add a check if 4 degrees are not enough
        table = NasaExoplanetArchive.query_region(table="ps", coordinates=SkyCoord(zen_ra, zen_dec), radius=4 * u.deg)
        coords = SkyCoord(zen_ra, zen_dec, unit=(u.deg, u.deg))
        stars_coords = SkyCoord(table['ra'], table['dec'], unit=(u.deg, u.deg))
        distances = coords.separation(stars_coords)
        closest_index = distances.argmin()
        closest_object = table[closest_index]
        closest_table = NasaExoplanetArchive.query_object(closest_object['pl_name'])
        return closest_table
        

    def get_zenith(self):
       """
       Get zenith coordinates
       """

       location = EarthLocation(lat=self.birth_lat, lon=self.birth_lon)
       zenith = SkyCoord(alt=90*u.deg, az=0*u.deg, frame=AltAz(obstime=self.time, location=location))
       zenith_radec = zenith.transform_to('icrs')
       
       return zenith_radec.ra, zenith_radec.dec



    def map_eccentricity_to_trait(self):
        if self.eccentricity == 0:
            return "are perfectly stable"
        elif 0 < self.eccentricity < 0.3:
            return "prefer stability"
        elif 0.3 <= self.eccentricity < 0.6:
            return "are balanced"
        elif 0.6 <= self.eccentricity < 0.9:
            return "prefer excitement"
        else:
            return "embrace change"

    def map_semimajor_axis_to_trait(self):
        if self.semimajor_axis < 0.1:
            return "are 'close to the action' and constantly influenced by your star's energy, suggesting a very outgoing and active nature"
        elif 0.1 <= self.semimajor_axis < 1:
            return "are still within a region of significant stellar influence, indicating a generally social and engaging character"
        elif 1 <= self.semimajor_axis < 5:
            return "strike a balance between the inner and outer regions, reflecting a well-rounded personality that is equally comfortable in social situations and solitude"
        elif 5 <= self.semimajor_axis < 30:
            return "are farther from the star, implying a more reserved and introspective nature, preferring less direct interaction"
        else:
            return "are on the outskirts, indicating a highly introspective and solitary disposition, thriving in their own space away from the hustle and bustle"

    def map_orbital_period_to_trait(self):
        if self.period < 10:
            return "rapid orbits suggest a fast-paced and reactive thinking style"
        elif 10 <= self.period < 100:
            return "orbits allow for rapid changes and adaptation, indicating an active and adaptive thinking style"
        elif 100 <= self.period < 365:
            return "orbital periods tend to experience balanced conditions, suggesting a balanced and analytical thinking style"
        elif 365 <= self.period < 3650:
            return "planets take longer to orbit their stars, implying a more deliberate and thoughtful approach"
        else:
            return "very long orbital periods embody a reflective and contemplative thinking style"

    def map_stellar_mass_to_trait(self):
        if self.stellar_mass < 0.5:
            return "stable and enduring"
        elif 0.5 <= self.stellar_mass < 1.5:
            return "balanced and nurturing"
        elif 1.5 <= self.stellar_mass < 3:
            return "dynamic and charismatic"
        else:
            return "intense and transformative"
        
    def get_horoscope(self):
        self.planet = self.closest_object_nasa_table['pl_name'][0]
        self.star = self.closest_object_nasa_table['hostname'][0]
        self.eccentricity = np.nanmean(self.closest_object_nasa_table["pl_orbeccen"])
        self.semimajor_axis = np.nanmean(np.asarray(self.closest_object_nasa_table["pl_orbsmax"].value))
        self.period = np.nanmean(np.asarray(self.closest_object_nasa_table["pl_orbper"].value))
        self.stellar_mass = np.nanmean(np.asarray(self.closest_object_nasa_table["st_mass"].value))
        eccentricity_trait = self.map_eccentricity_to_trait()
        axis_trait = self.map_semimajor_axis_to_trait()
        period_trait = self.map_orbital_period_to_trait()
        stellar_mass_trait = self.map_stellar_mass_to_trait()

        message = (f"{self.user}, your birth exoplanet is {self.planet} orbiting star {self.star}. "
                f"Based on an eccentricity of {self.eccentricity:.2f}, you {self.map_eccentricity_to_trait()}. "
                f"With an orbit semi-major axis of {self.semimajor_axis:.2f} AU, you {self.map_semimajor_axis_to_trait()}. "
                f"With a birth exoplanet period of {self.period:.2f} days, these {self.map_orbital_period_to_trait()}, "
                f"and with a stellar mass of {self.stellar_mass:.2f} solar masses, you are {self.map_stellar_mass_to_trait()}.")
        return message

