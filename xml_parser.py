__author__ = "Olesia Melnychyn"

import pandas as pd
import xmltodict


def parse_join_xml(filename):
    df_places = pd.DataFrame(columns=['id', 'x', 'y', 'label'])
    df_transition = pd.DataFrame(columns=['id', 'x', 'y', 'label'])
    df_arc = pd.DataFrame(columns=['id', 'type', 'sourceId', 'destinationId', 'multiplicity'])
    with open(filename, 'r') as file:
        data = file.read().replace('\n', '')
        print(data)
        obj = xmltodict.parse(data)
        for (item, value) in obj.items():
            for idx, val in value.items():
                new_row = {'id': "", 'x': "", 'y': "", 'label': ""}
                for va in val:
                    for i, j in va.items():
                        if i == "id":
                            new_row["id"] = j
                        if i == "x":
                            new_row["x"] = j
                        if i == "y":
                            new_row["y"] = j
                        if i == "label":
                            new_row["label"] = j

                if idx == "transition":
                    df_transition = df_transition.append(new_row, ignore_index=True)
                elif idx == "place":
                    df_places = df_places.append(new_row, ignore_index=True)

                if idx == "arc":
                    for va in val:
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
                        df_arc = df_arc.append(new_row, ignore_index=True)
    return df_places, df_transition, df_arc


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
