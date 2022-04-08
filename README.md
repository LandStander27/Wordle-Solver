# Wordle-Solver
Solves wordle using selenium

Only tested on Python 3.10 and Windows 10/11

Install directions:
---
1. Download code as a zip and extract it to anywhere
2. Download a build of chromium (here: https://download-chromium.appspot.com/) and place the chrome-win folder into the root. (Make sure it's named "chrome-win")
4. Run pip install -r requirements.txt using the requirements.txt in the root, using Python 3.10
5. Run py ./app to run

- The folder structure should look like this
```
app -> Program
chrome-win -> Chromium
chromedriver.exe
requirements.txt
```

# Commands
## Help
```
-h, --help
```
- Just shows these commands.
## Solve
```
-s, --solve
```
- Solves todays wordle.
## Wordle Archive
```
-wa ARCHIVE_NUMBER, --wordle-archive ARCHIVE_NUMBER
```
- Solves a wordle archive where ARCHIVE_NUMBER is the specific day to solve
## Show Browser
```
-sb, --show-browser
```
- Default = False
- If false then the browser will open headless
## Save Screenshot
```
-ss FILE_PATH, --save_screenshot FILE_PATH
```
- Saves a screenshot once the right answer was found
