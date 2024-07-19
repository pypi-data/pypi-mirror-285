import npyscreen
from textwrap import wrap  # 用于处理动态换行
from src.dao import InstDao, InstExtraDao, OptDao  # 确保正确导入了 InstDao 和 InstExtraDao
import src.logic.tfidf as tfidf
import sys

# 定义搜索框
class SearchBox(npyscreen.BoxTitle):
    _contained_widget = npyscreen.Autocomplete

# 定义显示搜索结果的文本框
class SearchResults(npyscreen.MultiLineAction):
    def actionHighlighted(self, act_on_this, keypress):
        selected_id, selected_name = self.parent.parentApp.getForm('MAIN').all_results_dict[act_on_this]
        instruct_form = self.parent.parentApp.getForm('INSTRUCT')
        instruct_form.selected_id = selected_id
        instruct_form.selected_name = selected_name
        self.parent.parentApp.switchForm("INSTRUCT")

# 搜索表单
class SearchForm(npyscreen.FormBaseNew):
    def afterEditing(self):
        self.parentApp.setNextForm('INSTRUCT')  # 设定在当前窗口退出后显示 InstructForm 窗口
    
    def create(self):
        self.add(npyscreen.FixedText, value="Press 'q' to exit, 'j' to Go Down, 'k' to Go Up, 'Enter' to Find.", editable=False, color="CAUTION", rely=1, relx=2)
        self.search_box = self.add(SearchBox, name="Search", max_height=3, editable=True, hidden=False, scroll_exit=False, slow_scroll=False, exit_left=False, exit_right=True, rely=2, relx=1)
        self.search_results = self.add(SearchResults, editable=True, hidden=False, scroll_exit=True, slow_scroll=True, exit_left=True, exit_right=False)
        # 绑定搜索框的输入事件
        self.search_box.entry_widget.when_value_edited = self.perform_search
        self.all_results = []
        self.all_results_dict = {}
    
    def perform_search(self):
        # 获取用户输入的搜索关键字
        self.search_keyword = self.search_box.value
        # 执行搜索操作
        self.all_results = self.searchui(self.search_keyword)
        # 更新搜索结果显示
        self.update_results()

    # 搜索
    def searchui(self, keyword):
        res = tfidf.search(keyword)
        return res

    # 显示搜索结果
    def update_results(self):
        formatted_results = []
        self.all_results_dict = {}  # 清空原来的字典
        temp = [i for i in self.all_results if i[4] > 0]
        for item in temp:
            id, name, description, type, relevance = item
            
            # 确定 name 字段的最大长度为15
            max_name_length = 15
            truncated_name = name
            if len(name) > max_name_length:
                truncated_name = name[:max_name_length - 3] + '...'
            
            formatted_result = f"{id:<10} {truncated_name:<15} {type:<10} {relevance:<10.4f} {description:<50}"
            formatted_results.append(formatted_result)
            self.all_results_dict[formatted_result] = (id, name)
        
        self.search_results.values = formatted_results
        self.search_results.display()  # 刷新显示搜索结果
    
    # 进行键绑定
    def handle_input(self, key):
        if key in [ord('q'), ord('Q')]:
            sys.exit(0)
        else:
            super().handle_input(key)

# 定义指令内容选项框
class InstructSelect(npyscreen.MultiLineAction):
    def actionHighlighted(self, act_on_this, keypress):
        instruct_form = self.parent
        selected_option = act_on_this.split()[1] 
        instruct_form.selected_option = selected_option
        self.parent.parentApp.switchForm("DETAIL")

# 指令内容选项表单
class InstructForm(npyscreen.FormBaseNew):
    def create(self):
        self.add(npyscreen.FixedText, value="You can press button to choose the details. Press 'q' to exit, 'z' to rollback.", editable=False, color="CAUTION", rely=1, relx=2)
        self.viewbrief_box = self.add(npyscreen.FixedText, value=[], editable=False,rely=2,relx=4)
        self.instruct_box = self.add(InstructSelect, name="InstrSelect", values=[], editable=True, hidden=False, scroll_exit=True, slow_scroll=True, exit_left=True, exit_right=False, rely=4)
        self.selected_id = None
        self.selected_name = None
        self.selected_option = None
        
    
    def beforeEditing(self):
        if self.selected_name:
            extra = InstExtraDao().SelectById(int(self.selected_id))
            titles = [info.title.lower().replace(' ', '_') for info in extra]

            # 用序号替换选项前面的名称
            options = ["description", "synopsis", "example", "option"] + titles
            self.instruct_box.values = [f"[{i + 1}] {option}" for i, option in enumerate(options)]
            
            self.viewbrief_box.value = self.get_viewbrief(self.selected_id)
        else:
            self.instruct_box.values = []
            self.viewbrief_box.value = "The instruction brief not found"

    def get_viewbrief(self, ins_id):
        inst_dao = InstDao()
        inst = inst_dao.SelectById(int(ins_id))
        if ins_id:
            brief = inst.brief
        return brief

    def while_waiting(self):
        self.handle_input()

    def handle_input(self, key=None):
        if key is None:
            key = self.getch()  # 使用 getch() 来获取键盘输入
        if key in [ord('q'), ord('Q')]:
            sys.exit(0)  # 直接退出应用
        elif key in [ord('z'), ord('Z')]:
            self.parentApp.switchForm('MAIN')  # 回退到 SearchForm


