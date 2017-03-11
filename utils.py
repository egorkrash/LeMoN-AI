import c3d
import numpy as np
import subprocess
import os
import librosa
import matplotlib.pyplot as plt
from scipy.io import wavfile

def positions_to_moves(positions):
    moves = np.array([np.subtract(positions[i+1, :, :3], positions[i, :, :3]) for i in range(len(positions)-1)])
    return moves

def get_sound_from_vid(vid_path, save_dir="audio/"):
    name = vid_path.split("/")[-1].split(".")[0]
    command = "ffmpeg -i {0} -ab 160k -ac 2 -ar 44100 -vn {1}".format(vid_path, save_dir+name+".wav")
    subprocess.call(command, shell=True)
    return save_dir+name+".wav"

def get_sound_from_wav(wav_path, split_second=60, sr=44100):
    rec, sr = librosa.load(wav_path, sr=sr)
    pows_in_split = int(sr/split_second)
    pieces = np.array([rec[i:i+pows_in_split] for i in range(0, len(rec)-pows_in_split, pows_in_split)])
    return pieces

def all_videos_to_sound(vid_dir="videos/"):
    for file in os.listdir(vid_dir):
        get_sound_from_vid(vid_dir+file, "audio/")

### Dont use yet
def get_data(npy_path):
    data_matr = np.load(npy_path)
    return np.array([np.array([y[0] for y in x]) for x in data_matr]),\
        np.array([np.array([y[1] for y in x]) for x in data_matr])

def iterate_mini_batches(points, music, batch_size=100, block_size=15):
    blocks_left = [int(p.shape[0]/block_size) for p in points]
    moves = np.array([positions_to_moves(x) for x in points])
    batch_count = 0
    batch = []
    while np.any(blocks_left != 0):
        inst = np.random.choice(range(len(blocks_left)))
        start = -blocks_left[inst]*block_size
        fin = -blocks_left[inst]*block_size+block_size            

        train_moves = moves[inst][start:fin-1]
        pred_move = moves[inst][fin]

        start_pos = points[inst][start]

        batch.append(np.array([music[inst][start:fin], train_moves, start_pos, pred_move]))
        blocks_left[inst] -= 1

        batch_count += 1

        if batch_count == 100:
            yield np.array(batch)
            batch = []
            batch_count = 0