# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['tdf_tool',
 'tdf_tool.modules.cli',
 'tdf_tool.modules.cli.bean',
 'tdf_tool.modules.cli.utils',
 'tdf_tool.modules.config',
 'tdf_tool.modules.fix_header',
 'tdf_tool.modules.gitlab',
 'tdf_tool.modules.i18n',
 'tdf_tool.modules.i18n.flutter',
 'tdf_tool.modules.i18n.ios',
 'tdf_tool.modules.i18n.tools',
 'tdf_tool.modules.module',
 'tdf_tool.modules.package',
 'tdf_tool.modules.translate',
 'tdf_tool.modules.translate.flutter',
 'tdf_tool.modules.translate.flutter.tools',
 'tdf_tool.modules.translate.ios',
 'tdf_tool.modules.translate.ios.tools',
 'tdf_tool.modules.translate.tools',
 'tdf_tool.pipelines',
 'tdf_tool.tools',
 'tdf_tool.tools.vscode']

package_data = \
{'': ['*']}

install_requires = \
['environs>=9.5.0,<10.0.0',
 'fire>=0.4.0,<0.5.0',
 'googletrans==3.1.0a0',
 'python-gitlab==1.15.0',
 'requests==2.27.1',
 'ruamel.yaml>=0.17.21,<0.18.0']

entry_points = \
{'console_scripts': ['tdf_tool = tdf_tool.app:main', 'tl = tdf_tool.app:main']}

