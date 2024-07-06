<p align="center">
  <img src="assets/banner.png" alt="StringSculpt Banner" width="400"/>
</p>

<p align="center">
  
</p>

<p align="center">
    <i>StringSculpt is a minimalistic Windows application that allows you to quickly format and replace selected text, or generate new text using a simple keyboard shortcut.</i>
</p>


</br>

## Demos:

You can find demos on StringSculpt's project page!

**https://dotjust.in/projects/stringsculpt**


</br>

# How it works:
1. When the keyboard shortcut `Ctrl + Shift + F` is recognized, it calls our CustomTkinter UI.
   - If there is text selected, it enters "sculpt mode", where it will edit your selected text
   - if there is *no* text selected, it enters "generative mode", where it generates any text you want based on the prompt.
2. Once the text to be edited (if any), as well as the user prompt get sent to an LLM api. I personally recommend [groq](https://console.groq.com), as it's super fast, and free.
3. Your old text is replaced by your sculpted text!

</br>

# Quick start guide:

Make sure [python](https://python.org/downloads) and [git](https://git-scm.org/downloads) are installed. 

Navigate to the directory you want to install StringScript, and run:

```
git clone https://github.com/dot-justin/stringsculpt
cd StringSculpt
pip install -r requirements.txt
```
Now, you need to add your api key in the *.env*. I have provided a `.env.example`, so you can edit it and remove the .example file extension, so you're only left with `.env`. This is where the program will pull your api key from, and you need to edit this before you can use the program.

Contents of .env:
```
API_KEY=GROQ_API_KEY_HERE
BASE_URL=https://api.groq.com/openai/v1/chat/completions
```

Once that's finished, StringSculpt is installed and ready to go! To run the application, run:

`python main.py`

You won't see anything happen, so go select some text and commit the shortcut `Ctrl + Shift + F` to memory :)

</br>


## Current Bugs:
These are all of the bugs I'm aware of. If you stumble across another one, I would be very greatful if you could open an issue! I am currently working on fixes for all of these, so keep an eye on the commit history.

- When rapid-fire selecting and formatting, some may get missed, causing the LLM to respond similar to this: `Nothing to fix here!`
   - When this happens, unfortunately you need to select your text and reprompt.
- When doing the shortcut to active StringSculpt, if you don't let go of all of the keys in time, it won't be able to capture your selected text, and as a result, fail to format it.
- Sometimes when asking it to summarize or fix, etc. it will give a preamble like `Here is the summarized/fixed text`. This is a prompting issue, and I'm playing with the prompt as well as the temperature to minimize this.

</br>

# Quick Actions

### What are Quick Actions?
Quick actions are a quick and easy way to get StringSculpt to do specific things to your text.

For example, if you wanted a summary of the selected text, you could just input `summarize` and it will do so. You can also combine Quick Actions, for example: `remove exclamation points and rewrite as shakespeare`

### Editing:
| **Quick Action** | **Description** |
| --- | --- |
| `fix` | Proofreads, fixes grammar and spelling, and rewrites selected text, keeping language the same |
| `rewrite` | Rewrites your text in a similar style as your own writing, or, if specified, someone else's writing |
| `replace` / `remove` | Searches and replaces or removes text in selected text |
| `finish` / `complete` | Finishes selected sentence or paragraph

### Summarization:
| **Quick Action** | **Description** |
| --- | --- |
| `summarize` | Gives an overarching summary of selected text |
| `action items` | Finds action items and outputs in bullet point format |
| `key points` | Finds key points and lists them |
| `notes` | Makes notes on the selected text |

</br>

# Customization:

- Hotkey: The default hotkey is `Ctrl + Shift + F`. You can change this by modifying the `hk.register` call in the script.
- LLM Temperature: Adjust the creativity of the AI by changing the LLM_TEMPERATURE variable on line `18` of `main.py`.
