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

    #Translate the chair statistics to a value for each chair
    seats_per_party = sorted(seats_per_party.items(),key=lambda x: x[1],reverse=True)
    seats = []

    for party,value in seats_per_party:
        for chair in range(value):
            seats.append(party)

    #Translate the history of party mentions to series of percentages
    series_of_percentages_per_party = {}

    for mentions_in_period in history_of_party_mentions:
        total_mentions_this_period = sum(mentions_in_period.values())

        for party_name, number_of_mentions in mentions_in_period.items():

            percentage = round(100*(number_of_mentions/total_mentions_this_period),2)

            try:
                series_of_percentages_per_party[party_name].append(percentage)
            except KeyError:
                series_of_percentages_per_party[party_name] = [percentage]

    #Order the series, so the parties will always be presented to the Javascript in the same order
    series_of_percentages_per_party = sorted(series_of_percentages_per_party.items(),key=lambda x: x[0])

    #Generate the page
    return Template(open(template).read()).render(seats=enumerate(seats),seats_per_party=seats_per_party,
                                                  series_of_percentages_per_party=series_of_percentages_per_party)

if __name__ == '__main__':

    current_settings = import_settings()
    backup_previous_static_page(current_settings['static_page'],current_settings['previous_static_pages_folder'])

    #Create a new one
    politicaltweets = electionstats.PoliticalTweets()
    politicaltweets.readtweets()
    seats_per_party = politicaltweets.get_seats_per_party()
    history_of_party_mentions = politicaltweets.get_history_of_party_mentions()
    new_page_content = refresh_static_page(seats_per_party,history_of_party_mentions,current_settings['template'])

    open(current_settings['static_page'],'w').write(new_page_content)
