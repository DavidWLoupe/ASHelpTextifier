# AsHelpTextifier
Processes B&R Help files and generates a folder structure of text files, mimicking the Table of Contents tree, that can be opened and searched (e.g. with VSCode)


## Using the Textifier

NOTE: Running took about 16 hours to process AS4.12 Help on my Parallels Windows OS with all options activated. It will be a little faster with the default options. Feel free to give it a whirl, but don't expect it to be snappy.

### Setup

- Install python, if you do not yet have it. 
- Install the modules with `pip install -r requirements.txt`
    - Tip: Use virtual environments if you don't want to install the modules on your machine


### Running Textifier
- Configure script options
    - Set Settings at the top of ASHelpTextifier.py and save
- `cd` to Repository root
- Run `python .\ASHelpTextify.py`
- When prompted, browse to the folder containing `brhelpcontent.xml`
    - e.g. `C:\BrAutomation\AS411\Help-en\Data\`
- Wait...
- When done, the textified files will be in newly created folder `./out/ASHelpTestYYMMDDHHMM/`


## Downloading pre-generated output
- Links to Pre-generated textifications of AS Help can be found in the GitHub release assets