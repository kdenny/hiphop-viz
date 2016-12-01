import csv
from pprint import pprint
import urllib2
import json
import spotipy

from spotify_query_functions import spQuery, get_infile_artists


def getArtist(artist):

    artistInfo = {}
    result = spQuery(artist)['artists']['items'][0]
    pprint(result)
    artistInfo['name'] = result['name']
    artistInfo['popularity'] = result['popularity']
    artistInfo['id'] = result['id']
    artistInfo['featured_artists'] = {}
    artistInfo['featured_by_artists'] = {}
    artistInfo['albums'] = []

    return artistInfo


def processArtists(artist_list):
    artist_data = []

    for artist in artist_list:
        if str(artist).lower() != 'name':
            pname = str(artist).replace(" ","%20").replace('"',"")
            pname = pname.decode('utf-8')
            info = getArtist(pname)
            pprint(info)
            artist_data.append(info)

    return artist_data

def processFirstDegFeatures(artist_data):
    new_artist_data = []

    for arecord in artist_data:

        artist_name = arecord['name']
        uri_string = 'spotify:artist:{0}'.format(arecord['id'])
        spotify = spotipy.Spotify()

        artist_albums = spotify.artist_albums(uri_string, album_type='album')['items']

        pprint(artist_albums)


        ### Properly save all albums to the artist


        ### For each album, find every song: albumSongs

            ### For each albumSong, check if other artists are featured

            ### If other artists are featured -

                ### Save song to artist's album

                ### Save artist2 to artist1's featured artists

                    ### Save song to artist2's features

                ### Save artist1 to artist2's featured by artists

                    ### Save song to artist1's featured ons












original_artist_list = get_infile_artists()

artist_data = processArtists(original_artist_list)

new_artist_data = processFirstDegFeatures(artist_data)




