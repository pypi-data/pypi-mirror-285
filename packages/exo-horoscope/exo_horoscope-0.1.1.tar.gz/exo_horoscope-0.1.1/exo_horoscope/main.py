from astropy.time import Time
from astropy.coordinates import EarthLocation, AltAz, SkyCoord
import astropy.units as u
from geopy.geocoders import Nominatim
import numpy as np
from astropy.io import ascii
import warnings
import importlib.resources

import os

#file_path = "confirmed_exoplantes_table.ecsv"

with importlib.resources.path('exo_horoscope', 'main.py') as package_root_path:
    package_root = package_root_path.parent

catalog_path = os.path.join(package_root, 'confirmed_exoplanets_table.ecsv')

if not os.path.exists(catalog_path):
   from exo_horoscope import update_exoplanet_catalog
   print(catalog_path)

with importlib.resources.path('exo_horoscope', 'confirmed_exoplanets_table.ecsv') as catalog_path:
    exoplanets_table = ascii.read(catalog_path)



class User(object):
    """
    User class
    """

    def __init__(self, user, citystate, year, month, day, hour, minute, second):
        """
        Args:
            user (str): User's name in the form 'User'
            citystate (str): City and State of birth in the form: 'City State' / 'City Country'
            year (int): Birthyear of User
            month (int): Birthmonth of User
            day (int): Birthday of User
            hour (int): Birthhour of User
            minute (int): Birthminute of User
            second (float): Birthsecond of User
        """

        if not isinstance(user, str):
            raise TypeError("User name must be a string.")

        if not isinstance(citystate, str):
            raise TypeError("City State / City Country must be a string.")

        if not isinstance(year, int):
            raise TypeError("Year must be an integer.")

        if year<=0:
            raise ValueError("Year must be a positive integer.")
        
        if not isinstance(month, int):
            raise TypeError("Month must be an integer.")
        if month<=0 or month>12:
            raise ValueError("Month must be an integer between 1 and 12.")
        
        if not isinstance(day, int):
            raise TypeError("Day must be an integer.")
        if day<=0 or day>31:
            raise ValueError("Day must be an integer between 1 and 31.")
        
        if not isinstance(hour, int):
            raise TypeError("Hour must be an integer.")
        if hour<0 or hour>23:
            raise ValueError("Hour must be an integer between 0 and 23.")
        
        if not isinstance(minute, int):
            raise TypeError("Minute must be an integer.")
        if minute<0 or minute>59:
            raise ValueError("Minute must be an integer between 0 and 59.")
        
        if not isinstance(second, (int, float)):
            raise TypeError("Second must be a float or an integer.")
        if second < 0 or second >= 60:
            raise ValueError("Second must be a float or an integer between 0 and 60.")
            raise TypeError("Second must be a float.")
        if second<0 or second>=60:
            raise ValueError("Second must be a float between 0 and 60.")

        
        self.user = user

        self.citystate = citystate

        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            date_and_time = Time(f'{self.year}-{self.month}-{self.day} {self.hour}:{self.minute}:{self.second}')
        self.time = date_and_time
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.closest_object_nasa_table = self.get_closest_table()

        self.planet = self.closest_object_nasa_table['pl_name']
        self.star = self.closest_object_nasa_table['hostname']



    def get_closest_table(self):
        """
        Get table of closest object

        This method finds the Nasa Exoplanet Archive table of the object which transits nearest birth zenith of the user.

        Args:
            citystate (str): City and State of birth in the form: 'City State'
            year (int): Birthyear of User
            month (int): Birthmonth of User
            day (int): Birthday of User
            hour (int): Birthhour of User
            minute (int): Birthminute of User
            second (float): Birthsecond of User

        Returns:
            astropy.table.table.QTable: table of closest object to birth zenith
        """
            
        geolocator = Nominatim(user_agent='moeur')
        location = geolocator.geocode(self.citystate)
        self.birth_lat, self.birth_lon = location[1][0], location[1][1]
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            coords = self.get_zenith()
            stars_coords = SkyCoord(exoplanets_table['ra'], exoplanets_table['dec'], unit=(u.deg, u.deg))
        distances = coords.separation(stars_coords)
        closest_index = distances.argmin()
        closest_table = exoplanets_table[closest_index]
        return closest_table
        
    def get_zenith(self):
        """
        Compute birth zenith

        This method takes latitude and longitude coordinates of the user's birth city and time of birth and calculates the celestial coordinates of the zenith.
        
        Returns:
            astropy.coordinates.sky_coordinate.SkyCoord: celestial coordinates of the zenith.
        """
        location = EarthLocation(lat=self.birth_lat, lon=self.birth_lon)
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            zenith = SkyCoord(alt=90*u.deg, az=0*u.deg, frame=AltAz(obstime=self.time, location=location))
            zenith_radec = zenith.transform_to('icrs')
        return zenith_radec



    def map_eccentricity_to_trait(self):
        """
        Map orbital eccentricity to personality trait

        This method assigns a personality trait to the user based on the value of their birth exoplanet's orbital eccentricity.

        Returns:
            str: the personality trait
        """
        if self.eccentricity == np.nan:
            return ""
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
        """
        Map orbital semimajor axis to personality trait

        This method assigns a personality trait to the user based on the value of their birth exoplanet's orbital semimajor axis.

        Returns:
            str: the personality trait
        """
        if self.semimajor_axis == np.nan:
            return ""
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
        """
        Map exoplanet system's orbital period to a personality trait (thinking style).

        Returns: 
            str: The personality trait text message.
        """
        if self.period == np.nan:
            return ""
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
        """
        Map exoplanet system's stellar mass to a personality trait.

        Returns:
            str: The personality trait based on the stellar mass.
        """

        if self.stellar_mass == np.nan:
            return ""
        if self.stellar_mass < 0.5:
            return "stable and enduring"
        elif 0.5 <= self.stellar_mass < 1.5:
            return "balanced and nurturing"
        elif 1.5 <= self.stellar_mass < 3:
            return "dynamic and charismatic"
        else:
            return "intense and transformative"
        
    def get_horoscope(self):
        """
        User class method to get the User's horoscope based on User's attributes.

        Returns:
            str: The horoscope message for the User.
        """
        self.eccentricity = np.nanmean(self.closest_object_nasa_table["pl_orbeccen"])
        self.semimajor_axis = np.nanmean(np.asarray(self.closest_object_nasa_table["pl_orbsmax"].value))
        self.period = np.nanmean(np.asarray(self.closest_object_nasa_table["pl_orbper"].value))
        self.stellar_mass = np.nanmean(np.asarray(self.closest_object_nasa_table["st_mass"].value))
        #self.planet_mass = np.nanmean(np.asarray(self.closest_object_nasa_table["pl_bmassj"].value))
        #self.planet_radius = np.nanmean(np.asarray(self.closest_object_nasa_table["pl_radj"].value))
        #self.planet_density = np.nanmean(np.asarray(self.closest_object_nasa_table["pl_dens"].value))
        #self.planet_temp = np.nanmean(np.asarray(self.closest_object_nasa_table["pl_eqt"].value))
        #self.stellar_magnitude = np.nanmean(np.asarray(self.closest_object_nasa_table["st_optmag"].value)) # I think this one is wrong
        #self.stellar_radius = np.nanmean(np.asarray(self.closest_object_nasa_table["st_rad"].value))
        #self.stellar_temp = np.nanmean(np.asarray(self.closest_object_nasa_table["st_teff"].value))


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


    def map_radius_to_life_suggestion(self):
        """
        Map planet radius to life suggestion.

        This method assigns a life suggestion to the user based on the value of their birth exoplanet's radius.

        Returns:
            string: the life suggestion
        """
        if self.radius == np.nan:
            return ""
        if self.radius < 1:
            return "focus on the little things; small steps can lead to big achievements"
        elif 1 <= self.radius < 2:
            return "find balance between ambition and contentment"
        elif 2 <= self.radius < 5:
            return "be bold and take on challenges head-on"
        else:
            return "aim high and don't be afraid to dream big"

    def map_magnitude_to_life_suggestion(self):
        """
        Map planet magnitude to life suggestion.

        This method assigns a life suggestion to the user based on the value of their birth exoplanet's magnitude.

        Returns:
            string: the life suggestion
        """
        if self.magnitude == np.nan:
            return ""
        if self.magnitude < 10:
            return "embrace your bright and positive nature"
        elif 10 <= self.magnitude < 15:
            return "find ways to shine even in the dark moments"
        else:
            return "be a guiding light for others around you"

    def map_density_to_life_suggestion(self):
        """
        Map planet density to life suggestion.

        This method assigns a life suggestion to the user based on the value of their birth exoplanet's density.

        Returns:
            string: the life suggestion
        """
        if self.density == np.nan:
            return ""
        if self.density < 3:
            return "keep a light-hearted and flexible approach to life"
        elif 3 <= self.density < 5:
            return "balance your seriousness with moments of joy"
        elif 5 <= self.density < 8:
            return "stay grounded and practical in your decisions"
        else:
            return "be resilient and unyielding in the face of challenges"

    def get_life_suggestions(self):
        """
        User class method to get the User's life suggestions based on exoplanet's orbital properties.

        Returns:
            str: The life suggestions message for the User.
        """
        self.radius = np.nanmean(np.asarray(self.closest_object_nasa_table["pl_radj"].value))
        self.magnitude = np.nanmean(np.asarray(self.closest_object_nasa_table["sy_gaiamag"].value))
        self.density = np.nanmean(np.asarray(self.closest_object_nasa_table["pl_dens"].value))
        radius_suggestion = self.map_radius_to_life_suggestion()
        magnitude_suggestion = self.map_magnitude_to_life_suggestion()
        density_suggestion = self.map_density_to_life_suggestion()

        message = (f"{self.user}, your birth exoplanet is {self.planet} orbiting star {self.star}. "
                f"Based on a radius of {self.radius:.2f} Jupiter radii, {radius_suggestion}. "
                f"With a magnitude of {self.magnitude:.2f}, {magnitude_suggestion}. "
                f"And with a density of {self.density:.2f} g/cm³, {density_suggestion}.")
        return message
    
    def get_lucky_numbers(self):
        """
        Generate lucky numbers based on the first two letters of the exoplanet and user names.

        Returns:
            str: A message with the lucky numbers and their corresponding adjectives.
        """
        # Dictionary to map letters to their positions in the alphabet
        letter_to_number = {chr(i + 96): i for i in range(1, 27)}

        # Function to get number from letter
        def letter_number(letter):
            return letter_to_number.get(letter.lower(), 0)

        # Function to get an adjective based on a number
        def number_to_adjective(number):
            adjectives = [
                "amazing", "brave", "creative", "dynamic", "elegant", "fearless", "graceful", "honest",
                "intelligent", "joyful", "kind", "lively", "mighty", "noble", "optimistic", "passionate",
                "quick", "radiant", "strong", "trustworthy", "unique", "vibrant", "wise", "youthful", "zealous"
            ]
            return adjectives[number % len(adjectives)]

        # Get the first two letters of the exoplanet and user names
        planet_letters = self.planet[:2].lower()
        user_letters = self.user[:2].lower()

        # Generate the lucky numbers
        lucky_numbers = [letter_number(letter) for letter in planet_letters + user_letters]

        # Generate the message with lucky numbers and adjectives
        lucky_numbers_message = ", ".join([f"{num} ({number_to_adjective(num)})" for num in lucky_numbers])

        message = f"Lucky numbers: {lucky_numbers_message}."
        return message