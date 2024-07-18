from ffre import FileFinder
from stcube._pyqt_pack import UISupport
import colorama
import files3
import atexit
import sys
import os

VERSION = '0.1.1'


HOME_DIR = os.path.expanduser("~")
DESKTOP_DIR = os.path.join(HOME_DIR, "Desktop")
HOME_DIR = os.path.join(HOME_DIR, ".stcube")
if not os.path.exists(HOME_DIR):
    os.makedirs(HOME_DIR)
LIBS_DIR = os.path.join(HOME_DIR, "libs")
MODS_DIR = os.path.join(HOME_DIR, "mods")
# REPOS
REPO_DIR = os.path.join(HOME_DIR, "repos")
LOCAL_REPO = os.path.join(REPO_DIR, ".local")
INDEX_PATH = os.path.join(REPO_DIR, "index.txt")

HOME_F = files3.files(HOME_DIR)

def reinsert_indent(text, keep_raw:bool=False, *, indent:str=None, strip:str=None) -> str:
    """
    Reinsert the indent of each line.
    :param text: str. The text to reinsert the indent.
    :param keep_raw: bool. Keep the raw indent of the each line. / If False, strip each line
    *
    :param indent: str. The indent to reinsert. Default is \t.
    :param strip: str. The characters to strip from the start of each line. Default is " \t".
    :return: str. The text with the indent reinserted.
    """
    if indent is None:
        indent = "\t"
    if strip is None:
        strip = " \t"

    lines = [line for line in text.split("\n") if line]
    if not lines:
        return text

    if not keep_raw:
        lines = [line.lstrip(strip) for line in lines]

    return "\n".join(indent + line for line in lines)

def str_table(heads:list, *values:tuple[list]):
    """
    str a table.
    :param heads:
    :param values:
    :return:
    """
    # 计算每列的最大宽度, 以此作为每列的宽度
    ## 不足的部分用空格填充，最后再加上一个\t
    _length = len(heads)

    for value in values:
        assert len(value) == _length, f"str_table: The length of value is not equal to the length of heads."

    tables = [heads] + list(values)
    # 转置
    _T = list(zip(*tables))

    _widths = [max(len(str(item)) for item in col) for col in _T]

    _lines = []
    # print heads
    _head_line = ""
    for i, head in enumerate(heads):
        _head_line += head + ' ' * (_widths[i] - len(head)) + '\t'
    _lines.append(_head_line)

    # --------------------- 行
    _sep_line = ""
    for width in _widths:
        _sep_line += '-' * width + '----'
    _lines.append(_sep_line)

    # print values
    for value in values:
        _line = ""
        for i, v in enumerate(value):
            _line += v + ' ' * (_widths[i] - len(v)) + '\t'
        _lines.append(_line)

    return '\n'.join(_lines)




class Setting:
    def __init__(self):
        self.data = {}

        self.load()

    def save(self):
        HOME_F.stcube = self.data

    def load(self):
        if HOME_F.has('stcube'):
            self.data = HOME_F.stcube

        if 'language' not in self.data:
            self.data['language'] = 'en'

    def list(self) -> list[tuple[str, str]]:
        """
        获取所有的设置项和值
        :return: list[(str, str)]
        """
        return list(self.data.items())

    @property
    def language(self):
        return self.data['language']

    @language.setter
    def language(self, value):
        assert value in ('en', 'zh'), f"Setting.language: Language '{value}' is not supported."
        self.data['language'] = value
        self.save()

setting = Setting()
# setting.language = 'zh'



class Functional:
    key = 'undefined'
    doc = None
    doc_zh = None
    sys = ['loading', 'key', 'doc', 'doc_zh']
    def __init__(self, ce):
        self.ce = ce

    def loading(self):
        """
        This function is called when the functional is loading.
        * Used in child class.
        :return:
        """
        pass

    def __call__(self):
        print("This is System Functionalities. Used for test.")

    def __str__(self):
        _doc = self.doc if self.doc is not None else ''
        return f"{self.__class__.__name__}({self.key}): \n{_doc}"

