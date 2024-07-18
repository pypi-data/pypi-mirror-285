from stcube.core import *
import re

"""
MEMORY
{
  FLASH (rx)     : ORIGIN = 0x08000000, LENGTH = 2048K
  DTCMRAM (xrw)  : ORIGIN = 0x20000000, LENGTH = 128K
  RAM_D1 (xrw)   : ORIGIN = 0x24000000, LENGTH = 512K
  RAM_D2 (xrw)   : ORIGIN = 0x30000000, LENGTH = 288K
  RAM_D3 (xrw)   : ORIGIN = 0x38000000, LENGTH = 64K
  ITCMRAM (xrw)  : ORIGIN = 0x00000000, LENGTH = 64K
}
"""
MEMORY_PAT = re.compile(r"MEMORY[^}]+}")
LINE_LENGTH_PAT = re.compile(r"LENGTH\s*=\s(\d+K)")


class STCubeld:
    def __init__(self, fpath):
        self.fpath = fpath
        if not os.path.exists(self.fpath):
            raise FileNotFoundError(f"Can not find the file '{self.fpath}'.")
        with open(self.fpath, 'r') as f:
            self._ld = f.read()
            self._flash, self._ram = self.__parse_ld(self._ld)

        self.loading()

    def loading(self):
        pass

    @staticmethod
    def __parse_ld(txt) -> tuple[int|None, int|None]:
        _m = MEMORY_PAT.search(txt)

        if not _m:
            return None, None

        _lines = [line.strip() for line in _m.group().split('\n') if 'LENGTH' in line]
        _flash, _ram = 0, 0
        for _l in _lines:
            _l = _l.upper()
            if 'RAM' in _l:
                _m = LINE_LENGTH_PAT.search(_l)
                if _m:
                    _ = _m.group(1)
                    _ = _.replace('K', '000').replace('M', '000000')
                    _ram += int(_) if _.isdigit() else 0
            elif 'FLASH' in _l:
                _m = LINE_LENGTH_PAT.search(_l)
                if _m:
                    _ = _m.group(1)
                    _ = _.replace('K', '000').replace('M', '000000')
                    _flash += int(_) if _.isdigit() else 0


        return _flash, _ram

    @property
    def flash(self):
        return self._flash

    @property
    def ram(self):
        return self._ram


    def __repr__(self):
        return f"STCubeld({self.fpath})"

    def __str__(self):
        return f"STCubeld({self.fpath}): \n\tFlash: {self.flash} \n\tRAM: {self.ram}"


if __name__ == '__main__':

    path = r"C:\Users\22290\Desktop\H743II\STM32H743IITX_FLASH.ld"
    ld = STCubeld(path)

    print(ld)




