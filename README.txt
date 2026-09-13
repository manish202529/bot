CLIPCHAMP ACTIVITY BOT — STANDALONE WINDOWS BUILD

WHAT THIS IS
A small Windows GUI automation tool designed around the Clipchamp layout in
the supplied 1920x1080 screenshot. It moves the cursor, opens selected
Clipchamp editing tools, and performs conservative test clicks in a panel.

IMPORTANT
- It is intentionally NOT a whole-screen random clicker.
- It avoids the Export and Share controls and the timeline.
- It can still change your Clipchamp project because filter/effect controls
  may be real editing controls. Test on a copy of your project first.
- PyAutoGUI emergency stop: move the mouse to the top-left corner.

HOTKEYS
F8 = Start
F9 = Stop

NO PYTHON INSTALLATION FOR THE FINAL EXE
The GitHub Actions workflow builds a standalone Windows EXE with Python and
all required packages bundled into the EXE. Your Windows computer does not
need Python to run the finished EXE.

HOW TO BUILD THE EXE WITHOUT INSTALLING PYTHON
1. Create a new GitHub repository in your browser.
2. Upload ALL files from this folder to the repository:
     clipchamp_bot.py
     requirements.txt
     .github/workflows/build-windows.yml
3. Open the repository's "Actions" tab.
4. Select "Build Windows EXE".
5. Click "Run workflow".
6. Wait for the green check to finish.
7. Open the completed workflow run.
8. Under "Artifacts", download:
     ClipchampActivityBot-Windows
9. Extract it. The folder contains:
     ClipchampActivityBot.exe

The build uses Windows runners, so the resulting EXE is a real Windows
executable and does not require Python.

USAGE
1. Maximize Clipchamp.
2. Open your project and video.
3. Start playback if desired.
4. Run ClipchampActivityBot.exe.
5. Select the activities you want.
6. Press START or F8.
7. Press STOP or F9 to stop.

The current program does not automatically determine that a video has ended.
It runs until you stop it. This is deliberate in this first standalone build
because reliable end-of-playback detection should be calibrated to the exact
Clipchamp version and UI. Do not leave it unattended until you have tested it.
