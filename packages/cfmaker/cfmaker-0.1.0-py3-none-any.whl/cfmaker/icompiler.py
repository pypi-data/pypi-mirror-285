#coding:utf-8
import os
import subprocess
import sys
from typing import List, Optional
from .fconfig import ProjectConfig
from .tools import gen_flag, is_str_not_empty, is_str_empty, merge_path_dirs
from .file_manager import source_manager

class compile_manager:

  def __init__(self, config: ProjectConfig, target_type: Optional[str] = None) -> None:
    # 如果配置类有定义属性，则使用配置类中的属性，否则使用默认值
    self.config = config
    if is_str_empty(self.config.project_build_dir):
      print("project_build_dir is empty")
      sys.exit(1)
    self.config.project_build_dir = os.path.abspath(self.config.project_build_dir)
    
    self.need_update = 'update' in sys.argv
    
    if target_type is None:
      # 确保命令行参数的数量至少为2（脚本名和至少一个参数）
      if len(sys.argv) > 1:
        args = sys.argv[1:]
        if 'debug' in args:
          target_type = "debug"
        elif 'release' in args:
          target_type = "release"
        else:
          target_type = "debug"
      else:
        target_type = "debug"
        
    if target_type != "debug" and target_type != "release":
      print("target_type must be debug or release")
      sys.exit(1)
  
    # 现在target_type包含从命令行读取的编译类型或默认值
    self.target_type = target_type
    self.construct_dir()
    self.check_compile_order()
    
    if os.path.exists(self.f_file_manager):
      self.f_parser = source_manager.load_from_file(self.f_file_manager)
    else:
      self.f_parser = source_manager(self.config.f_srcs, self.config.project_build_dir,
                                     self.obj_dir_d, self.obj_dir_r, self.obj_attr,
                                     self.obj_ext, self.f_file_manager, 'fortran')
      
    if os.path.exists(self.c_file_manager):
      self.c_parser = source_manager.load_from_file(self.c_file_manager)
    else:
      self.c_parser = source_manager(self.config.c_srcs, self.config.project_build_dir,
                                     self.obj_dir_d, self.obj_dir_r, self.obj_attr,
                                     self.obj_ext, self.c_file_manager, 'c')

  def update_source_files(self):
    if 'f' in self.compile_ordered:
      self.f_parser.find_source_files()
      with open(self.f_obj_list_file, "w") as f:
        object_files = [attr[self.obj_attr] for f, attr in self.f_parser.source_files.items()]
        for obj in object_files:
            f.write(obj + "\n")
          
    if 'c' in self.compile_ordered:
      self.c_parser.find_source_files()
      with open(self.c_obj_list_file, "w") as f:
        object_files = [attr[self.obj_attr] for f, attr in self.c_parser.source_files.items()]
        for obj in object_files:
            f.write(obj + "\n")
  def find_libs(self):
    # 初始化一个存储完整路径的列表
    self.slibs = []
    # 遍历所有的静态库
    for lib in self.config.static_libraries:
      # 检查lib是否是一个绝对路径
      if os.path.isabs(lib) or os.path.isfile(lib):
        self.slibs.append(os.path.normpath(lib))
      else:
        # 如果不是绝对路径，则在当前目录和所有lib_dirs中查找
        # 检查所有提供的lib_dirs
        for dir in self.config.lib_dirs:
          full_path = os.path.join(dir, lib)
          if os.path.isfile(full_path):
            self.slibs.append(os.path.normpath(full_path))
            break

  def construct_dir(self):
    if self.target_type == 'debug':
      self.mid_dir = os.path.join(self.config.project_build_dir, "debug")
      self.fc_options = self.config.fc_options_debug
      self.cc_options = self.config.cc_options_debug
      self.obj_attr = 'obj_path_d'
    elif self.target_type == 'release':
      self.mid_dir = os.path.join(self.config.project_build_dir, "release")
      self.fc_options = self.config.fc_options_release
      self.cc_options = self.config.cc_options_release
      self.obj_attr = 'obj_path_r'
      
    self.obj_dir_d = os.path.join(self.config.project_build_dir, "debug", "objs")
    self.obj_dir_r = os.path.join(self.config.project_build_dir, "release", "objs")
    if os.name == 'nt':
      self.obj_ext = '.obj'
      self.lib_ext = '.lib'
    else:
      self.obj_ext = '.o'
      self.lib_ext = '.a'
      
    self.f_file_manager = os.path.join(self.config.project_build_dir, 'f_file_manager.pkl')
    self.c_file_manager = os.path.join(self.config.project_build_dir, 'c_file_manager.pkl')
    # 创建目录结构
    self.obj_dir = os.path.join(self.mid_dir, "objs")
    self.mod_dir = os.path.join(self.mid_dir, "mods")
    self.lib_dir = os.path.join(self.mid_dir, "libs")
    self.bin_dir = os.path.join(self.mid_dir, "bin")
    self.f_obj_list_file = os.path.join(self.mid_dir, "fobjs.txt")
    self.c_obj_list_file = os.path.join(self.mid_dir, "cobjs.txt")
    os.makedirs(self.mid_dir, exist_ok=True)
    os.makedirs(self.obj_dir, exist_ok=True)
    os.makedirs(self.mod_dir, exist_ok=True)
    os.makedirs(self.lib_dir, exist_ok=True)
    os.makedirs(self.bin_dir, exist_ok=True)
    self.config.lib_dirs = merge_path_dirs(self.config.lib_dirs, [self.lib_dir])
    self.f_exe_file = os.path.join(self.bin_dir, self.config.f_exe_name) if is_str_not_empty(self.config.f_exe_name) else ''
    self.f_lib_file = os.path.join(self.lib_dir, self.config.f_lib_name) if is_str_not_empty(self.config.f_lib_name) else ''
    self.c_exe_file = os.path.join(self.bin_dir, self.config.c_exe_name) if is_str_not_empty(self.config.c_exe_name) else ''
    self.c_lib_file = os.path.join(self.lib_dir, self.config.c_lib_name) if is_str_not_empty(self.config.c_lib_name) else ''

  def check_compile_order(self):
    '''检查混合编译顺序'''
    self.compile_ordered = []
    if is_str_not_empty(self.c_lib_file) and is_str_not_empty(self.c_exe_file):
      print('同一种语言不能生成exe又生成lib')
      sys.exit(1)
    if is_str_not_empty(self.f_lib_file) and is_str_not_empty(self.f_exe_file):
      print('同一种语言不能生成exe又生成lib')
      sys.exit(1)
    if is_str_not_empty(self.c_lib_file) and is_str_not_empty(self.f_exe_file):
      # 混合编译c编译为静态链接库，然后编译fortran
      self.compile_ordered = ['c', 'f']
    elif is_str_not_empty(self.c_exe_file) and is_str_not_empty(self.f_lib_file):
      self.compile_ordered = ['f', 'c']
    elif is_str_not_empty(self.c_exe_file) or is_str_not_empty(self.c_lib_file):
      self.compile_ordered = ['c']
    elif is_str_not_empty(self.f_exe_file) or is_str_not_empty(self.f_lib_file):
      self.compile_ordered = ['f']
    else:
      print('需要指定一种生成目标')
      sys.exit(1)
  
  def check_need_link(self, cmp_files, exe_file):
    if not os.path.isfile(exe_file):
      return True
    newest_mtime = 0
    for obj in cmp_files:
      newest_mtime = max(newest_mtime, os.path.getmtime(obj))
      if newest_mtime > os.path.getmtime(exe_file):
        return True
    return False
  
  # 执行编译命令
  def f_compile_files(self, files_to_compile: List[str]):
    for file in files_to_compile:
      obj_path = self.f_parser.source_files[file][self.obj_attr]
      cmd = [
          self.config.fc, 
          self.fc_options, 
          self.config.f_flag_silent.gen_flag(),
          self.config.f_flag_include.gen_flag(self.config.include_dirs),
          self.config.f_flag_mod_path.gen_flag(self.mod_dir),
          self.config.f_flag_nolink.gen_flag(),
          file,
          self.config.f_flag_obj.gen_flag(obj_path)
      ]
      print(f"Compiling {os.path.basename(file)}")
      result = subprocess.run(" ".join(cmd), shell=True)
      if result.returncode != 0:
        print(f"Error: Compilation of {file} failed!")
        sys.exit(result.returncode)

  # 执行编译命令
  def c_compile_files(self, files_to_compile: List[str]):
    for file in files_to_compile:
      obj_path = self.c_parser.source_files[file][self.obj_attr]
      cmd = [
          self.config.cc, 
          self.cc_options, 
          self.config.c_flag_include.gen_flag(self.config.include_dirs),
          self.config.c_flag_nolink.gen_flag(),
          file,
          self.config.c_flag_obj.gen_flag(obj_path)
      ]
      print(f"Compiling {os.path.basename(file)}")
      result = subprocess.run(" ".join(cmd) + " > NUL 2>&1", shell=True)
      if result.returncode != 0:
        print(f"Error: Compilation of {file} failed!")
        sys.exit(result.returncode)
  # 执行链接命令
  def f_link_files(self):
    self.find_libs()
    need = self.check_need_link(self.slibs, self.f_exe_file)
    if not need:
      object_files = [attr[self.obj_attr] for f, attr in self.f_parser.source_files.items()]
      need = self.check_need_link(object_files, self.f_exe_file)
    if not need:
      print('fortran已经是最新的!')
      return
    cmd = [
        self.config.fc,
        self.config.f_flag_silent.gen_flag(),
        gen_flag('', self.slibs, ' ', ispath=True, isList=True),
        gen_flag('@', self.f_obj_list_file, '', ispath=True, isList=False),
        self.config.f_flag_exe.gen_flag(self.f_exe_file),
        self.config.link_flag_use.gen_flag(),
        self.config.link_flag_lib_dir.gen_flag(self.config.lib_dirs),
    ]
    print("Linking fortran object files...")
    result = subprocess.run(" ".join(cmd), shell=True)
    if result.returncode != 0:
      print("Error: Linking failed!")
      sys.exit(result.returncode)
    else:
      print('生成成功！，可执行文件路径为：', os.path.relpath(self.f_exe_file))

  # 执行链接命令
  def c_link_files(self):
    self.find_libs()
    need = self.check_need_link(self.slibs, self.c_exe_file)
    if not need:
      object_files = [attr[self.obj_attr] for f, attr in self.c_parser.source_files.items()]
      need = self.check_need_link(object_files, self.c_exe_file)
    if not need:
      print('c已经是最新的!')
      return
    cmd = [
        self.config.cc,
        gen_flag('', self.slibs, ' ', ispath=True, isList=True),
        gen_flag('@', self.f_obj_list_file, '', ispath=True, isList=False),
        self.config.c_flag_exe.gen_flag(self.c_exe_file),
        self.config.link_flag_use.gen_flag(),
        self.config.link_flag_lib_dir.gen_flag(self.config.lib_dirs),
    ]
    print("Linking c object files...")
    result = subprocess.run(" ".join(cmd) + " > NUL 2>&1", shell=True)
    if result.returncode != 0:
      print("Error: Linking failed!")
      sys.exit(result.returncode)
    else:
      print('生成成功！，可执行文件路径为：', os.path.relpath(self.f_exe_file))
  # 执行链接命令
  def f_pack_lib(self):
    object_files = [attr[self.obj_attr] for f, attr in self.f_parser.source_files.items()]
    need = self.check_need_link(object_files, self.f_lib_file)
    if not need:
      print('c静态链接库已经是最新的!')
      return
    cmd = [
        self.config.lib_tool,
        self.config.lib_flag.gen_flag(self.f_lib_file), 
        gen_flag('@', self.f_obj_list_file, '', ispath=True, isList=False),
    ]
    print("正在打包lib...")
    result = subprocess.run(" ".join(cmd), shell=True)
    if result.returncode != 0:
      print("Error: 打包lib失败!")
      sys.exit(result.returncode)
    else:
      print('生成成功！，lib文件路径为：', os.path.relpath(self.f_lib_file))
      
  # 打包lib
  def c_pack_lib(self):
    object_files = [attr[self.obj_attr] for f, attr in self.c_parser.source_files.items()]
    need = self.check_need_link(object_files, self.c_lib_file)
    if not need:
      print('c静态链接库已经是最新的!')
      return
    cmd = [
        self.config.lib_tool,
        self.config.lib_flag.gen_flag(self.c_lib_file), 
        gen_flag('@', self.c_obj_list_file, '', ispath=True, isList=False),
    ]
    print("正在打包lib...")
    result = subprocess.run(" ".join(cmd) + " > NUL 2>&1", shell=True)
    if result.returncode != 0:
      print("Error: 打包lib失败!")
      sys.exit(result.returncode)
    else:
      print('lib打包完成！，路径为：', os.path.relpath(self.c_lib_file))
    
  def check_must_update_file(self):
    '''检查是否必须更新文件'''
    if 'c' in self.compile_ordered and not os.path.isfile(self.c_file_manager):
      return True
    if 'f' in self.compile_ordered and not os.path.isfile(self.f_file_manager):
      return True
    
  def make(self):
    '''编译项目'''
    if self.check_must_update_file() or self.need_update:
      self.update_source_files()
    
    for cpl in self.compile_ordered:
      if cpl == 'c':
        files = self.c_parser.c_get_files_need_compile()
        self.c_compile_files(files)
        if is_str_not_empty(self.c_exe_file):
          self.c_link_files()
        else:
          self.c_pack_lib()
      elif cpl == 'f':
        self.f_parser.gen_dependency_graph()
        files = self.f_parser.f_get_files_need_compile()
        self.f_compile_files(files)
        if is_str_not_empty(self.f_exe_file):
          self.f_link_files()
        else:
          self.f_pack_lib()