from shutil import copyfile
from settings import import_settings
from scripts import generate_statistics
from time import time
from jinja2 import Template

def backup_previous_static_page(static_page_location,backup_folder):

    try:
        copyfile(static_page_location,backup_folder+str(time()))
    except FileNotFoundError:
        pass

def refresh_static_page(chairs_per_party,history_of_party_mentions,template):

    #Translate the chair statistics to a value for each chair
    chairs_per_party = sorted(chairs_per_party.items(),key=lambda x: x[1],reverse=True)
    chairs = []

    for party,value in chairs_per_party:
        for chair in range(value):
            chairs.append(party)

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
    return Template(open(template).read()).render(chairs=enumerate(chairs),chairs_per_party=chairs_per_party,
                                                  series_of_percentages_per_party=series_of_percentages_per_party)

if __name__ == '__main__':

    current_settings = import_settings()
    backup_previous_static_page(current_settings['static_page'],current_settings['previous_static_pages_folder'])

    #Create a new one
    chairs_per_party = generate_statistics.get_chairs_per_party(fake=True)
    history_of_party_mentions = generate_statistics.get_history_of_party_mentions(fake=True)
    new_page_content = refresh_static_page(chairs_per_party,history_of_party_mentions,current_settings['template'])

    open(current_settings['static_page'],'w').write(new_page_content)