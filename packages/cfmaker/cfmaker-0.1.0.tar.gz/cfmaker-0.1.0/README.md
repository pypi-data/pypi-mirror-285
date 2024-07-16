# fmaker

简易的用于intel oneapi fortran与c项目的编译，适用于小项目
若oneapi又发疯改一堆编译选项，可以自定义设置编译和链接等选项

## Getting Started

1. write 'maker.py'

```python
from cfmaker import compile_manager, ProjectConfig

config = ProjectConfig(
  f_srcs=['src/**'],
  c_srcs=['src/**'],
  project_build_dir='./build',
  f_exe_name='example.exe',
  c_lib_name='example.lib',
  static_libraries=['example.lib']
)

config.auto_add_intel_mpi()
config.auto_set_cc_options()
config.auto_set_fc_options()

compile_manager(config).make()
```

2. execute 'maker.py'

```python
python maker.py #默认以debug模式编译
python maker.py debug #以debug模式编译
python maker.py release #以release模式编译
python maker.py debug update #更新源文件列表后进行debug模式编译
python maker.py release update #更新源文件列表后进行release模式编译
```

## Advanced

```python
from cfmaker import inner_flag_opt
config.fc_options_debug = '-g -O0'  #设置fortran debug编译选项

#修改输出exe的选项
config.f_flag_exe = inner_flag_opt('/Fe', '', ispath=True, isList=False )
#修改输出include的选项
config.f_flag_include = inner_flag_opt('-I', '', ispath=True, isList=True )

```

## Contributing

```
pip install build installer
python -m build
```
