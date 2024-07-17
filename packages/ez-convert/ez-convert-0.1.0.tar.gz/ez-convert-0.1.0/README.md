# ez-cli-convert
An open-source repository based in Python for easily converting files from one form to another using the command-line interface (CLI).

## Installation

```bash
pip install ez-convert
```

## Usage

1. Copy the path of the file you wish to convert to your clipboard. (on MacOS, `option` + right-click --> `Copy ... as pathname`; on Windows, `Shift` + right-click --> `Copy as Path`)
2. Open the terminal and simply run 

```bash
ezconvert --otype {your desired output file type}
```

The script will produce a file of the desired type (*i.e.* `pdf`, `jpg`, `mp4`, `mov`, etc.) in the location of the copied file as well as the same file name. Currently, functionalities will be added as they become needed.

## Dependencies

- This tool uses `ffmpeg` under the hood for video file conversion, so you will need to have that installed on your system
- The clipboard functionality is provided by `pyperclip`
- Conversion from images to pdf and vice versa is accomplished using the `Pillow` module