#!/usr/bin/env python3

import argparse
import logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s\t%(message)s')

import folium
from folium.plugins import FastMarkerCluster, MarkerCluster

import pandas as pd
import numpy as np
from aipolit.sejmvote.voting_sejm_general_results import VotingSejmGeneralResults


def parse_arguments():
    """parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Creates map using general election results from Sejm 2019'
    )

    parser.add_argument(
        '--output',
        required=True,
        help='HTML filepath to save output map')

    parser.add_argument(
        '--okreg', '-o',
#        default='13',
        default=None,
        help='Limit query only to data from the given Sejm okreg')

    parser.add_argument(
        '--city', '-c',
        default=None,
#        default='Kraków',
        help='Limit query only to data from the given city')

    parser.add_argument(
        '--val-key', '-vk',
        required=True,
        choices=['opozycja', 'konfederacja', 'pis', 'ko', 'psl', 'sld'],
        help='Defines what should be taken into account to count value displayed on map')

    parser.add_argument(
        '--cand-index', '-ci',
        type=int,
        help='If set, then takes only votes on candidate number cand-index (starting from 1) from the given list')

    parser.add_argument(
        '--topn',
        type=int,
        help='If set, then leaves only TOP N values')

    parser.add_argument(
        '--lown',
        type=int,
        help='If set, then leaves only LOWEST N values')

    parser.add_argument(
        '--map-type', '-mt',
        choices=['clustered', 'normal'],
        default='normal',
        help='Type of map to create: clustered or normal (default)')

    args = parser.parse_args()

    return args

def create_description(row, party):
    obwod_number = row['obwod_number']
    perc_val = row['perc_val']
    perc_rank = int(row['perc_rank'])
    weight = row['weight']
    total_possible_voters = row['total_possible_voters']
    total_possible_voters_rank = int(row['total_possible_voters_rank'])
    borders_description = row['borders_description']
    number_of_obwods_in_same_place = row['number_of_obwods_in_same_place']
    location_name = row['location_name']
    city = row['city']
    powiat_name = row['powiat_name']
    gmina_name = row['gmina_name']
    total_valid_votes = row['total_valid_votes']
    freq_vote = row['freq_vote']
    freq_vote_rank = int(row['freq_vote_rank'])
    counted_votes = row['counted_votes']
    counted_votes_rank = int(row['counted_votes_rank'])

    description = \
      f"<b>POPARCIE DLA {party}</b></br>" + \
      f"<b>Nr obwodu</b>: {obwod_number}</br>" + \
      f"<b>Siedziba:</b> {location_name} ({city})</br>" + \
      f"<b>Powiat / gmina:</b> {powiat_name} / {gmina_name}</br>" + \
      f"<b>Liczba obwodów w tej samej siedzibie</b>: {number_of_obwods_in_same_place}</br>" + \
      f"<b>Populacja</b>: {total_possible_voters} (miejsce: {total_possible_voters_rank})</br>" + \
      f"<b>Ważnych głosów (ogółem)</b>: {total_valid_votes}</br>" + \
      f"<b>Frekwencja</b>: {freq_vote}% (miejsce: {freq_vote_rank})</br>" + \
      f"<b>Głosów na {party}</b>: {counted_votes} (miejsce: {counted_votes_rank})</br>" + \
      f"<b>% wynik:</b> {perc_val}% (miejsce: {perc_rank})</br>" + \
      f"<b>WAGA:</b> {weight}<br/>" + \
      f"<b>Granice obwodu:</b> {borders_description}"

    return description

def create_marker_size(row):
    population = row['total_possible_voters']
    max_size = 30
    min_size = 8
    if population > 2000:
        return max_size
    elif population > 200:
        return min_size + int( ( (population - 200) / 1800) * (max_size - min_size))
    else:
        return min_size

def create_data_for_map(obwod_ids, general_results_data, val_key):
    raw_data = []
    for obwod_id in obwod_ids:
        results_entry = general_results_data.get_results_entry_by_obwod_id(obwod_id)
        place_entry = general_results_data.voting_place_data.get_voting_place_by_id(obwod_id)
        location_entry = general_results_data.voting_place_data.location_data.obwod_id_to_location_data[obwod_id]

        location_deduplicated = general_results_data.voting_place_data.location_data.deduplicate_coordinates(obwod_id)

        obwod_number = place_entry['obwod_number']
        borders_description = place_entry['borders_description']
        total = results_entry['total_valid_votes']
        total_possible_voters = results_entry['total_possible_voters']
        number_of_obwods_in_same_place = location_entry['duplicate_count']
        location_name = place_entry['location_name']
        city = place_entry['city']
        powiat_name = place_entry['powiat_name']
        gmina_name = place_entry['gmina_name']

        # opozycja
        counted = 0
        if val_key == 'opozycja':
            counted = results_entry['total_votes_lista_ko'] \
              + results_entry['total_votes_lista_psl'] \
              + results_entry['total_votes_lista_sld']
        elif val_key == 'konfederacja':
            counted = results_entry['total_votes_lista_konfederacja']
        elif val_key == 'pis':
            counted = results_entry['total_votes_lista_pis']
        elif val_key == 'ko':
            counted = results_entry['total_votes_lista_ko']
        elif val_key == 'psl':
            counted = results_entry['total_votes_lista_psl']
        elif val_key == 'sld':
            counted = results_entry['total_votes_lista_sld']
        else:
            raise Exception(f"Unknown val_key = {val_key}")

        perc_val = int(10000 * counted / total) / 100

        freq_vote = int(10000 * total / total_possible_voters) / 100

        new_entry = [
            obwod_id,
            perc_val,
            obwod_number,
            location_deduplicated[0],
            location_deduplicated[1],
            total_possible_voters,
            borders_description,
            number_of_obwods_in_same_place,
            location_name,
            city,
            powiat_name,
            gmina_name,
            counted,
            total,
            freq_vote]
        raw_data.append(new_entry)

    df = pd.DataFrame(
        raw_data,
        columns=[
            'obwod_id',
            'perc_val',
            'obwod_number',
            'latitude',
            'longitude',
            'total_possible_voters',
            'borders_description',
            'number_of_obwods_in_same_place',
            'location_name',
            'city',
            'powiat_name',
            'gmina_name',
            'counted_votes',
            'total_valid_votes',
            'freq_vote'])

    min_value = df['perc_val'].min()
    max_value = df['perc_val'].max()


#    labels = ['b_mało', 'mało', 'średnio', 'dużo', 'b_dużo']
    labels = ['bb_słabiutko', 'b_słabiutko', 'słabiutko', 'słabo-', 'słabo', 'średnio-', 'średnio', 'średnio+', 'sporo', 'sporo+', 'wysoko', 'b_wysoko', 'bb_wysoko']
    bins = np.linspace(min_value, max_value, len(labels) + 1)


    label_to_color = {
        'bb_słabiutko': '#ab0000',
        'b_słabiutko': '#c23e00',
        'słabiutko': '#d66500',
        'słabo-': '#e58b00',
        'słabo': '#efb200',
        'średnio-': '#f4d800',
        'średnio': '#f3ff00',
        'średnio+': '#cae800',
        'sporo': '#a3d000',
        'sporo+': '#7eb800',
        'wysoko': '#5ca000',
        'b_wysoko': '#398800',
        'bb_wysoko': '#117000',
    }

    #label_to_color = {
    #    'b_mało': '#f60404',
    #    'mało': '#f87b05',
    #    'średnio': '#f8e604',
    #    'dużo': '#d4ff32',
    #    'b_dużo': '#089000',
    #}

    df['weight'] = pd.cut(df['perc_val'], bins=bins, labels=labels, include_lowest=True)
    df['perc_rank'] = df['perc_val'].rank(ascending=False)
    df['freq_vote_rank'] = df['freq_vote'].rank(ascending=False)
    df['counted_votes_rank'] = df['counted_votes'].rank(ascending=False)
    df['total_possible_voters_rank'] = df['total_possible_voters'].rank(ascending=False)

    df['color'] = df.apply(lambda row: label_to_color[row['weight']], axis=1)
    df['description'] = df.apply(lambda row: create_description(row, val_key), axis=1)
    df['marker_size'] = df.apply(lambda row: create_marker_size(row), axis=1)
    return df

def preprocess_data_for_map(data_for_map, args):
    if args.topn:
        df = data_for_map.nlargest(args.topn, ['perc_val'])
        df = df.reset_index(drop=True)
        return df

    if args.lown:
        df = data_for_map.nsmallest(args.lown, ['perc_val'])
        df = df.reset_index(drop=True)
        return df

    return data_for_map

def create_map_normal(df, out_fp):
    map1 = folium.Map(
        location=[df.head(1).latitude, df.head(1).longitude],
        tiles='cartodbpositron',
        zoom_start=12,
        control_scale=True)

    df.apply(
        lambda row:
        folium.CircleMarker(
            location=[row["latitude"], row["longitude"]],
            popup=folium.Popup(
                row['description'],
                max_width=500),
            radius=row['marker_size'],
            fill=True,
            color=row['color'],
            fill_color=row['color'],
            fill_opacity=0.9,
            ).add_to(map1), axis=1)

    map1.save(outfile=out_fp)


def create_map_cluster(df, out_fp):
    df_text = df[['description']]
    df_color = df[['color']]
    df_marker_size = df[['marker_size']]

    xlat = df['latitude'].tolist()
    xlon = df['longitude'].tolist()
    locations = list(zip(xlat, xlon))

    map1 = folium.Map(
        location=[df.head(1).latitude, df.head(1).longitude],
        tiles='cartodbpositron',
        zoom_start=15,
    )

    marker_cluster = MarkerCluster().add_to(map1)

    for point in range(0, len(locations)):
        folium.CircleMarker(
            locations[point],
            popup=folium.Popup(df_text['description'][point], max_width=500),
            radius=int(df_marker_size['marker_size'][point]),
            fill=True,
            fill_color=df_color['color'][point],
            color=df_color['color'][point],
            fill_opacity=0.9,
        ).add_to(marker_cluster)

    logging.info("Save map to %s", out_fp)
    map1.save(outfile=out_fp)

def main():
    args = parse_arguments()
    general_results_data = VotingSejmGeneralResults()
    obwod_ids = general_results_data.voting_place_data.get_obwod_ids_matching_criteria(
        city=args.city,
        sejm_okreg_number=args.okreg,
        with_location_data=True,
        min_population=300)

    logging.info("We have %i obwod IDS available to show on MAP", len(obwod_ids))
    data_for_map = create_data_for_map(obwod_ids, general_results_data, args.val_key)

    data_for_map = preprocess_data_for_map(data_for_map, args)
    if args.map_type == 'clustered':
        create_map_cluster(data_for_map, args.output)
    elif args.map_type == 'normal':
        create_map_normal(data_for_map, args.output)
    else:
        raise Exception(f"Unknown map type in args {args.map_type}")


main()
