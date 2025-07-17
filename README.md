# HELLO
Welcome to our initiative tracker. Lots of updates coming soon

### Directory
- '/admin' - takes you to admin panel page to edit the initiative list and such
- '/player' - players can waffle about on this page so they know when they'll need to act

### CSV DESIGN
```
    name,initiative,status
    Grod,1,alive
    Boblin,25,alive
    Murder Hobo,2,dead
```

### TODO

- [`x`] automatically update page at every global change
- [`x`] make 'vertical view' so we can place a tablet upright and everyone can see in large letters/nums
- [`x`] make a round counter to keep track of rounds
- [`x`] add a note-tracker to keep track of debuffs and such
- [`x`] create a system to accept initiative from a .csv
- [`x`] fix error when there is not initiative\_data.json starting file
- [`x`] add pytest for csv imports
- [] fix up UI (it's hideous)
- [`x`] allow for csv exports
- [] include timestamp in export filename **i can do this on my OWN**


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