setup_kwargs = {
    'name': 'tdf-tool',
    'version': '2.4.19',
    'description': '二维火 flutter 脚手架工具',
    'long_description': '## History\n\n### 2.4.16（2024-4-29）\n-  修复 tl module open 命令偶现复用上一个 vscode 窗口的问题；（改为每次新建一个 vscode）\n\n### 2.4.15（2024-4-24）\n\n- 该版本包含自身版本控制逻辑\n- 若远端存在新版本，会有提示更新（1.重大更新(强制)，2.api更新(强制)，3.小功能更新，4.无功能更新，5.异常更新）\n- 提供远端版本查看链接，可以自行查看版本更新文案自行选择是否更新 tl 命令\n\n### 2.4.13（2024-4-23）\n\n- 新增tl 版本号校验，以便及时告知开发者更新最新版本号\n\n### 2.4.11（2024-4-20）\n\n- 修复路由丢失问题；\n\n### 2.4.7（2024-4-20）\n\n- tl router start 替换为 tl annotation start\n- 新增支持通过下标指定模块执行脚本\n- 针对新增的 api 自动注册文件，增加 tl 版本号标注，以便出现文件生成不一致，可进行比对\n\n### 2.1.00\n\n- 路由功能支持flutter版本3.3.10，兼容flutter版本2.2.3；\n\n### 2.0.61\n\n- Flutter国际化字符串整合；\n\n### 2.0.38\n\n- 路由生成完后增加路由相关代码format（解决windows代码生成后顺序错乱）；\n\n### 2.0.01\n\n- Cli 框架升级；\n- 代码重构；\n\n### **1.1.00（2022-4-28）**\n\n- 国际化解决输出json中包含转义字符的问题，如\\n；\n- 四类语言输出文件自动格式化\n\n### **1.0.55（2022-4-28）**\n\n- 国际化key使用中文（依照ios项目开发形式）；\n\n### **1.0.53（2022-4-28）**\n\n- 国际化流程中，兼容解决部分json解析失败问题，譬如字符串中包含"="符号；\n\n> 错误日志如：Unterminated string starting at: line 1 column 5650 (char 5649)\n\n### **1.0.50（2022-4-28）**\n\n- 国际化增加繁体字翻译；\n\n## 帮助文档\n\n```shell\nNAME\n    tdf_tool - 二维火 Flutter 脚手架工具，包含项目构建，依赖分析，git等功能。。\n\nSYNOPSIS\n    tdf_tool GROUP | COMMAND\n\nDESCRIPTION\n    二维火 Flutter 脚手架工具，包含项目构建，依赖分析，git等功能。。\n\nGROUPS\n    GROUP is one of the following:\n\n     module\n       模块相关工具： tdf_tool module -h 查看详情\n\n     package\n       封包工具相关：tdf_tool package -h 查看详情\n\n     translate\n       国际化相关：tdf_tool translate -h 查看详情\n\nCOMMANDS\n    COMMAND is one of the following:\n\n     git\n       tdf_tool git【git 命令】：批量操作 git 命令, 例如 tdf_tool git push\n\n     router\n       tdf_tool router：会以交互式进行路由操作，对指定的模块执行路由生成和路由注册逻辑\n\n     upgrade\n       tdf_tool upgrade：升级插件到最新版本\n        \n```\n\n## 插件安装方式\n\n安装python包\n\n```\npip3 install tdf-tool --user\n```\n\n安装并更新python包\n\n```\npip3 install --upgrade tdf-tool --user\n```\n\n安装测试环境python包\n\n```\npip3 install -i https://test.pypi.org/simple/ tdf-tool --user\n```\n\n安装并更新测试环境python包\n\n```\npip3 install --upgrade -i https://test.pypi.org/simple/ tdf-tool --user\n```\n\n## 工具使用流程说明\n\n### 1.准备工作\n\n- 确保python的bin插件目录已经被配置到环境变量中（这一步不满足的话，插件安装之后是无法识别到本插件命令的）\n\n- 在~目录下，创建.tdf_tool_config文件并配置相关必需属性如下\n\n```json\ngit_private_token=***\n```\n\ngit_private_token是gitlab的token\n\n获取途径：进入gitlab页面，点击右上角头像，选择Preferences，选择左侧列表中的AccessToken进行创建\n\n**上述步骤如果没有做，会在使用插件时，会有提示**\n\n### 2.初始化\n\n#### i.进入壳目录（确保执行命令在壳目录内）\n\n#### ii.执行tdf_tool module init\n\n- 判断当前目录是否存在tdf_cache，若不存在，则会自动创建tdf_cache\n- 自动读取当前壳模块名称，写入initial_config.json配置文件；\n- 读取当前壳分支，写入initial_config.json配置文件；\n- 交互式提示用户输入需要开发的模块名并写入initial_config.json配置文件的moduleNameList列表字段中\n- ！退出，即输入完成\n- 自动clone所有开发模块到  ```../.tdf_flutter```  隐藏目录中；\n- 将所有开发模块分支切换至与壳一致；\n- 自动分析依赖树，并**由下至上**对所有模块自动执行```flutter pub upgrade```;\n\n#### iii.开发过程中\n\n##### 1.开发模块添加\n\n- 若是有新模块需要添加入开发模块中，可直接修改initial_config.json配置文件，修改moduleNameList字段；\n- 执行tdf_tool deps更新依赖\n\n##### 2.新开发模块添加\n\n- 添加新模块后，会提示找不到模块，实际查找的是```tdf_cache```文件夹中的module_config.json文件；\n- 如果没有找到该模块，则可以执行```tdf_tool module-update```,更新远程module_config.json文件；\n- 删掉本地的module_config.json文件，重新执行命令即可，脚本会自动判断本地是否存在该配置文件，如果不存在会**下载**；\n\n<span style="color:#ff0000">请确保gitlab仓库的新开发模块master分支是一个flutter模块，如果判定不是flutter模块，则会报错（判定条件为存在pubspec.yaml文件）</span>\n\n### 3.版本控制\n\n版本控制请使用tdf_tool命令，命令详情可使用  ```tdf_tool -h```  查看，现已支持大部分命令，若有特殊命令需要执行，可以使用  ```tdf_tool <git命令>``` ，如：```tdf_tool git add .```\n\n### 4.自动打包发布\n\n暂未接入打包工具，预计下一季度进行支持；\n\n**<span style="color:#ff0000">FAQ</span>**\n\nwindows系统请使用bash命令；\n\n## 额外功能说明\n\n### 1.二维数组表达依赖树\n\n生成一个二维数组，可根据该二维数组的数据进行**并发**打tag，每一层的模块，都可以同时进行打tag发布操作，减少发布耗时；\n\n```json\n[\n ["tdf_channel", "tdf_event", "tdf_network"], \n ["tdf_widgets"], \n ["tdf_smart_devices", "tdf_account_module"], \n ["flutter_reset_module"]\n]\n```\n\n如上数据，数组中每一个节点中的模块均可同时打tag，节点之间需要由上至下的顺序进行tag操作\n\n### 2.插件更新\n\n执行 ```tdf_tool upgrade```\n\n### 3.远程模块配置文件更新\n\n执行 ```tdf_tool module module_update```\n\n## 依赖树分析原理\n\n采用有向有/无环图进行依赖树的分析\n\n数据结构采用如下：\n\n```python\nclass DependencyNode:\n    def __init__(self):\n        self.nodeName = \'\'\n        self.parent = []  # 父亲节点列表\n        self.children = []  # 子孙节点列表\n        self.delete = False\n```\n\n![dependency](./README_DIR/dependency.png)\n\n如上图1：一个正常的依赖树表示；\n\n如上图2：对图1中，依赖树所有节点去重，变换为图2有向图；\n\n**分析流程：**\n\n**依赖图构建**\n\n```python\n# 生成依赖图\n    def _generateDependenciesMap(self):\n        for package in self.__moduleDependenciesMap:\n            for module in moduleNameList:\n                if package == module:\n                    # 到这一步表明当前这个模块属于开发模块且在当前模块的依赖模块列表中，是当前模块的子模块\n                    self._mNodeDict[self.__moduleName].children.append(package)\n                    self._mNodeDict[package].parent.append(self.__moduleName)\n```\n\n- 共5个节点\n\n  - node构建：\n\n    - ```python\n      {\n       "模块1":{\n          "nodeNmae": "模块1",\n          "parent": [],\n          "children": ["模块2","模块3","模块4","模块5"],\n          "delete": False\n       },\n       "模块2":{\n          "nodeNmae": "模块2",\n          "parent": ["模块1"],\n          "children": ["模块4","模块5"],\n          "delete": False\n       }\n       "模块3":{\n          "nodeNmae": "模块3",\n          "parent": ["模块1"],\n          "children": ["模块5"],\n          "delete": False\n       }\n       "模块4":{\n          "nodeNmae": "模块4",\n          "parent": ["模块1","模块2"],\n          "children": [],\n          "delete": False\n       }\n       "模块5":{\n          "nodeNmae": "模块5",\n          "parent": ["模块1","模块2","模块3"],\n          "children": [],\n          "delete": False\n       }\n      }\n      ```\n\n**依赖图解析伪代码（以一维数组为例）**\n\n```python\n# 返回二维数组，用于并发打tag\n    def _generateDependenciesOrder(self):\n        resList = []\n        while 存在节点delete属性不为True:\n            \n            for：查找子节点为0的节点\n             设置节点delete属性为True\n              \n            for：deleteItemList = 拿到所有delete属性为true的节点\n\n            for：遍历所有节点，如果节点的子节点中包含deleteItemList的节点，则将其从子节点列表中删除\n```\n\n- **initial_config.json文件说明**\n\n  ```json\n  {\n      "featureBranch": "feature/test_dev_1", // 开发分支\n      "shellName": "flutter_reset_module",\n      // 项目需要开发的模块,可自由配置\n      "moduleNameList": [\n          "flutter_reset_module",\n          "tdf_smart_devices",\n          "tdf_widgets",\n          "tdf_channel"\n      ]\n  }\n  ```\n\n- **module_config.json文件说明**\n\n  ```json\n  {\n      "flutter_globalyun_us_module": {\n         "id": "11111"\n          "type": "shell",\n          "git": "git@git.2dfire.net:app/flutter/app/flutter_globalyun_us_module.git"\n      },\n      "tdf_router_anno": {\n          "type": "base",\n          "git": "git@git.2dfire.net:app/flutter/app/tdf_router_anno.git"\n      },\n  }\n  //语意\n  {\n    "模块名":{\n      "id": 项目gitlab id\n      "类型": gitlab group名\n      "git": gitlab地址\n    }\n  }\n  ```\n\n## 后续计划\n\n<span style="color:#ff0000">**问题：**</span>由于现在flutter ci 【lint】【tag】任务脚本成功率过于低，很多时候是因为项目模块的配置问题导致的，且后续会接入一键打tag工具\n\n方案：在执行统一push前，对所有模块的项目配置信息进行校验，确保数据规范；\n\n## 插件打包发布命令\n\n**插件打包命令**\n\n```\npoetry build\n```\n\n**插件发布命令**\n\n```\npoetry publish\n```\n\n## vscode 调试配置 ##\n\n```json\n{\n    "version": "0.2.0",\n    "configurations": [\n        {\n            "name": "i18n",\n            "type": "python",\n            "request": "launch",\n            "pythonpath": "/Users/admin/Library/Caches/pypoetry/virtualenvs/tdf-tool-_Qh8vdX_-py3.11/bin/python", // python路径\n            "cwd": "${workspaceFolder}",\n            "module": "poetry",\n            // "justMyCode": false,\n            "args": [\n                "run",\n                "tl",\n                "i18n",\n                "reflow",\n                "start",\n            ]\n        }\n    ]\n}\n```\n',
    'author': 'Jian Xu',
    'author_email': '3386218996@qq.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://git.2dfire.net/app/flutter/tools/package_tools',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.9.0,<4.0.0',
}


setup(**setup_kwargs)
