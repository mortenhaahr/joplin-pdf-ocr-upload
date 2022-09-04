#!/usr/bin/env python3
from pdf2image import convert_from_path
import os
import requests
import json
import shutil

MIME = 'multipart/form-data'

def joplinPdf2Images(pdf_path : str, notebook_page_id : str, API_TOKEN : str):
    """Takes a PDF and converts the pages to images. Uploads it to a Joplin notebook."""

    cwd = os.path.abspath(os.getcwd())
    output_dir = cwd + "/output"
    try:
        os.mkdir(output_dir)
    except FileExistsError:
        shutil.rmtree(output_dir)
        os.mkdir(output_dir)

    pages = convert_from_path(pdf_path=pdf_path, size=(1000, None))
    
    # Get the current body for appending:
    params = {"token": API_TOKEN}
    try:
        response = requests.get(
            f'http://localhost:41184/notes/{notebook_page_id}?fields=id,body', params=params)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(f"Couldn't retrieve page body. Received error:\n{err}")

    body = response.json()

    # Upload resources and update body
    page_body = body['body'] + "\n"
    for i, page in enumerate(pages):
        filename = f'image{i}.jpg'
        image_path = f'{output_dir}/{filename}'
        page.save(image_path, 'JPEG')
        file = {'data': (image_path, open(image_path, 'rb'), MIME)}
        try:
            response = requests.post('http://localhost:41184/resources', params=params, files=file,
                                     data={'props': json.dumps({'title': "",
                                                                'filename': f"{filename}"})})
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            raise SystemExit(f"Failed to upload image: {i}. Exiting. Got error:\n{err}")
        body = response.json()
        page_body += f"![{filename}](:/{body['id']})\n\n\n"
    print("Done uploading images. Putting in note now")

    try:
        response = requests.put(f'http://localhost:41184/notes/{notebook_page_id}', params=params, data=json.dumps({'body': page_body}))
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(f"Failed edit notebook page. Exiting. Got error:\n{err}")