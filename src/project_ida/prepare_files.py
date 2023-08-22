import pandas as pd
import os

"""
Script to generate the files in the folder affect_area_files. 

The methods below show how the regular expressions are generated, how the affected cities are selected, and more
(almost) all files in the folder affect_area_files are made here, such that it can be reproduced, checked and changed easily
"""
def setup_us_city_files(path):
    """
    SETTING UP FILES FOR FOLDER: us_city_files
    """

    world_cities = pd.read_csv(os.path.join(path, "geonames-all-cities-with-a-population-1000.csv"),
                               usecols=["Name", "Country name EN"], header=0, sep=";")  # 140k global cities

    world_cities = world_cities.rename(columns={"Country name EN": "country"})
    world_non_us = world_cities[world_cities["country"] != "United States"]  # Remove US cities
    print("World cities (excluding US): ", len(world_non_us))

    us_cities = pd.read_excel(os.path.join(path, "uscities.xlsx"))  # 30k cities
    us_cities = us_cities[["city", "state_id", "state_name"]]
    us_cities = us_cities.rename(columns={"state_id": "state_abbrev", "state_name": "state"})
    print("US cities: ", len(us_cities))

    # SETTING UP FILES: only_US, non_only_US
    # These files will be used for the US regex file

    # Cities that only exist by name in the US
    only_us = pd.merge(us_cities, world_non_us, indicator=True, how='outer', left_on="city", right_on="Name").query(
        '_merge=="left_only"').drop('_merge', axis=1)

    # Drop duplicate cities because with these files we only want to know if a user lives in the US, and we do not
    # care about where exactly
    only_us = only_us.drop_duplicates(subset=["city"]).reset_index(drop=True)

    # Make a column "Name"
    only_us["Name"] = only_us.apply(lambda row: "{city}".format(city=row.city), axis=1)
    only_us = only_us[["Name", "city", "state", "state_abbrev"]]

    only_us.to_excel(os.path.join(path, "only_US.xlsx"))
    print("US cities only in US: ", len(only_us))

    # Cities that also exist by name elsewhere in the world.
    non_only_us = us_cities.merge(world_non_us, left_on="city", right_on="Name")

    # Drop duplicate city and states because for cities not unique to the US, we care about the combinations of (city, state)
    non_only_us = non_only_us.drop_duplicates(subset=["city", "state"]).reset_index(drop=True)
    non_only_us["Name"] = non_only_us.apply(
        lambda row: "{city}, {abbrev}".format(city=row.city, abbrev=row.state_abbrev), axis=1)
    non_only_us = non_only_us[["Name", "city", "state", "state_abbrev"]]

    non_only_us.to_excel(os.path.join(path, "non_only_US.xlsx"))
    print("US cities that also exist elsewhere in the world: ", len(non_only_us))

def setup_ida_files(path):
    """
    SETTING UP FILES FOR FOLDER: Ida_files
    """

    us_cities = pd.read_excel("/Users/arneeichholtz/Documents/MIT/affect_area_files/us_city_files/uscities.xlsx")
    us_cities = us_cities[["city", "state_id", "state_name", "county_name"]]
    aff_counties = pd.read_excel(os.path.join(path, "Counties Hurricane Ida.xlsx"))

    aff_cities = pd.merge(aff_counties, us_cities, left_on=["state", "county"], right_on=["state_name", "county_name"])
    aff_cities = aff_cities[["state", "county", "city", "state_id"]]
    aff_cities = aff_cities.rename(columns={"state_id": "state_abbrev"})

    # Add a column "Name" with city and state abbreviation (like New Orleans, LA) because this will be the location name
    aff_cities["Name"] = aff_cities.apply(lambda row: row.city+", "+row.state_abbrev, axis=1)

    # Affected cities to csv
    aff_cities.to_csv(os.path.join(path, "aff_cities.csv"))
    print("Cities affected by Ida: ", len(aff_cities))

    # Find affected north and write to csv
    north = aff_cities[aff_cities["state"].isin(["New Jersey", "Pennsylvania", "New York", "Connecticut", "Delaware"])]
    north.to_csv(os.path.join(path, "north.csv"))

    # Find affected south and write to csv
    south = aff_cities[aff_cities["state"].isin(["Mississippi", "Louisiana"])]
    south.to_csv(os.path.join(path, "south.csv"))


    # FINDING UNIQUE CITIES IN THE US
    # We make a distinction between unique and non unique cities because the regex is different

    # Cities that are unique in the US (ie, appear only once)
    unique_us = us_cities.drop_duplicates(subset=["city"], keep=False)

    # Find the cities that are unique in the US (ie, appear only once) and are affected by Ida
    unique_ida = aff_cities.merge(unique_us, left_on="city", right_on="city")
    print("Cities unique in US and affected by Ida: ", len(unique_ida))
    unique_ida = unique_ida[["Name", "state", "city", "state_abbrev"]]
    unique_ida.to_excel(os.path.join(path, "unique_Ida.xlsx"))

    # Find the cities that are not unique (ie, appear multiple times in the US) and are affected by Ida
    non_unique_ida = pd.merge(aff_cities, unique_ida, indicator=True, how='outer').query('_merge=="left_only"').drop(
        '_merge', axis=1)
    print("Cities NOT unique in US and affected by Ida: ", len(non_unique_ida))
    non_unique_ida = non_unique_ida[["Name", "state", "city", "state_abbrev"]]
    non_unique_ida.to_excel(os.path.join(path, "non_unique_Ida.xlsx"))

