#!/usr/bin/env python3
import sys
import argparse
import os

from joplinPdf2Images import joplinPdf2Images
from joplinFindNote import joplinFindNote
from joplinOcrImages import joplinOcrImages

if __name__ == "__main__":
    use_id_provided = '--use-id' in sys.argv

    parser = argparse.ArgumentParser(description='Example command line options')
    parser.add_argument('--use-id', default=False, action='store_true', help='Specify the note ID. Default=False')

    parser.add_argument('--notebooks', nargs='+', required=not use_id_provided, help="The notebook structure. Can be nested.")
    parser.add_argument('--note-name', required=not use_id_provided, type=str, help="Name of the note")
    parser.add_argument('--pdf', required=True, type=str, help="Path of the PDF")
    parser.add_argument('--note-id', required=use_id_provided in sys.argv, type=str, help="ID of the PDF")
    parser.add_argument('--api-token', type=str, help="Joplin Web Clipper API Token. Can also be provided as environment variable: `JOPLIN_API_TOKEN`")

    args = parser.parse_args()

    if args.use_id and args.note_name:
        raise argparse.ArgumentTypeError("Specifying --note-name not allowed with --use-id")
    elif (not args.use_id) and args.note_id:
        raise argparse.ArgumentTypeError("Specifying --note-id not allowed without --use-id")

    if args.pdf[-4:] != ".pdf":
        raise argparse.ArgumentTypeError("--pdf must be a PDF file")
    pdf_path = args.pdf
    
    if args.api_token:
        api_token = args.api_token
    else:
        api_token = os.environ.get('JOPLIN_API_TOKEN')
    
    if not api_token:
        raise argparse.ArgumentTypeError("Must provide api token either through CLI or environment variable")
    
    if not use_id_provided:
        note_id = joplinFindNote(args.note_name, args.notebooks, api_token)
    else:
        note_id = args.note_id

    joplinPdf2Images(pdf_path, note_id, api_token)
    joplinOcrImages(note_id, api_token)