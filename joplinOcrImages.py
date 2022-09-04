#!/usr/bin/env python3
import requests
import re
from PIL import Image
import pytesseract
import io
import json

def joplinOcrImages(notebook_page_id : str, API_TOKEN : str):
    """Runs OCR on existing images in a Joplin page"""
    # Get page body:
    params = {"token": API_TOKEN}
    try:
        response = requests.get(
            f'http://localhost:41184/notes/{notebook_page_id}?fields=id,body', params=params)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        print("Couldn't retrieve page body")
        raise SystemExit(err)
    body = response.json()
    page_body = body['body']

    # Regex stolen from https://regex101.com/r/u2DwY2/2/ , but modified for grp 2 to also match on "".
    md_file_re = r'!\[[^\]]*\]\((.*?)\s*("(?:.*)")?\s*\)'
    file_matches = re.findall(md_file_re, page_body)
    # Return all the files where there is no alternative text and that are native Joplin resources
    file_ids = [file_match[0] for file_match in file_matches if not file_match[1] and file_match[0].startswith(":/")]
    file_ids = [file[2:] for file in file_ids] # Remove ":/"
    image_ids = []

    # Check that the files are images and exist in the db. (Perhaps unnecessary)
    for file_id in file_ids:
        try:
            response = requests.get(
                f'http://localhost:41184/resources/{file_id}?fields=id,file_extension', params=params)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(f"Failed to retrieve for resource {file_id}. Continuing.")
        body = response.json()
        if not (body['file_extension'].lower() == 'png' or body['file_extension'].lower() == 'jpg'):
            print(f"Skipping {file_id} as it is not a .png or .jpg file.")
            continue        
        image_ids.append({'id': file_id, 'alt_text': ""})

    # Do OCR on the images
    for image_id in image_ids:
        try:
            response = requests.get(
                f"http://localhost:41184/resources/{image_id['id']}/file", params=params)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(f"Failed to retrieve for resource {file_id}. Continuing.")

        image = Image.open(io.BytesIO(response.content))
        #image.show()
        image_text = pytesseract.image_to_string(image)
        # Replace what is not allowed - in the most inefficient manner...
        image_text = image_text.replace("\n", " ")
        image_text_chars = []
        for char in image_text:
            if char.isalnum():
                image_text_chars.append(char)
            else:
                image_text_chars.append(" ") # Append a space seems to be the best for searching
        image_text = "".join(image_text_chars)
        image_id['alt_text'] = image_text

    # Make new page body
    new_page_body = page_body
    for image_id in image_ids:
        new_page_body = new_page_body.replace(image_id['id'], f'{image_id["id"]} "{image_id["alt_text"]}"')
    
    # Upload new page body
    try:
        response = requests.put(f'http://localhost:41184/notes/{notebook_page_id}', params=params, data=json.dumps({'body': new_page_body}))
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(f"Failed edit notebook page. Exiting. Got error:\n{err}")