from bs4 import BeautifulSoup
import requests
import pandas as pd
import csv


class DataPullAPI:

    def __init__(self, hostname, turnout_by_county_path, turnout_by_precinct_path):
        self.hostname = hostname
        self.turnout_by_county_path = turnout_by_county_path
        self.turnout_by_precinct_path = turnout_by_precinct_path

    def request(self, path):
        """Make the request to the website, returns the body of the website."""
        response = requests.get("{0}{1}".format(self.hostname, path))
        return response.content

    def parse_html_table(self, table):
        n_columns = 0
        n_rows = 0
        column_names = []

        # Find number of rows and columns
        # we also find the column titles if we can
        for row in table.find_all('tr'):

            # Determine the number of rows in the table
            td_tags = row.find_all('td')
            if len(td_tags) > 0:
                n_rows += 1
                if n_columns == 0:
                    # Set the number of columns for our table
                    n_columns = len(td_tags)

            # Handle column names if we find them
            th_tags = row.find_all('th')
            if len(th_tags) > 0 and len(column_names) == 0:
                for th in th_tags:
                    column_names.append(th.get_text())

        # Safeguard on Column Titles
        if len(column_names) > 0 and len(column_names) != n_columns:
            raise Exception("Column titles do not match the number of columns")

        columns = column_names if len(column_names) > 0 else range(0, n_columns)
        df = pd.DataFrame(columns=columns,
                          index=range(0, n_rows))
        row_marker = 0
        for row in table.find_all('tr'):
            column_marker = 0
            columns = row.find_all('td')
            for column in columns:
                df.iat[row_marker, column_marker] = column.get_text()
                column_marker += 1
            if len(columns) > 0:
                row_marker += 1

        # Convert to float if possible
        for col in df:
            try:
                df[col] = df[col].astype(float)
            except ValueError:
                pass

        return df

    def pull_table(self, response_text):
        soup = BeautifulSoup(response_text, "html.parser")
        table = soup.find("table")

        df = self.parse_html_table(table)

        return df

    def import_url_suffixes(self, csv_file):
        with open(csv_file) as csvfile:
            url_suffixes = list(csv.reader(csvfile))

        return url_suffixes

    def pull_table_loop(self, url_suffixes):
        dfs = []
        for i in url_suffixes:
            new_response_text = self.request(self.turnout_by_precinct_path + str(str(i).strip("[]")).strip("''"))
            soup = BeautifulSoup(new_response_text, "html.parser")
            table = soup.find("table")
            temp_df = self.parse_html_table(table)
            temp_df["County"] = str(i)
            dfs = dfs + [temp_df]

        df2 = pd.concat(dfs)
        return df2

