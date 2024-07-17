from stcube.core import *
import colorama
class BaseSTCubeIOC:
    def __init__(self, fpath):
        self.fpath = fpath
        if not os.path.exists(self.fpath):
            raise FileNotFoundError(f"Can not find the file '{self.fpath}'.")
        with open(self.fpath, 'r') as f:
            self._ioc = f.read()
            self._len, self._unparsed, self._data = self.__parse_ioc(self._ioc)

        self.loading()

    def loading(self):
        pass

    @staticmethod
    def __parse_ioc(txt) -> tuple[int, dict, dict]:
        _cnt = 0
        _res = {}
        _unparsed = {}
        _lines = [line.strip() for line in txt.split('\n') if line.strip()]
        for i, line in enumerate(_lines):
            _cnt += 1
            if '=' not in line:
                _unparsed[i] = line
                continue

            _pos = line.index('=')
            left, right = line[:_pos].strip(), line[_pos+1:].strip()
            _res[left] = right
        return _cnt, _unparsed, _res
    @property
    def ioc(self):
        return self._ioc

    @property
    def data(self):
        return self._data

    @property
    def unparsed(self):
        return self._unparsed

    def rebuild(self) -> str:
        _lines = []

        i = 0
        upit, dait = iter(self._unparsed.items()), iter(self._data.items())
        unparse_index, unparse_line = next(upit, (None, None))
        while True:
            while unparse_index is not None and i >= unparse_index:
                _lines.append(unparse_line)
                unparse_index, unparse_line = next(upit, (None, None))
                i += 1

            data_key, data_value = next(dait, (None, None))
            if data_key is not None:
                _lines.append(f"{data_key} = {data_value}")
                i += 1

            if unparse_index is None and data_key is None:
                break
        return '\n'.join(_lines)


    def save(self, fpath=None):
        if fpath is None:
            fpath = self.fpath
        with open(fpath, 'w') as f:
            f.write(self.rebuild())

    def __str__(self):
        return f"STCubeIOC: from r'{self.fpath}'"

    def __len__(self):
        return self._len


class STCubeIOC(BaseSTCubeIOC):
    BUILD_MXVERSION = ('6', '10', '0')  # checked version
    def loading(self):
        versions = CommandExecutor.split(self.version, '.')
        if len(versions) <= 1:
            versions = versions + ('0', '0')
        # 主版本差异超过1，产生警告
        if versions[0] != self.BUILD_MXVERSION[0]:
            print(
                colorama.Fore.YELLOW +
                f"Warning: The main version of STM32CubeMX IOC is '{versions[0]}', but the version of 'stcube' is '{self.BUILD_MXVERSION[0]}'.\n\tThis may led to some exceptions."
                + colorama.Style.RESET_ALL
            )

        # 获取几个主要属性，要确保这些属性存在
        if self.project_name is None:
            raise ValueError(f"Can not find the 'ProjectManager.ProjectName' in the file '{self.fpath}'.")
        if self.project_file_name is None:
            raise ValueError(f"Can not find the 'ProjectManager.ProjectFileName' in the file '{self.fpath}'.")
        if self.mcu_name is None:
            raise ValueError(f"Can not find the 'Mcu.Name' in the file '{self.fpath}'.")
        # if self.no_main is None:
        #     raise ValueError(f"Can not find the 'ProjectManager.NoMain' in the file '{self.fpath}'.")
        # if self.couple_file is None:
        #     raise ValueError(f"Can not find the 'ProjectManager.CoupleFile' in the file '{self.fpath}'.")
        if self.main_location is None:
            raise ValueError(f"Can not find the 'ProjectManager.MainLocation' in the file '{self.fpath}'.")




    @property
    def project_name(self):
        return self._data.get('ProjectManager.ProjectName', None)

    @project_name.setter
    def project_name(self, value):
        self._data['ProjectManager.ProjectName'] = value

    @property
    def project_file_name(self):
        return self._data.get('ProjectManager.ProjectFileName', None)

    @project_file_name.setter
    def project_file_name(self, value):
        self._data['ProjectManager.ProjectFileName'] = value

    @property
    def mcu_name(self):
        return self._data.get('Mcu.Name', None)

    @mcu_name.setter
    def mcu_name(self, value):
        self._data['Mcu.Name'] = value

    @property
    def version(self):
        return self._data.get('MxCube.Version', None)

    @version.setter
    def version(self, value):
        self._data['MxCube.Version'] = value

    @property
    def no_main(self):
        return self._data.get('ProjectManager.NoMain', None)

    @no_main.setter
    def no_main(self, value):
        self._data['ProjectManager.NoMain'] = value

    @property
    def couple_file(self):
        return self._data.get('ProjectManager.CoupleFile', None)

    @couple_file.setter
    def couple_file(self, value):
        self._data['ProjectManager.CoupleFile'] = value

    @property
    def main_location(self):
        return self._data.get('ProjectManager.MainLocation', None)


    def save(self, fpath=None):
        if fpath is None:
            fpath = self.fpath
        with open(fpath, 'w') as f:
            f.write(self.rebuild())


    def __str__(self):
        return f"STCubeIOC<{self.mcu_name}>: from r'{self.fpath}'"


if __name__ == '__main__':
    path = r"C:\Users\22290\Desktop\H743II\STCubePRoject.ioc"
    st_ioc = STCubeIOC(path)

    print(st_ioc.ioc)
    print('--------------------------------')
    for k,v in st_ioc.data.items():
        print(k, '=', v)

    st_ioc.save(r"C:\Users\22290\Desktop\H743II\STCubePRoject2.ioc")

