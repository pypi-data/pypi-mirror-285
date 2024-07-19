# proj52-Openeuler应用助手-OSTutor

[![](https://img.shields.io/badge/主页-OSTutor%2FREADME-orange)](https://gitlab.eduxiji.net/T202414655993206/project2210132-239674)
[![](https://img.shields.io/badge/开源协议-Mulan_PSL_v1-blue)](http://license.coscl.org.cn/MulanPSL)

时间：2024.05.15

选题：[proj52-OpenEuler应用助手](https://github.com/oscomp/proj52-OS-Tutor)

学校：深圳技术大学

队伍ID：
T202414655993206

队伍成员：

| 身份 | 名称 |
|:--------:|:---------:|
| 队伍 | 管你对不队 |
| 队员1 | 陈子健 |
| 队员2 | 吴奇墉 |
| 队员3 | 梁臻鑫 |

> `OSTutor` 是一个辅助使用**基于rpm的Linux**的工具，在接收到用户给出的几个关键字后，返回可能相关的命令及其它进一步的相关帮助信息，是一个从所需功能到所用具体命令的一个桥梁。

## 目录

[TOC]

## 1. 分析与调研

### 1.1 比赛题目分析

- openEuler是一个**基于RPM包管理**的Linux发行版。
海量的配置文件、包、命令不利于初学者学习，使用者也可能忘记部分命令的使用。

- 比赛题目的目标是开发一个**主机范围内**的搜索提示工具，为用户提供从所需功能到具体命令的映射。

- **按可信度排序**给予用户命令提示，达到降低学习使用Openeuler的困难、方便用户快速查找和使用openEuler中的各种命令和功能的效果。

### 1.2 相关资料调研

- openEuler**使用RPM**作为基础,结合DNF和Yum来管理软件包。
- RPM(RPM Package Manager)是Linux系统中广泛使用的软件包管理工具。它用于安装、卸载、升级、查询和验证软件包。
- 通过RPM命令,可以查看已安装包的信息、检查包的完整性、重建RPM数据库等。
- 编程语言：**Python**
    - *语言简洁*：Python作为一种解释型语言,开发效率很高。无需编译,修改后可直接运行。
    - ***功能强大***: 拥有丰富的标准库和第三方库,可以快速实现各种功能。
    - *扩展性强*：能与其它语言联合使用。
- 数据库：**SQLite**
    - ***轻量化***: SQLite是一个无服务器的嵌入式数据库引擎,不需要单独的服务器进程,可直接嵌入应用程序中。这使得它非常轻量级和便携。
    - *高可靠性*: SQLite遵循ACID(原子性、一致性、隔离性、持久性)原则,保证数据的完整性和一致性。
    - *高性能*: SQLite采用了高效的B-Tree存储引擎,在大多数情况下性能表现优异。
    - ***单文件数据库***: SQLite的整个数据库是存储在单个磁盘文件中的,易于备份和传输。
    - *开源免费*: SQLite是开源免费的,可以免费用于任何项目中。

### 1.3 OSTutor应该具有的特征/优势
- `反向搜索`：现在的工具大多是根据命令找功能，如果不知道命令只能通过网络搜索。
- `本地更新`：自动搜索本机内容，无需联网，本地化处理，保证隐私安全。
- `联网更新`：联网导入知识库（可选）。
- `个性化`：可根据已安装软件自动建立知识库，不存储冗余信息，也可以导入现成知识库。
- `可维护`：提供用户修改知识库的方式、评分机制。
- `便捷性`：便捷导入导出知识库、备份恢复安装包列表。
- `易用性`：提供简单便捷的“*命令行搜索*”与全功能的“*UI搜索*”、自动更新知识库。
- `广泛支持`：理论上支持所有基于RPM包管理的Linux发行版。


## 2. 工具设计

### 2.1 软件框架设计
![软件框架设计](./ANNEX/Software_architecture.png)

### 2.2 开发计划
- [ ] 知识库
    - [x] 收集主机rpm包命令
    - [x] 分析rpm包命令
    - [x] 数据库存储
    - [ ] 用户自定义修改
    - [ ] 自动本地/联网更新
    - [ ] 导入导出知识库
- [ ] 搜索
    - [x] 基础搜索-按可信度排序
    - [ ] 评分机制-推荐参考选项
- [ ] 界面
    - [x] 命令行界面
    - [x] UI
    - [ ] 优化显示效果
- [ ] 打包
    - [ ] 打包发布

## 3. 初赛过程中的重要进展

### 第一阶段：知识库设计于存储
1. 编写shell命令采集rpm包信息与man文档
2. 设计数据库

Info 视图
- `rpm_id`: 关联的rpm包的ID。
- `ins_id`: 关联的指令的ID。
- `rpm_name`: rpm包的名称。
- `rpm_summary`: rpm包的简短描述。
- `ins_name`: 指令的名称。
- `ins_brief`: 指令的简短描述。
- `ins_description`: 指令的详细描述。
- `rpm_description`: rpm包的详细描述。

Rpm 表
- `id`: rpm包的唯一标识符。
- `name`: rpm包的名称。
- `version`: rpm包的版本。
- `release`: rpm包的发布号。
- `architecture`: rpm包的目标架构。
- `source_rpm`: 代表rpm包的源rpm名称。
- `packager`: rpm包打包组织。
- `url`: rpm包官方网站。
- `summary`: rpm包的简短描述。
- `description`: rpm包的详细描述。

Ins 表
- `id`: 指令的唯一标识符。
- `rpm_id`: 关联的rpm包的ID。
- `brief`: 指令的简短描述。
- `name`: 指令的名称。
- `help`: 指令的帮助信息。
- `description`: 指令的详细描述。

Opt 表
- `id`: 选项的唯一标识符。
- `instruction_id`: 关联的指令的ID。
- `content`: 选项的内容。

Conf 表
- `id`: 配置文件的唯一标识符。
- `rpm_id`: 关联的rpm包的ID。
- `position`: 配置文件的位置信息。

Readme 表
- `id`: README文件的唯一标识符。
- `rpm_id`: 关联的rpm包的ID。
- `name`: README文件的名称。
- `content`: README文件的内容。

### 第二阶段：搜索算法的编写
使用TF-IDF算法来计算用户输入与数据库中rpm包和指令的相似度。

### 第三阶段：界面设计
**命令行界面**设计程序交互运行逻辑并实现：
![命令行模式操作逻辑](./ANNEX/Command_line(cli)_mode_interaction_logic.png)

**UI界面**：
![UI界面](./ANNEX/UI.png)

## 4. 系统测试

### 源码运行

1. 安装依赖

```python
pip install -r .\requirements.txt
```

在window上测试还需要安装专用依赖：

```python
pip install windows-curses==2.3.3
```

2. 帮助信息
- 可直接运行获取软件的描述信息：

```python
python .\__main__.py
```

> Usage: \_\_main\_\_.py [OPTIONS] COMMAND [ARGS]...
> 
>   OSTutor - OpenEuler 应用助手
> 
> Options:
>   --help  Show this message and exit.
> 
> Commands:
>   init    初始化数据库。
>   search  命令行检索。
>   ui      启动用户界面模式。

- 软件工作模式的帮助信息:

```python
# python .\__main__.py [模式] --help
python .\__main__.py search --help 
```

3. 初始化本机知识库
```python
# 可不运行，源码已包含初始化过的数据库
python .\__main__.py init
```

4. 搜索命令
```python
# 命令行界面
python __main__.py search --cli -i "multiple keywords"
# UI
python __main__.py ui -i
```

5. 视频演示
演示环境：openEuler-Standard-22.03-LTS-SP3 + VScode

视频链接：
链接: [https://pan.baidu.com/s/12jMRfM4nCgmAhwCVQhz24Q?pwd=n54a](https://pan.baidu.com/s/12jMRfM4nCgmAhwCVQhz24Q?pwd=n54a) 提取码: n54a

## 5. 遇到的主要问题和解决方法

### 5.1 textwrap对中文等其它编码支持不友好
`问题描述`：展示信息的时候屏幕大小有限，需要换行显示，一开始使用有自动换行功能的“textwrap”，但当文件中包含中文的时候，显示上会出现首行提示语消失的情况。

`解决方式`：选择自行编写换行函数，使用“wcwidth”来统计字符长度，并计算换行。

### 5.3 TF-IDF向量检索性能不够理想
`问题描述`：因为数据具有一定的规模，在处理用户输入时，每次都需要读取数据并拟合，涉及大量的矩阵运算，导致用户等待时间过长，影响用户体验。

`解决方式`：将计算得到的TF-IDF矩阵和向量化器保存到本地，以便后续可以直接加载和重用，避免重复计算。

### 5.2 数据存储方式如何抉择
`问题描述`：在处理数据时，有效的数据存储和查询方式对于数据分析和应用程序的逻辑处理至关重要，选择一个合适的数据存储方式是本项目的一大难点。

`解决方式`：选择SQLite作为数据存储方案。SQLite是一个嵌入式数据库管理系统，它不需要独立的服务器进程，可以直接嵌入到应用程序中。它支持标准的SQL语法，具有零配置、事务处理、并发访问等特性，而且python内置sqlite库，非常适合作为本项目的数据存储方式。

### 5.4 如何提升用户友好性
`问题描述`：本项目作为用户与系统指令之间的桥梁，如何提升用户接口的友好性对用户体验至关重要。

`解决方式`：设计命令行与UI的多种用户操作方式，提供简洁的操作指令与用户界面，让用户自行选择喜好的操作方式。

## 6. 提交仓库目录和文件描述

### 目录结构
```
.
├── ANNEX                                               # 附件
│   ├── Command_line(cli)_mode_interaction_logic.png
│   ├── DISCRETION.md                                   # 具体描述文件
│   └── Software_architecture.png
├── controller.py                                       # 控制进入软件不同模式
├── dao                                                 # 数据库处理
│   ├── dao.py
│   └── model.py
├── data                                                # 数据库存放
│   ├── data.py                                         # 数据库插入脚本
│   ├── data.sh                                         # 数据搜集脚本
│   ├── README.md
│   ├── rpm_data.csv
│   ├── rpm_data.db                                     # sqlite数据库
│   ├── rpm.sql                                         # 数据库建表语句
│   ├── tfidf_matrix.pickle
│   └── tfidf_vectorizer.pickle
├── logic
│   ├── clisearch.py                                    # 命令行模式搜索
│   ├── display.py                                      # 命令行翻页显示
│   ├── tfidf.py                                        # TF-IDF 检索
│   └── ui.py                                           # UI模式
├── __main__.py                                         # 程序入口
├── README.md                                           # 项目介绍
└── requirements.txt                                    # 运行依赖
```
### 文件描述
具体文件描述请看

[DISCRETION.md](https://gitlab.eduxiji.net/T202414655993206/project2210132-239674/-/blob/main/ANNEX/DISCRETION.md)

## 7. 比赛收获
通过这次比赛，我们队伍获得了以下收获：

1. 系统软件开发经验

这个项目实际上是在开发一个系统软件工具，需要对操作系统有一定的理解。在开发过程中,接触到了文件解析、数据库设计、命令行交互等方面的相关编程。增加了对Openeuler文件结构、rpm包管理的认识。

2. 文本处理和信息检索技能

该助手的核心是对命令手册等文本数据进行解析和处理，从中提取关键信息构建数据库。这需要运用文本处理、模式匹配、信息检索等技术，加深了对模型训练的理解。

3. 数据库设计相关知识

使用SQLite数据库存储命令信息，需要合理设计数据库模式。加深了对数据库系统的理解，学习了python与SQLite的结合使用。

4. 用户体验设计意识

为了提高工具的易用性，需要考虑用户界面、交互逻辑等方面的设计。

6. 团队协作和项目管理经验

对于软件的架构设计、展示形式、结果测试等各个方面，互相取长补短，能发现许多设计上的缺漏并提供更好的建议；
学习并应用了项目管理工具Git，为代码合并与同步提供了一个便捷的途径，加快了开发效率。

7.  注意开发环境的差异


项目的研发用到了Windows和Openeuler两个平台，发现有一些开发环境的差异。例如Windows上不带有curses库且安装时库名称为“windows-curses”；还有python在windows上创建txt默认编码为GBK，但Openeuler为utf-8，创建文本文件要注意指定编码。

## 8. License

OSTutor is licensed under the Mulan PSL v1. You can use this software according to the terms and conditions of the Mulan PSL v1. You may obtain a copy of Mulan PSL v1 at: http://license.coscl.org.cn/MulanPSL

THIS SOFTWARE IS PROVIDED ON AN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE. See the Mulan PSL v1 for more details.