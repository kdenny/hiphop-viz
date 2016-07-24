__author__ = 'kdenny'

import spotipy
from pprint import pprint
import random
import urllib2
import json
import csv


## {{{ http://code.activestate.com/recipes/511478/ (r1)
import math
import functools




def spQuery(artist):
    "https://api.spotify.com/v1/artists/0OdUWJ0sBjDrqHygGUXeCF"
    url = "https://api.spotify.com/v1/search?"
    url += "q=artist:{0}&type=artist".format(artist)
    print(url)


    conn = urllib2.urlopen(url, None)
    try:
        response = json.loads(conn.read())
    finally:
        conn.close()

    # pprint(response)
    return response

def spQuerySongs(artist,offset):
    if offset == 0:
        offs = ''
    else:
        offs = '&offset={0}'.format(offset)
    url = "https://api.spotify.com/v1/search?"
    url += "q=artist:{0}&type=track&limit=50{1}".format(artist, offs)

    try:
        conn = urllib2.urlopen(url, None)
        try:
            response = json.loads(conn.read())
        finally:
            conn.close()
    except urllib2.HTTPError:
        print 'Could not download page'




    # pprint(response)
    return response

sp = spotipy.Spotify()

def percentile(N, percent, key=lambda x:x):
    """
    Find the percentile of a list of values.

    @parameter N - is a list of values. Note N MUST BE already sorted.
    @parameter percent - a float value from 0.0 to 1.0.
    @parameter key - optional key function to compute value from each element of N.

    @return - the percentile of the values
    """
    if not N:
        return None
    k = (len(N)-1) * percent
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return key(N[int(k)])
    d0 = key(N[int(f)]) * (c-k)
    d1 = key(N[int(c)]) * (k-f)
    return d0+d1

def get_artist(name):
    items = []
    pname = str(name).replace(" ","%20").replace('"',"")
    pname = pname.decode('utf-8')
    if is_ascii(pname):
        results = spQuery(pname)
        items = results['artists']['items']
    if len(items) > 0:
        return items[0]
    else:
        return None

def get_songs(name,offs):
    items = []
    pname = str(name).replace(" ","%20").replace('"',"")
    pname = pname.decode('utf-8')
    if is_ascii(pname):
        results = spQuerySongs(pname,offs)
        items = results
    if len(items) > 0:
        return items
    else:
        return None


def clearDumb(infile_artists):

    newconnections = []

    fty = open("connections_2.csv", 'rb')
    try:
        reader = csv.DictReader(fty)
        for row in reader:
            if row['target'] in infile_artists:
                newconnections.append(row)
    finally:
        fty.close()


    with open('connections_2.csv', 'wb') as fb:  # Just use 'w' mode in 3.x
        w = csv.DictWriter(fb, ['source','target'])
        w.writeheader()

        for af in newconnections:
            w.writerow(af)





usedartists = []

allfeatures = []

artistFeatures = {}
artistFeatureCounts = {}

processed_rappers = []

artists = ['Kanye West']

f = open("connections_2.csv", 'rb')
try:
    reader = csv.reader(f)
    for row in reader:
        rname = row[0]
        processed_rappers.append(rname)
finally:
    f.close()


rappers_infile = []


f = open("rappers_2.csv", 'rb')
try:
    reader = csv.reader(f)
    for row in reader:
        rname = row[0]
        rappers_infile.append(rname)
        if rname not in processed_rappers:
            artists.append(rname)
finally:
    f.close()


clearDumb(rappers_infile)


genres = ['hip hop', 'pop rap', "alternative hip hop", "hip hop", "rap", "deep trap", "west coast rap", "g funk",
          "gangster rap", "crunk", "old school hip hop", "southern hip hop", "east coast hip hop", "hardcore hip hop", "trap music"]

count = 0

