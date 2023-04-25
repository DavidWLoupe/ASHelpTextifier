# AsHelpTextifier
Processes B&R Help files and generates a folder structure of text files, mimicking the Table of Contents tree, that can be opened and searched (e.g. with VSCode)


# Using the Textifier to Generate code

NOTE: Running took about 2 hours on my Parallels Windows OS. Feel free to give it a whirl, but don't expect it to be snappy.

## Setup

- Install python, if you do not yet have it. 
- Install the modules with `pip install -r requirements.txt`
    - Tip: Use virtual environments if you don't want to install the modules on your machine


## Running Textifier
- Configure script options
    - Set Settings at the top of ASHelpTextifier.py and save
- `cd` to Repository root
- Run `python .\ASHelpTextify.py`
- When prompted, browse to the folder containing `brhelpcontent.xml`
    - e.g. `C:\BrAutomation\AS411\Help-en\Data\`
- Wait...
- When done, the textified file will be in newly created folder `./out/ASHelpTestYYMMDDHHMM/`
