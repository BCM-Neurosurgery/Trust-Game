from psychopy import core, prefs, visual
import os

from Code.Class.parameters import Parameters 

# Set hardware preferences
prefs.hardware['audioLib'] = ['sounddevice', 'pygame']
prefs.hardware['audioLatencyMode'] = '3'

# Load parameters globally
PARAMETERS = Parameters()

# Conduct EMU startup operations as needed
MATENG = ...
if PARAMETERS.ID['expEnv'] == "BCM-EMU":
    # import Code.BlackRockUtils as bru
    # emuNum, subjID, logTable = bru.get_next_log_entry()
    # fileName = bru.make_EmuSaveName(emuNum, subjID, PARAMETERS.exp['name'])
    # PARAMETERS.ID.update({'emuNum': emuNum,
    #                    'name': subjID,
    #                    'logTable': logTable,
    #                    'fileName': fileName})
    import matlab.engine                                                        # import the matlab engine
    MATENG = matlab.engine.start_matlab()                                       # Fire up the matlab engine
    logEntry = MATENG.eval("getNextLogEntry();", nargout = 2)                   # Gather the log Entry for the patient
    emuRunNum = int(logEntry[0])                                                # Isolate the EMU number 
    expName = PARAMETERS.exp["name"]
    emuSaveName = f'EMU-{emuRunNum:04}_subj-{logEntry[1]}_{expName}'     # Generate a filename for the Neural recordings
    print(emuSaveName)
    MATENG.workspace['emuSaveName'] = MATENG.cellstr(list(emuSaveName))         # Save the filename in the matlab workspace
    MATENG.eval("emuSaveName = [emuSaveName{:}];", nargout = 0)                 # Modify the filename in the correct format (cell->char)
    PARAMETERS.ID.update({'emuRunNum': emuRunNum})                              # Save the emu run number in the emu parameters
    PARAMETERS.ID['name'] = logEntry[1]                                         # Save the EMU codename as the patient's ID
PARAMETERS.generate_output_dest()
PARAMETERS.save()


# Set up experiment settings
DATA_PATH = os.path.join(os.getcwd(), "data")
if not os.path.exists(DATA_PATH):
    os.makedirs(DATA_PATH)

# Global experiment clock
ABS_CLOCK = core.Clock()
REL_CLOCK = core.Clock()

# Global UI Window creation
# UI_WIN = visual.Window(size=PARAMETERS.window['size'], fullscr=PARAMETERS.screen['fullscr'], screen = PARAMETERS.screen['number'],
UI_WIN = visual.Window(fullscr=PARAMETERS.screen['fullscr'], screen = PARAMETERS.screen['number'],
                       units=PARAMETERS.window['units'], color=PARAMETERS.window['bgColor'], colorSpace='rgb255')

PARAMETERS.window.update({'size': UI_WIN.size})

EVENTS = []
ABORT = False

def abort():
    global ABORT
    ABORT = True