import argparse
import common
import numpy as np
import scipy.stats

DEFAULT_AUDIO_SCALE = 0.01
DEFAULT_VIDEO_SCALE = 6541
DEFAULT_KERNEL_WIDTH = 32

parser = argparse.ArgumentParser(description='Process raw extracted features for use.')
parser.add_argument('input', type=str, help='Path to the input raw features.')
parser.add_argument('output', type=str, help='Path for the output processed.')
parser.add_argument('--audio_scale', type=float, default=DEFAULT_AUDIO_SCALE, help='Scale factor for audio features.')
parser.add_argument('--video_scale', type=float, default=DEFAULT_VIDEO_SCALE, help='Scale factor for video features.')
parser.add_argument('--kernel_width', type=int, default=DEFAULT_KERNEL_WIDTH, help='Width of the augmenting convolution kernel.')

def get_kernel(width):
    k = scipy.stats.norm.pdf(np.linspace(-3, 3, 2 * width + 1))
    k[:width + 1] = 0
    return k

def augment_feature(feature, k):
    return np.stack(
        [
            common.convolve_left(feature, k),
            common.convolve_left(feature, np.flip(k)),
        ], axis=1)

def process(
        raw_data,
        audio_scale=DEFAULT_AUDIO_SCALE,
        video_scale=DEFAULT_VIDEO_SCALE,
        kernel_width=DEFAULT_KERNEL_WIDTH):
    t = raw_data[:, 0]
    audio = raw_data[:, 1] / audio_scale
    video = raw_data[:, 2] / video_scale

    k = get_kernel(kernel_width)
    output = [
        t[:, np.newaxis],
        audio[:, np.newaxis],
        augment_feature(audio, k),
        video[:, np.newaxis],
        augment_feature(video, k),
    ]
    if raw_data.shape[1] == 4:
        output.append(raw_data[:, 3][:, np.newaxis])
    return np.hstack(output)

def main():
    args = parser.parse_args()
    raw_data = np.loadtxt(args.input, delimiter=',')
    processed_data = process(raw_data, args.audio_scale, args.video_scale, args.kernel_width)
    np.savetxt(args.output, processed_data, delimiter=',', fmt='%.18g')

if __name__ == '__main__':
    main()