__author__ = ["Olesia Melnychyn", "Tibor Sloboda"]

import pandas as pd
import xmltodict


def parse_join_xml(filename):
    df_places = {}
    df_transitions = {}
    df_arcs = {}
    places_i = 0
    transitions_i = 0
    arcs_i = 0
    with open(filename, 'r') as file:
        data = file.read().replace('\n', '')
        obj = xmltodict.parse(data)
        for item, value in obj.items():
            for idx, val in value.items():
                if type(val) is str:
                    continue

                try:
                    iter(val)
                except TypeError:
                    continue

                for va in val:
                    new_row = {'id': "", 'x': "", 'y': "", 'label': ""}

                    try:
                        va.items()
                    except AttributeError:
                        continue

                    if idx in ("transition", "place"):
                        for i, j in va.items():
                            if i == "id":
                                new_row["id"] = j
                            if i == "x":
                                new_row["x"] = int(j)
                            if i == "y":
                                new_row["y"] = int(j)
                            if i == "label":
                                new_row["label"] = j

                    if idx == "transition":
                        df_transitions[transitions_i] = new_row
                        transitions_i += 1
                    elif idx == "place":
                        df_places[places_i] = new_row
                        places_i += 1
                    elif idx == "arc":
                        new_row = {'id': "", 'type': "", 'sourceId': "", 'destinationId': "", "multiplicity": ""}
                        for i, j in va.items():
                            if i == "id":
                                new_row["id"] = j
                            if i == "type":
                                new_row["type"] = j
                            if i == "sourceId":
                                new_row["sourceId"] = j
                            if i == "destinationId":
                                new_row["destinationId"] = j
                            if i == "multiplicity":
                                new_row["multiplicity"] = j
                        df_arcs[arcs_i] = new_row
                        arcs_i += 1

    return pd.DataFrame.from_dict(df_places, "index"), \
        pd.DataFrame.from_dict(df_transitions, "index"), \
        pd.DataFrame.from_dict(df_arcs, "index")


def dfs_to_xml(df_places: pd.DataFrame, df_transitions: pd.DataFrame, df_arcs: pd.DataFrame, file: str) -> None:
    start_str = "<document xmlns:xsi=\"http://www.w3.org/2001/XMLSchema-instance\" xsi:noNamespaceSchemaLocation=" \
                "\"https://modeler.netgrif.com/petriflow_schema.xsd\">\n<id>new_model</id>\
                <initials>NEW</initials>\
                <title>New Model</title>\
                <defaultRole>true</defaultRole>\
                <transitionRole>false</transitionRole>\
                <!--  TRANSACTIONS  -->\
                <!--  ROLES  -->\
                <!--  PROCESS ROLE REFS  -->\
                <!--  PROCESS USER REFS  -->\
                <!--  DATA  -->\
                <!--  I18NS  -->\
                <!--  TRANSITIONS  -->"
    end_str = "</document>"
    with open(file, "w") as f:
        f.write(start_str)
        for index, row in df_transitions.iterrows():
            transition_string = "<transition>\n<id>{}</id>\n<x>{}</x>\n<y>{}</y>\n<layout>\n<offset>0" \
                                "</offset>\n</layout>\n<label>{}</label>\n</transition>"
            transition = transition_string.format(row["id"], row["x"], row["y"], row["label"])
            f.write(transition)
        for index, row in df_places.iterrows():
            place_string = "<place>\n<id>{}</id>\n<x>{}</x>\n<y>{}</y>\n<label>{}</label>\n" \
                           "<tokens>0</tokens>\n<static>false</static>\n</place>"
            place = place_string.format(
                row["id"], row["x"], row["y"], row["label"])
            f.write(place)
        for index, row in df_arcs.iterrows():
            arc_string = "<arc>\n<id>{}</id>\n<type>{}</type>\n<sourceId>{}</sourceId>\n<destinationId>{}" \
                         "</destinationId>\n<multiplicity>{}</multiplicity>\n</arc>"
            arc = arc_string.format(
                row["id"], row["type"], row["sourceId"], row["destinationId"], row["multiplicity"])
            f.write(arc)
        f.write(end_str)
        f.close()
