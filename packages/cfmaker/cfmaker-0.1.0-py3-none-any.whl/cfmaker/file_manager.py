#coding:utf-8
import os
import networkx as nx
import pickle
import time
from .tools import f_parse_dependencies


class source_manager:
  def __init__(self,
               src_dirs,
               build_dir,
               obj_dir_d,
               obj_dir_r,
               obj_attr,
               obj_ext,
               save_file,
               language='fortran'):
    self.language = language
    self.src_dirs = src_dirs
    self.build_dir = os.path.abspath(build_dir)
    self.obj_dir_d = os.path.abspath(obj_dir_d)
    self.obj_dir_r = os.path.abspath(obj_dir_r)
    self.obj_ext = obj_ext
    self.source_manager_file = save_file
    self.obj_attr = obj_attr

    if language == 'fortran':
      self.exts = ['f90', 'f', 'f95']
    elif language == 'c':
      self.exts = ['c', 'cpp', 'cc', 'cxx']
    else:
      raise Exception('Unsupported language: ' + language)
    self.exts = ['.' + ext if not ext.startswith('.') else ext for ext in self.exts]
    self.dependency_graph = nx.DiGraph()
    self.module_file_map = {}
    self.source_files = {}
    self.newest_source_mtime = 0  #源文件最新更新时间
    #self.find_source_files()
    #print(self.source_files)

  # 保存对象到文件
  def save_to_file(self):
    with open(self.source_manager_file, 'wb') as file:
      pickle.dump(self, file)

  # 从文件加载对象
  @classmethod
  def load_from_file(cls, filepath) -> 'source_manager':
    with open(filepath, 'rb') as file:
      return pickle.load(file)
    
  def add_source_file(self, filepath):
    fpath = os.path.abspath(filepath)
    name, ext = os.path.splitext(os.path.basename(fpath))
    if ext in self.exts:
      self.source_files[fpath] = {
          'mtime': os.path.getmtime(fpath),
          'dep_mtime': 0,
          'obj_path_d': os.path.join(self.obj_dir_d, name + self.obj_ext),
          'obj_path_r': os.path.join(self.obj_dir_r, name + self.obj_ext)
        }

  def find_source_files(self):
    self.source_files = {}
    for src in self.src_dirs:
      # 检查是否以'**'结尾，并去除'**'
      if src.endswith('**'):
        src_dir = src[:-3]  # 移除末尾的'**'
        # 递归搜索所有子目录
        for root, dirs, files in os.walk(src_dir):
          for file in files:
            fpath = os.path.join(root, file)
            self.add_source_file(fpath)
              
      # 如果不是以'**'结尾，则按不进行子目录检索
      elif os.path.isdir(src):
        # 搜索该目录下的所有文件
        with os.scandir(src) as it:  
          for entry in it:  
            if entry.is_file():  # 确保是一个文件  
              # 获取文件的完整路径（虽然在这个上下文中，我们可能只需要文件名来检查后缀）  
              fpath = entry.path 
              self.add_source_file(fpath)
      # 如果src是文件且其后缀在exts中
      elif os.path.isfile(src):
        self.add_source_file(src)
    self.save_to_file()
  
  # 构建文件的依赖关系图
  def gen_dependency_graph(self):
    file_depends = {}
    delfiles = []
    for source_file, attribs in self.source_files.items():
      if os.path.exists(source_file):
        smtime = os.path.getmtime(source_file)
        if smtime > attribs['dep_mtime']:
          #文件需要重新构建依赖
          dependencies, module_names = f_parse_dependencies(source_file)
          for m_name in module_names:
            self.module_file_map[m_name] = source_file
          file_depends[source_file] = dependencies
      else:
        print('检测到一个源文件被删除', source_file)
        delfiles.append(source_file)

    for source_file in delfiles:
      del self.source_files[source_file]

    for source_file, deps in file_depends.items():
      if self.dependency_graph.has_node(source_file):
        in_edges = list(self.dependency_graph.in_edges(source_file))
        if len(in_edges) > 0:
          self.dependency_graph.remove_edges_from(in_edges)
      else:
        self.dependency_graph.add_node(source_file)
      #self.dependency_graph.add_node(source_file)
      for dep in deps:
        if dep in self.module_file_map:  #模块可能是内置的，没有对应源文件
          mfile = self.module_file_map[dep]
          self.dependency_graph.add_edge(mfile, source_file)
        # else:
        #   print('no source module', dep)
      self.source_files[source_file]['dep_mtime'] = time.time()
    self.save_to_file()

  #获取需要被编译的文件列表
  def f_get_files_need_compile(self):
    cmp_files = set()
    sorted_files = []
    for source_file, attribs in self.source_files.items():
      objfile = attribs[self.obj_attr]
      if os.path.exists(objfile):
        obj_mtime = os.path.getmtime(objfile)
      else:
        obj_mtime = 0
      smtime = os.path.getmtime(source_file)
      if smtime > obj_mtime:
        cmp_files.add(source_file)
        if source_file in self.dependency_graph:
          cmp_files.update(nx.descendants(self.dependency_graph, source_file))
    if len(cmp_files) > 0:
      sorted_files = list(
          nx.topological_sort(self.dependency_graph.subgraph(cmp_files)))
      self.save_to_file()
    return sorted_files
  
  def c_get_files_need_compile(self):
    '''获取c中被修改的源文件列表,c编译不需要排序'''
    cmp_files = set()
    for source_file, attribs in self.source_files.items():
      objfile = attribs[self.obj_attr]
      if os.path.exists(objfile):
        obj_mtime = os.path.getmtime(objfile)
      else:
        obj_mtime = 0
      smtime = os.path.getmtime(source_file)
      if smtime > obj_mtime:
        cmp_files.add(source_file)
    if len(cmp_files) > 0:
      self.save_to_file()
    return list(cmp_files)

if __name__ == '__main__':
  s = source_manager(['D:/study/SPH/program/PSFD/src/**'], 'build', 'build/obj', '.o', 'build/source_manager.pkl', 'c')
  