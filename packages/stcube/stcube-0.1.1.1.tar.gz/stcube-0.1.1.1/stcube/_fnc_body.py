import os.path

from stcube.core import *
from stcube._fnc_library import Library, unzip_folder
from stcube._fnc_modules import Module
from stcube._pyqt_pack import *
import time
import sys



class FNew(Functional):
    key = 'n|new'
    doc = """
    Create a new Project from Library.
    Add new module to the current project.
    """
    doc_zh = """
    使用库创建一个新项目。
    向当前项目添加新模块。
    """
    sys = Functional.sys + ['library', 'get_wizard_info', "get_module_select"]
    def loading(self):
        library = self.ce.get(Library)
        modules = self.ce.get(Module)
        update = self.ce.get(FUpdate)
        if not library:
            raise Exception("\n\nSystem Error: \n\tComponent<Library> not found. "
                            if setting.language == 'en' else
                            "\n\n系统错误: \n\t组件<Library>未找到。")
        if not modules:
            raise Exception("\n\nSystem Error: \n\tComponent<Module> not found. "
                            if setting.language == 'en' else
                            "\n\n系统错误: \n\t组件<Module>未找到。")
        if not update:
            raise Exception("\n\nSystem Error: \n\tComponent<FUpdate> not found. "
                            if setting.language == 'en' else
                            "\n\n系统错误: \n\t组件<FUpdate>未找到。")
        self.library = library
        self.modules = modules
        self.update = update

    def get_wizard_info(self) -> tuple[str, str, str]:
        """
        UI
        title: 'New Project Wizard'
            'Input project name:'
            [       Edit                        ]
            'Select a directory:'   btn[...]
            [       ReadOnly Edit               ]
            'Select a library:'
            [       Select Edit                 ]  # lib['name'], lib['mcu'], lib['flash'], lib['ram'], lib['time']
            btn['Create']            btn['Cancel']

        :return:
        """
        libs:list[dict] = self.library.libs()
        if not libs:
            print("No library found."
                  if setting.language == 'en' else
                  "未找到任何库。")
            return
        lib_names = [f"{lib['name']} ({lib['mcu']}, FLASH={lib['flash']}, RAM={lib['ram']})" for lib in libs]

        _DEFAULT_DIR = DESKTOP_DIR
        _DEFAULT_PNAME = 'untitled'
        if os.path.exists(os.path.join(_DEFAULT_DIR, _DEFAULT_PNAME)):
            i = 1
            while os.path.exists(os.path.join(_DEFAULT_DIR, f"{_DEFAULT_PNAME}{i}")):
                i += 1
            _DEFAULT_PNAME = f"{_DEFAULT_PNAME}{i}"

        # UI
        app = UISP.app
        win = MyQWidget()
        win.setFixedHeight(440)
        win.setFixedWidth(720)
        win.setWindowTitle('New Project Wizard'
                           if setting.language == 'en' else
                           '新项目向导')
        layout = QVBoxLayout()
        win.setLayout(layout)
        # Input project name
        layout.addWidget(QLabel('Input project name:'
                                if setting.language == 'en' else
                                '输入项目名称:'))
        pname_edit = QLineEdit()
        pname_edit.setText(_DEFAULT_PNAME)
        pname_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        def _auto_default_name():
            if not pname_edit.text():
                pname_edit.setText(_DEFAULT_PNAME)
        pname_edit.textChanged.connect(_auto_default_name)
        pname_edit.setStyleSheet('font-size: 20px; color: #242430;')
        layout.addWidget(pname_edit)

        # Select a directory
        hline = QHBoxLayout()
        layout.addLayout(hline)
        hline.addWidget(QLabel('Select a directory:'
                               if setting.language == 'en' else
                               '选择一个目录:'))
        dir_edit = QLineEdit()
        dir_edit.setText(_DEFAULT_DIR)
        dir_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        def _auto_default_dir():
            if not dir_edit.text():
                dir_edit.setText(_DEFAULT_DIR)
        dir_edit.textChanged.connect(_auto_default_dir)
        dir_edit.setStyleSheet('font-size: 20px; color: #242430;')
        def select_dir():
            dir = QFileDialog.getExistingDirectory(win, 'Select Project Directory:' if setting.language == 'en' else '选择项目目录:',
                                                   DESKTOP_DIR)
            dir_edit.setText(dir)
        btn = QPushButton('...')
        btn.setFixedWidth(80)
        btn.clicked.connect(select_dir)
        hline.addWidget(btn)
        layout.addWidget(dir_edit)

        # Select a library
        layout.addWidget(QLabel('Select a library:'
                                if setting.language == 'en' else
                                '选择一个库:'))
        lib_box = QComboBox()
        lib_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        lib_box.setStyleSheet('font-size: 20px; color: #242430;')
        lib_box.setEditable(True)
        for i, lib_name in enumerate(lib_names):
            lib_box.addItem(lib_name)
            lib_box.setItemData(i, libs[i])
        layout.addWidget(lib_box)
        _change_lock = [False]
        def _on_text_change(*a):
            if _change_lock[0]:
                return
            _change_lock[0] = True
            # search the lib
            _new = []
            _ctxt = lib_box.currentText()
            for i, lib_name in enumerate(lib_names):
                if _ctxt in lib_name:
                    _new.append(libs[i])
            _new_names = [f"{lib['name']} ({lib['mcu']}, FLASH={lib['flash']}, RAM={lib['ram']})" for lib in _new]
            lib_box.clear()

            for i, lib in enumerate(_new):
                lib_box.addItem(lib_name)
                lib_box.setItemData(i, lib)

            if not _new:
                # set red fore
                lib_box.setStyleSheet('color: red; font-size: 20px;')

                _change_lock[0] = False
                return
            lib_box.setStyleSheet('font-size: 20px; color: #242430;')

            if _ctxt not in _new_names:
                lib_box.setStyleSheet('color: #CA884400; font-size: 20px;')


            lib_box.setCurrentText(_ctxt)

            _change_lock[0] = False

        lib_box.editTextChanged.connect(_on_text_change)
        _res = [False, None, None, None]  # Flag, pname, dir, lib

        # Buttons
        def create():
            pname = pname_edit.text()
            dir = dir_edit.text()
            lib_key = lib_box.currentText()
            if not pname or not dir or not lib_key:
                print('Please input all the information.'
                      if setting.language == 'en' else
                      '请填写所有信息后重试。')
                QPop(RbpopWarn('Please input all the information.' if setting.language == 'en' else '请填写所有信息后重试。'
                               , 'Not enough inputs:'))
                return
            if not os.path.isdir(dir):
                print('Please select a valid directory.'
                      if setting.language == 'en' else
                      '请选择一个有效的目录。')
                QPop(RbpopWarn('Please select a valid directory.' if setting.language == 'en' else '请选择一个有效的目录。',
                               'Invalid directory:'))
                return
            # 判断name是否是合法文件夹名
            if not os.path.isdir(os.path.join(dir, pname)):
                # create the project directory
                try:
                    os.makedirs(os.path.join(dir, pname))
                except:
                    print('Please input a valid project name.'
                          if setting.language == 'en' else
                          '请输入一个有效的项目名称。')
                    QPop(RbpopWarn('Please input a valid project name.' if setting.language == 'en' else '请输入一个有效的项目名称。',
                                   'Invalid project name:'))
                    return
            else:
                select = QMessageBox.question(win, 'Warning:', f"Project '{pname}' already exists. Do you want to next?" if setting.language == 'en' else f"项目 '{pname}' 已经存在。是否继续？",
                                              QMessageBox.Yes | QMessageBox.No)
                if select == QMessageBox.No:
                    return
            if lib_key not in lib_names:
                print('Please select a valid library.'
                      if setting.language == 'en' else
                      '请选择一个有效的库。')
                QPop(RbpopWarn('Please select a valid library.' if setting.language == 'en' else '请选择一个有效的库。',
                               'Invalid library:'))
                return
            lib = lib_box.itemData(lib_names.index(lib_key) )
            _res[0] = True
            _res[1] = pname
            _res[2] = dir
            _res[3] = lib
            win.close()
        def cancel():
            _res[0] = True
            win.close()

        space = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addItem(space)
        hline = QHBoxLayout()
        layout.addLayout(hline)
        btn = QPushButton('Create')
        btn.clicked.connect(create)
        btn.setFixedHeight(60)
        hline.addWidget(btn)
        btn = QPushButton('Cancel')
        btn.clicked.connect(cancel)
        btn.setFixedHeight(60)
        hline.addWidget(btn)

        # 绑定快捷键 Enter和Esc
        def keyPressEvent(event):
            if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
                create()
            elif event.key() == Qt.Key_Escape:
                cancel()
        win.keyPressEvent = keyPressEvent

        # 大字体，consolas
        win.setStyleSheet("font-size: 25px; font-family: Consolas; color: #323648; ")
        # Label设为#643232
        for label in win.findChildren(QLabel):
            label.setStyleSheet('color: #645555; font-size: 20px;')
        win.on_delete = cancel
        win.show()

        while not _res[0]:
            app.processEvents()

        return _res[1:]


    def get_module_select(self) -> str:
        """
        UI
        title: 'Select Module'
            'Select a module:'                       |  'Description:'
            [       Select Edit                 ]    |  [
            ---------------separator-------------    |
            "Module author:"                         |                  TextEdit
            [       ReadOnly Edit               ]    |
            "Module brief:"                          |
            [       ReadOnly Edit               ]    |
            btn['Add']            btn['Cancel']      |                                          ]
        :return:
        """
        modules = self.modules.mods()
        if not modules:
            print("No module found."
                  if setting.language == 'en' else
                  "未找到任何模块。")
            return
        module_names = [f"{module['name']} ({module['author']})" for module in modules]

        # UI
        app = UISP.app
        win = MyQWidget()
        # 去掉最大变化、最小化及关闭按钮
        win.setWindowFlags(Qt.WindowCloseButtonHint|Qt.WindowStaysOnTopHint|Qt.WindowCloseButtonHint)
        win.setFixedHeight(440)
        win.setFixedWidth(720)
        win.setWindowTitle('Select Module'
                           if setting.language == 'en' else
                           '选择模块')
        layout = QHBoxLayout()
        win.setLayout(layout)
        left_layout = QVBoxLayout()
        right_layout = QVBoxLayout()
        layout.addLayout(left_layout)
        layout.addLayout(right_layout)
        # Select a module
        left_layout.addWidget(QLabel('Select a module:'
                                if setting.language == 'en' else
                                '选择一个模块:'))
        mod_box = QComboBox()
        mod_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        mod_box.setStyleSheet('font-size: 20px; color: #242430;')
        mod_box.setEditable(True)
        for i, mod_name in enumerate(module_names):
            mod_box.addItem(mod_name)
            mod_box.setItemData(i, modules[i])
        left_layout.addWidget(mod_box)
        # author
        left_layout.addWidget(QLabel('Module author:'
                                if setting.language == 'en' else
                                '模块作者:'))
        author_edit = QLineEdit()
        author_edit.setReadOnly(True)
        author_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        author_edit.setStyleSheet('font-size: 20px; color: #242430;')
        left_layout.addWidget(author_edit)
        # adjust
        cbtn = QCheckBox('Need Adjust' if setting.language == 'en' else '需要调整定义')
        # readonly
        cbtn.setDisabled(True)
        left_layout.addWidget(cbtn)

        # brief
        left_layout.addWidget(QLabel('Module brief:'
                                if setting.language == 'en' else
                                '模块简介:'))
        brief_edit = QTextEdit()
        brief_edit.setReadOnly(True)
        brief_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        brief_edit.setStyleSheet('font-size: 20px; color: #242430;')
        left_layout.addWidget(brief_edit)

        #description
        right_layout.addWidget(QLabel('Description:'
                                if setting.language == 'en' else
                                '描述:'))
        description_edit = QTextEdit()
        description_edit.setReadOnly(True)
        description_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        description_edit.setStyleSheet('font-size: 20px; color: #242430;')
        right_layout.addWidget(description_edit)

        def _on_mod_change():
            mod = mod_box.currentData()
            author_edit.setText(mod['author'])
            cbtn.setChecked(mod['adjust'])
            brief_edit.setText(mod['brief'])
            description_edit.setText(mod['desc'])

        mod_box.currentIndexChanged.connect(_on_mod_change)

        try:
            _on_mod_change()
        except:
            pass

        _res = [False, None]
        # Buttons
        def add():
            mod_key = mod_box.currentText()
            if mod_key not in module_names:
                print('Please select a valid module.'
                      if setting.language == 'en' else
                      '请选择一个有效的模块。')
                QPop(RbpopWarn('Please select a valid module.' if setting.language == 'en' else '请选择一个有效的模块.',
                               'Invalid module:'))
                return
            mod = mod_box.itemData(module_names.index(mod_key))
            _res[0] = True
            _res[1] = mod
            win.close()
        def cancel():
            _res[0] = True
            win.close()

        space = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Expanding)
        left_layout.addItem(space)
        hline = QHBoxLayout()
        left_layout.addLayout(hline)
        btn = QPushButton('Add')
        btn.clicked.connect(add)
        btn.setFixedHeight(60)
        hline.addWidget(btn)
        btn = QPushButton('Cancel')
        btn.clicked.connect(cancel)
        btn.setFixedHeight(60)
        hline.addWidget(btn)

        # 绑定快捷键 Enter和Esc
        def keyPressEvent(event):
            if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
                add()
            elif event.key() == Qt.Key_Escape:
                cancel()

        win.keyPressEvent = keyPressEvent

        # 大字体，consolas
        win.setStyleSheet("font-size: 25px; font-family: Consolas; color: #323648; ")
        # Label设为#643232
        for label in win.findChildren(QLabel):
            label.setStyleSheet('color: #645555; font-size: 20px;')

        win.on_delete = cancel
        win.show()

        while not _res[0]:
            app.processEvents()

        return _res[1]

    def __call__(self):
        if not self.ce.current:
            print('Please follow the wizard UI to create a new project:'
                  if setting.language == 'en' else
                  '请按照向导UI创建一个新项目：')
            pname, pdir, lib_select = self.get_wizard_info()
            if not pname:
                print('User canceled the operation.'
                      if setting.language == 'en' else
                      '用户取消了操作。')
                return
            unzip_dir = os.path.join(pdir, pname)
            # unzip the lib
            lib_path = lib_select['path']
            if not os.path.exists(lib_path):
                print(f"Non-exists library path: '{lib_path}'."
                      if setting.language == 'en' else
                      f"不存在的库路径: '{lib_path}'.")
                return
            print(f"Create project: from '{lib_select['name']}' to '{unzip_dir}', please wait..."
                  if setting.language == 'en' else
                  f"创建项目: 从 '{lib_select['name']}' 到 '{unzip_dir}'，请稍等...")
            unzip_folder(lib_path, unzip_dir)
            print(f'Set Current Project: {os.path.join(pdir, pname)}'
                  if setting.language == 'en' else
                  f'设置当前项目: {os.path.join(pdir, pname)}')
            self.ce.current = os.path.join(pdir, pname)
            print(f"Success create project: '{pname}'."
                  if setting.language == 'en' else
                  f"成功创建项目: '{pname}'.")
            self.update()
            # open explore into project dir
            os.system(f'explorer {os.path.join(pdir, pname)}')
        else:
            print('Please follow the wizard UI to add a new module to the current project:'
                  if setting.language == 'en' else
                  '请按照向导UI向当前项目添加一个新模块：')
            mod_select = self.get_module_select()
            if not mod_select:
                print('User canceled the operation.'
                      if setting.language == 'en' else
                      '用户取消了操作。')
                return
            mod_path = mod_select['path']
            if not os.path.exists(mod_path):
                print(f"Non-exists module path: '{mod_path}'."
                      if setting.language == 'en' else
                      f"不存在的模块路径: '{mod_path}'.")
                return
            print(f"Add module: '{mod_select['name']}' to '{self.ce.current}', please wait..."
                  if setting.language == 'en' else
                  f"添加模块: '{mod_select['name']}' 到 '{self.ce.current}'，请稍等...")
            unzip_folder(mod_path, self.ce.current)
            print(f"Success add module: '{mod_select['name']}' to '{self.ce.current}'."
                  if setting.language == 'en' else
                  f"成功添加模块: '{mod_select['name']}' 到 '{self.ce.current}'。")


