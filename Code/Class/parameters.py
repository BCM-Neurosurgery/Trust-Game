import random, os
from pandas import DataFrame, ExcelWriter
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox as tkm

from psychopy import prefs

# Set hardware preferences for PsychoPy
prefs.hardware['audioLib'] = ['sounddevice', 'pygame']
prefs.hardware['audioLatencyMode'] = '3'

class Parameters:
    def __init__(self):
        # Screen, text, and window configurations
        self.screen = {'number': 0, 'fullscr': True}
        self.window = {'size': [1024, 768], 'bgColor': [90,90,90], 'units': 'norm'}
        
        self.text = {'font': 'Arial', 'size': 24, 'color': [255, 255, 255]}  # Simplified font to 'Arial'
        
        # General experiment settings
        self.exp = {
            'name'     : "TrustGame",   # A name for the task to be used in filenames
            'numBlocks': 10,            # Number of blocks in the experiment
            'trialsPerBlock': 12,       # The number of trials in each block
            'language': 'English'       # The language to be used
        }

        # Experiment timing settings in seconds
        self.timing = {
            'photodiode' : 0.25,        # The duration for which we see the photodiode
            'decisionDuration': 0.5,#3,      # Decision phase duration (in seconds)
            'intervalDuration': 0.5,#12,     # Interval between decision and outcome
            'outcomeDuration': 0.5#1        # Outcome display duration
        }

        # Image and stimuli settings
        self.stimuli = {
            "imageFolder": "Images/CFD-MR",  # Generic path to the folder containing images
            'numImages': 2,
            'sliderLabels': ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
        }
        self.lottery_ratio = 0.1  # For initial downsampling in the first block
        
        # Trustworthiness weights for each CPU type
        self.trustworthy_weights = {'low': 0.2, 'high': 0.8}
        self.untrustworthy_weights = {'low': 0.8, 'high': 0.2}

        # CPU partner configuration - consistent across all blocks
        self.partners = [
            {"name": "Sam Harris", "image": "CFD-MM-312-002-N.jpg", "trustworthiness": "trustworthy", "weights": self.trustworthy_weights},
            {"name": "Jasmine Acosta", "image": "CFD-MF-302-027-N.jpg", "trustworthiness": "untrustworthy", "weights": self.untrustworthy_weights},
            {"name": "Ana Rodriguez", "image": "CFD-MF-319-016-N.jpg", "trustworthiness": "neutral", "weights": None}  # Neutral partner, no weights
        ]
        
        # Create output directory and a participant ID.
        self.outputDir=''           # Initialize the directory name
        self.ID={}                  # Initialize the ID 
        self.__launch_ID_UI()       # Launch the UI that generates the ID


    # GENERATES A LIST OF TRIAL TYPES PER BLOCK. 1ST BLOCK HAS DELAYED LOTTERY TRIALS
    def get_interleaved_trial_types(self, block_idx):
        # Generating variables for code readability
        numPartners = len(self.partners)
        trialsPerBlock = self.exp['trialsPerBlock']
        
        # Carry out first block functions separately
        if block_idx == 0:
            # Generate a list of all possible partners, expand it to half the trials of the block and randomize it
            firstHalf = list(range(numPartners)) * int(trialsPerBlock / (2*numPartners) )
            random.shuffle(firstHalf)

            # Generate a list of all lottery trials with the remainder of the trust trials and randomize it
            secondHalf = ([-1] * int(trialsPerBlock/4)) + list(range(numPartners)) * int(trialsPerBlock / (4*numPartners) )
            random.shuffle(secondHalf)
            return firstHalf + secondHalf # Return the concatenation of the 2 lists
        
        else:
            # Generate a list of all partners and the lottery, expand it, and randomize it
            options = list(range(-1,numPartners))
            options *= int(trialsPerBlock /  (numPartners+1) )
            random.shuffle(options)
            return options


    # FUNCTION THAT GENERATES AN OUTPUT DESTINATION BASED ON THE EXPERIMENT NAME, ID AND TIME
    def generate_output_dest(self):
        # Generate dynamic strings
        now:str = datetime.now().strftime("%Y%m%d_%H%M") 
        idName= self.ID['name']
        expName= self.exp['name']
        userPath = os.path.expanduser('~')
        
        # Generate the directories needed for the outputdirectory
        outputDir = f'{userPath}/Documents/PatientData'
        if not os.path.exists(outputDir): os.mkdir(outputDir)

        outputDir += f'/{idName}'
        if not os.path.exists(outputDir): os.mkdir(outputDir)

        outputDir += f'/{expName}'
        if not os.path.exists(outputDir): os.mkdir(outputDir)
    
        self.outputDir = outputDir + f'/{expName}__{idName}_{now}/'
        if not os.path.exists(self.outputDir): os.mkdir(self.outputDir)


    # SAVES THE PARAMETERS
    def save(self):
        columnData = ["Item", "Value"]

        screenData = [(key,str(value)) for key, value in self.screen.items()]
        screenData.extend([(key, str(value)) for key, value in self.window.items()])
        screenDataFrame = DataFrame(screenData, columns=columnData)

        expData = [(key,str(value)) for key, value in self.exp.items()]
        expData.extend([(f'{key} dur', str(value)) for key, value in self.window.items()])
        expDataFrame = DataFrame(expData, columns=columnData)

        partnerData = [(partner['name'], partner['image'], partner['trustworthiness']) for partner in self.partners]
        partnerDataFrame = DataFrame(partnerData, columns=['name', 'image', 'trustworthiness'])

        with ExcelWriter(f'{self.outputDir}Parameters.xlsx') as writer:
            screenDataFrame.to_excel(writer, sheet_name="Screen Settings")
            expDataFrame.to_excel(writer, sheet_name="Experiment General")
            partnerDataFrame.to_excel(writer, sheet_name="Partner Info")

    

    # GUI FOR GETTING THE PARTICIPANT'S ID
    def __launch_ID_UI(self):
        idUI = tk.Tk() 
        idUI.title('ID specifications')
        rowNum = 0

        # Label text for Name
        nameLabel = ttk.Label(idUI, text = "Please enter the participant's name/refID:")
        nameLabel.grid(row =rowNum, column=1, padx=10, sticky='W')
        rowNum += 1

        # Text Box for the Name
        nameEntry = ttk.Entry(idUI, textvariable=tk.StringVar(), justify=tk.LEFT)
        nameEntry.insert(0, 'TEST')
        nameEntry.grid(row=rowNum, column=1, padx=10, sticky='W')
        rowNum += 1

        # Blank Space
        ttk.Label(idUI).grid(row =rowNum, column=1)
        rowNum += 1

        # Label for exp Env Option
        expEnvLabel = ttk.Label(idUI, text='Select Experimental Setup:')
        expEnvLabel.grid(row=rowNum, column=1, padx=10, sticky='W')
        rowNum += 1

        # Combobox creation 
        expEnvList = ttk.Combobox(idUI, width = 20, textvariable = tk.StringVar()) 
        expEnvList['values'] = ('None', 'BCM-EMU') 
        expEnvList.grid(row=rowNum, column=1, padx=10, sticky='W') 
        expEnvList.current() 
        rowNum += 1

        # Blank Space
        ttk.Label(idUI).grid(row =rowNum, column=1)
        rowNum += 1

        def save_button():
            self.ID.update({'name': nameEntry.get(),
                            'expEnv': expEnvList.get()})
            shouldDestroy = True
            for key in self.ID.keys():
                if self.ID[key] == '': shouldDestroy = False

            if self.ID['expEnv'] not in expEnvList['values']:
                shouldDestroy = False

            if shouldDestroy:
                idUI.destroy()
            else:
                tkm.showwarning(title='Incorrect values', message='Some of the values appear to be missing or incorrect')
            
        saveButton = ttk.Button(idUI, text='Save', command=save_button)
        saveButton.grid(row=rowNum, column = 1)
        idUI.mainloop() 

