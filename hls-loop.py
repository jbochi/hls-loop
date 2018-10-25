import itertools
import math
import re
import time
from decimal import Decimal


SEGMENTS_IN_PLAYLIST = 10

from flask import Flask, Response, make_response
app = Flask(__name__)

def read_file_durations():
    with open("static/bipbop_4x3/gear1/prog_index.m3u8") as f:
        content = f.read()
    file_durations = re.findall(r"EXTINF:([\d\.]+),\s*\n([\w\.]+)", content, flags=re.M)
    return [(float(duration), filename) for duration, filename in file_durations]

files_and_durations = read_file_durations()
total_duration = sum(duration for duration, filename in files_and_durations)
n_segments = len(files_and_durations)
zero = time.time()

@app.route("/variant.m3u8")
def variant():
    return Response("""#EXTM3U
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=232370,CODECS="mp4a.40.2, avc1.4d4015"
playlist1.m3u8
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=649879,CODECS="mp4a.40.2, avc1.4d401e"
playlist2.m3u8
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=991714,CODECS="mp4a.40.2, avc1.4d401e"
playlist3.m3u8
#EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=1927833,CODECS="mp4a.40.2, avc1.4d401f"
playlist4.m3u8
""", mimetype="application/x-mpegURL", headers={'Access-Control-Allow-Origin': '*'})

@app.route("/playlist<int:id>.m3u8")
def playlist(id):
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

    def format(segment):
        duration, filename = segment
        return "#EXTINF:{duration},\n/static/bipbop_4x3/gear{id}/{filename}".format(duration=duration, id=id, filename=filename)

    segments_txt = '\n'.join([format(segment) for segment in segments])

    return Response("""#EXTM3U
#EXT-X-TARGETDURATION:11
#EXT-X-VERSION:3
#EXT-X-MEDIA-SEQUENCE:{media_sequence}
{segments_txt}""".format(media_sequence = media_sequence + sequence_in_loop, segments_txt=segments_txt),
    mimetype="application/x-mpegURL", headers={'Access-Control-Allow-Origin': '*'})

@app.route("/crossdomain.xml")
def crossdomain():
    return Response("""<cross-domain-policy>
<site-control permitted-cross-domain-policies="all"/>
<allow-access-from domain="*" secure="false"/>
<allow-http-request-headers-from domain="*" headers="*" secure="false"/>
</cross-domain-policy>""", mimetype="text/xml")

@app.route("/static/bipbop_4x3/gear<int:id>/<string:filename>")
def segment(id, filename):
    with open('./static/bipbop_4x3/gear%d/%s' % (id, filename), 'rb') as f:
        binary = f.read()
    response = make_response(binary)
    response.headers.set('Content-Type', 'video/MP2T')
    response.headers.set('Access-Control-Allow-Origin', '*')
    return response

if __name__ == "__main__":
    #app.debug = True
    app.run(host='0.0.0.0')
