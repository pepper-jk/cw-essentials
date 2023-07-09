import argparse
import copy
import csv
import json
import os
import sys

from itertools import chain


class converter:
    """A converter for star wars animated series metadata from csv to json."""

    def __init__(self):
        self.args = None

        self.metadata = {}
        self.data = {
            "titles": []
        }
        self.series = {
            "C": {"series": "The Clone Wars", "chrono": 2000},
            "T": {"series": "Tales of the Jedi", "chrono": 2000},
            "B": {"series": "The Bad Batch", "chrono": 3000},
            "R": {"series": "Star Wars Rebels", "chrono": 4000}
        }

        self.fields = {
            "id": "",
            "importance": "",
            "chronological": 0,
            "series": "",
            "release": "",
            "number": "",
            "title": "",
            "arc": "",
            "phase": 0,
            "tags": {
                "primary": "",
                "secondary": []
            },
            "characters": {
                "main": [],
                "side": [],
                "extra": []
                },
            "recommended": [],
            "relevance": []
        }

        self.macros = {
            "Crew": ["Ezra", "Kanan", "Hera", "Sabine", "Zeb", "Chopper"],
            "Batch": ["Hunter", "Wrecker", "Tech", "Echo", "Omega"]
        }

        self.main_chars = ["Ahsoka", "Anakin", "Obi-Wan", "Rex", "Cody", "Fives",
                           "Ezra", "Kanan", "Hera", "Sabine", "Zeb", "Chopper",
                           "Hunter", "Wrecker", "Tech", "Echo", "Omega", "Crosshair"]
        self.side_chars = ["Ventress", "Grevious", "Kalani", "Dooku", "Maul", "Savage",
                           "Padme", "R2-D2", "C-3PO", "Organa", "Leia", "Monmothma",
                           "Tarkin", "Rampart", "Kallus", "Minister Tua", "Pryce", "Thrawn",
                           "Grand Inquisitor", "Seventh Sister", "Fifth Brother", "Vader", "Emperor",
                           "Lama Su", "Nala Se",
                           "Saw", "Cham Syndulla",
                           "Sato", "Dodonna",
                           "Bo-Katan", "Fenn Rau", "Ursa Wren", "Tristan Wren", "Gar Saxon", "Saxon",
                           "Hondo", "Lando", "Vizago", "Azmorigan", "Cid",
                           "Cad Bane", "Boba Fett", "Ketsu Onyo",
                           "Cut Lawquane", "Fennec Shand"]


    def get_args(self, arguments):
        """Collects all parameters passed to the script."""
        parser = argparse.ArgumentParser()
        parser.add_argument('data_dir', type=str)

        self.args = parser.parse_args(arguments)


    def open_files(self):
        """Opens both the input csv and output json file."""
        json_path = self.args.data_dir+"/data.json"

        self.csv_files = []
        filenames = os.listdir(self.args.data_dir)
        for filename in (f for f in filenames if ".csv" in f):
            csv_path = self.args.data_dir + "/" + filename
            self.csv_files.append(open(csv_path, 'r'))
        self.json_file = open(json_path, 'w')


    def split_csl(self, data):
        """Splits comma separated list, strips whitespaces, and returns a list."""
        if data == "":
            return []
        data = data.split(',')
        for i, dat in enumerate(data):
            data[i] = dat.strip()
        return data


    def split_characters(self, characters):
        """Separates a list of characters and sorts them into categories of relevancy."""
        chars = {
            "main": [],
            "side": [],
            "extra": []
        }

        char_list = self.split_csl(characters)
        char_list = list(chain.from_iterable(self.macros[item] if item in self.macros.keys() else [item] for item in char_list))

        got_main_char = False
        for i, char in enumerate(char_list):
            if char in self.main_chars:
                chars["main"].append(char)
                got_main_char = True
            elif not got_main_char:
                chars["main"].append(char)
                if i == 1:
                    got_main_char = True
            elif char in self.side_chars:
                chars["side"].append(char)
            else:
                chars["extra"].append(char)

        return chars


    def split_tags(self, data):
        """Separates tags into primary and secondary based on their order."""
        if ',' in data:
            data = self.split_csl(data)
            primary = data[0]
            secondary = data[1:]
        else:
            primary = data
            secondary = []
        return {"primary": primary, "secondary": secondary}


    def annotate(self):
        """Iterates over csv data, annotates it, and sorts it into the json data structure."""
        titles = []
        for csv_file in self.csv_files:
            reader = csv.DictReader(csv_file, delimiter=';')
            for row in reader:
                episode = copy.deepcopy(self.fields)
                letter = row["id"][0]
                episode.update({"series": self.series[letter]["series"]})
                for key, data in row.items():
                    if key not in self.fields.keys():
                        continue
                    elif key == "chronological":
                        data = int(data) + self.series[letter]["chrono"]
                    elif key == "tags":
                        data = self.split_tags(data)
                    elif key == "characters":
                        data = self.split_characters(data)
                    elif key in ["recommended", "relevance"]:
                        data = self.split_csl(data)
                    elif str(data).isdigit():
                        data = int(data)
                    elif str(data).replace('.','',1).isdigit():
                        data = float(data)
                    episode.update({key: data})
                titles.append(episode)
        self.data["titles"] = titles


    def dump_json(self):
        """Dumps collected data into a JSON file."""
        json.dump(self.data, self.json_file, indent=2)
        self.json_file.write('\n')


def main(arguments):
    con = converter()
    con.get_args(arguments)
    con.open_files()
    con.annotate()
    con.dump_json()

if __name__ == "__main__":
    main(sys.argv[1:])
