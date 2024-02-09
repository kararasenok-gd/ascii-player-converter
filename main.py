import os
import cv2
import json
from moviepy.editor import *
from PIL import Image
from tqdm import tqdm

ASCII_CHARS = "@B%8WM#*oahkbdpwmZO0QCJYXzcvnxrjft/\|()1{}[]-_+~<>i!lI;:,\^`'. "

def scale_image(image, new_width=100):
    (original_width, original_height) = image.size
    aspect_ratio = original_height / float(original_width)
    new_height = int(aspect_ratio * new_width)
    new_image = image.resize((new_width, new_height))
    return new_image

def convert_to_grayscale(image):
    return image.convert("L")

def map_pixels_to_ascii(image, range_width=25):
    pixels = image.getdata()
    ascii_str = ""
    for pixel_value in pixels:
        ascii_str += ASCII_CHARS[pixel_value // range_width]
    return ascii_str

def convert_image_to_ascii(image, new_width=100):
    image = scale_image(image, new_width)
    image = convert_to_grayscale(image)
    ascii_str = map_pixels_to_ascii(image)
    return ascii_str

def save_ascii_to_txt(ascii_str, txt_path):
    with open(txt_path, "w") as f:
        f.write(ascii_str)

def split_video_into_frames(video_path):
    video_file_name = os.path.splitext(os.path.basename(video_path))[0]
    output_folder = f"{video_file_name}_frames"
    os.makedirs(output_folder, exist_ok=True)

    video_capture = cv2.VideoCapture(video_path)
    total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

    with tqdm(total=total_frames, desc='Splitting frames') as pbar:
        frame_count = 0
        while True:
            ret, frame = video_capture.read()
            if not ret:
                break

            frame_path = os.path.join(output_folder, f"{frame_count:05d}.png")
            cv2.imwrite(frame_path, frame)
            frame_count += 1

            pbar.update(1)

    video_capture.release()
    return output_folder

def main(video_path, new_width=100, fps = 24, custom_name = "video"):
    frames_folder = split_video_into_frames(video_path)

    frames = []
    frame_files = sorted([filename for filename in os.listdir(frames_folder) if filename.endswith(".png")])
    with tqdm(total=len(frame_files), desc='Processing frames') as pbar:
        for filename in frame_files:
            frame_index = int(filename.split("_")[-1].split(".")[0])
            try:
                image = Image.open(os.path.join(frames_folder, filename))
            except Exception as e:
                print(e)
                continue

            ascii_str = convert_image_to_ascii(image, new_width)
            img_height = int(len(ascii_str) / new_width)
            ascii_str = "\n".join([ascii_str[i:i + new_width] for i in range(0, len(ascii_str), new_width)])
            frames.append({"frame": frame_index, "content": ascii_str})

            pbar.update(1)

    output_json = {"fps": fps, "frames": frames}  # Укажите правильное значение FPS
    with open(f'{custom_name}.json', 'w') as f:
        json.dump(output_json, f, indent=2)

    convert_to_mp3(video_path, f'{custom_name}.mp3')

def convert_to_mp3(mp4_file, mp3_file):
    video = VideoFileClip(mp4_file)
    audio = video.audio
    audio.write_audiofile(mp3_file)

if __name__ == "__main__":
    video_path = input("Path to .mp4 file: ")
    custom_name = input("Name files: ")
    fps = input("FPS: ")
    main(video_path, fps=fps, custom_name=custom_name)
