import os
import git
import shutil
from files3 import files
from git.cmd import Git
from git.exc import InvalidGitRepositoryError
from stcube.core import *
import tempfile

url = "https://gitee.com/eagle-s_baby/stcube_libmos"


def is_subpath(a, b):
    """
    判断 a 是否是 b 的子路径
    """
    # 规范化路径，消除路径中的 '.' 和 '..'
    a = os.path.normpath(a)
    b = os.path.normpath(b)

    # 将路径分割成部分
    a_parts = a.split(os.sep)
    b_parts = b.split(os.sep)

    # 检查 a 的路径部分是否是 b 的前缀
    return a_parts[:len(b_parts)] == b_parts


class _ULGitRepoBase:
    URL_REPO = {}

    @classmethod
    def save(cls):
        HOME_F._GIT_REPO = cls.URL_REPO

    @classmethod
    def load(cls):
        if HOME_F.has('_GIT_REPO'):
            cls.URL_REPO = HOME_F._GIT_REPO

    @staticmethod
    def available(repo_url:str):
        try:
            # 使用 GitPython 执行 git ls-remote 命令
            git = Git()
            output = git.execute(['git', 'ls-remote', repo_url])

            # 如果命令执行成功，输出将包含仓库信息
            print("Success check url. " if setting.language == 'en' else "repo url验证通过。")
            return True

        except Exception as e:
            # 如果命令执行失败，打印错误信息
            print(f"Failed check url: {e}" if setting.language == 'en' else f"repo url验证失败: {e}")
            return False

    @staticmethod
    def different(repo: git.Repo, branch:str=None) -> bool:
        """
        检查仓库是否有不同
        * print diff
        """
        local_branch = repo.active_branch if branch is None else repo.branches[branch]
        remote_branch = local_branch.tracking_branch()

        if remote_branch is None:
            print(f"no remote branch for {local_branch}")
            return False

        diff = repo.git.diff(f"{remote_branch.name}..{local_branch.name}")
        if diff:
            print(diff)
            return True
        else:
            print("no diff")
            return False


class ULGitRepo(_ULGitRepoBase):
    """
    用于连接到适用于STCube
    """
    _FIRST = True

    def __init__(self, target_url, u: bool = False, specific_dir: str = None):
        """
        :param target_url: 仓库地址
        :param u: 是否更新
        """
        self.target_url = target_url
        self._need_update_flag = False

        if self.__class__._FIRST:
            self.load()
            self.__class__._FIRST = False

        self.initial(specific_dir, u)

    def initial(self, custom_dir: str = None, u: bool = False):
        if not u and self.target_url in self.URL_REPO and os.path.exists(self.URL_REPO[self.target_url]) and (custom_dir is None or custom_dir == self.URL_REPO[self.target_url]):
            self.repo_dir = self.URL_REPO[self.target_url]
            self.repo = git.Repo(self.repo_dir)
        else:
            self.repo_dir = tempfile.mkdtemp() if custom_dir is None else custom_dir
            self.repo = git.Repo.clone_from(self.target_url, self.repo_dir)
            self.URL_REPO[self.target_url] = self.repo_dir
            self.save()

    def add(self, *files):
        new_paths = []
        files = [os.path.abspath(f) for f in files]
        for f in files:
            fnametype = os.path.basename(f)
            repo_this = os.path.join(self.repo_dir, fnametype)
            if not is_subpath(f, self.repo_dir):
                if os.path.isdir(f):
                    if not os.path.exists(repo_this):
                        shutil.copytree(f, repo_this)
                elif os.path.isfile(f):
                    if not os.path.exists(repo_this):
                        shutil.copy(f, repo_this)
                else:
                    print(f"file {f} not found")
                    continue
            new_paths.append(repo_this)
        if not new_paths:
            return
        self.repo.index.add(new_paths)
        self._need_update_flag = True

    def push(self, info="user update"):
        if not self._need_update_flag:
            return
        self.repo.index.commit(info)
        remote = self.repo.remote('origin')
        remote.push('master')

    def clone(self, target_dir):
        shutil.copytree(self.repo_dir, target_dir)

    def __repl__(self):
        return f"STCubeModuleRepo({self.target_url})|{self.repo_dir}"

    def __str__(self):
        txt = f"STCubeModuleRepo:\n  url:   {self.target_url}\n  local: {self.repo_dir}\n  files:\n"
        for file in self:
            txt += f"    {file}\n"

        return txt + '\n'

    def __iter__(self):
        return iter(os.listdir(self.repo_dir))


class STCubeModuleRepo(ULGitRepo):
    pass


class FRepo(Functional):
    key = "r|repo"
    doc_zh = """
    * 只适用于用于STCUBE的仓库
    * 只能管理体积较小的MODS(不能管理Library)
    > 用于同步你的'MODS'到指定url的仓库
    > 可以访问他人的仓库，将其克隆到本地
        .exp: 打开本地仓库管理文件夹
        # ----------- 您的仓库 -------------
        .url: 设置你的上传同步git仓库地址
        .push: 手动上传MODS更新到仓库
        .pull: 手动拉取同步到本地
        # ----------- 他人的仓库 ------------
        .index: 打开访问索引文件，此文件告诉STCUBE需要访问哪些仓库
        .visit: 根据索引文件访问本地仓库，可以选择你所需的MODS并克隆到本地
    """
    doc = """
    * Only for the repository used for STCUBE
    * Can only manage small MODS (cannot manage Library)
    > Synchronize your 'MODS' to the repository with the specified url
    > You can access other people's repositories and clone them locally
        .exp: Open the local repository management folder
        # ----------- Your repository -------------
        .url: Set the address of your upload synchronization git repository
        .push: Manually upload MODS updates to the repository
        .pull: Manually pull synchronization to local
        # ----------- Other people's repositories ------------
        .index: Open the access index file, which tells STCUBE which repositories to access
        .visit: Access the local repository according to the index file, and you can select the MODS you need and clone them locally    
    """

    def loading(self):
        self.url = None if not HOME_F.has('REPO_URL') else HOME_F.REPO_URL

        if not os.path.exists(REPO_DIR):
            os.makedirs(REPO_DIR)

        if self.url:
            if not os.path.exists(LOCAL_REPO):
                self.local_repo = STCubeModuleRepo(url, specific_dir=LOCAL_REPO)
            else:
                self.local_repo = STCubeModuleRepo(url)
        else:
            self.local_repo = None

        # INDEX_FILE
        if not os.path.exists(INDEX_PATH):
            with open(INDEX_PATH, 'w') as f:
                f.write('# STCUBE REPO INDEX\n# Each line is a url of a repo\n')


    def exp(self):
        os.startfile(REPO_DIR)

    def url(self):
        self.url = input('input url: ' if setting.language == 'en' else '输入url: ')
        # check url available
        if ULGitRepo.available(self.url):
            HOME_F.REPO_URL = self.url
            self.local_repo = STCubeModuleRepo(self.url)
        else:
            print("cancel for invalid url" if setting.language == 'en' else "无效的url，操作取消")

    def push(self):
        self.local_repo.push()

if __name__ == '__main__':
    fr = FRepo(None)
    fr.loading()
    repo = git.Repo(LOCAL_REPO)
    print(ULGitRepo.different(repo))
