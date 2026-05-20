# 新版 MDB → 旧版 MDB 映射分析报告

## 1. 文件概况

- 旧版数据库：`/opt/data/cache/documents/doc_cc55439b1e05_旧版.mdb`
- 新版数据库：`/opt/data/cache/documents/doc_41e1406aaae1_新版.mdb`

统计结果：

- 旧版表数：87
- 新版表数：438
- 同名表数：72
- 仅旧版存在：15
- 仅新版存在：366

## 2. 总体结论

这两个数据库**不是简单的一对一结构升级**，而是：

1. **新版库大幅扩展**，新增了大量业务表；
2. 大多数旧版同名表在新版中仍然存在，但通常：
   - 保留旧字段；
   - 追加一批新字段；
   - 个别表发生字段重排或字段语义体系变化；
3. 因此“新版转旧版”的总体策略应当是：
   - **以旧版库作为模板**；
   - **只把旧版需要的字段从新版抽取出来写回旧版结构**；
   - 新版新增字段直接丢弃；
   - 旧版存在但新版没有的配置表，保留旧版模板原值。

## 3. 可直接自动映射的主要模式

### 模式 A：新版只是比旧版多一个 `lzid`
这类表最容易处理。旧版字段几乎全部保留，新版只是在尾部新增 `lzid`。

典型表：

- `d_DZBuLiang`
- `d_DZDuanCeng`
- `d_DZGouZao`
- `d_DZSDCY`
- `d_DZTaKan`
- `d_DZZhenZhong`
- `d_XZZT`
- `d_XZZTTuceng`
- `g_CeLiangDian`
- `g_JiChu`
- `g_JTTjzTcmDuizhao`
- `p_Connect`
- `p_JiChuBiaoGao`
- `p_SheJiBiaoGao`
- `x_MuLu`
- `z_g_CengJiLu`
- `z_g_ChaoShiDu`
- `z_g_FengHua`
- `z_g_KeSuXing`
- `z_g_KongJin`
- `z_g_TempTuCeng`
- `z_g_User1`
- `z_g_User2`
- 以及大量 `z_c_*`、`z_y_*` 表

这类表可以直接按**旧字段名从新版同名字段读取**。

---

### 模式 B：新版在保留旧字段的基础上追加扩展字段
这类表也可以自动转换，因为旧字段仍然保留，只需忽略新增列。

典型表：

- `g_PeiZhi`
- `g_SJDuiZhao`
- `g_STuCengGC`
- `g_ZiDuan`
- `p_DiMianXian`
- `p_DunTai`
- `x_FenDuan`
- `x_SheJi`
- `z_g_ShuiWei`
- `z_g_YXRQD`
- `z_y_YeHua`
- `z_y_JingTan`
- `z_y_DongTan`
- `z_y_PangYa`
- `z_y_BiaoGuan`
- `z_y_TouShuiLv`
- `z_y_STXiShu`
- `z_y_ShiZiBan`
- `z_y_ZaiHe*`

这类表脚本同样可以自动做：**仅写入旧版字段集合**。

## 4. 需要重点注意的特殊表

### 4.1 `p_DiZhiTeZheng`
旧版字段：
- `gcsy, dzbh, dzlx, qsdh, qslc, zzdh, zzlc, dztz`

新版字段：
- `gcsy, dzbh, qsdh, qslc, zzdh, zzlc, dztz, lzid`

差异：
- 旧版有 `dzlx`
- 新版没有 `dzlx`

当前脚本处理：
- `dzlx` 暂时写 `NULL`

如果你知道 `dzlx` 在新版对应哪个字段或可由哪个规则推导，需要再补业务映射。

---

### 4.2 `z_c_GuJie`
这是**变化最大**的一类表之一。

旧版使用大量粒径区间命名字段，如：
- `gjxs00501`
- `gjml00501`
- `gjkxb005`
- `gjxs0608`
- `gjml0608`
- `gjxs128256`
- ...

新版改成了新的“分组/序号式”命名，如：
- `gjxsxm1..gjxsxm25`
- `gjmlxm1..gjmlxm25`
- `gjkxbxm1..gjkxbxm25`
- `sxgjxs1..sxgjxs25`
- 以及 `...99`

这说明：
- 字段**不是简单同名追加**；
- 更像是新版把旧版离散粒径字段重构成了新的项目化字段体系；
- 需要人工确认“旧粒径段 ↔ 新 xmx 编号”的业务对照表。

