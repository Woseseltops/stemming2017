from shutil import copyfile
from settings import import_settings
from scripts import electionstats
from time import time
from jinja2 import Template
from math import floor,ceil

def backup_previous_static_page(static_page_location,backup_folder):

    try:
        copyfile(static_page_location,backup_folder+str(time()))
    except FileNotFoundError:
        pass

def refresh_static_page(seats_per_party,history_of_party_mentions,peak_explanation_file_location,template):

    NR_OF_DAYS_TO_SHOW_BEFORE_ELECTIONS = 56

    #Clean the party names
    seats_per_party_cleaned = {}
    for party_name,value in seats_per_party.items():

        skipping_this_party = False

        #We're not interested in parties with no seats
        if value == 0:
            skipping_this_party = True

        if not skipping_this_party:
            seats_per_party_cleaned[party_name] = value

    seats_per_party = seats_per_party_cleaned
    nr_parties_with_seats = len(seats_per_party)
    nr_rows_parties_with_seats_right = floor(nr_parties_with_seats/2)
    nr_rows_parties_with_seats_left = ceil(nr_parties_with_seats/2)

    #Translate the chair statistics to a value for each seat
    seats_per_party = sorted(seats_per_party.items(),key=lambda x: x[1],reverse=True)
    seats = []

    for party_name,value in seats_per_party:

        for chair in range(value):
            seats.append(party_name)

    #Translate the history of party mentions to series of percentages
    party_mentions_ordered_by_time = sorted(history_of_party_mentions.items(),key=lambda x:x[0],reverse=False)
    date_names = [number_to_date_string(date_number) for date_number,value in party_mentions_ordered_by_time]
    date_names = date_names[-NR_OF_DAYS_TO_SHOW_BEFORE_ELECTIONS:] #only the date names of the last two months
    series_of_percentages_per_party = {}
    series_of_last_ten_percentages_per_party = {}
    date_index = 0

    for date_name, mentions_in_period in party_mentions_ordered_by_time:

        for party_name, percentage_of_mentions in mentions_in_period.items():

            #If we discovered an invalid party name, we clean it right away
            if party_name[0] in '0123456789':
                party_name = '_'+party_name

            percentage_of_mentions = round(percentage_of_mentions,2)

            if len(party_mentions_ordered_by_time) - date_index <= NR_OF_DAYS_TO_SHOW_BEFORE_ELECTIONS:
                try:
                    series_of_percentages_per_party[party_name].append(percentage_of_mentions)
                except KeyError:
                    series_of_percentages_per_party[party_name] = [percentage_of_mentions]

            if len(party_mentions_ordered_by_time) - date_index <= 10:
                try:
                    series_of_last_ten_percentages_per_party[party_name].append(percentage_of_mentions)
                except KeyError:
                    series_of_last_ten_percentages_per_party[party_name] = [percentage_of_mentions]

        date_index += 1

    #Add empty values if we don't have all data until the elections yet
    for party_name, series_of_percentages in series_of_percentages_per_party.items():

        while len(series_of_percentages) < NR_OF_DAYS_TO_SHOW_BEFORE_ELECTIONS:
            series_of_percentages.append(None)

        series_of_percentages_per_party[party_name] = series_of_percentages

    party_names_order_by_yesterday_mentions = [party_name for party_name, value in sorted(party_mentions_ordered_by_time[-1][1].items(),
                                                                            key=lambda x: x[1],reverse=True)]

    #Order the series, so the parties will always be presented to the Javascript in the same order
    series_of_percentages_per_party = sorted(series_of_percentages_per_party.items(),key=lambda x: x[0])
    series_of_last_ten_percentages_per_party = sorted(series_of_last_ten_percentages_per_party.items(),key=lambda x: x[0])

    #Remove every other label
    even_date_names = []

    for n, date_name in enumerate(date_names):
        if n%2 == 0:
            even_date_names.append(date_name)
        else:
            even_date_names.append(None)

    peak_explanation = open(peak_explanation_file_location).read()

    #Generate the page
    return Template(open(template).read()).render(seats=enumerate(seats),seats_per_party=seats_per_party,
                                                  nr_rows_parties_with_seats_right = nr_rows_parties_with_seats_right,
                                                  nr_rows_parties_with_seats_left = nr_rows_parties_with_seats_left,
                                                  series_of_percentages_per_party=series_of_percentages_per_party,
                                                  series_of_last_ten_percentages_per_party=series_of_last_ten_percentages_per_party,
                                                  party_names_order_by_yesterday_mentions=party_names_order_by_yesterday_mentions,
                                                  date_names=date_names,
                                                  even_date_names=even_date_names,
                                                  last_ten_date_names=date_names[-10:],
                                                  peak_explanation=peak_explanation)

def number_to_date_string(date_number):

    if date_number[4:6] == '12':
        month = 'dec'
    elif date_number[4:6] == '01':
        month = 'jan'
    elif date_number[4:6] == '02':
        month = 'feb'
    elif date_number[4:6] == '03':
        month = 'maa'
    elif date_number[4:6] == '04':
        month = 'apr'

    return date_number[6:] + ' '+month

if __name__ == '__main__':

    current_settings = import_settings()
    backup_previous_static_page(current_settings['static_page'],current_settings['previous_static_pages_folder'])

    #Create a new one
    politicaltweets = electionstats.PoliticalTweets(current_settings['db_host'],current_settings['db_user'],
                                                    current_settings['db_password'],current_settings['db_name'])
    politicaltweets.readtweets(singleparty=True)

    seats_per_party = politicaltweets.get_seats_per_party(usewindow=False)
    history_of_party_mentions = politicaltweets.get_history_of_party_mentions()
    new_page_content = refresh_static_page(seats_per_party,history_of_party_mentions,
                                           current_settings['peak_explanation_file_location'],current_settings['template'])

    open(current_settings['static_page'],'w').write(new_page_content)
