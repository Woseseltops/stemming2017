def get_chairs_per_party(fake=False):
    """Should return a dictionary of the shape {'party1':140,'party2': 10}"""

    if fake:
        return {'vvd':40,'pvda':36,'sp':15,'cda':13,'d66':12,'pvv':12,'gl':5,'pvdd':5,'cu':4,'vijftigplus':4,'sgp':4}
    else:

        return None

def get_history_of_party_mentions(fake=False):
    """Should return a list of dictionaries of the shape [{'party1':14000,'party2': 1000},{'party1':15000,'party2': 800}]"""

    if fake:
        return [{'vvd': 1000,'pvda': 600,'sp': 300,'cda': 200,'d66': 120,'pvv': 350,'gl': 50,'pvdd': 20,'cu': 10,'vijftigplus': 20,
                 'sgp': 40},
                {'vvd': 1100,'pvda':  1600,'sp': 200,'cda': 220,'d66': 800,'pvv': 30,'gl': 150,'pvdd': 20,'cu':  10,
                 'vijftigplus': 20,'sgp': 40},
                {'vvd': 800, 'pvda': 1200, 'sp': 300, 'cda': 270, 'd66': 300, 'pvv': 1000, 'gl': 230, 'pvdd': 100,
                 'cu': 100, 'vijftigplus': 100, 'sgp': 350},
                ]*2
    else:

        return None

if __name__ == '__main__':
    print(main(fake=True))