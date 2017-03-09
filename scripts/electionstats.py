import pymysql
from fake_data import FAKE_SEATS_PER_PARTY, FAKE_HISTORY_OF_PARTY_MENTIONS_PERCENTAGES

class PoliticalTweets:

    def __init__(self, db_host, db_user, db_password, db_name):
        self.db = {'host':db_host,'user':db_user,'passwd':db_password,'dbname':db_name}
        self.allparties = []
        self.counts_per_party = {}
        self.nrdays = 0
        self.means_per_party = {}
        self.seats_per_party = {}
        self.history_of_party_mentions_counts = {}
        self.history_of_party_mentions_percentages = {}

    def readtweets(self,denkfactor=0.5,singleparty=False):
        if singleparty == True:
            dbasetable = 'elections170315_singlepartytweets'
        else:
            dbasetable = 'elections170315_multipartytweets'
        try:
            tweetdb = pymysql.connect(host=self.db['host'], user=self.db['user'], passwd=self.db['passwd'],db=self.db['dbname'])
            cur = tweetdb.cursor()
            try:
                cur.execute("SELECT * from " + dbasetable)
                for row in cur:
                    party = row[0]
                    day = row[1]
                    counts = row[3]
                    if party == 'denk':
                        counts = int(counts * denkfactor)
                    if not party in self.allparties:
                        self.allparties.append(party)
                    if not day in self.history_of_party_mentions_counts:
                        self.history_of_party_mentions_counts[day] = {}
                    if not party in self.history_of_party_mentions_counts[day]:
                        self.history_of_party_mentions_counts[day][party] = 0
                    if not party in self.counts_per_party:
                        self.counts_per_party[party] = 0
                    self.history_of_party_mentions_counts[day][party] += counts   
                    self.counts_per_party[party] += counts
                    if not "allparties" in self.history_of_party_mentions_counts[day]:
                        self.history_of_party_mentions_counts[day]["allparties"] = 0
                    self.history_of_party_mentions_counts[day]["allparties"] += counts   
                cur.close()

                self.nrdays = len(self.history_of_party_mentions_counts)
                for party in self.allparties:
                    self.means_per_party[party] = self.counts_per_party[party] / self.nrdays

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

    def get_seats_per_party(self,nrdays=10,restseatmethod='largestmean'):
    #def get_seats_per_party(self,nrdays=10,restseatmethod='largestrest'):

        #If we have no real data, show fake data (for local development)
        if self.history_of_party_mentions_counts == {}:
            return FAKE_SEATS_PER_PARTY

        partycounts = {}
        #partymeans = {}
        partyrestpercentages = {}
        for party in self.allparties:
            partycounts[party] = 0
            #partymeans[party] = 0
            partyrestpercentages[party] = 0
        partycounts["allparties"] = 0
        includedates = self.get_last_dates_ordered(nrdays)

        ### count total number of mentions per party ###
        for day in self.history_of_party_mentions_counts:
            if day in includedates:
                for party in self.allparties:
                    if not party in self.history_of_party_mentions_counts[day]:
                        self.history_of_party_mentions_counts[day][party] = 0
                    if self.peakday(party,day):
                        partycounts[party] += self.means_per_party[party]
                        partycounts["allparties"] += self.means_per_party[party]
                    else:
                        partycounts[party] += self.history_of_party_mentions_counts[day][party]
                        partycounts["allparties"] += self.history_of_party_mentions_counts[day][party]

        ### compute seats ###
        for party in self.allparties:
            self.seats_per_party[party] = int(150 * partycounts[party] / partycounts["allparties"])
            partyrestpercentages[party] = 150 * partycounts[party] / partycounts["allparties"] - self.seats_per_party[party]

        ### add rest seats ###
        if restseatmethod == 'largestrest':
            for party in sorted(partyrestpercentages, key=partyrestpercentages.get, reverse=True):
                if self.sumofseats() < 150:
                    self.seats_per_party[party] += 1
                    #print(party)

        else: # largestmean
            while self.sumofseats() < 150:
                biggestmeannrofvotesforrestseat = 0
                for party in self.allparties:
                    if party in self.seats_per_party:
                        meannrofvotesforrestseat = partycounts[party] / (self.seats_per_party[party] + 1)
                    else:
                        meannrofvotesforrestseat = partycounts[party]
                    if meannrofvotesforrestseat > biggestmeannrofvotesforrestseat:
                        restseatparty = party
                        biggestmeannrofvotesforrestseat = meannrofvotesforrestseat
                if restseatparty in self.seats_per_party:
                    self.seats_per_party[restseatparty] += 1
                else:
                    self.seats_per_party[restseatparty] = 1
                #print(restseatparty)


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

    def peakday(self,party,day,peakfactor=2):
        if party in self.history_of_party_mentions_counts[day]:
            if self.history_of_party_mentions_counts[day][party] > peakfactor * self.means_per_party[party]:
                return True
        return False
