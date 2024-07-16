#coding:utf-8
from typing import List, Set, Optional
import platform
import os
import shutil
from .tools import *
from pathlib import Path

class inner_flag_opt:
  def __init__(self, flag:str, sep:str='', ispath:bool=False, isList:bool=False):
    """  
        内置选项，用于重新定义编译的内置选项，如exe输出选项，include文件夹选项
  
        Args:  
            flag (str): 选项的字符串表示。  
            sep (str): 分隔符，默认为空字符串。  
            ispath (bool): 后面连接的是否表示路径，默认为False。  
            isList (bool): 后面连接的是否表示列表，默认为False。  
    """  
    self.flag = flag
    self.sep = sep
    self.ispath = ispath
    self.isList = isList
    
  def gen_flag(self, content: str | List[str] = '') -> str:
    if self.isList:
      if self.ispath:
        return " ".join([f"{self.flag}{self.sep}\"{dir}\"" for dir in content])
      else:
        return " ".join([f"{self.flag}{self.sep}{dir}" for dir in content])
    else:
      if self.ispath:
        return f"{self.flag}{self.sep}\"{content}\""
      else:
        return f"{self.flag}{self.sep}{content}"

class ProjectConfig:
  '''项目配置，支持intel oneapi fortran和cpp编译器
      支持fortran和c混合编程'''
  def __init__(self,
               f_srcs: Optional[List[str]] = ['src/**'],
               c_srcs: Optional[List[str]] = ['src/clib/**'],
               project_build_dir: Optional[str] = 'build',
               cf: Optional[str] = 'ifx',
               cc: Optional[str] = 'icx',
               lib_tool_linux: Optional[str] = 'ar',
               lib_tool_win: Optional[str] = 'lib',
               f_exe_name: Optional[str] = '',
               f_lib_name: Optional[str] = '',
               c_exe_name: Optional[str] = '',
               c_lib_name: Optional[str] = '',
               oneapi_home_win: Optional[str] = '',
               oneapi_home_linux: Optional[str] = '',
               linker: Optional[str] = '',
               fc_options_debug: Optional[str] = '',
               fc_options_release: Optional[str] = '',
               cc_options_debug: Optional[str] = '',
               cc_options_release: Optional[str] = '',
               linker_options: Optional[str] = '',
               include_dirs: Optional[List[str]] = [],
               lib_dirs: Optional[List[str]] = [],
               static_libraries: Optional[List[str]] = []):
    """
        初始化项目配置类，通过指定f_exe_name，c_exe_name，f_lib_name，c_lib_name来确定生成的类型
        其中同一个语言的exe和lib只能选一个，不支持两个同时生成
        
        Args: 
            f_srcs: Fortran源文件路径列表，默认为['src/**']
            c_srcs: C源文件路径列表，默认为['src/clib/**']
            project_build_dir: 项目构建目录，默认为'build'
            cf: Fortran编译器，默认为'ifx'（Intel Fortran编译器）
            cc: C编译器，默认为'icx'（Intel C/C++编译器）
            lib_tool_linux: Linux平台下的库工具，默认为'ar'
            lib_tool_win: Windows平台下的库工具，默认为'lib'
            f_exe_name: Fortran可执行文件名，默认为空字符串，不指定不会生成exe
            f_lib_name: Fortran生成的库文件名，默认为空字符串，不指定不会生成lib
            c_exe_name: C可执行文件名，默认为空字符串，不指定不会生成exe
            c_lib_name: C库文件名，默认为空字符串，不指定不会生成lib
            oneapi_home_win: Windows平台下Intel oneAPI安装路径，默认为空字符串
            oneapi_home_linux: Linux平台下Intel oneAPI安装路径，默认为空字符串
            linker: 链接器，默认为空字符串
            fc_options_debug: Fortran编译器调试模式下的选项，默认为空字符串
            fc_options_release: Fortran编译器发布模式下的选项，默认为空字符串
            cc_options_debug: C编译器调试模式下的选项，默认为空字符串
            cc_options_release: C编译器发布模式下的选项，默认为空字符串
            linker_options: 链接器选项，默认为空字符串
            include_dirs: 头文件包含目录列表，默认为空列表
            lib_dirs: 库文件目录列表，默认为空列表
            static_libraries: 静态库列表，默认为空列表
    """
    self.f_srcs = f_srcs
    self.c_srcs = c_srcs
    self.project_build_dir = project_build_dir
    self.fc = cf
    self.cc = cc
    self.lib_tool_linux = lib_tool_linux
    self.lib_tool_win = lib_tool_win
    self.lib_tool = self.lib_tool_win if os.name == 'nt' else self.lib_tool_linux
    self.oneapi_home_win = oneapi_home_win
    self.oneapi_home_linux = oneapi_home_linux
    self.oneapi_home = self.oneapi_home_win if os.name == 'nt' else self.oneapi_home_linux
    self.linker = linker
    self.fc_options_debug = fc_options_debug
    self.fc_options_release = fc_options_release
    self.cc_options_debug = cc_options_debug
    self.cc_options_release = cc_options_release
    self.linker_options = linker_options
    self.include_dirs = include_dirs
    self.lib_dirs = lib_dirs
    self.static_libraries = static_libraries
    self.f_exe_name = f_exe_name
    self.f_lib_name = f_lib_name
    self.c_exe_name = c_exe_name
    self.c_lib_name = c_lib_name
    
    '''内置fortran选项'''
    self.f_flag_include = inner_flag_opt('-I', '', ispath=True, isList=True) 
    self.f_flag_mod_path = inner_flag_opt('-module', ':', ispath=True, isList=False)
    self.f_flag_nolink = inner_flag_opt('-c')
    self.f_flag_silent = inner_flag_opt('-nologo')
    self.f_flag_obj = inner_flag_opt('-object', ':', ispath=True, isList=False)
    self.f_flag_exe = inner_flag_opt('-exe', ':', ispath=True, isList=False)
    
    '''内置c选项'''
    self.c_flag_include = inner_flag_opt('-I', '', ispath=True, isList=True)
    self.c_flag_nolink = inner_flag_opt('-c')
    self.c_flag_obj = inner_flag_opt('-Fo', '', ispath=True, isList=False)
    self.c_flag_exe = inner_flag_opt('-Fe', '', ispath=True, isList=False)
    
    if os.name == 'nt':
      self.lib_flag = inner_flag_opt('/OUT', ':', ispath=True, isList=False)
      self.link_flag_use = inner_flag_opt('/link')
      self.link_flag_lib_dir = inner_flag_opt('/libpath', ':', ispath=True, isList=True)
    else:
      self.lib_flag = inner_flag_opt('-crs', ' ', ispath=True, isList=False)
      self.link_flag_use = inner_flag_opt('')
      self.link_flag_lib_dir = inner_flag_opt('-L', '', ispath=True, isList=True)

  def auto_set_fc_options(self, version: str = '2024.2'):
    '''自动设置fortran编译选项，可能不对，目前只对2024.2，2023.2，2017三个版本正确'''
    if version == '2024.2':
      self.fc_options_debug = '-debug-parameters:all -Od -check:all -traceback -Qmkl:parallel -real-size:64 -fpp'
      self.fc_options_release = '-O3 -Qmkl:parallel -real-size:64 -fpp'
      self.f_flag_include = inner_flag_opt('-I', '', ispath=True, isList=True)
      self.f_flag_mod_path = inner_flag_opt('-module', ':', ispath=True, isList=False)
      self.f_flag_nolink = inner_flag_opt('-c')
      self.f_flag_silent = inner_flag_opt('-nologo')
      self.f_flag_obj = inner_flag_opt('-object', ':', ispath=True, isList=False)
      self.f_flag_exe = inner_flag_opt('-exe', ':', ispath=True, isList=False)
    elif version == '2023.2':
      self.fc_options_debug = '-g -D__debug__ -fpp -check all -traceback -warn interfaces -r8 -qmkl=parallel -standard-semantics -m64'
      self.fc_options_release = '-fpp -r8 -qmkl=parallel -standard-semantics -m64'
      self.f_flag_include = inner_flag_opt('-I', '', ispath=True, isList=True)
      self.f_flag_mod_path = inner_flag_opt('-module', ' ', ispath=True, isList=False)
      self.f_flag_nolink = inner_flag_opt('-c')
      self.f_flag_silent = inner_flag_opt('-nologo')
      self.f_flag_obj = inner_flag_opt('-Fo', '', ispath=True, isList=False)
      self.f_flag_exe = inner_flag_opt('-o', ' ', ispath=True, isList=False)
    else:
      self.fc_options_debug = '-g -fpp -check all -traceback -warn interfaces -r8 -mkl=parallel -standard-semantics -m64'
      self.fc_options_release = '-fpp -r8 -mkl=parallel -standard-semantics -m64'
      self.f_flag_include = inner_flag_opt('-I', '', ispath=True, isList=True)
      self.f_flag_mod_path = inner_flag_opt('-module', ' ', ispath=True, isList=False)
      self.f_flag_nolink = inner_flag_opt('-c')
      self.f_flag_silent = inner_flag_opt('-nologo')
      self.f_flag_obj = inner_flag_opt('-Fo', '', ispath=True, isList=False)
      self.f_flag_exe = inner_flag_opt('-o', ' ', ispath=True, isList=False)
      
  def auto_set_cc_options(self, version: str = '2024.2'):
    '''自动设置c编译选项，可能不对，只对2024.2，2023.2，2017三个版本正确'''
    if version == '2024.2':
      self.cc_options_debug = '-Zi -debug:full -Od'
      self.cc_options_release = '-O3'
    elif version == '2023.2':
      self.cc_options_debug = '-g -debug=full -Rno-debug-disables-optimization'
      self.cc_options_release = ''
    else:
      self.cc_options_debug = '-g -debug=full -Rno-debug-disables-optimization'
      self.cc_options_release = ''
      
  def get_oneapi_home(self):
    '''获取oneapi根目录'''
    if is_str_empty(self.oneapi_home):
      #利用编译器路径，从而获取oneapi的根目录
      if self.fc != '':
        if Path(self.fc).is_absolute():
          self.oneapi_home = find_oneapi_home_by_path(self.fc)
      if is_str_not_empty(self.oneapi_home):
        return
      
      if self.cc != '':
        if Path(self.cc).is_absolute():
          self.oneapi_home = find_oneapi_home_by_path(self.cc)
      if is_str_not_empty(self.oneapi_home):
        return    
      
      #利用命令行获取ifort路径，从而获取oneapi的根目录
      ifort_path = shutil.which('ifort')
      if ifort_path == '':
        return
      else:
        self.oneapi_home = find_oneapi_home_by_path(ifort_path)
      if is_str_not_empty(self.oneapi_home):
        return
  def auto_add_intel_mpi(self):
    '''自动添加mpi路径'''
    cf = Path(self.fc).stem
    if cf == 'mpiifort' or cf == 'mpiifx':
      print('温馨提示：使用mpiifort或mpiifx时不需要添加mpi路径')
      return
    self.get_oneapi_home()
    if is_str_empty(self.oneapi_home):
      print('没有找到intel编译器根目录，如要自动添加mpi，请先指定根目录')
      print('温馨提示：使用mpiifort或mpiifx时不需要添加mpi路径')
      return
    lib_dirs, include_dirs, lib_path = find_oneapi_mpi_by_home(Path(self.oneapi_home))
    if len(lib_dirs) == 0 or len(include_dirs) == 0:
      print('没有找到mpi路径，如用到mpi请手动填写include和lib路径，或者编译器使用mpiifort或mpiifx')
      return
    self.lib_dirs = merge_path_dirs(self.lib_dirs, lib_dirs)
    self.include_dirs = merge_path_dirs(self.include_dirs, include_dirs)
    self.static_libraries = merge_path_dirs(self.static_libraries, [lib_path])

  def auto_add_intel_mkl(self):
    '''自动添加mkl路径'''
    self.get_oneapi_home()
    if is_str_empty(self.oneapi_home):
      print('没有找到intel编译器根目录，如要自动添加mkl，请先指定根目录')
      print('温馨提示：使用mkl动态链接库时不需要添加mkl路径')
      return
    lib_dirs, include_dirs = find_oneapi_mkl_by_home(Path(self.oneapi_home))
    if len(lib_dirs) == 0 or len(include_dirs) == 0:
      print('没有找到mkl路径，如用到mkl静态链接库请手动填写，使用动态链接库这里可以不填')
      return
    self.lib_dirs = merge_path_dirs(self.lib_dirs, lib_dirs)
    self.include_dirs = merge_path_dirs(self.include_dirs, include_dirs)
    
if __name__ == '__main__':
  config = ProjectConfig()
  