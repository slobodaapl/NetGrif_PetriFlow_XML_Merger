__author__ = "Tibor Sloboda"

import data_parser
import xml_parser
import xmlschema
import pandas as pd
import sys
import os
import re


def coord_dictify(dfp: pd.DataFrame, dft: pd.DataFrame, dfa: pd.DataFrame, x_c, y_c):
    return {'x': x_c, 'y': y_c, 'df': data_parser.dictify(dfp, dft, dfa)}


if __name__ == "__main__":
    files = []
    coords = []
    dicts = []
    input_file = ""
    output_file = ""
    xsd = xmlschema.XMLSchema("petriflow_schema.xsd")

    if len(sys.argv) != 3:
        raise Exception("Incorrect number of arguments")
    else:
        input_file = sys.argv[1]
        output_file = sys.argv[2]

        if not os.path.exists(input_file) or not os.path.isfile(input_file):
            raise Exception("Input file can't be found or is a directory.")

        if os.path.exists(output_file) and os.path.isdir(output_file):
            raise Exception("Output file is a directory. Can't overwrite a directory with a file.")

    with open(input_file, 'r') as file:
        while line := re.sub(r'\s*,\s*', ',', file.readline().strip()):

            if len(line) == 0:
                continue

            split_line = line.split(",")

            if len(split_line) != 3:
                raise Exception("Input file has incorrect formatting")

            if not os.path.exists(split_line[0]) or not os.path.isfile(split_line[0]):
                raise Exception("File {} does not exist or is a directory.".format(split_line[0]))
            else:
                try:
                    xsd.validate(split_line[0])
                except xmlschema.XMLSchemaValidationError:
                    raise Exception("File {} is not a valid builder.netgrif.com PetriFlow XML".format(split_line[0]))

            try:
                x = int(split_line[1])
                y = int(split_line[2])

                if x < 0 or y < 0:
                    raise RuntimeError

            except ValueError:
                raise Exception("The x or y values are not parse-able numbers.")
            except RuntimeError:
                raise Exception("The x and y values must be positive integers.")

            files.append(split_line[0])
            coords.append({'x': x, 'y': y})

    for idx, file in enumerate(files):
        df_places, df_transitions, df_arcs = xml_parser.parse_join_xml(file)
        dicts.append(
            coord_dictify(
                df_places,
                df_transitions,
                df_arcs,
                coords[idx]['x'],
                coords[idx]['y']
            )
        )

    for idx, coord_dict in enumerate(dicts):
        print("Working on {} / {} ...".format(idx + 1, len(dicts)))
        dicts[idx]['df'] = data_parser.update_ids(
            data_parser.normalize(dicts[idx]['df'])
        )

        dicts[idx] = data_parser.dictify(
            *data_parser.update_xy(
                dicts[idx]['df']['places'],
                dicts[idx]['df']['transitions'],
                dicts[idx]['x'],
                dicts[idx]['y']
            ),
            dicts[idx]['df']['arcs']
        )

        print("Done\n")

    dict_new = data_parser.concat_models(dicts)
    xml_parser.dfs_to_xml(dict_new['places'], dict_new['transitions'], dict_new['arcs'], output_file)
    print("Successfully outputted file {}".format(output_file))
