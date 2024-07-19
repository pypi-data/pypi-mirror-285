from src.dao import InstDao, OptDao
from prompt_toolkit.key_binding import KeyBindings
from src.view.display import display
import curses
import os

# 指令执行
def Execute(Terminal, user_input: str):
    """ execution instruction. """
    # 内置指令捕获
    if user_input == '.exit':
        Terminal.console.print('[green]Goodbye![/green]')
        exit(0)

    if user_input == '.help':
        PrintHelp(Terminal.console)
        return
    
    # cd 指令捕获
    if user_input.split(' ')[0] == 'cd':
        try:
            os.chdir(user_input.split(' ')[-1])
        except Exception as err:
            Terminal.console.print(f'[red]{err}[/red]')
        return
    
    # 执行指令
    try:
        os.system(user_input)
    except Exception as err:
        Terminal.console.print(f'[red]{err}[/red]')
    
    return


# 按键绑定
Bindings = KeyBindings()

@Bindings.add('c-right')
def _(event): 
    text = event.current_buffer.text
    words = text.split(' ')
    insts = InstDao().SelectExistByName(words[0])
    if insts is None:
        return
    
    opts = OptDao().SelectById(insts.id)
    opts = [f'   {opt.content}' for opt in opts]

    lines = ['Usage:',f'\t{insts.synopsis}','OPTIONs: ', *opts]
    curses.wrapper(display, lines)


# 打印帮助信息
def PrintHelp(console):
    """ print help information. """
    console.print(
        """[#00FFFF]
      ____  ____________  ____________  ___ 
     / __ \/ __/_  __/ / / /_  __/ __ \/ _ \\
    / /_/ _\ \  / / / /_/ / / / / /_/ / , _/
    \____/___/ /_/  \____/ /_/  \____/_/|_|  - OpenEuler Assistant. [/#00FFFF]""")
    
    console.print(
        """[#FFF]
    Usage:
        command

    Commands:
        .help     Print help information.
        .exit     Exit terminal program.
[/#FFF] 
"""
    )