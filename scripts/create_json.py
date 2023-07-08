import argparse
import copy
import csv
import json
import sys

from itertools import chain


class converter:
    """A converter for star wars animated series metadata from csv to json."""
    def __init__(self):
        self.args = None
        self.letter = "C"
        self.chrono = 0

        self.metadata = {}
        self.data = {
            "name": "The Clone Wars",
            "episodes": []
        }
        self.episodes = []

        self.fields = {
            "id": "",
            "importance": "",
            "chronological": 0,
            "number": "",
            "name": "",
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
        parser.add_argument('filename', type=str)
        parser.add_argument('-s', '--series', type=str, default="C", choices=["C","T","B","R"])

        self.args = parser.parse_args(arguments)

        self.letter = self.args.series

        self.series = {
            "C": {"name": "The Clone Wars", "chrono": 2000},
            "T": {"name": "Tales of the Jedi", "chrono": 2000},
            "B": {"name": "The Bad Batch", "chrono": 3000},
            "R": {"name": "Star Wars Rebels", "chrono": 4000}
        }

        self.chrono = self.series[self.letter]["chrono"]
        self.data["name"] = self.series[self.letter]["name"]

    def open_files(self):
        """Opens both the input csv and output json file."""
        jsonfilename = self.args.filename.replace("csv","json")

        csvfile = open(self.args.filename, 'r')
        self.jsonfile = open(jsonfilename, 'w')

        self.reader = csv.DictReader(csvfile, delimiter=';')


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
        for row in self.reader:
            episode = copy.deepcopy(self.fields)
            for key, data in row.items():
                if key not in self.fields.keys():
                    continue
                elif key == "chronological":
                    data = int(data) + self.chrono
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
            self.episodes.append(episode)


    def dump_json(self):
        """Dumps collected data into a JSON file."""
        self.data["episodes"] = self.episodes
        json.dump(self.data, self.jsonfile, indent=2)
        self.jsonfile.write('\n')


def main(arguments):
    con = converter()
    con.get_args(arguments)
    con.open_files()
    con.annotate()
    con.dump_json()

if __name__ == "__main__":
    main(sys.argv[1:])
