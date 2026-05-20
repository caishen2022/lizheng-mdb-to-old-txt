---
name: lizheng-mdb-to-old-txt
description: Use when 需要把新版理正 Access .mdb 数据库转换成旧版软件可导入的 TXT 接口文件。强制使用 mdbtools，遵循当前已确认的段格式、字段映射与钻孔分组规则。
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [lizheng, access, mdb, txt, mdbtools, mapping, gb18030]
    related_skills: [access-mdb-migration, hermes-agent, hermes-agent-skill-authoring]
---

# 理正新版 MDB → 旧版 TXT 接口文件

## Overview

用于把**新版理正 Access `.mdb` 数据库**转换成**旧版软件可导入的标准 TXT 接口文件**。

本技能基于当前已经验证过的项目经验，总结了：
- 读取方式：**强制使用 `mdbtools`**，不依赖 Access ODBC
- 输出规则：旧版接口 TXT 的段标记、钻孔分组、编码与换行格式
- 字段映射策略：同名直映射、尾部下划线别名映射、复杂业务段保守留空
- 交付方式：弹窗选择 `.mdb`，输出 TXT 到源数据库同目录，完成/失败弹窗提示

当前主脚本路径：
- `/opt/hermes/convert_new_mdb_to_old.py`

当前映射分析文档：
- `/opt/hermes/mdb_mapping_report.md`

## When to Use

适用于以下请求：
- “把新版数据库转成旧版 TXT 接口文件”
- “把理正新版 `.mdb` 导成旧版能导入的 TXT”
- “不要 ODBC，强制用 `mdbtools` 转换”
- “运行时弹窗选文件，输出到数据库同目录”

不适用于：
- 需要回写旧版 `.mdb`
- 需要支持 `.accdb`
- 需要 100% 业务语义还原，但复杂段映射尚未人工确认的场景

## Core Rules

### 1. 输入与依赖

- 只支持 `.mdb`
- 强制使用 `mdbtools`
- 不使用 `pyodbc` / Access ODBC 驱动
- GUI 使用 Python 标准库 `tkinter`
- 输出编码使用 `gb18030`

### 2. TXT 接口格式规则

#### 2.1 不输出字段名示例行
错误示例：
```text
#GC#GCKCJD\tGCJSDW\t...
详细勘察\t...
```

正确做法：直接输出真实数据行。

#### 2.2 段标记后面直接接首字段值
正确示例：
```text
#GC#详细勘察\t...
#ZK#GZK1\t控制孔\t...
#TC#素填土\t...
```

注意：
- `#GC#` 与首字段之间**不加空格**
- `#GC#` 与首字段之间**不加额外 Tab**
- 第二列开始才用 `\t` 分隔

#### 2.3 钻孔主记录
钻孔主记录本身写成：
```text
#ZK#钻孔编号\t钻孔类型\tX\tY\t...
```

例如：
```text
#ZK#GZK1\t控制孔\t...
```

#### 2.4 钻孔下属项目的分组规则
对 `TC/BG/DT/SW/...` 这类带 `ZKBH` 的项目表：

- 当进入某个钻孔的该项目数据块时，先单独输出一行：
```text
#ZK#钻孔编号
```
- 后面的项目数据重新起一行：
```text
#TC#素填土\t...
#TC#粉质黏土\t...
```
- **同一个钻孔、同一个项目段内**，只在第一条前输出一次 `#ZK#钻孔编号`
- 后续同项目连续记录**不要重复输出** `#ZK#钻孔编号`
- 切换到下一个钻孔时，再输出新的 `#ZK#钻孔编号`

示例：
```text
#ZK#GZK26
#TC#素填土\t...
#TC#粉质黏土\t...
#TC#细砂\t...
#ZK#GZK25
#TC#素填土\t...
```

#### 2.5 不要插入多余空行
- `#ZK#GZK26` 与后面的 `#TC#...` 之间不要空行
- 文件换行使用 `\r\n`
- 写文件时避免 `newline='\r\n'` 和手工拼 `\r\n` 叠加，否则容易出现双空行

### 3. 字段映射总原则

#### 3.1 默认规则
- 新版表和旧版接口字段**同名** → 直接映射
- 新版表有额外字段 → 忽略
- 旧接口字段新版不存在 → 先留空
- 不猜测复杂业务语义

#### 3.2 别名映射
新版字段常出现“旧字段名 + 下划线 `_`”的模式。
此时必须在 `FIELD_ALIAS_MAP` 中补别名，不然这些字段会全部导出为空。

当前已确认并已落地的一组关键别名是 `QY` 段（取样）字段。

### 4. 当前已确认的关键映射结论

