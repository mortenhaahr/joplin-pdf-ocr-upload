#!/usr/bin/env python3
import sys

API_TOKEN = 'ca43312f9a55d98fdc9559a8b8b6cd7b72862528a87fa874ff57d78cdfeec13d7bc465a31f2dcf09d7877e9292d00e233a39230aa6a84571334f82d4d4a03608'

from joplinPdf2Images import joplinPdf2Images
from joplinFindNote import joplinFindNote
from joplinOcrImages import joplinOcrImages

if __name__ == "__main__":
    # Get parent folder:
    argv = sys.argv.copy() # Copy because we want to manipulate
    script_name = argv[0]
    argv.pop(0)
    if(len(argv) < 2 or argv[-1][-4:] != ".pdf"):
        raise SystemExit(f"Usage: {script_name} [parent-notebooks] <note-name> <pdf-path>")
    note_parents = argv[:-2]
    note_name = argv[-2]
    pdf_path = argv[-1]
    
    notebook_page_id = joplinFindNote(note_name, note_parents, API_TOKEN)
    joplinPdf2Images(pdf_path, notebook_page_id, API_TOKEN)
    joplinOcrImages(notebook_page_id, API_TOKEN)