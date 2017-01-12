import pymysql
from fake_data import FAKE_SEATS_PER_PARTY, FAKE_HISTORY_OF_PARTY_MENTIONS_PERCENTAGES

class PoliticalTweets:
    def __init__(self):
        self.db = {'host':'spitfire.science.ru.nl','user':'landsdb_admin','passwd':'queeveehiozei','dbname':'landsdb'}
        self.allparties = []
        self.seats_per_party = {}
        self.history_of_party_mentions_counts = {}
        self.history_of_party_mentions_percentages = {}

    def readtweets(self):
        try:
            tweetdb = pymysql.connect(host=self.db['host'], user=self.db['user'], passwd=self.db['passwd'],db=self.db['dbname'])
            cur = tweetdb.cursor()
            try:
                cur.execute("SELECT * from elections170315")
                for row in cur:
                    party = row[0]
                    day = row[1]
                    counts = row[3]
                    if not party in self.allparties:
                        self.allparties.append(party)
                    if not day in self.history_of_party_mentions_counts:
                        self.history_of_party_mentions_counts[day] = {}
                    if not party in self.history_of_party_mentions_counts[day]:
                        self.history_of_party_mentions_counts[day][party] = 0
                    self.history_of_party_mentions_counts[day][party] += counts   
                    if not "allparties" in self.history_of_party_mentions_counts[day]:
                        self.history_of_party_mentions_counts[day]["allparties"] = 0
                    self.history_of_party_mentions_counts[day]["allparties"] += counts   
                cur.close()
            except:
                tweetdb.rollback()
                
            tweetdb.close()
        except:
            pass

    def get_history_of_party_mentions(self):

        #If we have no real data, show fake data (for local development)
        if self.history_of_party_mentions_counts == {}:
            return FAKE_HISTORY_OF_PARTY_MENTIONS_PERCENTAGES

        for day in self.history_of_party_mentions_counts:
            if not day in self.history_of_party_mentions_percentages:
                self.history_of_party_mentions_percentages[day] = {}
            for party in self.allparties:
                if not party in self.history_of_party_mentions_counts[day]:
                    self.history_of_party_mentions_counts[day][party] = 0
                self.history_of_party_mentions_percentages[day][party] = float(100) * float(self.history_of_party_mentions_counts[day][party]) / float(self.history_of_party_mentions_counts[day]["allparties"])

        return self.history_of_party_mentions_percentages

    def get_seats_per_party(self):

        #If we have no real data, show fake data (for local development)
        if self.history_of_party_mentions_counts == {}:
            return FAKE_SEATS_PER_PARTY

        partycounts = {}
        partypercentages = {}
        partyrestpercentages = {}
        for party in self.allparties:
            partycounts[party] = 0
            partypercentages[party] = 0
            partyrestpercentages[party] = 0
        partycounts["allparties"] = 0
        includedates = self.get_last_dates_ordered(10)

        ### count total number of mentions per party ###
        for day in self.history_of_party_mentions_counts:
            if day in includedates:
                for party in self.allparties:
                    if not party in self.history_of_party_mentions_counts[day]:
                        self.history_of_party_mentions_counts[day][party] = 0
                    partycounts[party] += self.history_of_party_mentions_counts[day][party]
                    partycounts["allparties"] += self.history_of_party_mentions_counts[day][party]

        ### compute seats ###
        for party in self.allparties:
            self.seats_per_party[party] = int(150 * partycounts[party] / partycounts["allparties"])
            partyrestpercentages[party] = 150 * partycounts[party] / partycounts["allparties"] - self.seats_per_party[party]

        ### add rest seats ###
        for party in sorted(partyrestpercentages, key=partyrestpercentages.get, reverse=True):
            if self.sumofseats() < 150:
                self.seats_per_party[party] += 1

        return self.seats_per_party

                
    def get_all_party_names(self):
        return self.allparties

    def get_all_dates_ordered(self):
        return sorted(self.history_of_party_mentions_counts.keys())

    def get_last_dates_ordered(self,count=10):
        return sorted(self.history_of_party_mentions_counts.keys())[-count:]

    def sumofseats(self):
        sum = 0
        for party in self.seats_per_party:
            sum += self.seats_per_party[party]
        return sum
