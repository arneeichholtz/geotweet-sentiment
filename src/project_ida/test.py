import re
import os
import pandas as pd
import gzip
import json
import pprint



if __name__ == "__main__":

    strings = ["Ramsey, NJ", "Ramsey Nj", "Ramsey New Jersey", "Ramsey"]
    pattern = r"(?i:Ramsey),?\s((?i:NJ\b)|(?i:New Jersey))"

    # for s in strings:
    #     try:
    #         m = re.search(pattern, s)
    #         print(f"Match found {m.group(0)}")
    #     except:
    #         print(f"No match found for {s}")


    path = "/Users/arneeichholtz/Downloads/aff_2021_08_01_00_onepercent.csv"

    df = pd.read_csv(path, engine="python")
    print(df.head().to_string())






    additional_data = pd.DataFrame.from_dict({
        "name_short": ["United Kingdom",
                       "United States",
                       "United States Virgin Islands",
                       "Christmas Island",
                       "Cocos (Keeling) Islands",
                       "Cook Islands",
                       "South Georgia and South Sandwich Is.",
                       "St. Barths"],
        "name_official": ["United Kingdom of Great Britain and Northern Ireland",
                          "United States of America",
                          "Virgin Islands of the United States",
                          "Christmas island",
                          "Territory of the Cocos (Keeling) Islands",
                          "Cook Islands",
                          "South Georgia and The South Sandwich Islands",
                          "Territorial collectivity of Saint-Barthélemy"],
        "regex": [r".*(united.?kingdom|britain|\bu\.?k\.?\b|\bgb\b)",
                  r"(?!.*islands).*united.?states|\bu\.?s\.?a\.?\b|\bu\.?s\.?\b",
                  r"\bvirgin\b.{,5}\bislands?\b",
                  "christmas island",
                  "\bcocos islands|keeling islands",
                  "\bcook islands",
                  "sandwich islands|south.?georgia.*(?=sandwich islands)",
                  "(?=s.{,3}t).*barth?s"]
    })




