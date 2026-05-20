#!/usr/bin/env python3
"""
从新版 Access MDB 数据库导出“旧版软件读入接口 TXT 文件”。

按用户要求：
1. 强制使用 mdbtools，不使用 ODBC；
2. 运行时弹窗选择新版数据库文件；
3. 输出 TXT 自动放在数据库所在目录；
4. 完成后弹窗提示结果；
5. 默认输出编码 gb18030。

依赖：
- mdbtools（需要 mdb-tables、mdb-json 可执行）
- Python 标准库 tkinter（用于文件选择和提示框）

说明：
- 当前脚本面向 .mdb 文件；
- 复杂字段仍采用“同名优先，不存在留空”的保守策略；
- 若后续确认了复杂字段映射，可在 FIELD_ALIAS_MAP 中补充。
"""

from __future__ import annotations

import datetime as _dt
import json
import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from tkinter import Tk, filedialog, messagebox
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class SectionSpec:
    id: str
    marker: str
    tag: str
    table: str
    fields: List[str]

    @property
    def record_prefix(self) -> str:
        return f"{self.marker}{self.tag}{self.marker}"


SECTIONS: List[SectionSpec] = [
    SectionSpec("GC", "#", "GC", "x_GongCheng", ["GCKCJD", "GCJSDW", "GCSJDW", "GCKCDW", "GCSGDW", "GCDD", "GCX", "GCY", "GCBG", "GCQSLC", "GCJSLC", "GCZXDH", "GCZXLC", "GCZXLX", "GCZXSM", "GCYX", "GCZBZ", "GCBLC", "GCBZ", "KGRQ", "WGRQ"]),
    SectionSpec("ZK", "#", "ZK", "z_ZuanKong", ["ZKBH", "ZKLX", "ZKX", "ZKY", "ZKPIL", "ZKBG", "ZKHSBG", "ZKSD", "ZKTJSD", "ZKZJ", "ZKKSRQ", "ZKZZRQ"]),
    SectionSpec("TC", "#", "TC", "z_g_TuCeng", ["TCMC", "TCCDSD", "TCHD", "TCZCBH", "TCYCBH", "TCCYCBH", "TCDZSD", "TCDZCY", "TCYS", "TCMSD", "TCSID", "TCKSX", "TCHYD", "TCJYX", "TCFHCD", "TCYSQX", "TCYSQJ", "TCKWCF", "TCJGGZ", "TCBHW", "TCQW", "TCMS", "TCZTX", "TCJYCD", "TCPL", "TCJLFY", "TCJLJJ"]),
    SectionSpec("JT", "#", "JT", "z_y_JingTan", ["JTDSD", "JTLX", "JTZTZL", "JTCMZ", "JTBGRZL"]),
    SectionSpec("BG", "#", "BG", "z_y_BiaoGuan", ["BGDSD", "BGLX", "BGTZZ", "BGGC", "BGYZCD", "BGYZJS", "BGJS", "BGXS", "BGXZJS", "BGSXZ", "CY"]),
    SectionSpec("DT", "#", "DT", "z_y_DongTan", ["DTDSD", "DTLX", "DTGC", "DTCD", "DTYZJS", "DTGRD", "DTJS", "DTXZJS", "DTXZ", "CY"]),
    SectionSpec("SW", "#", "SW", "z_g_ShuiWei", ["SWSD", "SWLX", "SWCH", "SWCSRQ", "SWDXSW", "SWFW", "SWXZ", "CY"]),
    SectionSpec("BS", "#", "BS", "z_y_BoSu", ["BSSD", "BSHBS", "BSZBS", "BSSHB", "BSSZB"]),
    SectionSpec("CS", "#", "CS", "z_g_ChaoShiDu", ["CSDSD", "CSD", "CY"]),
    SectionSpec("FH", "#", "FH", "z_g_FengHua", ["FHSD", "FHCD", "FHCH", "CY", "BZ"]),
    SectionSpec("KS", "#", "KS", "z_g_KeSuXing", ["KSXSD", "KSX", "CY"]),
    SectionSpec("U1", "#", "U1", "z_g_User1", ["USRSD", "VALUE", "CY"]),
    SectionSpec("U2", "#", "U2", "z_g_User2", ["USRSD", "VALUE", "CY"]),
    SectionSpec("LF", "#", "LF", "z_y_LFMiDu", ["LFDSD", "LFDMD", "LFDQJ", "LFDZJ", "CY", "BZ"]),
    SectionSpec("ST", "#", "ST", "z_y_STXiShu", ["CTXSD", "CTXFA", "CTXK", "CTXSP", "CTXSZ", "CY", "BZ"]),
    SectionSpec("TS", "#", "TS", "z_y_TouShuiLv", ["TSLSD", "TSLFA", "TSTZZ", "TSLV", "TSLV1", "CY"]),
    SectionSpec("YR", "#", "YR", "z_g_YXRQD", ["YRSD", "YRCQL", "YRRQD", "YRSCQL", "YRSRQD", "BZ"]),
    SectionSpec("SB", "#", "SB", "z_y_ShiZiBan", ["SZBSD", "SZBFA", "SZBQD", "SZBCQD", "CY"]),
    SectionSpec("QY", "#", "QY", "z_c_QuYang", ["QYBH", "QYSD", "QYHD", "QYLX", "QYZLMD", "QYBZ", "QYHSL", "QYYX", "QYSY", "QYZXMD", "QYZDMD", "QYXZJ1", "QYXZJ2", "QYSTXS", "QYSPSTXS", "QYCZSTXS", "QYDZKYQD", "QYZRKYQD", "QYBHKYQD", "QYKLQD", "QYKJQD", "QYRHQD", "QYZCMZL", "QYZDZL", "QYSZBQD", "QYKYDYZ", "QYKYDCS", "QYLMD", "QYTSL", "QYJQBS", "QYZBBS", "QYDTML", "QYDJML", "QYBSB", "QYHTML", "QYYJZHL", "QYHYL", "QYCZBCBR25", "QYCZBCBR5", "QYTXKLXS", "QYXSL", "QYBHXSL"]),
    SectionSpec("SX", "#", "SX", "z_c_ShiXian", ["SXJSYL", "SXXS", "SXSX02", "SXSX03", "SXZXS", "SXQSYL"]),
    SectionSpec("GJ", "#", "GJ", "z_c_GuJie", ["GJSYFF", "GJSYGD", "GJZZP0", "GJXSP0005", "GJMLP0005", "GJXS00501", "GJML00501", "GJXS0102", "GJML0102", "GJXS0203", "GJML0203", "GJXS0304", "GJML0304", "GJXS0405", "GJML0405", "GJXS0506", "GJML0506", "GJKXBP0", "GJKXB005", "GJKXB01", "GJKXB02", "GJKXB03", "GJKXB04", "GJKXB05", "GJKXB06", "GJBXML", "GJTXML", "GJBSB", "GJYSZS", "GJHTZS", "GJQQGJYL", "GJKXSYLXSA", "GJKXSYLXSB", "GJSXXISHU", "GJHXXISHU", "GJXS005", "GJXS01", "GJXS02", "GJXS03", "GJXS04", "GJXS05", "GJXS08", "GJXS0204", "GJML0204", "GJXS0406", "GJML0406", "GJXSP0_005", "GJMLP0_005", "GJXSP0_01", "GJMLP0_01", "GJXSP0_02", "GJMLP0_02", "GJXSP0_03", "GJMLP0_03", "GJXSP0_04", "GJMLP0_04", "GJXSP0_05", "GJMLP0_05", "GJXSP0_08", "GJMLP0_08", "GJXSP0_16", "GJMLP0_16", "GJXSP0_32", "GJMLP0_32", "GJUSER1", "GJUSER2", "GJUSER3", "GJUSER4", "GJUSER5", "GJUSER6", "GJMEM"]),
    SectionSpec("GY", "#", "GY", "z_c_GuJieShP", ["GJXS0408", "GJML0408", "GJXS0508", "GJML0508", "GJXS0816", "GJML0816", "GJXS1632", "GJML1632", "GJXS0608", "GJML0608", "GJXS0810", "GJML0810", "GJXS0812", "GJML0812", "GJXS1012", "GJML1012", "GJXS1216", "GJML1216", "GJKXB08", "GJKXB10", "GJKXB12", "GJKXB16", "GJKXB32", "GJXS1632", "GJML1632", "GJXS3264", "GJML3264"]),
    SectionSpec("GJ_DETAIL", "%", "GJ", "z_c_GuJieCSXM", ["XH", "GJCZYL", "GJYSBX"]),
    SectionSpec("KF", "#", "KF", "z_c_KeFen", ["KLSYFF", "KL800", "KL400", "KL200", "KL60", "KL40", "KL20", "KL10", "KL5", "KL2", "KL1", "KL_5", "KL_25", "KL_1", "KL_075", "KL_074", "KL_05", "KL_01", "KL_005", "KL_002", "KL0", "KLD10", "KLD15", "KLD30", "KLD50", "KLD60", "KLD85", "KLD90", "KLD95", "KLHL", "KLBJXS", "KLQLXS", "KLTYZL"]),
    SectionSpec("KF_DETAIL", "%", "KF", "z_c_KeFenCSXM", ["XH", "KLLJ", "KLSYZL"]),
    SectionSpec("ZJ", "#", "ZJ", "z_c_ZhiJian", ["ZJSYFF", "ZJMJ", "ZJNMJ00", "ZJNJL00", "ZJNMJ10", "ZJNJL10", "ZJNMJ11", "ZJNJL11"]),
    SectionSpec("ZJ_DETAIL", "%", "ZJ", "z_c_ZhiJianCSXM", ["XH", "ZJCZYL", "ZJYBXS", "ZJYBDS", "ZJKJQD"]),
    SectionSpec("ZH", "#", "ZH", "z_c_ShuiZhi", ["SZSA", "SZQSSD", "SZQW", "SZSW", "SZHW", "SZQSRQ", "SZSYRQ", "SZBGRQ", "SZQN", "SZKW", "SZSD", "SZTMD", "SZHZD", "SZPDJG"]),
    SectionSpec("ZH_DETAIL", "%", "ZH", "z_c_ShuiZhiCSXM", ["SZCSXM", "SZCSJG", "SZCSLB", "SZCSFF"]),
    SectionSpec("PY", "#", "PY", "z_y_PangYa", ["PYBH", "PYDSD", "PYYQBH", "PYSYRQ", "PYKKJL", "PYJSYL", "PYSPCYL", "PYTYL", "PYLSYL", "PYJXYL", "PYLSCZL", "PYJXCZL", "PYKJQD", "PYCYLXS", "PYML", "CY"]),
    SectionSpec("PY_DETAIL", "%", "PY", "z_y_PangYaCSXM", ["PYXH", "PYYL", "PYTJ1", "PYTJ2"]),
    SectionSpec("SZ", "#", "SZ", "z_c_SanZhou", ["SYFF", "SYRQ", "SHZF01", "SHZC00", "SHZF11", "SHZC10", "SHZF21", "SHZC20", "SHZC30", "SHZF31", "SHZC00_", "SHZF01_", "SHZC10_", "SHZF11_", "SHZC20_", "SHZF21_", "SHZC30_", "SHZF31_"]),
    SectionSpec("SZ_DETAIL", "%", "SZ", "z_c_SanZhouCSXM", ["SJBH", "SHJHXH", "SHWY", "SHYSGD", "SHYSZJ", "SHCXS", "SHKXYL", "SHCLHDS", "SHZXDS", "SHTJBH", "SHKXDS", "SHLSDS", "SHCSTZ"]),
    SectionSpec("PH", "#", "PH", "z_y_ZaiHe", ["ZHBH", "ZHYBXZ", "ZHBG", "ZHSYWZ", "ZHSYSD", "ZHTCMC", "ZHBSB", "ZHYBMJ", "ZHSBXH", "ZHSBZZ", "ZHJZFS", "ZHGCYQ", "ZHWDBZ", "ZHKSRQ", "ZHSYSS", "ZHDXSS", "ZHYSJJ", "ZHYSXL", "ZHXZXL", "ZHTXYL", "ZHJXYL", "ZHBXML", "ZHCZL", "ZHSFXZ"]),
    SectionSpec("PH_DETAIL", "%", "PH", "z_y_ZaiHeSnsy", ["ZHQYBH", "ZHQYXH", "ZHSNCY", "ZHTRHSL", "ZHTRZD", "ZHBHD", "ZHTRKXB", "ZHYX", "ZHSX", "ZHYXZS", "ZHSXZS", "ZHYSXS"]),
    SectionSpec("PP", "%", "PP", "z_y_ZaiHeSyCg", ["ZHZHXH", "ZHCGCY", "ZHZHDX", "ZHSJCD", "ZHLJCJL", "ZHZLCJL", "ZHJZCJL", "ZHJZZL"]),
    SectionSpec("PJ", "%", "PJ", "z_y_ZaiHeSyjilu", ["ZHZHXH", "ZHJLXH", "ZHSKCY", "ZHJHSJ", "ZHJHCJL", "ZHJHCJLXZ", "ZHCJWD"]),
    SectionSpec("PZ", "#", "PZ", "z_c_PengZhangTu", ["PZZYPZL", "PZHZPZL", "PZSSXS", "PZPZYL", "PZXZL", "PZTSL"]),
]

