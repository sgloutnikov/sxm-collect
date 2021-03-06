import logging
import os
import re
from itertools import filterfalse

logger = logging.getLogger(__name__)

replace_song_dict = {}


# Run through replace dictionary, and replace matches
def replace_definitions(station, now_playing_json):
    song = str(now_playing_json["title"])
    logger.info("[" + station + "] - " + "Song Before Replace Scrub: " + song)
    for song_match, song_replace in replace_song_dict[station].items():
        pattern = re.compile(song_match)
        if re.search(pattern, song):
            song = re.sub(pattern, str(song_replace), song)
            logger.info("[" + station + "] - " + "Song After Replace Scrub: " + song)
    now_playing_json["title"] = song
    return now_playing_json


# Strip the (xx)
def strip_year_tag(song_json):
    song = str(song_json["title"])
    song = re.sub(r"\s\(\d\d\)", "", song).strip()
    song_json["title"] = song
    return song_json


# If song length is 35 it has been stripped by the SXM API. Remove the last incomplete word.
def length_verification(song_name):
    song = str(song_name)
    if len(song) == 35:
        song = song.rsplit(" ", 1)[0]
        song = song.rstrip(",")
    return song


def __is_comment(s):
    return s.startswith("#")


def init(station):
    # Load Song Replace Dictionary from File
    replace_songs = {}
    fpath = os.path.join(os.path.dirname(__file__), "../filter_lists/" + station + "/edit_replace_song.txt")
    with open(fpath, "r") as f:
        for line in filterfalse(__is_comment, f):
            line_list = str(line).rsplit(";", 1)
            replace_songs[str(line_list[0])] = str(line_list[1].strip())
    replace_song_dict[station] = replace_songs
    logger.info("[" + station + "] - " + "Loaded Song Replace Dictionary: " +
                str(len(replace_song_dict[station])) + " definitions.")