# 定义详情框
class Detail(npyscreen.BoxTitle):
    _contained_widget = npyscreen.MultiLine

# 详情表单
class DetailForm(npyscreen.FormBaseNew):
    def create(self):
        self.add(npyscreen.FixedText, value="Press 'q' to exit, 'z' to rollback. 'j' to Go Down, 'k' to Go Up, 'l' to Find", editable=False, color="CAUTION", rely=1, relx=2)
        self.detail_box = self.add(Detail, name="Detail", editable=True, hidden=False, scroll_exit=True, slow_scroll=True, exit_left=True, exit_right=False)
        self.selected_id = None
        self.selected_option = None

    # 详情表单处理逻辑
    def beforeEditing(self):
        instruct_form = self.parentApp.getForm('INSTRUCT')
        selected_option = instruct_form.selected_option
        if instruct_form.selected_id and selected_option:
            details = self.get_details(instruct_form.selected_id, selected_option)
            if not details:  # 如果 details 为空
                self.detail_box.values = ["The instruction has no options"]
            else:
                details_with_indents = self.add_indents(details)
                wrapped_details = self.wrap_text(details_with_indents, self.detail_box.width - 3)
                self.detail_box.values = wrapped_details
        else:
            self.detail_box.values = ["No details available"]

    def get_details(self, ins_id, option):
        option = option.lower()
        inst_extra_dao = InstExtraDao() 
        extraInfo = inst_extra_dao.SelectById(int(ins_id))
        data = {info.title.lower().replace(' ', '_'):info.text for info in extraInfo}
        if option in ["description", "synopsis","example", "option"]:
            inst_dao = InstDao()  # 确保实例化了 InstDao
            inst = inst_dao.SelectById(int(ins_id))
            if option == "description":
                details = inst.description
            elif option == "synopsis":
                details = inst.synopsis
            elif option == "example":
                details = inst.example
            elif option == "option":
                optDao = OptDao().SelectById(ins_id)
                details = '\n'.join([f"<Opt {o.content}>" for o in optDao])
        elif option in data.keys():
            details = data[option]
        else:
            details = "Invalid option"

        return details

    def add_indents(self, text):
        lines = text.split('\n')
        modified_lines = []
        for i in range(len(lines) - 1):
            if lines[i + 1].strip() == '':
                modified_lines.append(f"  {lines[i]}")
            else:
                modified_lines.append(lines[i])
        if lines:
            # 检查最后一行前面是否有空行
            if len(lines) > 1 and lines[-2].strip() == '':
                modified_lines.append(f"  {lines[-1]}")
            else:
                modified_lines.append(lines[-1])  # 添加最后一行
        return '\n' + '\n'.join(modified_lines)

    def wrap_text(self, text, width):
        lines = text.split('\n')
        wrapped_lines = []
        for line in lines:
            wrapped_lines.extend(wrap(line, width))
        return wrapped_lines

    def while_waiting(self):
        self.handle_input()

    def handle_input(self, key=None):
        if key is None:
            key = self.getch()  # 使用 getch() 来获取键盘输入
        if key in [ord('q'), ord('Q')]:
            sys.exit(0)  # 直接退出应用
        elif key in [ord('z'), ord('Z')]:
            self.parentApp.switchForm('INSTRUCT')  # 回退到 InstructForm

class SearchApp(npyscreen.NPSAppManaged):
    def onStart(self):
        self.addForm('MAIN', SearchForm, name='EulerTutor')
        self.addForm('DETAIL', DetailForm)
        self.addForm('INSTRUCT', InstructForm)

# 启动函数
def defuisearch():
    app = SearchApp()
    app.run()
