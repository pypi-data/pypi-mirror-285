import cmd
from src.logic import tfidf
from .display import display
from src.dao import InstDao, InstExtraDao, OptDao
import curses
from rich.console import Console
from rich.table import Table
from src.data import Parse
import math


class Cli(cmd.Cmd):
    console = Console()
    prompt = '(^o^)* > '
    l = 0

    def Run(self):
        key = input("Please input key words: ")
         #########  关键词搜索  ########### 
        self.res = tfidf.search(key)
        #################################
        self.outputFormat()

        self.cmdloop()

    def do_info(self, arg):
        """
        Displays detailed information about the specified instruction

        Usage: info [id]
        """

        if arg.isdigit() == False:
            print("Please enter the number")
            return
        arg = int(arg)
        Info().Run(self.res[arg][0], self.res[arg][2])

        self.outputFormat()

    def do_next(self, _):
        'Page Down'

        if(self.l>len(self.res)): 
            print("It's the last page")
            return
        self.l += 10
        self.outputFormat()
    
    def do_back(self, _):
        'Page Up'

        if(self.l==0): 
            print("It's already page one")
            return
        self.l -= 10
        self.outputFormat()

    def do_refresh(self, _):
        'Redisplay'

        self.outputFormat()

    def do_anew(self, arg):
        """
        New Search

        Usage: newkey [key_words]
        """
        ##########  关键词搜索  ########### 
        self.res = tfidf.search(str(arg))
        #################################
        self.outputFormat()

    def do_page(self, arg):
        """
        Displays the specified number of pages

        Usage: page [number]        
        """

        if arg.isdigit() == False:
            print("Please enter the number")
            return
        arg = int(arg)
        if arg *10 < 0 or arg * 10 > len(self.res):
            print(f"请输入0-{math.ceil(len(self.res)/10)}")
            return
        self.l = arg*10
        self.outputFormat()

    def do_exit(self, _):
        'Exit'
        return True

    def do_quit(self, _):
        'Quit'
        exit(0)


    def outputFormat(self):
        # 清屏
        self.console.clear()
        cur = self.l+1
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column('cur')
        table.add_column('name')
        table.add_column('type')
        table.add_column('score')
        table.add_column('brief')
        for item in self.res[self.l:self.l+10]:
            id , name, brief, type, score = item
            name = name if len(name) <15 else name[:15]+ "..."
            table.add_row(
                f"{cur}",
                name,
                type,
                f"{score:.2f}",
                brief,
                style="bold yellow" if score > 0 else "dim"
            )
            cur+=1
        self.console.print(table)

        self.console.print(f"[bold blue]\nType help or ? View help.\n[/bold blue]")


class Info(cmd.Cmd):
    console = Console()
    prompt = '(^o^)* > '

    def Run(self, id, brief):
        self.id = id
        self.brief = brief

        inst = InstDao().SelectById(self.id)
        optDao = OptDao().SelectById(self.id)

        self.instInfo = {
            "DESCRIPTION": inst.description,
            "SYNOPSIS": inst.synopsis,
            "EXAMPLE": inst.example,
            'OPTION' : optDao
        }
        extraInfo = InstExtraDao().SelectById(self.id)
        extraInfo = {info.title:info.text for info in extraInfo}
 
        self.instInfoTitle =[i for i in self.instInfo.keys()] + [i for i in extraInfo.keys()]
        self.instInfo.update(extraInfo)

        self.show()
        self.cmdloop()
    def do_exit(self, _):
        'Exit'
        return True
    
    def do_quit(self, _):
        'Quit'
        exit(0)
    
    def do_dsp(self, arg):
        """
        Display specified information.

        Usage: dsp [number]
        """
        
        if arg.isdigit() == False:
            print("Please enter the number")
            return
        
        if int(arg) >= len(self.instInfoTitle) or int(arg) < 0:
            print(f"Please enter between 0-{len(self.instInfoTitle)-1}")
            return
        
        parse = Parse()
        title = self.instInfoTitle[int(arg)]
        print(title)
        content = self.instInfo[title]
        if title == 'OPTION':
            lines = [f"    {o.content}" for o in content]
            lines = ['OPTIONs:',*lines]
            curses.wrapper(display, lines)
        else:
            lines = parse.splitContent(content)
            lines = [f'    {i}' for i in lines]
            curses.wrapper(display, lines)

        self.show()
    
    def show(self):
         # 清屏
        self.console.clear()

        self.console.print(f"[bold magenta]{self.brief}[/bold magenta]\n")
        for index, value in enumerate(self.instInfoTitle):
            self.console.print(f"[bold yellow]{[index]}\t{value}[/bold yellow]")

        self.console.print(f"[bold blue]\nType help or ? View help.\n[/bold blue]")
    