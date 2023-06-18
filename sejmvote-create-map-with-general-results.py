#!/usr/bin/env python3

import os
import argparse
import logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(asctime)s\t%(message)s')

import folium
from folium.plugins import FastMarkerCluster, MarkerCluster

import re
import pandas as pd
import numpy as np
from aipolit.utils.html import write_report_header, write_report_bottom, create_interactive_html_table_string, create_html_link_string
from aipolit.utils.pandas_utils import df_to_list_of_lists
from aipolit.sejmvote.globals import AVAILABLE_ELECTIONS_IDS
from aipolit.sejmvote.voting_factory_general_results import create_voting_general_results
from aipolit.sejmvote.voting_factory_candidate_results import create_voting_candidate_results


def parse_arguments():
    """parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Creates map using general election results from elections of the given ID'
    )

    parser.add_argument(
        '--output',
        required=True,
        help='HTML filepath to save output map')

    parser.add_argument(
        '--elections-id', '-e',
        choices=AVAILABLE_ELECTIONS_IDS,
        required=True,
        help='Elections IDS to be quiried')

    parser.add_argument(
        '--okreg', '-o',
        default=None,
        help='Limit query only to data from the given Sejm okreg')

    parser.add_argument(
        '--city', '-c',
        default=None,
        help='Limit query only to data from the given city')

    parser.add_argument(
        '--powiat', '-p',
        default=None,
        help='Limit query only to data from the given powiat name')

    POSSIBLE_VAL_KEY_CHOICES = ['opozycja', 'konfederacja', 'pis', 'ko', 'psl', 'sld', 'frekwencja', '1_tura']
    parser.add_argument(
        '--val-key', '-vk',
        required=True,
        choices=POSSIBLE_VAL_KEY_CHOICES,
        help='Defines what should be taken into account to count value displayed on map')

    parser.add_argument(
        '--val-key2', '-vk2',
        choices=POSSIBLE_VAL_KEY_CHOICES,
        default=None,
        help='Same as --val-key, but if defined then takes linear combination of both val-key and val-key2')

    parser.add_argument(
        '--agg',
        choices=['average', 'multiply'],
        default='average',
        help='if val-key2 is defined then use the aggregation method: average, distance (Euclidean distance)')

    parser.add_argument(
        '--invert-val', '-iv',
        action="store_true",
        help='inverts value - high value becomes low and vice versa')

    parser.add_argument(
        '--invert-val2', '-iv2',
        action="store_true",
        help='inverts value2 - high value becomes low and vice versa')

    parser.add_argument(
        '--cand-index', '-ci',
        type=int,
        help='If set, then takes only votes on candidate number cand-index (starting from 0!) from the given list')

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

def create_description(row, party, val_key2):
    obwod_number = row['obwod_number']
    perc_val = row['perc_val']
    perc_rank = int(row['perc_rank'])

    perc_val2 = None
    perc_rank2 = None
    if val_key2:
        perc_val2 = row['perc_val2']
        perc_rank2 = int(row['perc_rank2'])

    weight = row['weight']
    total_possible_voters = row['total_possible_voters']
    total_possible_voters_rank = int(row['total_possible_voters_rank'])
    borders_description = row['borders_description']
    number_of_obwods_in_same_place = row['number_of_obwods_in_same_place']
    location_name = row['location_name']
    location_fullname = row['location_fullname']
    city = row['city']
    powiat_name = row['powiat_name']
    gmina_name = row['gmina_name']
    total_valid_votes = row['total_valid_votes']
    freq_vote = row['freq_vote']
    freq_vote_rank = int(row['freq_vote_rank'])
    counted_votes = row['counted_votes']
    counted_votes_rank = int(row['counted_votes_rank'])
    cand_index = row['cand_index']
    candidate_name = row['candidate_name']

    description = ''

    if candidate_name:
        description +=  f"<b>POPARCIE DLA {candidate_name} z listy {party}</b></br>"
    else:
        description +=  f"<b>POPARCIE DLA {party}</b></br>"

    if val_key2:
        if candidate_name:
            description +=  f"<b>(Drugi czynnik): POPARCIE DLA {candidate_name} z listy {val_key2}</b></br>"
        else:
            description +=  f"<b>(Drugi czynnik): POPARCIE DLA {val_key2}</b></br>"

    for_whom_votes = ''
    if candidate_name:
        for_whom_votes = candidate_name
    else:
        for_whom_votes = f"lista {party}"

    norm_val_round = int(row['norm_val'] * 100)

    description += \
      f"<b>Nr obwodu</b>: {obwod_number}</br>" + \
      f"<b>Siedziba:</b> {location_fullname} ({city})</br>" + \
      f"<b>Powiat / gmina:</b> {powiat_name} / {gmina_name}</br>" + \
      f"<b>Liczba obwodów w tej samej siedzibie</b>: {number_of_obwods_in_same_place}</br>" + \
      f"<b>Populacja</b>: {total_possible_voters} (miejsce: {total_possible_voters_rank})</br>" + \
      f"<b>Ważnych głosów (ogółem)</b>: {total_valid_votes}</br>" + \
      f"<b>Frekwencja</b>: {freq_vote}% (miejsce: {freq_vote_rank})</br>" + \
      f"<b>Głosów na {for_whom_votes}</b>: {counted_votes} (miejsce: {counted_votes_rank})</br>" + \
      f"<b>% wynik:</b> {perc_val}% (miejsce: {perc_rank})</br>"

    if perc_val2 is not None:
        description += \
          f"<b>% wynik2:</b> {perc_val2}% (miejsce: {perc_rank2})</br>"

    description += \
      f"<b>WAGA:</b> {weight} (znormalizowana ocena: {norm_val_round})<br/>" + \
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

def create_counted_value(val_key, general_results_entry, candidate_results_data, cand_index, obwod_id):

    if cand_index is not None:
        return candidate_results_data.get_candidate_result(obwod_id, val_key, cand_index)

    counted = 0
    if val_key == 'opozycja':
        counted = general_results_entry['total_votes_lista_ko'] \
          + general_results_entry['total_votes_lista_psl'] \
          + general_results_entry['total_votes_lista_sld']
    elif val_key == 'konfederacja':
        counted = general_results_entry['total_votes_lista_konfederacja']
    elif val_key == 'pis':
        counted = general_results_entry['total_votes_lista_pis']
    elif val_key == 'ko':
        counted = general_results_entry['total_votes_lista_ko']
    elif val_key == 'psl':
        counted = general_results_entry['total_votes_lista_psl']
    elif val_key == 'sld':
        counted = general_results_entry['total_votes_lista_sld']
    elif val_key == '1_tura':
        counted = general_results_entry['total_votes_lista_1_tura']
    elif val_key == 'frekwencja':
        counted = general_results_entry['frekwencja']
    else:
        raise Exception(f"Unknown val_key = {val_key}")

    return counted


def normalize_df_value(df, val_key, new_key):
    min_value = df[val_key].min()
    max_value = df[val_key].max()
    df[new_key] = (df[val_key] - min_value) / (max_value - min_value)


def create_data_for_map(obwod_ids, general_results_data, val_key, cand_index, candidate_results_data, val_key2, agg_method, invert_val, invert_val2):
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
        location_fullname = place_entry['location_fullname']
        city = place_entry['city']
        powiat_name = place_entry['powiat_name']
        gmina_name = place_entry['gmina_name']
        candidate_name = None

        freq_vote = results_entry['frekwencja']

        if cand_index is not None:
            candidate_name = candidate_results_data.get_candidate_name(val_key, cand_index)

        counted = create_counted_value(val_key, results_entry, candidate_results_data, cand_index, obwod_id)
        perc_val = counted
        if val_key not in ['frekwencja']:
            perc_val = int(10000 * counted / total) / 100

        counted2 = None
        perc_val2 = None
        if val_key2 is not None:
            counted2 = create_counted_value(val_key2, results_entry, candidate_results_data, cand_index, obwod_id)
            perc_val2 = counted2
            if val_key2 not in ['frekwencja']:
                perc_val2 = int(10000 * counted2 / total) / 100

        new_entry = [
            obwod_id,
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
            perc_val,
            counted2,
            perc_val2,
            total,
            freq_vote,
            cand_index,
            candidate_name,
            location_fullname]
        raw_data.append(new_entry)

    df = pd.DataFrame(
        raw_data,
        columns=[
            'obwod_id',
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
            'perc_val',
            'counted_votes2',
            'perc_val2',
            'total_valid_votes',
            'freq_vote',
            'cand_index',
            'candidate_name',
            'location_fullname'])

    normalize_df_value(df, 'perc_val', 'norm_val')
    if invert_val:
        df['norm_val'] = 1.0 - df['norm_val']

    normalize_df_value(df, 'perc_val2', 'norm_val2')
    if invert_val2:
        df['norm_val2'] = 1.0 - df['norm_val2']

#    labels = ['b_mało', 'mało', 'średnio', 'dużo', 'b_dużo']
    labels = ['bb_słabiutko', 'b_słabiutko', 'słabiutko', 'słabo-', 'słabo', 'średnio-', 'średnio', 'średnio+', 'sporo', 'sporo+', 'wysoko', 'b_wysoko', 'bb_wysoko']
    bins = np.linspace(0, 1, len(labels) + 1)

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

    df['final_norm_val'] = df['norm_val']

    if val_key2 is not None:
        if agg_method == 'average':
            df['final_norm_val'] = (df['norm_val'] + df['norm_val2']) * 0.5
        elif agg_method == 'multiply':
            df['weight_dist'] = df['norm_val'] * df['norm_val2']
            normalize_df_value(df, 'weight_dist', 'final_norm_val')
        else:
            raise Exception(f"Unknown agg method: {agg_method}")

    df['weight'] = pd.cut(df['final_norm_val'], bins=bins, labels=labels, include_lowest=True)

    df['perc_rank'] = df['perc_val'].rank(ascending=False)
    df['perc_rank2'] = df['perc_val2'].rank(ascending=False)
    df['freq_vote_rank'] = df['freq_vote'].rank(ascending=False)
    df['counted_votes_rank'] = df['counted_votes'].rank(ascending=False)
    df['total_possible_voters_rank'] = df['total_possible_voters'].rank(ascending=False)

    df['color'] = df.apply(lambda row: label_to_color[row['weight']], axis=1)
    df['description'] = df.apply(lambda row: create_description(row, val_key, val_key2), axis=1)
    df['marker_size'] = df.apply(lambda row: create_marker_size(row), axis=1)
    return df

def preprocess_data_for_map(data_for_map, args):
    if args.topn:
        df = data_for_map.nlargest(args.topn, ['final_norm_val'])
        df = df.reset_index(drop=True)
        return df

    if args.lown:
        df = data_for_map.nsmallest(args.lown, ['final_norm_val'])
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


def dump_raw_data(args, df, df_orig):
    map_out_fp = args.output
    raw_out_fp = re.sub(r".html$", "-raw.html", map_out_fp)
    if raw_out_fp == map_out_fp:
        raw_out_fp = map_out_fp + '-raw'

    logging.info("Write raw data to %s", raw_out_fp)

    def create_obwod_link(row):
        longitude = row['longitude']
        latitude = row['latitude']
        url = f"https://maps.google.com/?q={latitude},{longitude}"
        location_fullname = row['location_fullname'] + f" (nr obw. {row['obwod_number']})"
        return create_html_link_string(url, location_fullname, True)

    df['obwod_link'] = df.apply(create_obwod_link, axis=1)

    with open(raw_out_fp, "w") as f:
        write_report_header(f, "Surowe dane", "index.html")

        f.write("""