当前脚本策略：
- 同名字段自动映射；
- 旧版独有字段先写 `NULL`；
- 等你提供规则后，可在脚本 `EXPLICIT_FIELD_MAP` 中补齐。

---

### 4.3 `z_c_GuJieShP`
与 `z_c_GuJie` 类似，也是**字段体系重命名**。

需要业务确认后再做完整映射。

---

### 4.4 `z_c_QuYang`
行数：
- 旧版：122
- 新版：113

这说明不仅字段变了，**数据记录数也不同**，意味着可能存在：
- 记录合并/拆分
- 新版过滤逻辑不同
- 采样数据结构变化

另外旧版有以下字段在新版中缺失：
- `md_`
- `hsl_`
- `kxb_`
- `rz_`
- `kxd_`
- `bhd_`
- `gmd_`
- `gzd_`
- `bhmd_`
- `bhzd_`
- `yx_`
- `sx_`
- `yxzs_`
- `sxzs_`
- `hsb_`
- `yxb_`
- `zxmd_`
- `zdmd_`
- `zxkxb_`
- `zdkxb_`
- `xdmd_`
- `xzj1_`
- `xzj2_`
- `dzkyqd_`
- `zrkyqd_`
- `bhkyqd_`
- `rhqd_`
- `stxs_`
- `spstxs_`
- `czstxs_`
- `yxkxb_`

这部分不能靠字段名自动猜测，需要你补充业务含义。

## 5. 旧版独有表（新版中不存在）

以下 15 张表仅存在于旧版库：

- `g_BiaoLie`
- `g_BiaoTou`
- `g_DiZhi`
- `g_DuiZhao`
- `g_DuiZhaoDZSD`
- `g_OrgTree`
- `g_STuCeng`
- `g_SubTree`
- `g_TableName`
- `g_XiaoShuDian`
- `g_YanXing`
- `g_ZPTou`
- `g_ZZTTK`
- `g_ZztBiaoLie`
- `g_ZztBiaoTou`

这些表看起来大多属于：
- 配置表
- 字典表
- 报表/展示表头配置
- 岩性/对照元数据

建议处理方式：
- **保留旧版模板库中的原值**；
- 不要从新版强行映射。

## 6. 已编写的转换脚本

生成文件：

- `/opt/hermes/convert_new_mdb_to_old.py`

脚本策略：

1. 复制旧版 MDB 作为输出模板；
2. 用 ODBC 同时读取新版 MDB 和输出 MDB；
3. 对同名表：
   - 优先按旧字段名从新版同名字段读取；
   - 若配置了显式映射，则按显式映射；
   - 若旧字段在新版不存在，则写 `NULL`；
4. 对旧版特有表：
   - 保留模板中的原始数据不动；
5. 对新版特有表：
   - 不写入旧版。

## 7. 当前脚本的限制

当前脚本已经足够实现**第一版自动转换框架**，但还不能保证 100% 业务正确，主要限制在：

1. **需要 Windows + Access ODBC 驱动** 才能直接运行写回 MDB；
2. `z_c_GuJie` / `z_c_GuJieShP` / `z_c_QuYang` / `p_DiZhiTeZheng` 这几类表仍缺少业务级映射规则；
3. 新旧库部分表记录数不同，说明可能不只是“字段变换”，还可能涉及筛选、拆分或聚合逻辑；
4. 旧版特有配置表目前采用“保留模板原值”策略，而不是从新版自动重建。

## 8. 下一步建议

如果你希望把脚本做成**真正可落地、可批量跑**的版本，建议下一步这样推进：

1. 先让我继续输出一份**逐表映射清单**；
2. 你重点确认这几类复杂表：
   - `p_DiZhiTeZheng`
   - `z_c_GuJie`
   - `z_c_GuJieShP`
   - `z_c_QuYang`
3. 你只需要告诉我：
   - 旧字段对应新版哪个字段；或
   - 旧字段如何计算得出；或
   - 某些字段允许留空
4. 我再把这些规则写进 Python 脚本，生成最终版转换器。

---

如果你愿意，我下一步可以直接继续帮你做两件事之一：

1. **把复杂表的字段逐个列出来，生成“人工确认映射表”**；
2. **把脚本再升级成带日志、异常报告、字段缺失报告的正式版本**。
