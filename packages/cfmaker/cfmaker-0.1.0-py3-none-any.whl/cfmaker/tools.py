#coding:utf-8
import codecs
from typing import List, Set, Optional
import os
from pathlib import Path

# 尝试的编码列表
ENCODINGS = [
    'utf-8', 'gbk', 'gb2312', 'utf-16', 'utf-16le', 'utf-16be', 'latin-1',
    'iso-8859-1'
]


def is_str_not_empty(s):
  return s is not None and isinstance(s, str) and s.strip()

def is_str_empty(s):  
    return s is None or (isinstance(s, str) and not s.strip())
def find_oneapi_home_by_path(path: str):
  n = len(Path(path).parts)
  for i in range(n):
    dirName = os.path.basename(path).lower()
    if dirName == "oneapi" or "compilers_and_libraries" in dirName:
      return path
    path = os.path.dirname(path)
  return None


def find_folder(root_path, target_folder):
  # 递归搜索函数
  # 检查当前路径下是否有'mpi'文件夹
  mpi_folder = root_path / target_folder
  if mpi_folder.is_dir():
    return mpi_folder.absolute()

  # 递归遍历指定的子文件夹
  for subdir_name in ['latest', 'intel64', 'linux', 'windows']:
    subdir_path = root_path / subdir_name
    if subdir_path.is_dir():
      result = find_folder(subdir_path, target_folder)
      if result:
        return result
  # 如果没有找到，返回None
  return None


def find_file(root_path, target_file):
  # 递归搜索函数
  # 检查当前路径下是否有'mpi'文件夹
  file_path = root_path / target_file
  if file_path.is_file():
    return file_path.absolute()

  # 递归遍历指定的子文件夹
  for subdir_name in ['latest', 'intel64', 'linux', 'windows', 'mpi']:
    subdir_path = root_path / subdir_name
    if subdir_path.is_dir():
      result = find_file(subdir_path, target_file)
      if result:
        return result
  # 如果没有找到，返回None
  return None


def find_oneapi_mpi_by_home(oneapi_path: Path):
  lib_dirs = []
  include_dirs = []
  lib_path = None
  #找到mpi路径
  mpi_path = find_folder(oneapi_path, 'mpi')
  if mpi_path is None:
    return None
  lib_folder = find_folder(mpi_path, 'lib')
  if lib_folder is not None:
    libname = 'libmpifort.a'
    if os.name == 'nt':
      libname = 'impi.lib'
    lib_path = find_file(lib_folder, libname)
    if lib_path is not None:
      lib_dirs.append(lib_path.parent)

  include_folder = find_folder(mpi_path, 'include')
  if include_folder is not None:
    name = 'mpif.h'
    fpath = find_file(include_folder, name)
    if fpath is not None:
      include_dirs.append(fpath.parent)
    name = 'mpi.mod'
    fpath = find_file(include_folder, name)
    if fpath is not None:
      include_dirs.append(fpath.parent)

  return lib_dirs, include_dirs, lib_path

def find_oneapi_mkl_by_home(oneapi_path: Path):
  lib_dirs = []
  include_dirs = []
  #找到mpi路径
  mpi_path = find_folder(oneapi_path, 'mkl')
  if mpi_path is None:
    return None
  lib_folder = find_folder(mpi_path, 'lib')
  if lib_folder is not None:
    libname = 'libmkl_core.a'
    if os.name == 'nt':
      libname = 'mkl_core.lib'
    lib_path = find_file(lib_folder, libname)
    if lib_path is not None:
      lib_dirs.append(lib_path.parent)

  include_folder = find_folder(mpi_path, 'include')
  if include_folder is not None:
    name = 'mkl.h'
    fpath = find_file(include_folder, name)
    if fpath is not None:
      include_dirs.append(fpath.parent)

  return lib_dirs, include_dirs

def merge_path_dirs(dest: List[str], source: List[str]):
  dd = [Path(p) for p in dest]
  ss = [Path(p) for p in source]
  for p in ss:
    if p not in dd:
      dd.append(p)
  return [str(p) for p in dd]
  
def read_lines_safe(file_path: str):
  for encoding in ENCODINGS:
    try:
      with codecs.open(file_path, 'r', encoding=encoding) as file:
        return file.readlines()
    except UnicodeDecodeError:
      continue
  raise UnicodeDecodeError(
      f"Could not decode file {file_path} with any of the provided encodings.")


def f_get_depend_in_line(text: str, depend_modules: Set[str],
                       file_modules: Set[str]):
  #text = "use module1  , module2  , onlyme ,nnonly   , module3,   only :  subroutine1, variable1"
  text = text.strip().lower()
  # 检查是否以 'use ' 开头并包含 ' only:'
  if text.startswith('use '):
    # 去掉 'use ' 前缀
    text = text[4:]
    # 分割 'only:' 前后的部分
    list = text.split(',')
    for name in list:
      if 'only' in name or 'intrinsic' in name:
        tmp = name.split(':')[0]
        if tmp.strip() == 'only' or tmp.strip() == 'intrinsic':
          break
        else:
          depend_modules.add(name.strip())
      elif name != '':
        depend_modules.add(name.strip())
    #print(depend_modules)  # 输出: ['module1', 'module2', 'module3']
  elif text.startswith('module ') or text.startswith('program '):
    module_name = text.split(' ')[1]
    file_modules.add(module_name)
    
def f_parse_dependencies(file_path):
  lines = read_lines_safe(file_path)
  dependencies = set()
  modules = set()
  for line in lines:
    f_get_depend_in_line(line, dependencies, modules)
  return dependencies, modules

def gen_flag(flag, content, split=' ', ispath=False, isList=False) -> str:
  if isList:
    if ispath:
      return " ".join([f"{flag}{split}\"{dir}\"" for dir in content])
    else:
      return " ".join([f"{flag}{split}{dir}" for dir in content])
  else:
    if ispath:
      return f"{flag}{split}\"{content}\""
    else:
      return f"{flag}{split}{content}"

if __name__ == '__main__':
  a = Path('impi.lib')
  
  dirs = merge_path_dirs(['C:\\Program Files (x86)/Intel\\oneAPI/mpi/latest/include',
                   'C:/Program Files (x86)/Intel/oneAPI/mpi/latest/include/mpi',
                   'C:/Program Files (x86)/Intel/oneAPI/mpi'
],
                  ['C:/Program Files (x86)\\Intel/oneAPI/mpi/latest/include',
                   'C:/Program Files (x86)/Intel/oneAPI/mpi/latest/include/mpi\\',
                   'C:/Program Files (x86)/Intel/oneAPI'
])
  print(dirs)