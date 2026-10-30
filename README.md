# Certificate Renamer — Version 1

A beginner-friendly Streamlit application that renames numbered certificate images using a pasted list of names.

## What it does
- Accepts a ZIP of certificate images, or multiple images selected from an extracted folder.
- Matches `1.jpg`, `2.png`, etc. to names in the same order.
- Checks for missing/extra numbers and duplicate output filenames.
- Preserves each image's extension.
- Creates a new ZIP for download without modifying the originals.

## Requirements
- Python 3.10 or newer
- Internet access for the first installation of Streamlit

## Run on Windows
1. Extract this project folder.
2. Open Command Prompt in the extracted `certificate_renamer_v1` folder.
3. Create a virtual environment (recommended):

   ```bat
   py -m venv .venv
   .venv\Scripts\activate
   ```

4. Install dependencies:

   ```bat
   python -m pip install -r requirements.txt
   ```

5. Start the app:

   ```bat
   streamlit run app.py
   ```

6. Your browser will open the local app. If it does not, use the local URL printed in Command Prompt (usually `http://localhost:8501`).

## Important first-version limitations
- The extracted-folder option uploads selected image files; the standard browser upload control cannot directly grant a web app unrestricted access to a folder path.
- ZIPs are read in memory and output is downloaded as a new ZIP.
- The app supports numbered JPG, JPEG, PNG, and WEBP images.
- The app does not upload files to a remote server by itself when run locally, but files are processed by the local Streamlit process.

## Running Tests
Run the automated test suite at any time from your project folder:

```bat
python tests/test_renamer.py
python tests/test_end_to_end.py
```

## Next steps
1. Test with a small ZIP containing `1.jpg`, `2.png`, etc.
2. Add CSV/Excel name import and duplicate-name handling options.
3. Package a desktop version with native folder selection if desired.
