# Spelling Bee!
Script for generating Spelling Bee word lists and static HTML pages for presenters.

### Requirements
1. Python (2.7+) for generating HTML pages and word presentation lists.
2. Wordnik API Key (free). Get one [here](http://developer.wordnik.com/).

### Instructions
1. Fork and clone this repo
2. Create your word lists as text files e.g. `round1.txt` (one word per line) and save to the `words` folder
  - *IMPORTANT:* The words must be in the order you wish to present them
  - Suggested method is to create a word list for each "round"
  - An example text file is provided in `words/example_round.txt`
3. Run `python generate_words.py`
  - See output below for what this script generates
4. Navigate to `output/html/{round_name}/{filename_1_blank}.html` and open it in a browser!
  - The "blank" HMTL page shows no words and should be visible when the speller is spelling
  - The audio icon will play an .mp3 to pronounce the word (optional)
  - The green button will play a happy "ding!" to indicate the word is correct (and advance one slide to show the word to the audience)
  - The red button will play a sad "buzzzzz!" to indicate the word is incorrect (and advance one slide to show the word to the audience)
  - Next slide will be blank and the next word is queued for the next speller

### Script Output
