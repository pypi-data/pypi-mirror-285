import click
from src.view import Cli, defuisearch as UI
from colorama import Fore, Style
import os

@click.group()
def cmd():
    """OSTutor - OpenEuler Application Assistant."""

@cmd.command()
#@click.option('-r',is_flag=True, help='打开rpm包检索界面')
@click.option('-i',is_flag=True, help='Open the command retrieval screen')
def ui(i):
    """Start user interface mode."""
    UI()

@cmd.command()
def cli():
    """Command line retrieval."""
    Cli().Run()

@cmd.command()
def rpmsexp():
    """Export the local RPM list to the current directory."""
    from src.data import Collection
    Collection().exportRpmList()

@cmd.command()
@click.argument('path')
def dataexp(path):
    abs = os.path.join(os.getcwd(), path)
    if os.path.isdir(abs):
        abs = os.path.join(abs, 'inst.json')
        from src.data import Export
        Export(abs).exportDatabase()
    else:
        print(Fore.RED + 'Directory does not exist' + Style.RESET_ALL)

@cmd.command()
@click.argument('path')
def dataimp(path):
    """Import the specified json file to the database."""
    abs = os.path.join(os.getcwd(), path)
    suffix = os.path.splitext(abs)[1]
    if suffix == '.json':
        if os.path.exists(abs):
            from src.data import Import
            Import(abs).importDatabase()
        else:
            print(Fore.RED + 'file does not exist' + Style.RESET_ALL)
    else:
        print(Fore.RED + 'Please enter the json file path' + Style.RESET_ALL)


@cmd.command()
def install():
    """Do not differentially download the rpm package from the rpmsexport.txt file in the current directory."""
    from src.data import Collection
    Collection().downLoadRpmList()

@cmd.command()
def lrefresh():
    """Refresh the knowledge base locally."""
    from src.data import Collection
    Collection().collect()
    
@cmd.command()
@click.option('--user', is_flag=True, help='Query user instruction for which data does not exist')
@click.option('--admin', is_flag=True, help='Query administrator instruction for data that does not exist.')
@click.option('--all', is_flag=True, help='Query all instructions for non-existent data.')
def nodata(user, admin, all):
    """Search for local instructions without data."""
    from src.data import Collection
    nu, na = Collection().collectNoDataInsts()
    if user or all:
        print(Fore.MAGENTA + "user:")
        print(Fore.YELLOW + '\n'.join(nu), Style.RESET_ALL)
    if admin or all:
        print(Fore.MAGENTA + "admin:")
        print(Fore.YELLOW + '\n'.join(na)+ Style.RESET_ALL)


@cmd.command()
def terminal():
    """Open the terminal interface."""
    from src.view import Terminal
    Terminal().Run()