def setup_regex_files(path):
    """
    SETTING UP FILES FOR FOLDER: regex_files
    Here we add a regular expression column to the city files
    """

    # MAKE FILES: Ida, Location_north, Location_south

    # For the cities unique in the US and affected by Ida, the regex should match when we just see the city name
    # example regex: (?i:Jamesburg)
    unique_ida = pd.read_excel("/Users/arneeichholtz/Documents/MIT/affect_area_files/Ida_files/unique_Ida.xlsx")
    unique_ida["regex"] = unique_ida.apply(lambda row: "(?i:{city})".format(city=row.city), axis=1)
    unique_ida = unique_ida[["Name", "city", "state", "state_abbrev", "regex"]]

    # For the cities not unique in the US and affected by Ida, the regex should match the city only if it is followed by the state
    # abbreviation or the full state name (for both we do not care about capitalization)
    # example regex: (?i:Crowley),?\s((?i:LA\b)|(?i:Louisiana))
    non_unique_ida = pd.read_excel("/Users/arneeichholtz/Documents/MIT/affect_area_files/Ida_files/non_unique_Ida.xlsx")
    non_unique_ida["regex"] = non_unique_ida.apply(lambda row: r"(?i:{city}),?\s((?i:{abbrev}\b)|(?i:{state}))"
                                                   .format(city=row.city, abbrev=row.state_abbrev, state=row.state),
                                                   axis=1)
    non_unique_ida = non_unique_ida[["Name", "city", "state", "state_abbrev", "regex"]]

    # The names and regex for all US states. Manually created and edited this, see remarks in file
    full_country_states = pd.read_excel(
        "/Users/arneeichholtz/Documents/MIT/affect_area_files/regex_files/full_country_states.xlsx")

    # Name and regex for states that were fully affected
    aff_states = full_country_states[full_country_states["state"].isin(["Louisiana", "Mississippi", "New Jersey"])]

    # File with all location names (states and cities) and regex for the area affected by Ida
    location_ida = pd.concat([aff_states, unique_ida, non_unique_ida]).reset_index(drop=True)
    location_ida = location_ida[["Name", "city", "state", "state_abbrev", "regex"]]
    location_ida.to_excel(os.path.join(path, "Ida.xlsx"), engine='xlsxwriter')

    # Subset of Location Ida file, only relating to Northern area
    location_north = location_ida[
        location_ida["state"].isin(["New Jersey", "Pennsylvania", "New York", "Connecticut", "Delaware"])].reset_index(drop=True)
    location_north.to_excel(os.path.join(path, "Location_north.xlsx"), engine='xlsxwriter')

    # Subset of Location Ida file, only relating to Southern area
    location_south = location_ida[location_ida["state"].isin(["Mississippi", "Louisiana"])].reset_index(drop=True)
    location_south.to_excel(os.path.join(path, "Location_south.xlsx"), engine='xlsxwriter')


    # MAKE FILES: full_country_cities, Location_full_country

    # For cities that only exist in the US, the regex should match on just the city name
    # example regex: (?i:Seattle)
    only_us = pd.read_excel("/Users/arneeichholtz/Documents/MIT/affect_area_files/us_city_files/only_US.xlsx")
    only_us["regex"] = only_us.apply(lambda row: "(?i:{city})".format(city=row.city), axis=1)

    # For cities that also exist elsewhere in the world, the regex should match on the city name only when it
    # is followed by the state name or abbreviation
    # example regex: (?i:Pioneer),?\s((?i:OH\b)|(?i:Ohio))
    non_only_us = pd.read_excel("/Users/arneeichholtz/Documents/MIT/affect_area_files/us_city_files/non_only_US.xlsx")
    non_only_us["regex"] = non_only_us.apply(lambda row: r"(?i:{city}),?\s((?i:{abbrev}\b)|(?i:{state}))"
                                             .format(city=row.city, abbrev=row.state_abbrev, state=row.state), axis=1)

    # Full_country_cities has all US cities and their regex
    full_country_cities = pd.concat([only_us, non_only_us], ignore_index=True)
    full_country_cities = full_country_cities[["Name", "city", "state", "state_abbrev", "regex"]]
    full_country_cities.to_excel(os.path.join(path, "full_country_cities.xlsx"))

    # Location_full_country is just the combination of states and their regex, and cities and their regex
    location_full_country = pd.concat([full_country_states, full_country_cities], ignore_index=True)
    location_full_country = location_full_country[["Name", "city", "state", "state_abbrev", "regex", "Remarks"]]
    location_full_country.to_excel(os.path.join(path, "Location_full_country.xlsx"))


if __name__ == "__main__":
    # Uncomment the lines below to generate the files. This is from my local device, but the structure is the same in
    # the folder on Supercloud, so everything should work

    path_us_city_files = "/Users/arneeichholtz/Documents/MIT/affect_area_files/us_city_files"
    # setup_us_city_files(path_us_city_files)

    path_ida_files = path = "/Users/arneeichholtz/Documents/MIT/affect_area_files/Ida_files"
    # setup_ida_files(path_ida_files)

    path_regex_files = "/Users/arneeichholtz/Documents/MIT/affect_area_files/regex_files"
    # setup_regex_files(path_regex_files)