FIELD_ALIAS_MAP: Dict[str, Dict[str, Optional[str]]] = {
    "QY": {
        "QYZLMD": "QYZLMD_",
        "QYBZ": "QYBZ_",
        "QYHSL": "QYHSL_",
        "QYYX": "QYYX_",
        "QYSY": "QYSY_",
        "QYZXMD": "QYZXMD_",
        "QYZDMD": "QYZDMD_",
        "QYXZJ1": "QYXZJ1_",
        "QYXZJ2": "QYXZJ2_",
        "QYSTXS": "QYSTXS_",
        "QYSPSTXS": "QYSPSTXS_",
        "QYCZSTXS": "QYCZSTXS_",
        "QYDZKYQD": "QYDZKYQD_",
        "QYZRKYQD": "QYZRKYQD_",
        "QYBHKYQD": "QYBHKYQD_",
        "QYKLQD": "QYKLQD_",
        "QYKJQD": "QYKJQD_",
        "QYRHQD": "QYRHQD_",
        "QYZCMZL": "QYZCMZL_",
        "QYZDZL": "QYZDZL_",
        "QYSZBQD": "QYSZBQD_",
        "QYKYDYZ": "QYKYDYZ_",
        "QYKYDCS": "QYKYDCS_",
        "QYLMD": "QYLMD_",
        "QYTSL": "QYTSL_",
        "QYJQBS": "QYJQBS_",
        "QYZBBS": "QYZBBS_",
        "QYDTML": "QYDTML_",
        "QYDJML": "QYDJML_",
        "QYBSB": "QYBSB_",
        "QYHTML": "QYHTML_",
        "QYYJZHL": "QYYJZHL_",
        "QYHYL": "QYHYL_",
        "QYCZBCBR25": "QYCZBCBR25_",
        "QYCZBCBR5": "QYCZBCBR5_",
        "QYTXKLXS": "QYTXKLXS_",
        "QYXSL": "QYXSL_",
        "QYBHXSL": "QYBHXSL_",
    },
    "GJ": {},
    "GY": {},
}