while len(usedartists) < 200:

    anum = int(random.uniform(0, (len(artists))))
    ca = artists[anum]

    if is_ascii(ca):
        currentartist = ca.encode('utf-8')

        artistquery = get_artist(currentartist)
        ishiphop = 0
        ispopular = 0
        if artistquery:
            if 'popularity' not in artistquery:
                for alb in artistquery:

                    if alb['popularity'] > 10:
                        ispopular = 1
                    for yt in alb['genres']:
                        if yt in genres:
                            ishiphop = 1
                        else:
                            if yt in rappers_infile:
                                ishiphop = 1
                            print(yt)
            else:
                if artistquery['popularity'] > 10:
                    ispopular = 1
                    for yt in artistquery['genres']:
                        if yt in genres:
                            ishiphop = 1
                        else:
                            if yt in rappers_infile:
                                ishiphop = 1
                            print(yt)




            if currentartist not in usedartists and ishiphop > 0 and ispopular > 0 and currentartist not in processed_rappers:

                features = []

                alltracks = []
                pprint("Querying for {0}".format(currentartist))
                pprint("Currently have {0} artists in queue".format(len(artists)))
                pprint("Currently have processed {0} artists".format(len(usedartists)))
                thisr = get_songs(currentartist,0)
                results = sp.search(q=currentartist, limit=50)['tracks']
                for t in results['items']:
                    alltracks.append(t)
                offs = 50

                querycount = 0

                while results['next'] and querycount < 50:
                    if querycount % 10 == 0:
                        pprint("Querying for the {0} time for {1}".format(querycount, currentartist))
                    querycount += 1
                    thisr = get_songs(currentartist,offs)
                    nextresults = sp.search(q=currentartist, limit=50, offset=offs)['tracks']
                    results = nextresults
                    offs += 50
                    for ar in nextresults['items']:
                        # pprint(ar)
                        alltracks.append(ar)

                print("Processing tracks for {0}".format(currentartist))
                # pprint(results)

                for r in alltracks:
                    otherArtists = r['artists']
                    songTitle = r['name']
                    popularity = r['popularity']
                    thesefeatures = []
                    realArtist = False

                    for oa in otherArtists:
                        if oa['name'] != currentartist:
                            thesefeatures.append(oa['name'])
                        else:
                            realArtist = True

                    if realArtist == True and len(thesefeatures) > 0:
                        for tf in thesefeatures:
                            if tf not in features:
                                features.append(tf)
                                featdict = {}
                                featdict['source'] = currentartist
                                featdict['target'] = tf
                                allfeatures.append(featdict)
                                if currentartist in artistFeatures:
                                    artistFeatures[currentartist].append(tf)
                                else:
                                    artistFeatures[currentartist] = []
                                    artistFeatures[currentartist].append(tf)
                            if tf not in artists and tf not in usedartists:
                                artists.append(tf)

                artists.remove(currentartist)
                usedartists.append(currentartist)
                pprint(features)
                print(currentartist)
                artistFeatureCounts[currentartist] = len(features)

            else:
                usedartists.append(currentartist)


# pprint(artists)
pprint(artistFeatureCounts)
pprint(artistFeatures)

fkeys = allfeatures[0].keys()

rapper_list = []
rappers = []

import csv

with open('connections_2.csv', 'a') as f:  # Just use 'w' mode in 3.x
    w = csv.DictWriter(f, fkeys)
    # w.writeheader()

    for af in allfeatures:
        for ak in af:
            af[ak] = af[ak].encode('utf-8')
        w.writerow(af)
        if af['target'] not in rappers:
            rappers.append(af['target'])
            rd = {}
            rd['name'] = af['target']
            rd['size'] = 10
            rapper_list.append(rd)




# with open('rappers_2.csv', 'wb') as f:  # Just use 'w' mode in 3.x
#     w = csv.DictWriter(f, ['name', 'size'])
#     w.writeheader()
#
#     for rl in rapper_list:
#         w.writerow(rl)



with open("rappers_2.csv", 'a') as f:
    writer = csv.DictWriter(f, ['name', 'size'])
    for rl in rapper_list:
        if rl['name'] not in rappers_infile:
            writer.writerow(rl)



# finalArtistResults = {}
# finalArtists = []
#
# featurecounts = []
#
# for artist in artistFeatures:
#     featurecounts.append(len(artistFeatures[artist]))
#
# import numpy as np
# feature50 = np.percentile(featurecounts,60)
#
#
# for artist in artistFeatures:
#     if len(artistFeatures[artist]) > feature50:
#         finalArtistResults[artist] = artistFeatures[artist]
#     finalArtists.append(artist)
#
# pprint(finalArtists)

