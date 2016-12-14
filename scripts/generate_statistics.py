def main(fake=False):
    """Should return a dictionary of the shape {'party1':140,'party2': 10}"""

    if fake:
        return {'vvd':40,'pvda':36,'sp':15,'cda':13,'d66':12,'pvv':12,'gl':5,'pvdd':5,'cu':4,'vijftigplus':4,'sgp':4}
    else:

        return None

if __name__ == '__main__':
    print(main(fake=True))