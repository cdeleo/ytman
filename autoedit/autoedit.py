import extract_features
import process_features
import evaluate_model
import write_clips

import argparse
import numpy as np
import pickle

parser = argparse.ArgumentParser(description='Extract editing features from a video.')
parser.add_argument('video', type=str, help='Path to the input video.')
parser.add_argument('model', type=str, help='Model for feature evaluation.')
parser.add_argument('output', type=str, help='Path for the output clip list.')
args = parser.parse_args()

def main():
    raw_data = np.array(list(extract_features.extract(args.video)))
    processed_data = process_features.process(raw_data)
    t = processed_data[:, 0]
    X = processed_data[:, 1:]

    with open(args.model, 'rb') as model_file:
        model = pickle.load(model_file)
    y = evaluate_model.evaluate(X, model)

    doc = write_clips.create_document(t, y, args.video)
    with open(args.output, 'wb') as output_file:
        doc.write(output_file)

if __name__ == '__main__':
    main()