class MDBToolsReader:
    def __init__(self, db_path: str):
        self.db_path = os.path.abspath(db_path)
        self.mdb_tables_bin = self._find_bin("mdb-tables")
        self.mdb_json_bin = self._find_bin("mdb-json")
        self.env = os.environ.copy()
        extra_lib = self._guess_ld_library_path()
        if extra_lib:
            self.env["LD_LIBRARY_PATH"] = extra_lib + ((":" + self.env["LD_LIBRARY_PATH"]) if self.env.get("LD_LIBRARY_PATH") else "")
        self._tables: Optional[set[str]] = None
        self._cache: Dict[str, List[Dict[str, Any]]] = {}

    @staticmethod
    def _find_bin(name: str) -> str:
        candidates = [
            shutil.which(name),
            f"/tmp/mdbdl/mdbtools/usr/bin/{name}",
        ]
        for path in candidates:
            if path and os.path.exists(path):
                return path
        raise FileNotFoundError(f"找不到 {name}，请先安装 mdbtools。")

    @staticmethod
    def _guess_ld_library_path() -> str:
        libs = [
            "/tmp/mdbdl/libmdb3/usr/lib/x86_64-linux-gnu",
            "/tmp/mdbdl/libmdbsql3/usr/lib/x86_64-linux-gnu",
        ]
        return ":".join(p for p in libs if os.path.isdir(p))

    def _run(self, args: List[str]) -> str:
        proc = subprocess.run(args, capture_output=True, text=True, env=self.env)
        if proc.returncode != 0:
            raise RuntimeError(proc.stderr.strip() or proc.stdout.strip() or f"命令失败: {' '.join(args)}")
        return proc.stdout

    def _load_tables(self) -> set[str]:
        if self._tables is None:
            out = self._run([self.mdb_tables_bin, "-1", self.db_path])
            self._tables = {line.strip() for line in out.splitlines() if line.strip()}
        return self._tables

    def table_exists(self, table: str) -> bool:
        return table in self._load_tables()

    def fetch_rows(self, table: str) -> List[Dict[str, Any]]:
        if table not in self._cache:
            out = self._run([self.mdb_json_bin, self.db_path, table])
            rows: List[Dict[str, Any]] = []
            for line in out.splitlines():
                line = line.strip()
                if not line:
                    continue
                rows.append(json.loads(line))
            self._cache[table] = rows
        return self._cache[table]


