import os.path

from stcube.core import *
from stcube._pyqt_pack import *
from stcube._ds_ioc import STCubeIOC
from stcube._ds_ld import STCubeld
import colorama
import datetime
import zipfile
import shutil


def zip_folder(folder_path, output_path):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                zipf.write(file_path, os.path.relpath(file_path, folder_path))

def unzip_folder(zip_path, output_path):
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(output_path)

class Library(Functional):
    key = 'l|lib'
    doc = """
    Library management.
        - Library is made from stm32cube project directory.
        - Need gen codes first in cubemx
    .new: Create a new library from the stm32cube project directory.
    .exp: Open the library directory in the explorer.
    """
    doc_zh = """
    库管理模块, 展示当前的库列表.
        - 库是由STM32Cube项目目录创建的。
        - 需要在CubeMX中先生成代码
    .new: 从STM32Cube项目目录创建新库。
    .exp: 在资源管理器中打开库目录。
    """
    sys = Functional.sys + ['libs', 'is_ioc_dir']
    def loading(self):
        # check LIBS_DIR
        if not os.path.exists(LIBS_DIR):
            os.makedirs(LIBS_DIR)

    def libs(self) -> list[dict]:
        ff = FileFinder(LIBS_DIR)
        fc = ff.find('.zip', '.ZIP', pattern='STCUBE_.*')

        _res = []
        _infos = HOME_F.LIBS_INFO if HOME_F.has('LIBS_INFO') else {}
        for fpath in fc:
            fname = os.path.splitext(os.path.basename(fpath))[0]
            last_change_time = os.path.getmtime(fpath)
            if fname in _infos:
                _info = _infos[fname]
                _res.append({
                    'name': fname,
                    'path': fpath,
                    'mcu': _info['mcu'],
                    'flash': _info['flash'],
                    'ram': _info['ram'],
                    'time': datetime.datetime.fromtimestamp(last_change_time).strftime("%Y-%m-%d %H:%M:%S")
                })
            else:
                _res.append({
                    'name': fname,
                    'path': fpath,
                    'mcu': 'Unknown',
                    'flash': 'Unknown',
                    'ram': 'Unknown',
                    'time': datetime.datetime.fromtimestamp(last_change_time).strftime("%Y-%m-%d %H:%M:%S")
                })
        return _res

    @staticmethod
    def _ut_is_cube_mx_project(dir):
        """
        Check if the directory is a STM32Cube project directory.
        :param dir:
        :return:
        """
        # Check ioc in it
        _fnames = os.listdir(dir)
        _has_ioc = any([fname.endswith('.ioc') for fname in _fnames])
        if not _has_ioc:
            print(
                f"Can not find the .ioc file in the directory '{dir}'."
                if setting.language == 'en' else
                f"在目录 '{dir}' 中找不到 .ioc 文件。"
            )
            QPop(RbpopError, "'New' Failed:", "Can not find the .ioc file in the directory."
                 if setting.language == 'en' else
                 "在目录中找不到 .ioc 文件。")
        # Check .mxproject .project .cproject in it
        _has_flash_ld = any([fname.upper().endswith("_FLASH.LD") for fname in _fnames])
        if not _has_flash_ld:
            print(f"Can not find the *_FLASH.ld file in the directory '{dir}'."
                  if setting.language == 'en' else
                  f"在目录 '{dir}' 中找不到 *_FLASH.ld 文件。")
            print(f"Ignore as a non-stm32cubeide project."
                  if setting.language == 'en' else
                  f"忽略，因为可能不是STM32CubeIDE项目。")
            # QPop(RbpopError, "'New' Failed:", "Can not find the *_FLASH.ld file in the directory."
            #       if setting.language == 'en' else
            #       "在目录中找不到 *_FLASH.ld 文件。")
        # check Core directory
        _core_dir = os.path.join(dir, 'Core')
        if not os.path.exists(_core_dir):
            print(f"Can not find the 'Core' directory in the directory '{dir}'."
                  if setting.language == 'en' else
                  f"在目录 '{dir}' 中找不到 'Core' 目录。")
            print(f"Please save & gen codes in STM32CubeMX first."
                  if setting.language == 'en' else
                  f"请先在STM32CubeMX中保存并生成代码。")
            QPop(RbpopError, "'New' Failed:", "Can not find the 'Core' directory in the directory."
                  if setting.language == 'en' else
                  "在目录中找不到 'Core' 目录。")

        return _has_ioc and os.path.exists(_core_dir)

    def new(self):
        # Select stm32cube project directory
        # always at front
        print("Please select the STM32Cube project directory. In the dialog:"
              if setting.language == 'en' else
              "请在对话框中选择STM32Cube项目目录：")

        dir = QFileDialog.getExistingDirectory(None, 'Select STM32Cube Project Directory' if setting.language == 'en' else '选择STM32Cube项目目录',
                                               DESKTOP_DIR, QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks)

        if not dir:
            print("User canceled the operation."
                  if setting.language == 'en' else
                  "用户取消了操作。")
            return

        if not self._ut_is_cube_mx_project(dir):
            print(f'New lib stopped due to the previous errores.'
                  if setting.language == 'en' else
                  f'由于之前的错误，新建库的操作已终止。')
            return

        print(
            colorama.Fore.GREEN +
            (f"selecte: '{dir}'." if setting.language == 'en' else f"选择路径: '{dir}'.")
            + colorama.Style.RESET_ALL
        )

        # get the last directory name
        _dir = os.path.basename(dir)

        # check if the lib is already exists
        _tar_path = os.path.join(LIBS_DIR, f'STCUBE_{_dir}.zip')
        if os.path.exists(_tar_path):
            print(f"Library 'STCUBE_{_dir}' is already exists. Will move old into 'backups'."
                  if setting.language == 'en' else
                  f"库 'STCUBE_{_dir}' 已经存在。将会把旧的库移动到 'backups' 中。")

            # create backup dir
            _backup_dir = os.path.join(LIBS_DIR, 'backups')
            if not os.path.exists(_backup_dir):
                os.makedirs(_backup_dir)

            # backup the old lib
            last_change_time = os.path.getmtime(_tar_path)
            _backup_path = os.path.join(_backup_dir, f'backup_STCUBE_{_dir}_before_{datetime.datetime.fromtimestamp(last_change_time).strftime("%Y-%m-%d_%H-%M-%S")}.zip')
            shutil.move(_tar_path, _backup_path)

        # NOTE: Add info and save.

        # find ioc
        ff = FileFinder(dir)
        fc = list(ff.find('.ioc', pattern='.*'))
        if len(fc) > 1:
            print(
                colorama.Fore.YELLOW +
                (f"Find {len(fc)} .ioc files in the directory '{dir}'. Will use the first '{os.path.basename(fc[0])}'."
                 if setting.language == 'en' else
                 f"在目录 '{dir}' 中找到 {len(fc)} 个 .ioc 文件。将会使用第一个 '{os.path.basename(fc[0])}'。")
                + colorama.Style.RESET_ALL
            )
        ioc = STCubeIOC(fc[0])
        # find ld
        fc = list(ff.find('.ld', pattern='.*_[fF][lL][aA][sS][hH]'))
        if len(fc) > 1:
            print(
                colorama.Fore.YELLOW +
                (f"Find {len(fc)}_FLASH.ld files in the directory '{dir}'. Will use the first '{os.path.basename(fc[0])}'."
                 if setting.language == 'en' else
                 f"在目录 '{dir}' 中找到 {len(fc)} 个 *_FLASH.ld 文件。将会使用第一个 '{os.path.basename(fc[0])}'。")
                + colorama.Style.RESET_ALL
            )
        ld = STCubeld(fc[0]) if len(fc) > 0 else None

        mcu_name = ioc.mcu_name
        flash = f"{ld.flash // 1000}K" if ld else 'Unknown'
        ram = f"{ld.ram // 1000}K" if ld else 'Unknown'

        if not HOME_F.has('LIBS_INFO'):
            HOME_F.LIBS_INFO = {}
        _infos:dict = HOME_F.LIBS_INFO
        _infos[f'STCUBE_{_dir}'] = {
            'mcu': mcu_name,
            'flash': flash,
            'ram': ram
        }
        HOME_F.LIBS_INFO = _infos

        # zip the project directory
        print(f"Creating library 'STCUBE_{_dir}'<MCU:{mcu_name}, FLASH:{flash}, RAM:{ram}> from the directory '{dir}', please wait..."
              if setting.language == 'en' else
              f"正在从目录 '{dir}' 创建库 'STCUBE_{_dir}'<MCU:{mcu_name}, FLASH:{flash}, RAM:{ram}>，请稍等...")
        zip_folder(dir, _tar_path)
        print(f"Library 'STCUBE_{_dir}' is created."
              if setting.language == 'en' else
              f"库 'STCUBE_{_dir}' 创建完成。")

    def exp(self):
        """
        open liv dir in explore
        :return:
        """
        os.system(f'explorer {LIBS_DIR}')

    def __call__(self):
        """
        list libs
        :return:
        """
        _libs = self.libs()
        if _libs:
            print(colorama.Fore.BLUE + f"STCube Libraries:{colorama.Fore.RESET}"
                  if setting.language == 'en' else
                  colorama.Fore.BLUE + f"STCube 库列表:{colorama.Fore.RESET}")
            heads = ['Lib Name', 'MCU Type', 'Flash', 'RAM', 'Change Time'] \
                    if setting.language == 'en' else \
                    ['库名称', '芯片型号', 'Flash', 'RAM', '修改时间']
            values = []
            for lib in _libs:
                # print(f"{lib['name'][:30]}\t{lib['mcu']}\t{lib['flash']}\t{lib['ram']}\t{lib['time']}")
                values.append([lib['name'], lib['mcu'], lib['flash'], lib['ram'], lib['time']])
            print(str_table(heads, *values))

        else:
            print(f"No libraries found."
                  if setting.language == 'en' else
                  f"未找到任何库(use lib.new to create one)。")
