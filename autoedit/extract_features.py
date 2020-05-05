import argparse
import av
import math
import numpy as np
import scipy.ndimage

from collections import deque
from PIL import Image

parser = argparse.ArgumentParser(description='Extract editing features from a video.')
parser.add_argument('input', type=str, help='Path to the input video.')
parser.add_argument('output', type=str, help='Path for the output csv.')
parser.add_argument('--chunk_ms', type=int, default=250, help='Duration of each chunk in ms.')
parser.add_argument('--duration', type=int, default=-1, help='Duration of video to process in seconds.')
parser.add_argument('--video_divs', type=int, default=0, help='Number of cumulative spatial divisions to make in each video frame.')
args = parser.parse_args()

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

def main():
    c = av.open(args.input)
    last_video_frame = None
    with open(args.output, 'w') as output_file:
        for i, chunk in enumerate(ChunkReader(c, args.chunk_ms)):
            if args.duration >= 0 and chunk.start_ts > args.duration:
                break
            current_video_frame = scipy.ndimage.gaussian_filter(chunk.average_video_frame(), sigma=5)
            if last_video_frame is None:
                last_video_frame = current_video_frame

            output = [chunk.start_ts, chunk.average_audio_power()]
            frame_divs = (
                divide_frame(last_video_frame, args.video_divs),
                divide_frame(current_video_frame, args.video_divs)
            )
            for last_div, current_div in zip(*frame_divs):
                output.append(np.linalg.norm(unsigned_diff(last_div, current_div)))
            output_file.write(','.join(str(x) for x in output) + '\n')

            last_video_frame = current_video_frame

if __name__ == '__main__':
    main()