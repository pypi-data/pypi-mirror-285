import os
from vid_extract import extract_video

class VideoConverter:
    def __init__(self, video_folder_prefix):
        self.video_folder_prefix = video_folder_prefix

    def video_extract(self, video_file):
        """Extracts images from a single video file."""
        extract_video(os.getcwd(), video_file)

    def video_extract_folder(self):
        """Extracts images from all videos in the specified folder."""
        vids = os.listdir(self.video_folder_prefix)
        print("Video files found:", vids)
        for vid in vids:
            if vid.split('.')[-1] in ['mp4', '360', 'MP4']:
                video_path = os.path.join(os.getcwd(), self.video_folder_prefix, vid)
                print("Processing video:", video_path)
                self.video_extract(video_path)

# Example usage
if __name__ == "__main__":
    video_folder = "campus_video_test"  # Specify the folder where your video files are stored
    converter = VideoConverter(video_folder)
    converter.video_extract_folder()
