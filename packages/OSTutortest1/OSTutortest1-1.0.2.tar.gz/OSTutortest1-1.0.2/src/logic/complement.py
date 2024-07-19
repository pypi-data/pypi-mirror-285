from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.formatted_text import FormattedText
from src.dao import OptDao

# 指令补全逻辑
class InstCompleter(Completer):
    def __init__(self, insts):
        self.insts = {i.name:i.id for i in insts}
        self.briefs = {i.name:i.brief for i in insts}
        self.synopsis = {i.name:i.synopsis for i in insts}
        
    def get_completions(self, document, complete_event):
        text = document.current_line
        words = text.split(' ')

        if len(words) == 1:
            insts = [inst for inst in self.insts.keys() if inst.startswith(words[0])]
            for inst in insts:
                brief = self.briefs[inst].split('-')[-1]
                formatted_text = FormattedText([
                    ('fg:black', inst + ' '),  # 补全的实例名称
                    ('fg:grey italic',' - ' + brief)  # 实例的brief信息
                ])
                yield Completion(inst, start_position=-len(words[0]), display=formatted_text)
        else:
            if words[0] not in self.insts:
                return
            
            formatted_text = FormattedText([
                    ('fg:blue italic',self.synopsis[words[0]]) 
                ])
            yield Completion('', start_position=-len(words[-1]), display=formatted_text) # 显示语法
            
            opts = OptDao().SelectById(self.insts[words[0]])
            opts = {opt.name:opt.content for opt in opts}
            names = [opt for opt in opts.keys() if opt.startswith(words[-1])]
            
            for name in names:
                formatted_text = FormattedText([
                    ('fg:black', name + ' '),  # 补全的实例名称
                    ('fg:grey italic',f'  {opts[name]}')  # 实例的brief信息
                ])
                yield Completion(name, start_position=-len(words[-1]), display=formatted_text)