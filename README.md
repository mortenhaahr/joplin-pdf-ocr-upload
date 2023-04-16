# Overview
Finds a Joplin notebook page. Converts a PDF to images. Runs optical-character recognition on the images and adds it as alternative text. Adds the images to the page in Joplin and saves.
<br>
Result: Searchable printout of a PDF added to the page.

# How to use it?
- Install Tesseract on your system.
  - (Guide with Ubuntu: https://techviewleo.com/how-to-install-tesseract-ocr-on-ubuntu/)
- Make sure you have installed the Python requirements as found in `requirements.txt`.
    - It is recommended to use a virtual environment but not necessary.
- Make sure Joplin Web Clipper is enabled and started in the client.
    - Go to Tools -> Options -> Web Clipper and enable it.
- Export your API key to the environment variable `JOPLIN_API_TOKEN`
  - Alternative: Provide it through CLI with `--api-token`
- Run `./noteUpload.py --notebooks "parent" "child" --note-name "title" --pdf "/path/to/pdf"`
    - Concrete example: `./noteUpload.py --notebooks "Embedded Real Time Systems" "Week 2" --note-name "SystemC" --pdf L4_SystemC_part3.pdf`
        - Assumes notebook structure: Embedded Real-Time Systems -> Week 2 -> SystemC. Copies printout of "L4_SystemC_part3.pdf" to it.

# Known issues:
Currently, the script does not support:
- Changing server URL/port. Always assumes localhost:41184
- Create the note structure if it doesn't exist.