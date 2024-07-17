import subprocess
import pytesseract
import cv2
from docx2pdf import convert
from PIL import Image
from pillow_heif import register_heif_opener
from moviepy.editor import VideoFileClip

# allow for the reading of HEIC images
register_heif_opener()

def make_output_filename(in_path, otype):
    return in_path.rsplit('.', 1)[0] + '.' + otype

def convert_mov_to_mp4(mov_path):
    mp4_path = make_output_filename(mov_path, 'mp4')
    subprocess.run(['ffmpeg', '-i', mov_path, mp4_path])
    return mp4_path

def convert_mov_to_gif(mov_path):
    gif_path = make_output_filename(mov_path, 'gif')
    # use some function to convert mov to gif
    clip = VideoFileClip(mov_path, target_resolution=(360, 480))
    clip.write_gif(gif_path, fps=10)
    return gif_path

def convert_mp4_to_gif(mp4_path):
    gif_path = make_output_filename(mp4_path, 'gif')
    # use some function to convert mp4 to gif
    clip = VideoFileClip(mp4_path, target_resolution=(360, 480))
    clip.write_gif(gif_path, fps=10)
    return gif_path

def convert_mov_to_mp4_with_thumbnail(mov_path):
    mp4_path = convert_mov_to_mp4(mov_path)
    jpg_path = make_output_filename(mov_path, 'jpg')
    # load the video
    cap = cv2.VideoCapture(mp4_path)
    # check if the video loaded successfully
    if cap.isOpened():
        # read the first frame
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # convert the frame to a PIL Image
            img = Image.fromarray(frame)
            # save the image as a jpg
            img.save(jpg_path)
        else:
            print('Unable to read frame from video.')
    else:
        print('Unable to open video.')
    return mp4_path

def doc_to_pdf(doc_path):
    pdf_path = make_output_filename(doc_path, 'pdf')
    convert(doc_path, pdf_path)
    return pdf_path

def jpg_to_pdf(input_path):
    # specify output path
    output_path = make_output_filename(input_path, 'pdf')
    # Open the image file
    with Image.open(input_path) as img:
        # Convert and save as PDF
        img.save(output_path, "PDF", resolution=100.0, quality=95)
    return output_path

def jpg_to_txt(input_path):
    # specify output path
    output_path = make_output_filename(input_path, 'txt')
    # open the image file
    with Image.open(input_path) as img:
        text = pytesseract.image_to_string(img)
    # write the text file
    with open(output_path, 'w') as f:
        f.write(text)
    return output_path

def step_to_stl(input_path):
    # specify the output path
    output_path = make_output_filename(input_path, 'stl')
    # open the step file

    # convert the step to stl

    return output_path

def heic_to_jpg(input_path):
    # specify the output path
    output_path = make_output_filename(input_path, 'jpeg')

    # open the image
    img = Image.open(input_path)

    img.save(output_path, 'jpeg', resolution=100.0, quality=95)

    return output_path

