__author__ = "Tibor Sloboda"

import uuid
import itertools
from typing import Tuple, TypedDict, List
import pandas as pd


class PetriDict(TypedDict):
    places: pd.DataFrame
    transitions: pd.DataFrame
    arcs: pd.DataFrame


def normalize(df_dict: PetriDict):
    df_places = df_dict['places']
    df_transitions = df_dict['transitions']

    places_min_x = df_places['x'].min()
    transitions_min_x = df_transitions['x'].min()
    total_min_x = min(places_min_x, transitions_min_x)

    places_min_y = df_places['y'].min()
    transitions_min_y = df_transitions['y'].min()
    total_min_y = min(places_min_y, transitions_min_y)

    df_places, df_transitions = update_xy(df_places, df_transitions, -total_min_x, -total_min_y)

    return dictify(df_places, df_transitions, df_dict['arcs'])


def dictify(df_places: pd.DataFrame, df_transitions: pd.DataFrame, df_arcs: pd.DataFrame) -> PetriDict:
    return {'places': df_places, 'transitions': df_transitions, 'arcs': df_arcs}


def __rand_uuid():
    return uuid.uuid4()


def __get_max_xy(df_places: pd.DataFrame, df_transitions: pd.DataFrame) -> Tuple[int, int]:
    places_max_x = df_places['x'].max()
    transitions_max_x = df_transitions['x'].max()
    x = max(places_max_x, transitions_max_x)

    places_max_y = df_places['y'].max()
    transitions_max_y = df_transitions['y'].max()
    y = max(places_max_y, transitions_max_y)

    return x, y


def update_xy(df_places: pd.DataFrame, df_transitions: pd.DataFrame, x: int, y: int)\
        -> Tuple[pd.DataFrame, pd.DataFrame]:
    df_places['x'] = df_places['x'].map(lambda coord: coord + x)
    df_places['y'] = df_places['y'].map(lambda coord: coord + y)

    df_transitions['x'] = df_transitions['x'].map(lambda coord: coord + x)
    df_transitions['y'] = df_transitions['y'].map(lambda coord: coord + y)

    return df_places, df_transitions


def update_ids(df_dict: PetriDict) -> PetriDict:
    df_places = df_dict['places']
    df_transitions = df_dict['transitions']
    df_arcs = df_dict['arcs']

    rep_dict = {i: __rand_uuid() for i in itertools.chain(df_places.id, df_transitions.id)}
    rep_dict_arc_id = {i: __rand_uuid() for i in itertools.chain(df_arcs.id)}

    df_arcs.replace(rep_dict, inplace=True)
    df_arcs.replace(rep_dict_arc_id, inplace=True)
    df_places.replace(rep_dict, inplace=True)
    df_transitions.replace(rep_dict, inplace=True)

    # for i in range(len(df_arcs)):
    #     new_uuid_from = __rand_uuid()
    #     new_uuid_to = __rand_uuid()
    #     new_uuid_arc = __rand_uuid()
    #
    #     df_transitions.loc[df_transitions.id == df_arcs['sourceId'][i], 'id'] = new_uuid_from
    #     df_transitions.loc[df_transitions.id == df_arcs['destinationId'][i], 'id'] = new_uuid_to
    #
    #     df_places.loc[df_places.id == df_arcs['sourceId'][i], 'id'] = new_uuid_from
    #     df_places.loc[df_places.id == df_arcs['destinationId'][i], 'id'] = new_uuid_to
    #
    #     df_arcs.at[i, 'sourceId'] = new_uuid_from
    #     df_arcs.at[i, 'destinationId'] = new_uuid_to
    #     df_arcs.at[i, 'id'] = new_uuid_arc

    return dictify(df_places, df_transitions, df_arcs)


def concat_models(dict_list: List[PetriDict]):
    df_places = pd.concat([df_dict['places'] for df_dict in dict_list])
    df_transitions = pd.concat([df_dict['transitions'] for df_dict in dict_list])
    df_arcs = pd.concat([df_dict['arcs'] for df_dict in dict_list])

    return dictify(df_places, df_transitions, df_arcs)
