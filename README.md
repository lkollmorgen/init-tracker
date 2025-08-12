# HELLO
Welcome to our initiative tracker. Lots of updates coming soon

### Directory
- '/admin' - takes you to admin panel page to edit the initiative list and such
- '/player' - players can waffle about on this page so they know when they'll need to act
-'/landing' - visitors can start a new session or join another session

### USAGE
- You can create a new session (as a DM) or you can join a DM's session using their join code
- A DM's session will timeout after 30m of no changes
- You can add players to initiative, kill them, delete theme, and export the session to a csv


### CSV DESIGN (if importing or exporting)
```
    name,initiative,status
    Grod,1,alive
    Boblin,25,alive
    Murder Hobo,2,dead
```

### TODO
version 0.0
- [`x`] automatically update page at every global change
- [`x`] make 'vertical view' so we can place a tablet upright and everyone can see in large letters/nums
- [`x`] make a round counter to keep track of rounds
- [`x`] add a note-tracker to keep track of debuffs and such
- [`x`] create a system to accept initiative from a .csv
- [`x`] fix error when there is not initiative\_data.json starting file
- [`x`] add pytest for csv imports
- [`x`] fix up UI (it's hideous)
- [`x`] allow for csv exports
- [`x`] include timestamp in export filename **i can do this on my OWN**
version 1.0
- [`x`] fix CONSTANT refreshing on player view page
- [`x`] button to go to admin page from player page
- [`x`] create a join code like in jackbox so people can host united sessions
- [`x`] fix player_view methods=post thing
- [] run some stress tests to see how many games can function at once
- [`x`] add my github *cringes*
- [] fix the 'alive' button
- [`x`] add player 'timeout' page
- [] give DM a warning when their session is going to expire
- [] fix UI so buttons are horizontally placed on ADMIN page

#### Neat tricks:
```
cat file_to_copy.txt | clip.exe
```
- this copies the contents of this file to the clipboad

```
python -m tabnanny app.py
```
- this checks if your tabs are funkin

```
grep -rnw . -e "word to find"
```
gets you the lines in recursive search in current directory

```
grep -rl "word to find" .
```
gets you the file names only where this pattern shows up
