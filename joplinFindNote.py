#!/usr/bin/env python3
from pdf2image import convert_from_path
import os
import requests
import json
import shutil
import copy

MIME = 'multipart/form-data'

def joplinFindNote(note_name : str, note_parents : list, API_TOKEN : str):
    """Finds the Joplin page ID of a specific note given a `note_name` and the `note_parents`."""

    # Test connection
    params = {"token": API_TOKEN}
    try:
        response = requests.get(
            'http://localhost:41184/ping', params=params)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(f"Error communicating with server:\n{err}")

    # Search for notes:
    try:
        response = requests.get(
            f'http://localhost:41184/search?query=title:{note_name}', params=params)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(f"Error communicating with server:\n{err}")

    body = response.json()
    candidates = [{'id': x['id'], 'parent_id': x['parent_id'], 'title': x['title']} for x in body['items']]
    candidates = list(filter(lambda cand: cand['title'] == note_name, candidates)) # Only exact matches
    candidates_copy = copy.deepcopy(candidates)
    candidate_index = 0

    # Used to search backwards to figure out if tree is correct
    parents_reversed = copy.deepcopy(note_parents) # Don't modify argument
    parents_reversed.reverse() 

    # Search for correct notebook to isolate wrong candidates
    for candidate in candidates:
        search_id = candidate["parent_id"]
        parents_reversed_len = len(parents_reversed)
        for i, parent_title in enumerate(parents_reversed):
            try:
                response = requests.get(
                    f'http://localhost:41184/folders/{search_id}', params=params)
                response.raise_for_status()
            except requests.exceptions.HTTPError as err:
                print("Couldn't ping the server")
                raise SystemExit(err)
            body = response.json()
            if body['title'] != parent_title:
                candidates_copy.pop(candidate_index)
                candidate_index -= 1
                break
            # If we are not at the final parent, but the parent_id is empty.
            # Happens when the match is good, but we expected a parent.
            elif i != parents_reversed_len - 1 and not body['parent_id']:
                candidates_copy.pop(candidate_index)
                candidate_index -= 1
                break
            else:
                search_id = body['parent_id']
        candidate_index += 1

    candidates = candidates_copy
    if len(candidates) != 1:
        raise SystemExit("Something went wrong with finding the correct note. Exiting")

    notebook_page_id = candidates[0]['id']
    return notebook_page_id