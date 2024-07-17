import click
import os
import subprocess
import pyperclip
import sys; sys.path.append('./')
from ez_convert.utils import *

# add a command for the user defined output file type (--otype)
@click.command()
@click.option('--otype', help='Output file type')

def main(otype):
    # Get path from clipboard
    in_path = pyperclip.paste().strip()

    if not os.path.exists(in_path):
        click.echo("Invalid file path from clipboard. Please copy a valid file path to convert.")
        return
    
    # Get file extension
    ext = in_path.rsplit('.', 1)[-1]

    if ext == 'mov':
        if otype == 'mp4':
            out_path = convert_mov_to_mp4(in_path)
        elif otype == 'mp4jpg':
            out_path = convert_mov_to_mp4_with_thumbnail(in_path)
        elif otype == 'gif':
            out_path = convert_mov_to_gif(in_path)
    elif ext == 'mp4':
        if otype == 'gif':
            out_path = convert_mp4_to_gif(in_path)
    elif ext.lower() == 'jpg' or ext.lower() == 'jpeg':
        if otype == "pdf":
            out_path = jpg_to_pdf(in_path)
        elif otype == "txt":
            out_path = jpg_to_txt(in_path)
        else:
            raise NotImplementedError(f"Conversion from {ext} to {otype} is not yet supported.")
    elif ext == 'doc' or ext == 'docx':
        if otype == "pdf":
            out_path = doc_to_pdf(in_path)
    elif ext == 'step':
        if otype == "stl":
            out_path = step_to_stl(in_path)
    elif ext == 'heic' or ext == 'HEIC':
        if otype == "jpg":
            out_path = heic_to_jpg(in_path)
    else:
        # raise a Not Implemented Error
        raise NotImplementedError(f"Conversion from {ext} to {otype} is not yet supported.")
    
    click.echo(f"Converted {in_path} to {out_path} !")

if __name__ == "__main__":
    main()