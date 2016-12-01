import csv
from pprint import pprint
import urllib2
import json
import spotipy

from spotify_query_functions import spQuery, get_infile_artists

from unidecode import unidecode
def remove_non_ascii(text):
    for i in range(0, len(text)):
        try:
            text[i].encode("ascii")
        except:
            # means it's non-ASCII
            text = text.replace(text[i], " ")  # replacing it with a single space
    return text

def getArtist(artist):

    artistInfo = {}
    result = spQuery(artist)['artists']['items'][0]
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

        artist_name = remove_non_ascii(arecord['name'])
        uri_string = 'spotify:artist:{0}'.format(arecord['id'])
        spotify = spotipy.Spotify()

        artist_albums = spotify.artist_albums(uri_string, album_type='album')['items']

        # pprint(artist_albums)

        for alb in artist_albums:
            if 'US' in alb["available_markets"]:
                alb_item = {}

                alb_item['uri'] = alb['uri']
                alb_item['name'] = remove_non_ascii(alb['name'])
                album_tracks = spotify.album_tracks(alb_item['uri'])['items']

                alb_item['tracks'] = []

                for track in album_tracks:
                    track_item = {}
                    if 'edit' not in remove_non_ascii(track['name']).lower():
                        track_item['name'] = remove_non_ascii(track['name'])
                        track_item['artist'] = artist_name
                        track_item['id'] = track['id']
                        if 'popularity' in track:
                            track_item['popularity'] = track['popularity']
                        track_item['features'] = []

                        for feat_artist in track['artists']:
                            feat_item = {}
                            if remove_non_ascii((feat_artist['name'])) != artist_name:
                                feat_item['name'] = remove_non_ascii(feat_artist['name'])
                                feat_item['id'] = feat_artist['id']
                                track_item['features'].append(feat_item)

                        if len(track_item['features']) > 0:
                            alb_item['tracks'].append(track_item)

                arecord['albums'].append(alb_item)

        new_artist_data.append(arecord)
    pprint(new_artist_data)
    return new_artist_data


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




