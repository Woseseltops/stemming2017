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

def refresh_static_page(chairs_per_party,template):

    #Translate the statistics to a value for each pair
    chairs_per_party = sorted(chairs_per_party.items(),key=lambda x: x[1],reverse=True)
    chairs = []

    for party,value in chairs_per_party:
        for chair in range(value):
            chairs.append(party)

    return Template(open(template).read()).render(chairs=enumerate(chairs))

if __name__ == '__main__':

    current_settings = import_settings()
    backup_previous_static_page(current_settings['static_page'],current_settings['previous_static_pages_folder'])

    #Create a new one
    chairs_per_party = generate_statistics.main(fake=True)
    new_page_content = refresh_static_page(chairs_per_party,current_settings['template'])

    open(current_settings['static_page'],'w').write(new_page_content)