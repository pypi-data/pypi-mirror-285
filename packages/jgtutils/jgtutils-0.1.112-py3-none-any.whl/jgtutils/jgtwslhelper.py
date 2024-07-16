import subprocess

import os
import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

import jgtos

import platform

def pwsd_wsl_run_command1(bash_command_to_run):
    powershell_command = 'wsl.exe bash -c \'' + bash_command_to_run + '\''
    result = subprocess.run(
        ["pwsh.exe", "-Command", powershell_command], stdout=subprocess.PIPE, shell=True
    )
    return result.stdout.decode("utf-8")





def run_bash_command_by_platform(bash_cmd):
    try:
        if platform.system() == "Windows":
            shell = os.environ.get('COMSPEC', 'cmd.exe')
            if 'powershell' in shell.lower():
                # The interpreter is PowerShell            
                return subprocess.run(bash_cmd, shell=True, stdout=subprocess.PIPE).stdout.decode("utf-8")
            else:
                # The interpreter is cmd.exe
                return wsl_run_bash_on_cmd(bash_cmd)
        else:
            # The system is Linux
            return subprocess.run(bash_cmd, shell=True, stdout=subprocess.PIPE).stdout.decode("utf-8")
    except Exception as e:
        print(f"An error occurred running jgtfxcli: {str(e)}")
        print(f"   bash_cmd: {bash_cmd}")
        raise e
        #return None
    
def wsl_run_bash_on_cmd(bash_cmd):   
    
    powershell_command = 'wsl.exe bash -c \'' + bash_cmd + '\''
    result = subprocess.run(
        ["pwsh.exe", "-Command", powershell_command], stdout=subprocess.PIPE, shell=True
    )
    return result.stdout.decode("utf-8")



def run(bash_command):
    return run_bash_command_by_platform(bash_command)


    

def resolve_cli_path(cli_path=""):
    if cli_path == "" or cli_path is None or cli_path == 0 or cli_path == '0':
        cli_path = os.path.join(os.getenv('HOME'), '.local', 'bin', 'jgtfxcli')
    if not os.path.exists(cli_path):
        cli_path = 'jgtfxcli'    
    
    return cli_path #@STCIssue Should install : pip install --user jgtfxcon    (if not found)

def jgtfxcli_wsl(instrument:str, timeframe:str, quote_count:int,cli_path="", verbose_level=0,use_full=False):
    cli_path=resolve_cli_path(cli_path)
    if cli_path == "" or cli_path is None or cli_path == 0 or cli_path == '0':
        cli_path = '$HOME/.local/bin/jgtfxcli'
        #cli_path = "/home/jgi/.local/bin/jgtfxcli"
    if use_full:
        bash_command_to_run = f"pwd;{cli_path} -i \"{instrument}\" -t \"{timeframe}\" --full  -v {verbose_level} "
    else :
        bash_command_to_run = f"pwd;{cli_path} -i \"{instrument}\" -t \"{timeframe}\" -c {quote_count} -v {verbose_level}"
    if verbose_level > 0:
        print(f"bash_command_to_run: {bash_command_to_run}")
    
    return run_bash_command_by_platform(bash_command_to_run)


def _mkbash_cmd_string_jgtfxcli_range(instrument:str, timeframe:str,tlid_range=None,cli_path="", verbose_level=0,quote_count=420,use_full=False,keep_bid_ask=False):
    cli_path=resolve_cli_path(cli_path)
    
    
    #env variable bypass if env exist JGT_KEEP_BID_ASK=1, keep_bid_ask = True
    bidask_arg = " "
    if os.getenv("JGT_KEEP_BID_ASK","0") == "1":
        keep_bid_ask = True
    if keep_bid_ask:
        bidask_arg = " -kba "
    if tlid_range is not None:
        bash_command_to_run = f"pwd;{cli_path} -i \"{instrument}\" -t \"{timeframe}\" -r \"{tlid_range}\" -v {verbose_level} {bidask_arg}"
    else:
        if use_full:
            bash_command_to_run = f"pwd;{cli_path} -i \"{instrument}\" -t \"{timeframe}\" --full  -v {verbose_level}  {bidask_arg}"
        else:
            bash_command_to_run = f"pwd;{cli_path} -i \"{instrument}\" -t \"{timeframe}\" -c \"{quote_count}\" -v {verbose_level}  {bidask_arg}"
        
    
    return bash_command_to_run

def _mkbash_cmd_string_jgtfxcli_range1(instrument:str, timeframe:str,tlid_range=None,cli_path="", verbose_level=0):
    cli_path=resolve_cli_path(cli_path)
    
    date_from,date_to=jgtos.tlid_range_to_jgtfxcon_start_end_str(tlid_range)
    
    bash_command_to_run = f"pwd;{cli_path} -i \"{instrument}\" -t \"{timeframe}\" -s \"{date_from}\" -e \"{date_to}\" -v {verbose_level}"
    return bash_command_to_run

def jgtfxcli_wsl_range(instrument:str, timeframe:str, quote_count:int,tlid_range=None,cli_path="", verbose_level=0,use_full=False,keep_bid_ask=False):
    bash_command_to_run = _mkbash_cmd_string_jgtfxcli_range(instrument, timeframe,tlid_range,cli_path, verbose_level,quote_count,use_full=use_full)
        
    return run_bash_command_by_platform(bash_command_to_run)

def jgtfxcli(instrument:str, timeframe:str, quote_count:int,cli_path="", verbose_level=0,use_full=False):
    return jgtfxcli_wsl(instrument,timeframe,quote_count,cli_path,verbose_level,use_full=use_full)

def getPH(instrument:str, timeframe:str, quote_count:int,tlid_range=None, verbose_level=0,use_full=False,keep_bid_ask=False):
    return jgtfxcli_wsl_range(instrument, timeframe, quote_count,tlid_range,"", verbose_level,use_full=use_full,keep_bid_ask=keep_bid_ask)


def wsl_cd(directory):
    # Define the command to be executed
    command = ["wsl.exe", "cd", directory]

    # Execute the command
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


    # Print the error (if any)
    if result.stderr:
        return result.stderr.decode("utf-8")
    else:
        # Print the output
        return result.stdout.decode("utf-8")
        

def cd(tpath):
    wsl_cd(tpath)

def execute_wsl_command_v1_with_cd(directory, command_to_execute):
    # Define the command to be executed
    command = ["wsl.exe", "cd", directory, "&&", command_to_execute]

    # Execute the command
    result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Print the output
    print(result.stdout.decode("utf-8"))

    # Print the error (if any)
    if result.stderr:
        print("Error:", result.stderr.decode("utf-8"))


minimum_quote_count = 335

# Define the dividers for each timeframe
timeframe_dividers = {
    "m1": 0.0166,
    "mi1": 0.0166,
    "m5": 0.8,
    "m15": 0.25,
    "m30": 0.5,
    "H1": 1,
    "H2": 2,
    "H3": 3,
    "H4": 4,
    "H5": 5,
    "H6": 6,
    "H8": 8,
    "D1": 24,
    "W1": 110,
    "M1": 400
}

#@STCIssue Locks us to H1, should be interactive and receive an input from the user, lower TF
def get_timeframe_dividers(base_tf="H1"):
    return timeframe_dividers[base_tf]
