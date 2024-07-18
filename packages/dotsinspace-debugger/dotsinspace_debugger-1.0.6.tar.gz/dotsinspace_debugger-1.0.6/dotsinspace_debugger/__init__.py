#
# IMPORTS
#
import logging  # PIP: Logging library for python.
import re  # CORE: Python re library.
import os  # CORE: OS library for managing the environment.
import ujson  # PIP: Ultra fast JSON library for python.
import aiofiles  # PIP: Async file library for python.
import random  # CORE: Python random module.
import sentry_sdk  # PIP: Sentry for handling errors.
from colorama import Fore, Style  # PIP: Module for handling colored output


#
# GLOBALS
#
executionColors = {}
errorOrWarningOrInfoMaps = {
    'MISSING__CONTEXT': 'Expected context to execute route but it is missing.',
    'ERROR_FILE_NOT_FOUND': 'Error file not found',
    'MISSING_STATUS': 'Missing status code for given error.',
    'INTERNAL_SERVER_ERROR': 'Internal server error.',
    'UNAUTHORIZED__ACCESS': 'Unauthorized access.',
    'UNTAGGED_ERROR': 'Error is not tagged soon it will going to be tagged. Please use status for now.'
}


#
# FUNCTION
#
def Debugger(name):
    # Check if logger already exists
    if name in logging.Logger.manager.loggerDict:
        # Return logger.
        return logging.getLogger(name)

    # Variable assignment.
    colors = [
        Fore.BLACK,
        Fore.RED,
        Fore.GREEN,
        Fore.YELLOW,
        Fore.BLUE,
        Fore.MAGENTA,
        Fore.CYAN,
        Fore.WHITE,
        Fore.RESET,
        Fore.LIGHTBLACK_EX,
        Fore.LIGHTRED_EX,
        Fore.LIGHTGREEN_EX,
        Fore.LIGHTYELLOW_EX,
        Fore.LIGHTBLUE_EX,
        Fore.LIGHTMAGENTA_EX,
        Fore.LIGHTCYAN_EX,
        Fore.LIGHTWHITE_EX
    ]
    
    # Function to replace last occurrence of a string.
    def rreplace(s, old, new, occurrence):
        # Variable assignment.
        li = s.rsplit(old, occurrence)
        
        # Return new join.
        return new.join(li)
    
    # Update name.
    name = rreplace(name.replace('->', ':'), ':', '->', 1)

    # Logger for handling errors.
    logger = logging.getLogger(name)
    
    # Set the log level
    logger.setLevel(logging.DEBUG)

    # Create a console handler and set the log level
    ch = logging.StreamHandler()
    
    # Set the log level
    ch.setLevel(logging.DEBUG)

    # Use the function name to get the corresponding color, or assign a new random color if not found
    function_color = executionColors.get(name)
    
    # Check if function color is not defined then assign random color.
    if function_color is None:
        function_color = random.choice(colors)
        executionColors[name] = function_color

    # Create a formatter and attach it to the handler
    class ColoredFormatter(logging.Formatter):
        # Format method override.
        def format(self, message):
            # Execute override method with message
            formatted = super().format(message)
            return formatted.replace(message.name, f"{executionColors.get(name)}{message.name}:{Style.RESET_ALL}", 1)

    # Create a formatter and attach it to the handler.
    formatter = ColoredFormatter("%(name)-8s %(message)s")

    # Add the formatter to the handler.
    ch.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(ch)
    
    # Make sure that handlers have the formatter.
    for handler in logging.getLogger().handlers:
        # If handler has formatter then skip it.
        if handler.formatter:
            # Skip given loop.
            continue
        
        # Add formatter to handler.
        handler.setFormatter(formatter)

    # Return logger.
    return logger


async def ErrorHandler(error):
    try:
        # Only proceed if error is defined.
        if error:
            # Variable assignment.
            dataToReturn = []

            # Standardize error format it is object
            # then convert it to list and loop over it.
            error = error if isinstance(error, list) else [error]

            # Loop over each error and print it.
            for e in error:
                # Variable assignment.
                errorMessageToLog = ''
                errorStatusToLog = e['message'] if isinstance(e, dict) and 'message' in e else e

                # Only load error file if given e is not string.
                # and is exception.
                if isinstance(e, dict) and e.get('extensions') and len(e.get('extensions').get('exception').get('stacktrace')) > 0:
                    # Variable assignment.
                    fileNamesToIgnore = [
                        '/__mutation__/',
                        '/__resolver__/',
                        '/__subscription__/',
                        '/__query__/',
                        '/__directive__/'
                    ]

                    # Log error.
                    stackTrace = e.get('extensions').get('exception').get('stacktrace')

                    # Reverse given stack trace.
                    stackTrace.reverse()

                    # Loop over stack track.
                    for trace in stackTrace:
                        # Variable assignment.
                        filteredTrace = [re.escape(pattern) for pattern in fileNamesToIgnore]
                        filteredTrace = '|'.join(filteredTrace)

                        # if current trace includes __init__.py then consider it as
                        # root file which throwed the error.
                        if '__init__.py' in os.path.normpath(re.sub(filteredTrace, '', trace)):
                            # Path building.
                            path = os.path.normpath(re.sub(filteredTrace, '', trace))
                        else:
                            # Skip given loop.
                            continue

                        # Check if given file is origin of given error.
                        if os.path.normpath(re.sub(filteredTrace, '', path)):
                            # Search for file path.
                            m = re.search('"/(.+?)__init__.py"', trace)

                            # If found then load json of it.
                            if m:
                                # error handling.
                                try:
                                    # Load error json for given file.
                                    async with aiofiles.open(os.path.normpath(f'/{m.group(1)}/__error__.json'), mode='r') as file:
                                        # Variable assignment.
                                        fileContent = await file.read()

                                        # Load error json for given file.
                                        errorJson = ujson.loads(
                                            fileContent if fileContent else '{}')

                                        # Only try to get error message if errorJSON
                                        # is not empty else leave it.
                                        if errorJson.get(errorStatusToLog):
                                            # Load given e from error json.
                                            errorMessageToLog = errorJson.get(
                                                errorStatusToLog)
                                except FileNotFoundError:
                                    # Update message.
                                    errorStatusToLog = 'ERROR_FILE_NOT_FOUND'

                                    # Load error that file doesnt exist.
                                    errorMessageToLog = errorOrWarningOrInfoMaps.get(
                                        errorStatusToLog)

                # Check if errorOrWarningOrInfoMaps contains
                # given error status.
                if errorStatusToLog not in errorOrWarningOrInfoMaps and errorMessageToLog is None:
                    # Update message.
                    errorStatusToLog = 'MISSING_STATUS'
                    errorMessageToLog = errorOrWarningOrInfoMaps.get(
                        errorStatusToLog)
                elif errorMessageToLog is None:
                    # Update message.
                    errorMessageToLog = errorOrWarningOrInfoMaps.get(
                        errorStatusToLog)
                    
                # Update with default error message.
                if errorMessageToLog is None or errorMessageToLog is '':
                    # Update message.
                    errorMessageToLog = errorOrWarningOrInfoMaps.get('UNTAGGED_ERROR')

                # Update data to return.
                dataToReturn.append({'message': errorMessageToLog, 'status': str(errorStatusToLog)})

            # Return updated message.
            return dataToReturn
    except Exception as error:
        # Capture error.
        sentry_sdk.capture_exception(error)

        # Return none.
        raise error
