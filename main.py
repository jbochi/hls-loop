#!/usr/bin/env python
import webapp2
import itertools
import math
import re
import time
from decimal import Decimal

SEGMENTS_IN_PLAYLIST = 10
M3U8_TEMPLATE = """#EXTM3U
#EXT-X-TARGETDURATION:11
#EXT-X-VERSION:3
#EXT-X-MEDIA-SEQUENCE:{media_sequence}
{segments_txt}"""

class PlaylistHandler(webapp2.RequestHandler):
    def format_segment(self, id, segment):
        duration, filename = segment
        return "#EXTINF:{duration},\n/static/bipbop_4x3/gear{id}/{filename}".format(duration=duration, id=id, filename=filename)

    def next_segments(self):
        now = time.time()
        delta = now - zero
        n_loops = math.floor(delta / total_duration)
        delta_in_loop = delta - total_duration * n_loops
        media_sequence = int(n_loops * n_segments)
        sequence_in_loop = 0
        segments = []
        for duration, filename in itertools.cycle(files_and_durations):
            delta_in_loop -= duration
            if delta_in_loop > 0:
                sequence_in_loop += 1
            elif len(segments) < SEGMENTS_IN_PLAYLIST:
                segments.append([duration, filename])
            else:
                break
        return segments, media_sequence + sequence_in_loop

    def get(self, id):
        segments, media_sequence = self.next_segments()
        segments_txt = '\n'.join([self.format_segment(id, segment) for segment in segments])
        content = M3U8_TEMPLATE.format(media_sequence = media_sequence, segments_txt=segments_txt)
        self.response.headers['Content-Type'] = "application/vnd.apple.mpegurl"
        self.response.write(content)


def read_file_durations():
    with open("prog_index.m3u8") as f:
        content = f.read()
    file_durations = re.findall(r"EXTINF:([\d\.]+),\s*\n([\w\.]+)", content, flags=re.M)
    return [(float(duration), filename) for duration, filename in file_durations]


files_and_durations = read_file_durations()
total_duration = sum(duration for duration, filename in files_and_durations)
n_segments = len(files_and_durations)
zero = time.mktime((2013, 1, 1, 0, 0, 0, 0, 0, 0))

app = webapp2.WSGIApplication([
    ('/playlist(\d+)\.m3u8', PlaylistHandler)
], debug=True)
