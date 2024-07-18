import os
from gpmf_support import extract_metadata
from moviepy.editor import VideoFileClip
import datetime
import numpy as np
import sys


def get_metadata_for_frame(new_indices,metadata_list,frame_index):
    metadata_index = new_indices[frame_index]
    return metadata_list[metadata_index]

def extract_video(cur_folder,video_file):
    print('video file ',video_file)
    print('cur folder ',cur_folder)
    timestamp_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = None
    SAVING_FRAMES_PER_SECOND= 0
    video_clip = VideoFileClip(video_file)

    print("fps: ", video_clip.fps)
    number_of_frames = int(video_clip.fps * video_clip.duration)

    print("Number of frames:", number_of_frames)
    print(video_file)
    if filename is None:
        filename = video_file.split('\\')[-1]
        filename += "-moviepy"
        filename += "-" + timestamp_str
    output_dir = filename
    if not os.path.isdir(filename):
        os.mkdir(filename)
    frames_after_number_of_seconds = 1
    saving_frames_per_second = min(video_clip.fps, SAVING_FRAMES_PER_SECOND)
    step = 1 / video_clip.fps if saving_frames_per_second == 0 else 1 / saving_frames_per_second
    metadata_list = extract_metadata(video_file, output_dir)
    count = 0
    num_frames = int(np.ceil(video_clip.duration / step))

    old_indices = np.linspace(0, len(metadata_list) - 1, num=num_frames, endpoint=True)
    new_indices = np.round(old_indices).astype(int)  # Round indices to nearest integer
    for current_duration in np.arange(0, video_clip.duration, step):
        frame_name = get_metadata_for_frame(new_indices,metadata_list,count)
        frame_filename = os.path.join(filename, f"frame_{frame_name}.jpg")
        video_clip.save_frame(frame_filename, current_duration)
        count += 1
