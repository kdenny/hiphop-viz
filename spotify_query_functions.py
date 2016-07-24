import csv
from pprint import pprint
import urllib2
import json
import spotipy

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

def clearDumb(infile_artists):

    newconnections = []

    quickdict = {}

    fty = open("connections_2.csv", 'rb')
    try:
        reader = csv.DictReader(fty)
        for row in reader:
            if row['source'] not in quickdict:
                quickdict[row['source']] = []
                quickdict[row['source']].append(row['target'])
                newconnections.append(row)
            else:
                if row['target'] not in quickdict[row['source']]:
                    quickdict[row['source']].append(row['target'])

                    if row['target'] in infile_artists:
                        newconnections.append(row)
    finally:
        fty.close()


    with open('connections_2.csv', 'wb') as fb:  # Just use 'w' mode in 3.x
        w = csv.DictWriter(fb, ['source','target'])
        w.writeheader()

        for af in newconnections:
            w.writerow(af)

    return quickdict

def get_infile_artists():
    rappers_infile = []


    f = open("rappers_4.csv", 'rb')
    try:
        reader = csv.reader(f)
        for row in reader:
            if len(row) > 0:
                rname = row[0]
                rappers_infile.append(rname)
    finally:
        f.close()

    return rappers_infile

def resize_artists(artistfeatures):
    from pprint import pprint
    artistsizes = {}

    for artist in artistfeatures:
        artistsizes[artist] = {}
        artistsizes[artist]['size'] = len(artistfeatures[artist])
        artistsizes[artist]['name'] = artist

    with open("rappers_2.csv", 'wb') as f:
        writer = csv.DictWriter(f, ['name', 'size'])
        for rl in artistsizes:
            pprint(artistsizes[rl])
            if artistsizes[rl]['size'] > 1 or rl in artistfeatures:
                writer.writerow(artistsizes[rl])

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

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


def processFeatures(artists):
    sp = spotipy.Spotify()
    allfeatures = []
    usedartists = []
    artistFeatures = {}
    maybes = []

    for at in artists:
        if is_ascii(at) and at not in usedartists and at != 'Name':
            currentartist = at.encode('utf-8')
            artistquery = get_artist(currentartist)
            ishiphop = 0
            ispopular = 0
            if artistquery:
                # if 'popularity' not in artistquery:
                #     for alb in artistquery:
                features = []
                alltracks = []
                pprint("Querying for {0}".format(currentartist))
                pprint("Currently have {0} artists in queue".format(len(artists)))
                pprint("Currently have processed {0} artists".format(len(usedartists)))
                # thisr = get_songs(currentartist,0)
                results = sp.search(q=currentartist, limit=50)['tracks']
                # pprint(results)
                for t in results['items']:
                    alltracks.append(t)
                offs = 50

                querycount = 0

                while results['next'] and querycount < 50:
                    if querycount % 10 == 0:
                        pprint("Querying for the {0} time for {1}".format(querycount, currentartist))
                    querycount += 1
                    # thisr = get_songs(currentartist,offs)
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
                            if is_ascii(tf):
                                tf = tf.encode('utf-8')
                                if tf not in features and tf in artists:
                                    features.append(tf)
                                    featdict = {}
                                    featdict['source'] = currentartist
                                    featdict['target'] = tf
                                    writeFeatures([featdict])
                                    allfeatures.append(featdict)
                                    if currentartist in artistFeatures:
                                        artistFeatures[currentartist].append(tf)
                                    else:
                                        artistFeatures[currentartist] = []
                                        artistFeatures[currentartist].append(tf)
                                elif tf not in artists and tf not in maybes:
                                    print("Should you add {0} to the list?").format(tf)
                                    maybes.append(tf)


                # artists.remove(currentartist)
                usedartists.append(currentartist)
                pprint(features)
                # print(currentartist)
                # artistFeatureCounts[currentartist] = len(features)

            else:
                usedartists.append(currentartist)

    writeExtras(maybes)

    return allfeatures



def get_connections():
    currentConnections = {}
    masterConnections = []
    connectionCount = {}

    f = open("connections_2.csv", 'rb')
    try:
        reader = csv.reader(f)
        for row in reader:
            cot = {}
            source = row[0]
            target = row[1]
            if source not in currentConnections:
                currentConnections[source] = []
                currentConnections[source].append(target)
            elif target not in currentConnections[source]:
                currentConnections[source].append(target)

            if target not in currentConnections:
                currentConnections[target] = []
                currentConnections[target].append(source)
            elif source not in currentConnections[target]:
                currentConnections[target].append(source)

        for cc in currentConnections:
            connectionCount[cc] = len(currentConnections[cc])

    finally:
        f.close()

    return connectionCount


def writeFeatures(allfeatures):

    fkeys = allfeatures[0].keys()

    with open('connections_2.csv', 'a') as f:  # Just use 'w' mode in 3.x
        w = csv.DictWriter(f, fkeys)
        # w.writeheader()

        for af in allfeatures:
            for ak in af:
                af[ak] = af[ak].encode('utf-8')
            w.writerow(af)
            # if af['target'] not in rappers:
            #     # rappers.append(af['target'])
            #     rd = {}
            #     rd['name'] = af['target']
            #     rd['size'] = 10
            #     rapper_list.append(rd)

def writeExtras(allextras):

    fkeys = ['Name']

    with open('extras.csv', 'wb') as f:  # Just use 'w' mode in 3.x
        w = csv.DictWriter(f, fkeys)
        # w.writeheader()

        for ef in allextras:
            af = {}
            af['Name'] = ef.encode('utf-8')
            w.writerow(af)
            # if af['target'] not in rappers:
            #     # rappers.append(af['target'])
            #     rd = {}
            #     rd['name'] = af['target']
            #     rd['size'] = 10
            #     rapper_list.append(rd)

def writeNewRappers(rappers):

    rappercities = {}

    f = open("rappers_3.csv", 'rb')
    try:
        reader = csv.reader(f)
        for row in reader:
            if len(row) > 0:
                rappercities[row[0]] = row[1]
    finally:
        f.close()


    rapperprint = []
    for rp in rappers:
        rt = {}
        rt['name'] = rp
        rt['size'] = rappers[rp]
        rapperprint.append(rt)

    fkeys = ['name','size','city','featcount']

    with open('final_rappers.csv', 'wb') as f:  # Just use 'w' mode in 3.x
        w = csv.DictWriter(f, fkeys)
        w.writeheader()

        for ef in rapperprint:
            ef['name'] = ef['name'].encode('utf-8')
            ef['featcount'] = ef['size']
            ef['size'] = ef['size'] / 3
            if ef['name'] in rappercities:
                ef['city'] = rappercities[ef['name']]
            else:
                ef['city'] = 'null'
            # if ef['size'] < 1:
            #     ef['size'] = 1
            w.writerow(ef)
            # if af['target'] not in rappers:
            #     # rappers.append(af['target'])
            #     rd = {}
            #     rd['name'] = af['target']
            #     rd['size'] = 10
            #     rapper_list.append(rd)


# artistfeatures = clearDumb(existingartists)
# writeFeatures(features)

# existingartists = get_infile_artists()
# features = processFeatures(existingartists)


conresults = get_connections()
writeNewRappers(conresults)





# resize_artists(artistfeatures)