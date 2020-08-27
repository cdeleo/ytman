import argparse
import collections
import fractions
import numpy as np
import os.path
import xml.etree.ElementTree as ET

DEFAULT_FRAME_DURATION = fractions.Fraction(1, 30)
DEFAULT_WIDTH = 1280
DEFAULT_HEIGHT = 720

parser = argparse.ArgumentParser(description='Produce a clip list from model evaluation.')
parser.add_argument('input', type=str, help='Path to the evaluated model output.')
parser.add_argument('video', type=str, help='Path to the asset video.')
parser.add_argument('output', type=str, help='Path for the output clip list.')

Interval = collections.namedtuple('Interval', ('start', 'end', 'y'))

def get_intervals(t, y):
    t_frac = [fractions.Fraction(x).limit_denominator(100) for x in t]
    intervals = []
    start_index = 0
    for i in range(1, len(y)):
        if y[i] != y[start_index]:
            intervals.append(Interval(t_frac[start_index], t_frac[i], y[start_index]))
            start_index = i
    intervals.append(Interval(t_frac[start_index], 2 * t_frac[-1] - t_frac[-2], y[-1]))
    return intervals

class ClipDocument(object):

    def __init__(self, video_path, video_duration, frame_duration, width, height):
        self._video_duration = video_duration
        self._root = ET.Element('fcpxml', {'version': '1.8'})
        self.doc = ET.ElementTree(self._root)
        self._add_resources(video_path, video_duration, frame_duration, width, height)
        self._add_sequence()

    def _add_resources(self, video_path, video_duration, frame_duration, width, height):
        resources = ET.SubElement(self._root, 'resources')
        ET.SubElement(resources, 'format', {
            'id': 'r0',
            'name': 'VideoFormat',
            'frameDuration': str(frame_duration) + 's',
            'width': str(width),
            'height': str(height),
        })
        ET.SubElement(resources, 'asset', {
            'id': 'r1',
            'name': os.path.basename(video_path),
            'src': video_path,
            'duration': str(video_duration) + 's',
            'start': '0/1s',
            'format': 'r0',
            'hasVideo': '1',
            'hasAudio': '1',
            'audioSources': '1',
            'audioChannels': '2',
        })

    def _add_sequence(self):
        library = ET.SubElement(self._root, 'library')
        event = ET.SubElement(library, 'event', {'name': 'Auto edit'})
        project = ET.SubElement(event, 'project', {'name': 'Auto edit'})
        sequence = ET.SubElement(project, 'sequence', {
            'format': 'r0',
            'duration': str(self._video_duration) + 's',
            'tcStart': '3600/1s',
            'tcFormat': 'NDF',
        })
        self._spine = ET.SubElement(sequence, 'spine')

    def add_interval(self, interval):
        ET.SubElement(self._spine, 'asset-clip', {
            'format': 'r0',
            'ref': 'r1',
            'duration': str(interval.end - interval.start) + 's',
            'start': str(interval.start) + 's',
            'offset': str(interval.start) + 's',
            'enabled': '1',
            'name': 'interval',
            'tcFormat': 'NDF',
        })

def create_document(
        t,
        y,
        video_path,
        frame_duration=DEFAULT_FRAME_DURATION,
        width=DEFAULT_WIDTH,
        height=DEFAULT_HEIGHT):
    intervals = get_intervals(t, y)
    doc = ClipDocument(video_path, intervals[-1].end, frame_duration, width, height)
    for interval in (interval for interval in intervals if interval.y == 0):
        doc.add_interval(interval)
    return doc.doc

def main():
    args = parser.parse_args()
    data = np.loadtxt(args.input, delimiter=',')
    doc = create_document(data[:, 0], data[:, 1], os.path.abspath(args.video))
    with open(args.output, 'wb') as output_file:
        doc.write(output_file)

if __name__ == '__main__':
    main()