UISP = UISupport()


class FSetting(Functional):
    key = 's|set|setting'
    doc = """
    Setting the STCube command executor.
    .en: Set the language to English.
    .zh: Set the language to Chinese.
    """
    doc_zh = """
    设置STCube命令执行器。
    .en: 设置语言为英文。
    .zh: 设置语言为中文。
    """
    def __call__(self):
        values = setting.list()
        _k_t_v = []
        for k, v in values:
            _v = str(v) if not isinstance(v, str) else f"'{v}'"
            _k_t_v.append([k, type(v).__name__, _v])

        print(str_table(['Setting', 'Type', 'Value'], *_k_t_v))

    def zh(self):
        setting.language = 'zh'
        print("设置语言为中文。")

    def en(self):
        setting.language = 'en'
        print("Set language to English.")


class FQuit(Functional):
    key = 'q|quit'
    doc = """
    Quit the STCube command executor.
    """
    doc_zh = """
    退出STCube命令执行器。
    """
    def test(self):
        print("This is the test function.")

    def __call__(self):
        global UISP
        del UISP
        UISP = None
        exit()

class FHelp(Functional):
    key = 'h|help'
    doc = """
    Show the help information.
    .x: Show the help information of x.
    """
    doc_zh = """
    显示帮助信息。
    .x: 显示x的帮助信息。
    """
    def __call__(self):
        print(self.ce.gen_help())

    def __getattr__(self, item):
        if item.startswith('__'):
            print(f"Cannot access the private command '{item}'." if setting.language == 'en' else f"无法访问私有命令'{item}'。")
            return lambda : None
        _f = self.ce.get(item, expand=True)
        if _f is None:
            print(f"Command '{item}' not found." if setting.language == 'en' else f"命令'{item}'未找到。")
            return lambda : None
        _help = _f.doc if setting.language == 'en' else _f.doc_zh
        _help = _help if _help is not None else ('This functional has no doc.' if setting.language == 'en' else '此功能没有文档。')
        _help = reinsert_indent(_help, keep_raw=True, indent="\t")
        return lambda : print(_help)