<p>
Poniższe dane pozwalają przejrzeć dokładne wyniki w przebadanych obwodach do głosowania. Zawierają także drobne statystyki, które ułatwiają odnalezienie się w gąszczu liczb.
<b>Uwaga!</b> Ze wzgledu na pominięcie niektórych obwodów w algorytmie (z powodów technicznych) sumaryczne wyniki mogą się nieznacznie różnić od rzeczywistych wyników wyborów.
</p>
""")
        f.write("<h1>Parametry wywołania generatora raportu:</h1>\n")
        f.write("<ul>\n")
        f.write(f"<li>nazwa pliku: {os.path.basename(raw_out_fp)}</li>\n")
        f.write(f"<li>id wyborów: {args.elections_id}</li>\n")
        f.write(f"<li>parametr okręg: {args.okreg}</li>\n")
        f.write(f"<li>parametr miasto: {args.city}</li>\n")
        f.write(f"<li>parametr powiat: {args.city}</li>\n")
        f.write(f"<li>parametr identyfikator liczonej wartości 1: {args.val_key}</li>\n")
        f.write(f"<li>parametr identyfikator liczonej wartości 2 : {args.val_key2}</li>\n")
        f.write(f"<li>parametr indeks kandydata: {args.cand_index}</li>\n")
        if args.cand_index is not None:
            candidate_name =  df_orig['candidate_name'].iloc[0]
            f.write(f"<li>Imię i nazwisko kandydata: {candidate_name}</li>\n")
        f.write("</ul>\n")

        sum_val1 = df_orig['counted_votes'].sum()
        agg_val1_txt = 'suma'
        if args.val_key == 'frekwencja':
            agg_val1_txt = 'średnia'
            sum_val1 = df_orig['counted_votes'].mean()

        total_votes = df_orig['total_valid_votes'].sum()
        f.write("<h1>Statystyki:</h1>\n")
        f.write("<ul>\n")
        f.write(f"<li>suma wszystkich głosów ważnych: {total_votes} </li>\n")
        f.write(f"<li>{agg_val1_txt} wartości 1 ({args.val_key}) = {sum_val1}</li>\n")
        if agg_val1_txt == 'suma':
            sum_val1_perc = 0
            if total_votes:
                sum_val1_perc = int(10000 * (sum_val1 / total_votes)) / 100
            f.write(f"<li>procent głosów wartości 1 ({args.val_key}) = {sum_val1_perc}%</li>\n")

        if args.val_key2:
            sum_val2 = None
            f.write(f"<li>suma wartości 2 ({args.val_key2}) = {sum_val2} </li>\n")
        f.write("</ul>\n")


        raw_data = df_to_list_of_lists(df, ['obwod_link', 'powiat_name', 'gmina_name', 'total_possible_voters', 'total_possible_voters_rank', 'freq_vote', 'freq_vote_rank', 'perc_val', 'perc_rank'])

        html_str = create_interactive_html_table_string(
            raw_data,
            [
                'Lokalizacja',
                'Powiat',
                'Gmina',
                'Popul.',
                'Rank(pop)',
                'Frekw.',
                'Rank(frek)',
                'Wynik',
                "Rank(Wynik)",

            ],
            'raw_data',
            with_pagination=False,
            with_toggle_columns=True,
            with_search_in_each_column=True,
            add_index=False)
        f.write(html_str)
        write_report_bottom(f, "index.html")


def main():
    args = parse_arguments()
    general_results_data = create_voting_general_results(elections_id=args.elections_id)
    candidate_results_data = None
    if args.cand_index is not None:
        if args.okreg is None:
            raise Exception("Cant use --cand-index param if --okreg is not defined!")

        candidate_results_data = create_voting_candidate_results(elections_id=args.elections_id, okreg_no=args.okreg)
        if args.val_key not in candidate_results_data.lista_id_to_candidate_names:
            raise Exception("Cant use --val_key which is not one party on the list (do not use merged vals like: opozycja)!")

    obwod_ids = general_results_data.voting_place_data.get_obwod_ids_matching_criteria(
        city=args.city,
        okreg_number=args.okreg,
        with_location_data=True,
        min_population=300,
        powiat_name=args.powiat)

    logging.info("We have %i obwod IDS available to show on MAP", len(obwod_ids))
    data_for_map = create_data_for_map(
        obwod_ids,
        general_results_data,
        args.val_key,
        args.cand_index,
        candidate_results_data,
        args.val_key2,
        args.agg,
        args.invert_val,
        args.invert_val2)

    preprocessed_data_for_map = preprocess_data_for_map(data_for_map, args)
    if args.map_type == 'clustered':
        create_map_cluster(preprocessed_data_for_map, args.output)
    elif args.map_type == 'normal':
        create_map_normal(preprocessed_data_for_map, args.output)
    else:
        raise Exception(f"Unknown map type in args {args.map_type}")

    dump_raw_data(args, preprocessed_data_for_map, data_for_map)


main()