class FOpen(Functional):
    key = 'o|cd|open'
    doc = """
    Change the current project directory.
        * will close the current project if has.
    """
    doc_zh = """
    更改当前的项目目录。
        * 如果有当前项目，将会关闭。
    """

    def loading(self):
        update = self.ce.get(FUpdate)
        if not update:
            raise Exception("\n\nSystem Error: \n\tComponent<FUpdate> not found. "
                            if setting.language == 'en' else
                            "\n\n系统错误: \n\t组件<FUpdate>未找到。")
        self.update = update

    @staticmethod
    def ask_open() -> str:
        # Ask for the directory
        dir = QFileDialog.getExistingDirectory(None, 'Select Project Directory:' if setting.language == 'en' else '选择项目目录:',
                                               DESKTOP_DIR)
        if not dir:
            print('User canceled the operation.'
                  if setting.language == 'en' else
                  '用户取消了操作。')
            return
        if not Library._ut_is_cube_mx_project(dir):
            print(f'Cd/Open stopped due to the previous errores.'
                  if setting.language == 'en' else
                  f'由于之前的错误，Cd/Open操作已终止。')
            return
        return dir

    def __call__(self):
        print('Please select the project directory in UI dialog: '
              if setting.language == 'en' else
              '请在UI对话框中选择项目目录：')
        dir = self.ask_open()
        if not dir:
            return
        print(f"Set Current Project: {dir}"
              if setting.language == 'en' else
              f"设置当前项目: {dir}")
        self.ce.current = dir
        self.update()

