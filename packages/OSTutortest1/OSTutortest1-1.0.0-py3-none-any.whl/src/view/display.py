# import curses
from wcwidth import wcwidth

def display(stdscr, lines):
    # stdscr是curses库中的一个特殊窗口对象,代表整个屏幕区域
    # 获取终端的高度和宽度
    height, width = stdscr.getmaxyx()

    # -----分行显示-----
    now_page = 0
    lines_num_once = height - 4  # 留出两空行、一行显示页码、一行显示提示

    # 根据终端宽度进行换行处理，防止显示结果越界
    split_line_list = []
    for line in lines:
        split_line_list.extend(split_line(line, width))

    total_pages = (len(split_line_list) + lines_num_once - 1) // lines_num_once

    while True:
        stdscr.clear()
        stdscr.addstr(0, 0, "---Press 'q' to exit, 's' for next page, 'w' for previous page---")

        # 计算当前页面应该显示的行范围
        start_line = now_page * lines_num_once
        # end_line = min(start_line + lines_num_once, len(split_line_list)) # 行数较少则直接显示（可不用）
        end_line = start_line + lines_num_once

        # 显示当前页面的内容
        # enumerate--自动创建索引
        for idx, line in enumerate(split_line_list[start_line:end_line], start=2):
            stdscr.addstr(idx, 0, line)

        # 显示当前页码
        stdscr.addstr(height - 1, 0, f"---Page {now_page + 1} of {total_pages}---")
        stdscr.refresh()

        # 界面操作
        key = stdscr.getch()
        if key == ord('q'):
            break
        elif key == ord('s') and now_page < total_pages - 1:
            now_page += 1
        elif key == ord('w') and now_page > 0:
            now_page -= 1

# 考虑到一般显示结果不会过长，处理较快
# 尝试过使用textwrap，发现会有部分显示bug
# 所以没有选择现成的换行函数“textwrap.wrap”，自建函数进行分割，提高程序健壮性
def split_line(line, width):
    split_line_list = []
    current_line = ""
    current_width = 0

    for char in line:
        # wcwidth--获取当前字符的显示宽度
        char_width = wcwidth(char)
        if current_width + char_width > width:  # 如果加上当前字符会超过终端宽度
            split_line_list.append(current_line)  # 将当前行添加到结果列表
            current_line = char  # 重新开始一行
            current_width = char_width
        else:
            current_line += char
            current_width += char_width

    if current_line:  # 存在最后一行，也放入结果列表
        split_line_list.append(current_line)

    return split_line_list + [" "]
