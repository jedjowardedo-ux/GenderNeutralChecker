GENDER NEUTRAL LANGUAGE CHECKER

DESCRIPTION
Opens a .txt file, detects 16 predefined gender-specific words/phrases using
regular expressions, and shows each detected term, its number of occurrences,
and a suggested gender-neutral alternative. Matching ignores capitalization and
matches whole words only. Detected terms are also highlighted in a preview of
the document. The file is never modified; suggestions are for review.

REQUIREMENTS
- Python 3 with Tkinter (included in the standard Windows installer).
- No third-party packages.
- Input must be a .txt file saved as UTF-8.

FILES
gender_neutral_checker.py   Source code (VS code)
sample.txt                  Sample input for the demo
README.txt                  Setup and running instructions
test_files/                 Files used for the testing section of the document

HOW TO RUN (VISUAL STUDIO CODE)
1. Extract the ZIP file.
2. Open Visual Studio Code, choose File > Open Folder, and select the
   GenderNeutralChecker folder that contains gender_neutral_checker.py.
3. Click gender_neutral_checker.py in the file list to open it.
4. Click the Run button (triangle at the top right) or press Ctrl+F5.
   (Run > Start Debugging, F5, also works.)
5. In the window that opens, click "Upload .txt file" and select sample.txt.
   If the window does not appear, check the taskbar; it may be behind VS Code.
6. Review the table and the highlighted preview.
7. Close the window (or click the red stop square in VS Code) when finished.

TEST FILES (in the test_files folder)
test2_repeated_caps.txt     Same terms repeated with different capitalization
test3_no_terms.txt          No listed terms (includes "the" and "then")
test4_empty.txt             Empty file
test5_unsupported.docx      Unsupported file format