from api import *

config = {"hostname": "https://results.elections.virginia.gov",
          "turnout_by_county_path": "/vaelections/2018%20November%20General/Site/Statistics/Turnout.html",
          "turnout_by_precinct_path": "/vaelections/2018%20November%20General/Site/Statistics/Turnout/"
          }

virginia_elections_api = DataPullAPI(**config)
response_text = virginia_elections_api.request(virginia_elections_api.turnout_by_county_path)


counties_df = virginia_elections_api.pull_table(response_text)

counties_df.to_csv("turnout_by_county.csv")

url_suffixes = virginia_elections_api.import_url_suffixes("counties.csv")

precincts_df = virginia_elections_api.pull_table_loop(url_suffixes)

precincts_df.to_csv("turnout_by_precinct.csv")

