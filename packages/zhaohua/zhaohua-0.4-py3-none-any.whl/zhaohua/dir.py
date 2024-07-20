#########################################################################################################
# 选择文件夹 get_dir()
# 功能：弹出窗口，让用户选择文件夹；返回一个文件夹路径。
#########################################################################################################

import tkinter as tk
from tkinter import filedialog
import os

def get_dir():
    # 功能：弹出窗口，让用户选择文件夹；返回一个完整的文件夹路径。
    # 创建一个隐藏的主窗口
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    # 设置初始目录为桌面路径
    initialdir = os.path.join(os.path.expanduser("~"), "Desktop")

    # 弹出文件夹选择对话框，增加提示信息
    folder_selected = filedialog.askdirectory(
        initialdir=initialdir,  # 设置初始目录为桌面路径
        title="请选择一个文件夹"  # 对话框标题
    )

    # 确保路径以斜杠结尾并将反斜杠替换为正斜杠
    if folder_selected:
        folder_selected = folder_selected.replace("\\", "/")
        if not folder_selected.endswith("/"):
            folder_selected += "/"

    # 返回选择的文件夹完整路径
    return folder_selected

# 示例调用 dir = get_dir()




#########################################################################################################
# 选择一个文件 get_file_path()
# 功能：弹出窗口，让用户选择一个文件路径；返回一个完整的文件夹路径:完整文件夹路径+文件名+后缀。
#########################################################################################################

import tkinter as tk
from tkinter import filedialog
import os

def get_file_path():
    # 创建一个隐藏的主窗口
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口

    # 设置初始目录为桌面路径
    initialdir = os.path.join(os.path.expanduser("~"), "Desktop")

    # 打开文件选择对话框
    file_path = filedialog.askopenfilename(
        title="请选择一个文件",  # 对话框标题
        initialdir=initialdir,  # 设置初始目录为桌面路径
        defaultextension="*.*",  # 默认扩展名
        filetypes=(
            ("所有文件", "*.*"),
            ("文本文件", "*.txt"),
            ("PDF文件", "*.pdf"),
            ("Python文件", "*.py"),
            ("Word文件", "*.docx *.doc *.dot *.dotx"),
            ("Excel文件", "*.xlsx *.xls *.xlsm *.xlsb *.xltx *.xltm *.xlt"),
            ("PowerPoint文件", "*.pptx *.ppt *.pptm *.potx *.potm *.pot"),
            ("图像文件", "*.jpg *.jpeg *.png *.bmp *.gif *.webp *.tif *.tiff"),
            ("视频文件", "*.mp4 *.mkv *.avi *.rmvb *.wmv *.ts *.mpg *.mpeg *.rm *.ram *.mov *.flv *.swf"),
            ("音频文件", "*.mp3 *.wav *.wma *.ape *.flac *.ogg *.aac"),
            ("压缩文件", "*.zip *.rar *.7z *.tar.gz")
        )  # 文件过滤器
    )

    # 返回选择的文件完整路径
    return file_path


# 调用函数并打印返回的文件路径 file_path = get_file_path()
# 调用函数并打印返回的文件路径








#########################################################################################################

# 遍历文件夹和子文件夹的所有文件 get_all_file_path
# 两个参数，第一个参数为文件夹路径，第二个可变参数为可选。可选参数限制文件的后缀，如".doc",".docx"，也可以直接"word","excel","ppt"
# 功能：遍历文件夹和子文件夹下的所有文件；将每一个文件的完整路径分为四个部分：文件夹路径+子文件夹路径+文件名+后缀。
# 将一个完整路径分四部分写入一个列表，然后将所有列表写入一个二维列表。
# 示例调用 paths = get_all_file_path(dir,"word",".pdf")，返回一个二维数组

#########################################################################################################

import os


def get_all_file_path(get_dir, *suffixes):
    # 检查 get_dir 是否为空值
    if not get_dir:
        return []

    all_files = []

    # 将传入的路径转换为标准格式，确保以 / 结尾
    get_dir = os.path.normpath(get_dir).replace("\\", "/") + "/"

    # 定义文件类型后缀
    suffix_dict = {
        "word": [".doc", ".docx", ".docm", ".dot", ".dotx"],
        "excel": [".xls", ".xlsx", ".xlsm", ".xlsb", ".xlt", ".xltm", ".xltx"],
        "ppt": [".ppt", ".pptx", ".pptm", ".pot", ".potm", ".potx"]
    }

    # 扩展传入的后缀列表
    expanded_suffixes = set()
    for suffix in suffixes:
        if suffix in suffix_dict:
            expanded_suffixes.update(suffix_dict[suffix])
        else:
            expanded_suffixes.add(suffix)

    for root, dirs, files in os.walk(get_dir):
        for file in files:
            file_name, file_ext = os.path.splitext(file)
            if not suffixes or file_ext in expanded_suffixes:
                # 构建文件的完整路径
                relative_path = os.path.relpath(root, get_dir).replace("\\", "/")
                if relative_path == ".":
                    relative_path = ""
                else:
                    relative_path += "/"
                path_parts = [get_dir, relative_path, file_name, file_ext]
                all_files.append(path_parts)

    return all_files


# 示例调用 paths = get_file_path(dir, "word", "ppt", ".pdf")，返回一个二维数组







#########################################################################################################
# 选择文件的保存路径 get_save_file_path
# 弹出一个对话框，选择文件要保存的路径和文件名，返回保存文件的完整路径:完整文件夹路径+文件名+后缀。
#########################################################################################################

import tkinter as tk
from tkinter.filedialog import asksaveasfilename
import os

def get_save_file_path():
    # 创建一个隐藏的主窗口
    root = tk.Tk()
    root.withdraw()

    # 设置初始目录为桌面路径
    initialdir = os.path.join(os.path.expanduser("~"), "Desktop")

    # 打开保存文件对话框
    file_name = asksaveasfilename(
        title="请选择要保存的文件位置！",  # 对话框标题
        initialdir=initialdir,  # 设置初始目录为桌面路径
        defaultextension="*.*",  # 默认扩展名
        filetypes = (
            ("所有文件", "*.*"),
            ("文本文件", "*.txt"),
            ("PDF文件", "*.pdf"),
            ("Python文件", "*.py"),
            ("Word文件", "*.docx *.doc *.dot *.dotx"),
            ("Excel文件", "*.xlsx *.xls *.xlsm *.xlsb *.xltx *.xltm *.xlt"),
            ("PowerPoint文件", "*.pptx *.ppt *.pptm *.potx *.potm *.pot"),
            ("图像文件", "*.jpg *.jpeg *.png *.bmp *.gif *.webp *.tif *.tiff"),
            ("视频文件", "*.mp4 *.mkv *.avi *.rmvb *.wmv *.ts *.mpg *.mpeg *.rm *.ram *.mov *.flv *.swf"),
            ("音频文件", "*.mp3 *.wav *.wma *.ape *.flac *.ogg *.aac"),
            ("压缩文件", "*.zip *.rar *.7z *.tar.gz")
        )  # 文件过滤器
    )

    # 返回选择的文件名
    return file_name

# 调用函数并打印返回的文件名 file_path = get_save_file_path()
