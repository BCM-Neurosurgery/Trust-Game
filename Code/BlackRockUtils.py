# BLACKROCK UTILITIES FOR PYTHON TASKS
# DEVELOPED BY GEORGIOS KOKALAS

from os import path, listdir
from pandas import read_csv
from subprocess import run
from cerebus import cbpy

# GLOBAL OPERATIONS - EXECUTED UPON SCRIPT IMPORTATION
# IP acquisition - Utilize the port names to find the IPs of the neural recorders on the local network
#     For every port list port information and from that extract the IP address and store it in a list
PORT_NAMES = ['NSP1', 'NSP2']
IP_ADDRESSES = []
for port in PORT_NAMES:
    process = run(f'netsh interface ip show address "{port}" | findstr "IP Address"',\
                  shell = True, capture_output = True, text=True)
    IP_ADDRESSES.append(process.stdout.strip().split()[2])


# Online NSP acquisition - Find all of the NSPs active and list them
ONLINE_NSPS = [-1] * len(IP_ADDRESSES)   # Generate a list as big as the NSP ports
SUFFIXES = []                            # Store the suffixes for each NSP (helps in comments later)

for inst, address in enumerate(IP_ADDRESSES):   # list the IP addresses as 0: address1, 1: address2 etc.
    try:
        cbpy.open(instance=inst, parameter={'inst-addr':address})   # Use cpby to create a link per address, treating the nsp as a central machine
        ONLINE_NSPS[inst] = inst                                       # List the instance number
        SUFFIXES.append(f'_NSP-{inst+1}')                              # Create a new suffix for comments to have
    except:
        print(f"Issue opening NSP{inst+1}")
pass


# Instantiate global variables for persistent use in functions
EMU_NUM = -1
EMU_STR = ''
LOG_TABLE = ...
LOG_FILE = ''


# FUNCTION OPERATIONS - EXECUTED UPON CALL
# Function Name: get_next_log_entry
# Purpose: Find the log file with all the emu numbers and generate a new entry for the experiment
# Input: None
# Output: - EMU_NUM:  The new emu number to be used in this experiment
#         - subjID:   The subject ID of the patient
#         - LOG_FILE: The name of the file that stores the logs of the emu numbers
def get_next_log_entry():
    global EMU_NUM, LOG_TABLE, LOG_FILE

    # Generate a new path to the log file, ensuring that only 1 file resides there
    tablePath = path.join(path.expanduser('~'), 'Documents', 'MATLAB', 'PatientData', '+CurrentPatientLog')
    tableDir = listdir(tablePath)
    if len(tableDir) < 1:
        raise Exception("No file detected in +CurrentPatientLog")
    elif len(tableDir) > 1:
        raise Exception("More than 1 file detected in +CurrentPatientLog")
    else:
        # From the file, get the subject ID and the new emu number
        fileName = tableDir[0]
        fileParts = fileName.split('_')
        subjID = fileParts[0]
        LOG_FILE = path.join(tablePath, fileName)
        LOG_TABLE = read_csv(LOG_FILE)
        EMU_NUM = LOG_TABLE['emu_id'][LOG_TABLE.shape[0]-1] + 1
        return EMU_NUM, subjID, LOG_TABLE


# Function Name: make_EmuSaveName
# Purpose: Create a new blackrock name for this instance of the task. Update the log file with the new emu number and the emu save name
# Input: - EmuRunNum: The run number of the task instance
#        - SubjName:  The subject name for the patient
#        - ExpName:   The name of the task
# Output: - allString: the emu save name
def make_EmuSaveName(EmuRunNum, SubjName, ExpName):
    global EMU_STR, LOG_TABLE, LOG_FILE

    #Generate the string
    EMU_STR = f'EMU-{EmuRunNum:04}'
    allString = f'EMU-{EmuRunNum:04}_subj-{SubjName}_{ExpName}'

    # Save the new task entry in the log file
    LOG_TABLE.loc[len(LOG_TABLE)] = [EMU_NUM, allString]
    LOG_TABLE.to_csv(LOG_FILE, index=False)

    return allString


# Function Name: task_comment
# Purpose: Generate a blackrock comment. Kill the connection to the NSPs if needed
# Input: - Event:    The type/name of the event
#        - FileName: The emu save name
# Output: None
def task_comment(Event:str, FileName:str):
    # Crash if the comment is too long (NOTE: maybe find a better alternative)
    if len(Event)+len(SUFFIXES[0])+7 > 92:
        raise Exception("Event/comment provided is too long")

    # Instantiate the event message and color
    eventCode = ''
    eventColor = (0,255,255,255)#16777215
    closeAfter = False

    # Adjust behavior on event
    match Event:
        #tbgr
        case 'start':  # On start, send a green start message
            eventCode = f'$TASKSTART {FileName}'
            eventColor = (0,0,255,0)#65280
        case 'stop':   # On stop, send a pink stop message
            eventCode = f'$TASKSTOP {FileName}'
            eventColor =  (0,255,0,255)#16711935
            closeAfter = True
        case 'kill':  # On kill, send a red kill message
            eventCode = f'$TASKKILL {FileName}'
            eventColor = (0,0,0,255)#255
            closeAfter = True
        case 'error': # On error, send a red error message
            eventCode = f'$TASKERR {FileName}'
            eventColor = (0,0,0,255)#255
            closeAfter = True
        case 'annotate': # On annotate, send a blue generic event message
            eventCode = f'@EVENT {FileName}'
            eventColor = (0,255,0,0)#16711680
        case _:          # In any other case, send a white message with the event name as the message
            eventCode = f'{Event}-{EMU_STR}'

    # Send the message iterating in each NSP
    for nsp in ONLINE_NSPS:
        # Skip if we haven't connected
        if nsp == -1:
            continue

        # Combine the event code with the suffixes
        comment = f'{eventCode}{SUFFIXES[nsp]}'
        if Event == 'start': print(comment)      

        # Send the comment to blackrock
        cbpy.set_comment(comment, rgba_tuple=eventColor, instance=nsp)

    # On stop, kill or error, close the link to the NSP
    if closeAfter:
        for idx in range(len(ONLINE_NSPS)-1, -1, -1):
            if ONLINE_NSPS[idx] != -1: 
                cbpy.close(ONLINE_NSPS[idx])

                

    