class FUpdate(Functional):
    key = 'u|up|update'
    doc = """
    Update the current project to create cpp Entrence.
        * won't action if the main.cpp already exists.
    """
    doc_zh = """
    更新当前项目以创建cpp入口。
        * 如果main.cpp已经存在，则不会执行。
    """

    KEY_SETUP_BEGIN = "/* USER CODE BEGIN 2 */"
    KEY_LOOP_BEGIN = "/* USER CODE BEGIN 3 */"
    DECLARE_BEGIN = "/* USER CODE BEGIN EFP */"

    DECLARE_SETUP = "void setup();"
    DECLARE_LOOP = "void loop();"

    NEW_FILE_CONTENT = "/// This file won't changed by STCube later.\n\n"
    NEW_FILE_CONTENT += 'extern "C" {\n'
    NEW_FILE_CONTENT += '// Include c headers\n'
    NEW_FILE_CONTENT += '\t#include "main.h"\n\n'
    NEW_FILE_CONTENT += '}\n\n'
    NEW_FILE_CONTENT += 'void setup()\n{\n\t\n'
    NEW_FILE_CONTENT += '}\n\n'
    NEW_FILE_CONTENT += 'void loop()\n{\n\t\n'
    NEW_FILE_CONTENT += '}\n\n'

    def find_mainc(self):
        # find the main.c
        ff = FileFinder(self.ce.current)
        fc = list(ff.find('.c', pattern='main'))
        if not fc:
            print('Cannot find the main.c file.'
                  if setting.language == 'en' else
                  '找不到main.c文件。')
            return
        return fc[0]

    def find_mainh(self):
        # find the main.h
        ff = FileFinder(self.ce.current)
        fc = list(ff.find('.h', pattern='main'))
        if not fc:
            print('Cannot find the main.h file.'
                  if setting.language == 'en' else
                  '找不到main.h文件。')
            return
        return fc[0]

    def find_maincpp(self):
        # find the main.cpp
        ff = FileFinder(self.ce.current)
        fc = list(ff.find('.cpp', pattern='main'))
        if not fc:
            print('Cannot find the main.cpp file.'
                  if setting.language == 'en' else
                  '找不到main.cpp文件。')
            return
        return fc[0]

    def new_maincpp(self, mainc:str, mainh:str):
        src_dir = os.path.dirname(mainc)
        maincpp = os.path.join(src_dir, 'main.cpp')
        if os.path.exists(maincpp):
            print('main.cpp already exists.'
                  if setting.language == 'en' else
                  'main.cpp已经存在。')
            return
        with open(maincpp, 'w') as f:
            f.write(self.NEW_FILE_CONTENT)
        print(f"Create new main.cpp: '{maincpp}'"
              if setting.language == 'en' else
              f"创建新的main.cpp: '{maincpp}'")

        # add the call in main.c
        with open(mainc, 'r') as f:
            txt = f.read()
        # add the setup() call
        _pos = txt.index(self.KEY_SETUP_BEGIN)
        if _pos == -1:
            print(f"Cannot find the key '{self.KEY_SETUP_BEGIN}' in the main.c."
                  if setting.language == 'en' else
                  f"在main.c中找不到关键字'{self.KEY_SETUP_BEGIN}'。")
            return
        _pos += len(self.KEY_SETUP_BEGIN)
        txt = txt[:_pos] + f'\n\tsetup();\n' + txt[_pos:]
        # add the loop() call
        _pos = txt.index(self.KEY_LOOP_BEGIN)
        if _pos == -1:
            print(f"Cannot find the key '{self.KEY_LOOP_BEGIN}' in the main.c."
                  if setting.language == 'en' else
                  f"在main.c中找不到关键字'{self.KEY_LOOP_BEGIN}'。")
            return
        _pos += len(self.KEY_LOOP_BEGIN)
        txt = txt[:_pos] + f'\n\tloop();\n' + txt[_pos:]
        with open(mainc, 'w') as f:
            f.write(txt)
        print(f"Add the setup() and loop() call in the main.c: '{mainc}'"
              if setting.language == 'en' else
              f"在main.c中添加setup()和loop()的调用: '{mainc}'")

        # add the declaration in main.h
        with open(mainh, 'r') as f:
            txt = f.read()
        _pos = txt.index(self.DECLARE_BEGIN)
        if _pos == -1:
            print(f"Cannot find the key '{self.DECLARE_BEGIN}' in the main.h."
                  if setting.language == 'en' else
                  f"在main.h中找不到关键字'{self.DECLARE_BEGIN}'。")
            return
        _pos += len(self.DECLARE_BEGIN)
        txt = txt[:_pos] + f'\n{self.DECLARE_SETUP}\n{self.DECLARE_LOOP}\n' + txt[_pos:]
        with open(mainh, 'w') as f:
            f.write(txt)
        print(f"Add the setup() and loop() declaration in the main.h: '{mainh}'"
              if setting.language == 'en' else
              f"在main.h中添加setup()和loop()的声明: '{mainh}'")



    def __call__(self):
        if not self.ce.current:
            print('No current project. Try to open a project ...'
                  if setting.language == 'en' else
                  '没有当前项目。尝试打开一个项目 ...')
            dir = FOpen.ask_open()
            if not dir:
                return
            self.ce.current = dir

        mainc = self.find_mainc()
        if not mainc:
            return

        mainh = self.find_mainh()
        if not mainh:
            return

        maincpp = self.find_maincpp()
        if not maincpp:
            print('No main.cpp found, create a new one.'
                  if setting.language == 'en' else
                  '没有找到main.cpp，尝试新建该文件。')
            self.new_maincpp(mainc, mainh)
            print('Update the current project success.'
                  if setting.language == 'en' else
                  '更新当前项目成功。')
            return

        print('No need to update the current project.'
              if setting.language == 'en' else
              '不需要更新当前项目。')

class FClose(Functional):
    key = 'c|close'
    doc = """
    Close the current project.
    """
    doc_zh = """
    关闭当前项目。
    """
    def __call__(self):
        self.ce.current = None
