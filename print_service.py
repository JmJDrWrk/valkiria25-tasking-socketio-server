## @@ Logging 
import logging
import re
from datetime import datetime
# Set up logging configuration with a timestamp in the filename
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS
log_filename = f'./logs/application_{timestamp}.log'  # Create a new log file for each run

logging.basicConfig(
    filename=log_filename,  # Specify the log file with timestamp
    level=logging.DEBUG,     # Set the logging level
    format='%(asctime)s - %(levelname)s - %(message)s'  # Log format
)


import colorama
from colorama import Fore, Back, Style

colorama.init()

keyLevelOne = ["controlle", "client"]
keyLevelTwo = ["client", "get", "post", "accept"]

## Colored Services
colorMap = {
    'service': {
        'auth_manager': [Fore.WHITE, Back.BLUE, Style.NORMAL],
        'workers_handler': [Fore.GREEN, Back.BLACK, Style.BRIGHT],
        'controllers': [Fore.YELLOW, Back.BLACK, Style.BRIGHT],
        'decorators': [Fore.MAGENTA, Back.BLACK, Style.BRIGHT],
        'IoServer': [Fore.RED, Back.BLACK, Style.BRIGHT],
        'print_service': [Fore.CYAN, Back.BLACK, Style.BRIGHT],
        'self_control': [Fore.LIGHTWHITE_EX, Back.BLUE, Style.NORMAL],
        'clients_handler': [Fore.LIGHTGREEN_EX, Back.BLACK, Style.NORMAL],
        'load_balancer': [Fore.LIGHTYELLOW_EX, Back.MAGENTA, Style.BRIGHT],
        'ssl_context': [Fore.LIGHTCYAN_EX, Back.BLACK, Style.NORMAL],
    }
}

# Example usage
# def colorize(text, file_key):
#     fore, back, style = colorMap['service'][file_key]
#     return f"{fore}{back}{style}{text}{Style.RESET_ALL}"

_print = print

def colorPrint(*args, **kwargs):
    output = " ".join(map(str, args))

    
    ## Standard colorization ##
    if output.lower().startswith("error"):
        std = Fore.RED + output + Style.RESET_ALL
        logging.info(std)
        _print(std, **kwargs)
    elif output.lower().startswith("info"):
        std = Fore.BLUE + output + Style.RESET_ALL
        logging.info(std)
        _print(std, **kwargs)
    elif output.lower().startswith("warn"):
        std = Fore.YELLOW + output + Style.RESET_ALL
        logging.info(std)
        _print(std, **kwargs)
        
    # Later we must set a number to split to not let the code check in all string if contains, but the idea is like firts 6 chars contains...
    elif output.lower().startswith('['):
        try:
            first_chars = output[:20]
            file_key = first_chars.split(']')[0].split('[')[1]#.split('\\')[1].split('.py')[0]
            fore, back, style = colorMap['service'][file_key]
            # f"{fore}{back}{style}{output}{Style.RESET_ALL}"
            std = f"{fore}{back}{style}{output}{Style.RESET_ALL}"
            logging.info(output)
            _print(std, **kwargs)
        except:
            logging.info(output)
            _print(output, **kwargs)
    else:
        logging.info(output)
        _print(output, **kwargs)
        
        
pattern = r'[^\\/]+$'
class Printer():
    def __init__(self, service_name) -> None:
        if '.py' in service_name:
            match = re.search(pattern, service_name)
            if match:
                self.service_name = match.group(0).replace('.py','')  # Get the matched file name
            else:
                _print(':(')
                self.service_name = service_name
        else:
            self.service_name = service_name
            
    def print(self, *args, **kwargs):
        colorPrint(f'[{self.service_name}] '+" ".join(map(str, args)), **kwargs)