class AccessTxtExporter:
    def __init__(self, db_path: str, output_path: str, gcsy: Optional[int] = None, encoding: str = "gb18030", include_empty_sections: bool = False):
        self.db_path = os.path.abspath(db_path)
        self.output_path = os.path.abspath(output_path)
        self.gcsy = gcsy
        self.encoding = encoding
        self.include_empty_sections = include_empty_sections
        self.reader = MDBToolsReader(self.db_path)

    @staticmethod
    def format_value(value: Any) -> str:
        if value is None:
            return ""
        if isinstance(value, bool):
            return "1" if value else "0"
        if isinstance(value, (_dt.datetime, _dt.date)):
            return value.strftime("%Y-%m-%d")
        if isinstance(value, float):
            text = format(value, ".15g")
            return "0" if text == "-0" else text
        if isinstance(value, Decimal):
            text = format(value, "f").rstrip("0").rstrip(".")
            return text or "0"
        text = str(value)
        return text.replace("\r\n", " ").replace("\n", " ").replace("\r", " ").replace("\t", " ").strip()

    def row_to_interface_values(self, section: SectionSpec, row: Dict[str, Any]) -> List[str]:
        aliases = FIELD_ALIAS_MAP.get(section.id, {})
        source_map = {k.upper(): v for k, v in row.items()}
        out: List[str] = []
        for field in section.fields:
            source_field = aliases.get(field, field)
            out.append("" if source_field is None else self.format_value(source_map.get(source_field.upper())))
        return out

    def build_record_line(self, section: SectionSpec, row: Dict[str, Any]) -> str:
        values = self.row_to_interface_values(section, row)
        line = section.record_prefix
        if values:
            line += values[0]
            if len(values) > 1:
                line += "\t" + "\t".join(values[1:])
        return line

    def _filter_rows(self, rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        if self.gcsy is None:
            return rows
        result: List[Dict[str, Any]] = []
        for row in rows:
            upper = {k.upper(): v for k, v in row.items()}
            if "GCSY" in upper and str(upper["GCSY"]) != str(self.gcsy):
                continue
            result.append(row)
        return result

    def export(self) -> List[str]:
        lines: List[str] = []
        lines.append("; 由 Hermes 生成：新版 MDB -> 旧版理正接口 TXT")
        lines.append(f"; 数据源: {self.db_path}")
        lines.append("; 读取后端: mdbtools")
        if self.gcsy is not None:
            lines.append(f"; 过滤条件: gcsy = {self.gcsy}")
        lines.append(f"; 生成时间: {_dt.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        summary: List[str] = []
        for section in SECTIONS:
            rows = self._filter_rows(self.reader.fetch_rows(section.table)) if self.reader.table_exists(section.table) else []
            if rows:
                if section.id != "ZK" and any("ZKBH" in {k.upper() for k in row.keys()} for row in rows):
                    current_zkbh = None
                    for row in rows:
                        source_map = {k.upper(): v for k, v in row.items()}
                        zkbh = self.format_value(source_map.get("ZKBH"))
                        if zkbh != current_zkbh:
                            current_zkbh = zkbh
                            if zkbh:
                                lines.append(f"#ZK#{zkbh}")
                        lines.append(self.build_record_line(section, row))
                else:
                    for row in rows:
                        lines.append(self.build_record_line(section, row))
            elif self.include_empty_sections:
                lines.append(section.record_prefix)
                lines.append("")
            summary.append(f"{section.id}:{section.table} -> {len(rows)} 行")

        os.makedirs(os.path.dirname(self.output_path) or ".", exist_ok=True)
        with open(self.output_path, "w", encoding=self.encoding, newline="") as f:
            f.write("\r\n".join(lines).rstrip() + "\r\n")
        return summary


def choose_input_file() -> Optional[str]:
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    path = filedialog.askopenfilename(
        title="选择新版数据库文件",
        filetypes=[("Access 数据库", "*.mdb"), ("所有文件", "*.*")],
    )
    root.destroy()
    return path or None


def build_output_path(db_path: str) -> str:
    p = Path(db_path)
    stem = p.stem
    ts = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    return str(p.with_name(f"{stem}_旧版接口_{ts}.txt"))


def show_info(title: str, message: str) -> None:
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    messagebox.showinfo(title, message)
    root.destroy()


def show_error(title: str, message: str) -> None:
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)
    messagebox.showerror(title, message)
    root.destroy()


def main() -> None:
    db_path = choose_input_file()
    if not db_path:
        return
    if not db_path.lower().endswith(".mdb"):
        show_error("文件类型不支持", "当前脚本仅支持 .mdb 文件，并且强制使用 mdbtools。")
        return

    output_path = build_output_path(db_path)
    try:
        exporter = AccessTxtExporter(db_path=db_path, output_path=output_path)
        summary = exporter.export()
        brief = "\n".join(summary[:12])
        if len(summary) > 12:
            brief += f"\n... 共 {len(summary)} 个分段"
        show_info(
            "导出完成",
            f"旧版接口 TXT 已生成。\n\n输入文件：\n{db_path}\n\n输出文件：\n{output_path}\n\n分段统计：\n{brief}",
        )
    except Exception as e:
        show_error("导出失败", f"生成旧版接口 TXT 失败：\n\n{e}")
        raise


if __name__ == "__main__":
    main()