#### 4.1 QY（取样）
新版 `z_c_QuYang` 中，大量字段是旧接口字段名后面多一个下划线：
- `QYZLMD -> QYZLMD_`
- `QYBZ -> QYBZ_`
- `QYHSL -> QYHSL_`
- `QYYX -> QYYX_`
- `QYSY -> QYSY_`
- `QYZXMD -> QYZXMD_`
- `QYZDMD -> QYZDMD_`
- `QYXZJ1 -> QYXZJ1_`
- `QYXZJ2 -> QYXZJ2_`
- `QYSTXS -> QYSTXS_`
- `QYSPSTXS -> QYSPSTXS_`
- `QYCZSTXS -> QYCZSTXS_`
- `QYDZKYQD -> QYDZKYQD_`
- `QYZRKYQD -> QYZRKYQD_`
- `QYBHKYQD -> QYBHKYQD_`
- `QYKLQD -> QYKLQD_`
- `QYKJQD -> QYKJQD_`
- `QYRHQD -> QYRHQD_`
- `QYZCMZL -> QYZCMZL_`
- `QYZDZL -> QYZDZL_`
- `QYSZBQD -> QYSZBQD_`
- `QYKYDYZ -> QYKYDYZ_`
- `QYKYDCS -> QYKYDCS_`
- `QYLMD -> QYLMD_`
- `QYTSL -> QYTSL_`
- `QYJQBS -> QYJQBS_`
- `QYZBBS -> QYZBBS_`
- `QYDTML -> QYDTML_`
- `QYDJML -> QYDJML_`
- `QYBSB -> QYBSB_`
- `QYHTML -> QYHTML_`
- `QYYJZHL -> QYYJZHL_`
- `QYHYL -> QYHYL_`
- `QYCZBCBR25 -> QYCZBCBR25_`
- `QYCZBCBR5 -> QYCZBCBR5_`
- `QYTXKLXS -> QYTXKLXS_`
- `QYXSL -> QYXSL_`
- `QYBHXSL -> QYBHXSL_`

#### 4.2 GJ / GY（固结相关）
`z_c_GuJie` 与 `z_c_GuJieShP` 的字段体系变化很大。
当前结论：
- 不能只靠同名自动映射
- 不能宣称已完成业务映射
- 暂时采用“同名直映射 + 其余留空”的保守策略
- 若用户要求高精度导入，必须让用户确认旧粒径段与新版字段组的业务对应关系

#### 4.3 GC / TC / ZK / BG / SW
这些段当前是“可导出但存在缺字段”的状态：
- `GC`：有多项工程信息字段在新版样本中不存在
- `TC`：部分描述类字段缺失
- `ZK`：个别字段缺失，如 `ZKPIL` / `ZKHSBG` / `ZKTJSD`
- `BG`：`BGYZJS` 可能缺失
- `SW`：`SWDXSW` 可能缺失

因此要区分：
- “已成功导出 TXT”
- 和 “已 100% 完成所有字段业务映射”

## Recommended Workflow

### A. 审查阶段
1. 找到输入 `.mdb`
2. 确认旧版接口规范文件存在
3. 读取当前脚本 `/opt/hermes/convert_new_mdb_to_old.py`
4. 审查：
   - `SECTIONS` 是否与接口段一致
   - `FIELD_ALIAS_MAP` 是否覆盖关键别名
   - 是否存在多余字段名示例行
   - 是否存在 `#段标记#` 与首字段之间的多余 Tab
   - 是否存在钻孔项目分组规则错误

### B. 运行阶段
1. 运行脚本（GUI 版由用户弹窗选择 `.mdb`）
2. 输出到源库同目录，文件名类似：
   - `<数据库名>_旧版接口_<时间戳>.txt`
3. 编码：`gb18030`

### C. 验证阶段
至少检查：
1. 文件已生成
2. 头几行是否为真实数据而不是字段示例
3. `#GC#` / `#ZK#` 后是否直接接数据
4. 对 `TC/BG/DT/SW` 等段：
   - 是否出现独立的 `#ZK#钻孔编号`
   - 后续项目是否另起一行
   - 是否没有多余空行
5. 若用户给了样本库，抽样检查 `QY` 字段不再因下划线问题全部为空

## Practical Commands

### 1. 语法检查
```bash
python3 -m py_compile /opt/hermes/convert_new_mdb_to_old.py
```

### 2. 在无桌面环境下自动执行导出
如果当前环境没有 GUI / `tkinter` 不可用，可以在自动化验证时 stub 掉 `tkinter`，然后直接 import 主脚本中的 `AccessTxtExporter` 来生成 TXT。

### 3. 快速检查生成文件开头
```bash
python3 - <<'PY'
from pathlib import Path
p = Path('/path/to/output.txt')
with open(p, 'r', encoding='gb18030', errors='replace') as f:
    for i in range(15):
        print(f.readline().rstrip())
PY
```

## Common Pitfalls

1. **把接口字段名示例行也输出进 TXT**
   - 这是错的，接口文件里应直接写真实数据。

2. **在 `#GC#` 和首字段之间插入 Tab**
   - 错误：`#GC#\t详细勘察`
   - 正确：`#GC#详细勘察`

3. **钻孔下属项目每行都重复加 `#ZK#钻孔编号`**
   - 错误。
   - 正确做法是：项目块开始前单独一行输出一次。

4. **写文件换行处理错误，造成双空行**
   - 不要同时设置 `newline='\r\n'` 和手工拼接 `\r\n`。

5. **把“导出成功”误当成“映射完全正确”**
   - 对 `GJ/GY` 等复杂段，仍需业务确认。

## Verification Checklist

- [ ] 输入文件是 `.mdb`
- [ ] 读取后端是 `mdbtools`
- [ ] 输出编码是 `gb18030`
- [ ] TXT 中不包含字段名示例行
- [ ] `#段标记#` 后直接接首字段值
- [ ] 钻孔主记录为 `#ZK#钻孔编号\t...`
- [ ] 钻孔下属项目块前单独有 `#ZK#钻孔编号`
- [ ] 同钻孔同项目块内不重复输出 `#ZK#钻孔编号`
- [ ] `QY` 段尾部下划线别名映射已生效
- [ ] 复杂段 (`GJ/GY`) 未被错误宣称为“已完整映射”
