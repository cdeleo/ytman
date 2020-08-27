import argparse
import av
import bisect
import fractions
import itertools
import math
import numpy as np
import os.path
import scipy.ndimage
import xml.etree.ElementTree as ET

from collections import deque

DEFAULT_CHUNK_MS = 250
DEFAULT_DURATION = -1
DEFAULT_VIDEO_DIVS = 0

parser = argparse.ArgumentParser(description='Extract editing features from a video.')
parser.add_argument('input', type=str, help='Path to the input video.')
parser.add_argument('output', type=str, help='Path for the output csv.')
parser.add_argument('--chunk_ms', type=int, default=DEFAULT_CHUNK_MS, help='Duration of each chunk in ms.')
parser.add_argument('--duration', type=int, default=DEFAULT_DURATION, help='Duration of video to process in seconds.')
parser.add_argument('--video_divs', type=int, default=DEFAULT_VIDEO_DIVS, help='Number of cumulative spatial divisions to make in each video frame.')
parser.add_argument('--clips', type=str, help='Path to the clip xml file for ground truth.')
parser.add_argument('--clip_asset', type=str, help='Name of the input asset in the clip list, if different from the input video.')

frame_time = lambda f: f.pts * f.time_base

class Chunk(object):

    def __init__(self, video_frames, audio_frames, start_ts):
        self.video_frames = video_frames
        self.audio_frames = audio_frames
        self.start_ts = start_ts

    def average_video_frame(self):
        extract_y = lambda f: f.to_ndarray()[:f.format.height, :f.format.width]
        return np.average(
            np.stack([extract_y(f) for f in self.video_frames]), axis=0).astype(np.uint8)

    def average_audio_power(self):
        total_samples = np.concatenate([f.to_ndarray() for f in self.audio_frames], axis=1)
        return np.sum(np.linalg.norm(total_samples, axis=1)) / math.sqrt(total_samples.shape[1])

class ChunkReader(object):

    def __init__(self, c, chunk_size_ms):
        self.chunk_size_ms = chunk_size_ms
        self._packets = c.demux(video=0, audio=0)
        self._buffers = [deque(), deque()]
        self._ts_ms = 0

    def __iter__(self):
        return self

    def __next__(self):
        end_ts = (self._ts_ms + self.chunk_size_ms) / 1000
        chunk = ([], [])
        for i, buffer in enumerate(self._buffers):
            while buffer and frame_time(buffer[0]) < end_ts:
                chunk[i].append(buffer.popleft())
        while not all(self._buffers):
            packet = self._packets.__next__()
            i = 0 if packet.stream.type == 'video' else 1
            for frame in packet.decode():
                if frame_time(frame) < end_ts:
                    chunk[i].append(frame)
                else:
                    self._buffers[i].append(frame)
        start_ts = self._ts_ms / 1000
        self._ts_ms += self.chunk_size_ms
        return Chunk(chunk[0], chunk[1], start_ts)

class ClipList(object):

    def __init__(self, clip_tree, asset_name):
        self.time_points = list(self._extract_clip_times(clip_tree, asset_name))
        for i in range(1, len(self.time_points)):
            assert(self.time_points[i] > self.time_points[i-1])

    def _extract_clip_times(self, clip_tree, asset_name):
        for clip in clip_tree.findall('.//asset-clip[@name=\'%s\']' % asset_name):
            start = parse_fractional_seconds(clip.get('start'))
            yield start
            yield start + parse_fractional_seconds(clip.get('duration'))

    def includes(self, t):
        return bisect.bisect(self.time_points, t) % 2 == 1
        

def divide_frame(frame, levels):
    if levels:
        mid_h = frame.shape[0] // 2
        mid_w = frame.shape[1] // 2
        yield from divide_frame(frame[:mid_h, :mid_w], levels - 1)
        yield from divide_frame(frame[:mid_h, mid_w:], levels - 1)
        yield from divide_frame(frame[mid_h:, :mid_w], levels - 1)
        yield from divide_frame(frame[mid_h:, mid_w:], levels - 1)
    else:
        yield frame

def unsigned_diff(a, b):
    ab = a - b
    ba = b - a
    mask = a < b
    ab[mask] = ba[mask]
    return ab

def parse_fractional_seconds(t):
    assert(t[-1] == 's')
    parts = t[:-1].split('/')
    return fractions.Fraction(int(parts[0]), int(parts[1]) if len(parts) > 1 else 1)

def extract(
        video_path,
        clip_path=None,
        clip_asset_name=None,
        chunk_ms=DEFAULT_CHUNK_MS,
        duration=DEFAULT_DURATION,
        video_divs=DEFAULT_VIDEO_DIVS):
    c = av.open(video_path)
    if not clip_asset_name:
        clip_asset_name = os.path.basename(video_path)
    clip_list = ClipList(ET.parse(clip_path), clip_asset_name) if clip_path else None

    last_video_frame = None
    for i, chunk in enumerate(ChunkReader(c, chunk_ms)):
        if duration >= 0 and chunk.start_ts > duration:
            break
        if not i % 1000:
            print ('Starting chunk at %fs...' % (i * chunk_ms / 1000))
        current_video_frame = scipy.ndimage.gaussian_filter(chunk.average_video_frame(), sigma=5)
        if last_video_frame is None:
            last_video_frame = current_video_frame

        output = [chunk.start_ts, chunk.average_audio_power()]
        frame_divs = (
            divide_frame(last_video_frame, video_divs),
            divide_frame(current_video_frame, video_divs)
        )
        for last_div, current_div in zip(*frame_divs):
            output.append(np.linalg.norm(unsigned_diff(last_div, current_div)))
        if clip_list:
            output.append(0 if clip_list.includes(chunk.start_ts) else 1)
        yield output

        last_video_frame = current_video_frame

def main():
    args = parser.parse_args()
    with open(args.output, 'w') as output_file:
        for row in extract(
                args.input,
                args.clips,
                args.clip_asset,
                args.chunk_ms,
                args.duration,
                args.video_divs):
            output_file.write(','.join(str(x) for x in row) + '\n')

if __name__ == '__main__':
    main()