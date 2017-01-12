from shutil import copyfile
from settings import import_settings
from scripts import electionstats
from time import time
from jinja2 import Template

def backup_previous_static_page(static_page_location,backup_folder):

    try:
        copyfile(static_page_location,backup_folder+str(time()))
    except FileNotFoundError:
        pass

def refresh_static_page(seats_per_party,history_of_party_mentions,template):

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

    #Translate the chair statistics to a value for each seat
    seats_per_party = sorted(seats_per_party.items(),key=lambda x: x[1],reverse=True)
    seats = []

    for party_name,value in seats_per_party:

        for chair in range(value):
            seats.append(party_name)

    #Translate the history of party mentions to series of percentages
    day_names = [number_to_date_string(date_number) for date_number in history_of_party_mentions.keys()]
    party_mentions_ordered_by_time = sorted(history_of_party_mentions.items(),key=lambda x:x[0],reverse=False)
    series_of_percentages_per_party = {}

    for date_name, mentions_in_period in party_mentions_ordered_by_time:

        for party_name, percentage_of_mentions in mentions_in_period.items():

            #If we discovered an invalid party name, we clean it right away
            if party_name[0] in '0123456789':
                party_name = '_'+party_name

            percentage_of_mentions = round(percentage_of_mentions,2)

            try:
                series_of_percentages_per_party[party_name].append(percentage_of_mentions)
            except KeyError:
                series_of_percentages_per_party[party_name] = [percentage_of_mentions]

    #Order the series, so the parties will always be presented to the Javascript in the same order
    series_of_percentages_per_party = sorted(series_of_percentages_per_party.items(),key=lambda x: x[0])

    #Generate the page
    return Template(open(template).read()).render(seats=enumerate(seats),seats_per_party=seats_per_party,
                                                  series_of_percentages_per_party=series_of_percentages_per_party)

def number_to_date_string(date_number):

    if date_number[4:6] == '12':
        month = 'de'
    elif date_number[4:6] == '01':
        month = 'ja'
    elif date_number[4:6] == '02':
        month = 'fe'
    elif date_number[4:6] == '03':
        month = 'ma'

    return date_number[6:] + ' '+month

if __name__ == '__main__':

    current_settings = import_settings()
    backup_previous_static_page(current_settings['static_page'],current_settings['previous_static_pages_folder'])

    #Create a new one
    politicaltweets = electionstats.PoliticalTweets(current_settings['db_host'],current_settings['db_user'],
                                                    current_settings['db_password'],current_settings['db_name'])
    politicaltweets.readtweets()

    seats_per_party = politicaltweets.get_seats_per_party()
    history_of_party_mentions = politicaltweets.get_history_of_party_mentions()
    new_page_content = refresh_static_page(seats_per_party,history_of_party_mentions,current_settings['template'])

    open(current_settings['static_page'],'w').write(new_page_content)