class CommandExecutor:
    SPLITTER = '| '
    def __init__(self):
        self._current:str = None
        self.functionals = {}
        self.add(FQuit, FHelp, FSetting)

    @property
    def current(self):
        return self._current

    @current.setter
    def current(self, value):
        HOME_F.last = value
        self._current = value


    def __expand(self) -> dict[str, Functional]:
        _functionals = {}
        for key, functional in self.functionals.items():
            keys = self.split(key, self.SPLITTER)
            for _key in keys:
                assert _key not in _functionals, (
                    f"{self.__class__.__name__}.execute: Command '{_key}' is already exists."
                    if setting.language == 'en' else
                    f"{self.__class__.__name__}.execute: (遇到重复的命令)命令'{_key}'已经存在。"
                )
                _functionals[_key] = functional
        return _functionals

    @staticmethod
    def split(command: str, spliters) -> list:
        commands = [command]
        for sp in spliters:

            _removes, _appends = [], []

            for command in commands:
                _splits = command.split(sp)

                # strip
                for item in _splits:
                    _striped = item.strip()
                    if _striped:
                        _appends.append(_striped)

                if len(_appends) > 1:
                    _removes.append(command)

            for remove in _removes:
                commands.remove(remove)

            commands.extend(_appends)

        # 移除重复项并且保留顺序
        _commands = []
        for command in commands:
            if command not in _commands:
                _commands.append(command)

        return _commands


    def get(self, key:str|Functional, default=None, expand:bool=False):
        try:
            is_sub_class = issubclass(key, Functional)
        except TypeError:
            is_sub_class = False
        if is_sub_class:
            key = key.key
        elif expand:
            _functionals = self.__expand()
            return _functionals.get(key, default)

        return self.functionals.get(key, default)

    def add(self, *functionals:Functional):
        for functional in functionals:
            # Functional类的子类，但不能是实例
            if isinstance(functional, type) and issubclass(functional, Functional):
                self.functionals[functional.key] = functional(self)
            else:
                raise TypeError(f"{self.__class__.__name__}.add: Functional must be subclass of Functional. Not {type(functional)}") \
                    if setting.language == 'en' else (
                    TypeError(f"{self.__class__.__name__}.add: 传入参数必须是Functional的子类。而不是{type(functional)}"))

    def remove(self, *keys:str):
        for key in keys:
            if key in self.functionals:
                del self.functionals[key]

    def gen_help(self) -> str:
        """
        生成用于在cmd中显示的帮助信息
        :return:
        """
        help_info = ""
        for key, functional in self.functionals.items():
            _doc = functional.doc if setting.language == 'en' else functional.doc_zh
            _doc = _doc if _doc is not None else ('This functional has no doc.' if setting.language == 'en' else '此功能没有文档。')
            _doc = reinsert_indent(_doc, keep_raw=True, indent="\t")
            help_info += f"\t-{key}: \n{_doc}\n"
        return help_info

    def __call__(self):
        # loading for each functional
        for fal in self.functionals.values():
            fal.loading()

        # expand the functionals
        _functionals = self.__expand()

        _help = self.gen_help()

        print(colorama.Fore.CYAN, end='')
        print(
            "      -------------------------------------------------------------------")


        print(
            f"                       STCube Command Executor v{VERSION}"
            if setting.language == 'en' else
            f"                          STCube命令执行器 v{VERSION}"
        )
        print(
            "      -------------------------------------------------------------------")
        print(colorama.Style.RESET_ALL, end='')

        while True:
            if self.current is not None:
                print(f"[{self.current}:]", end=' ')
            acommands = self.split(input(">>> "), spliters='.')
            if not acommands or not acommands[0]:
                continue
            main_key = acommands[0]
            sub_keys = acommands[1:]

            if main_key not in _functionals:
                print(f"Command '{main_key}' not found."
                      if setting.language == 'en' else
                      f"命令'{main_key}'未找到。")
                print(_help)
                print(f"You used an uncorrect command:'{main_key}'. Please read help doc, and try again."
                      if setting.language == 'en' else
                      f"您使用了一个不正确的命令:'{main_key}'。请阅读帮助文档，然后再试一次。")
                continue

            _functional = _functionals[main_key]
            if sub_keys:
                for i, skey in enumerate(sub_keys):
                    if skey.startswith('__'):
                        print(
                            f"Cannot access the private command '{main_key}.{skey}'."
                            if setting.language == 'en' else
                            f"无法访问私有命令'{main_key}.{skey}'。"
                        )
                        _functional = None
                        break

                    _sys = getattr(_functional, 'sys', [])
                    if skey in _sys:
                        print(
                            f"Command '{main_key}.{skey}' is system command. Restricted."
                            if setting.language == 'en' else
                            f"命令'{main_key}.{skey}'是系统命令。受限制。"
                        )
                        _functional = None
                        break
                    _functional = getattr(_functional, skey, None)
                    if _functional is None:
                        _links = ".".join(sub_keys[:i+1])
                        print(f"Command '{main_key}.{_links}' not found."
                              if setting.language == 'en' else
                              f"命令'{main_key}.{_links}'未找到。")
                        print(_help)
                        print(f"You used an uncorrect command:'{main_key}.{_links}'. Please read help doc, and try again."
                              if setting.language == 'en' else
                              f"您使用了一个不正确的命令:'{main_key}.{_links}'。请阅读帮助文档，然后再试一次。")
                        break
                if _functional is None:
                    continue

            _functional()


if __name__ == '__main__':
    ce = CommandExecutor()
    ce()  # start the command executor


