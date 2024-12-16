import matlab
import Code.globals as glb

# if glb.PARAMETERS.ID.get('expEnv') == "BCM-EMU":
#     import Code.BlackRockUtils as bru

def markEvent(EventType: str, *args):
    """
    Log events during the experiment with standardized event names and timing.
    
    Parameters:
    ----------
    EventType : str
        The type of event to log (e.g., 'taskStart', 'trialStart').
    PARAMETERS : Parameters, optional
        The Parameters instance where events will be stored.
    *args : tuple
        Positional arguments for event specifics.
    **kwargs : dict
        Additional keyword arguments like 'trialIdx' or 'blockIdx'.
    """
    # Get the event time using the global clock
    eventTime = glb.ABS_CLOCK.getTime()
    
    # Define event names based on EventType and additional arguments
    eventName = ""
    match EventType:
        case "taskStart":
            eventName = "Task Started"
        case "taskStop":
            eventName = "Task Ended Successfully"
        case "taskAbort":
            print("ABORTING TASK")
            eventName = "Task Aborted"

        case "introStart":
            eventName = "Intro Started"
        case "introEnd":
            eventName = "Intro Ended"

        case "blockStart":
            eventName = f"Block {args[0]} Started"
        case "blockEnd":
            eventName = f"Block {args[0]} Ended"
        case "trialStart":
            eventName = f"Trial:{args[0]}-Block:{args[1]}-Type:{args[2]} Started"
        case "trialEnd":
            eventName = f"Trial:{args[0]}-Block:{args[1]}-Type:{args[2]} Ended"

        case "DecisionStart":
            eventName = "Decision Phase Started"
        case "DecisionMade":
            eventName = "Decision was entered"
        case "DecisionEnd":
            eventName = "Decision Phase Ended"
        case "OutcomeStart":
            eventName = "Outcome Phase Started"
        case "OutcomeEnd":
            eventName = "Outcome Phase Ended"

        case "TrustRankInitialStart":
            eventName = f"Early Trust Ranking Started for CPU {args[0]}"
        case "TrustRankInitialEnd":
            eventName = f"Early Trust Ranking Ended for CPU {args[0]}"
        case "TrustRankMiddleStart":
            eventName = f"Middle Trust Ranking Started for CPU {args[0]}"
        case "TrustRankMiddleEnd":
            eventName = f"Middle Trust Ranking Ended for CPU {args[0]}"
        case "TrustRankFinalStart":
            eventName = f"Late Trust Ranking Started for CPU {args[0]}"
        case "TrustRankFinalEnd":
            eventName = f"Late Trust Ranking Ended for CPU {args[0]}"
        case "RankingMade":
            eventName = "Ranking was entered"

        case _:
            eventName = "UNKNOWN EVENT"

    glb.EVENTS.append((eventName, eventTime))

    # Additional environment-specific handling if needed
    if glb.PARAMETERS.ID.get('expEnv') == "BCM-EMU":
        match EventType:
            case "taskStart":
                # bru.task_comment('start', glb.PARAMETERS.ID['fileName'])
                onlineNSP = glb.MATENG.eval("TaskComment('start', emuSaveName);", nargout=1)
                glb.MATENG.workspace['onlineNSP'] = matlab.double(onlineNSP)
            case "taskStop":
                # bru.task_comment('stop', glb.PARAMETERS.ID['fileName'])
                glb.MATENG.eval("TaskComment('stop', emuSaveName);", nargout=0)
            case "taskAbort":
                # bru.task_comment('kill', glb.PARAMETERS.ID['fileName'])
                glb.MATENG.eval("TaskComment('kill', emuSaveName);", nargout=0)
            case _:
                # bru.task_comment(eventName, glb.PARAMETERS.ID['fileName'])
                blackRockComment = glb.MATENG.cellstr([eventName])
                glb.MATENG.workspace['blackRockComment'] = blackRockComment
                glb.MATENG.eval("blackRockComment = [blackRockComment{:}];", nargout=0)
                glb.MATENG.eval("for i=1:numel(onlineNSP); cbmex('comment', 255, 0, blackRockComment, 'instance', onlineNSP(i)-1); end", nargout=0)
