import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = "E:/Codex/Wechill/outputs/guild_salary_cycle_20260801_20260815";
const reportPath = `${outputDir}/本周期公会薪资_含所属地区_20260801_20260815.xlsx`;

const guilds = [
  [3493, "公会test", "英语区 (region=0)", "8585743", "+86 15822223333"],
  [3512, "记得记得", "中东区 (region=2)", "8534705", "+212 16388889999"],
  [3525, "测试", "英语区 (region=0)", "8573893", "+86 13710000001"],
  [3529, "leon guild", "英语区 (region=0)", "8501168", "+86 15200711071"],
  [3541, "英语区自由政策", "英语区 (region=0)", "8511452", "+86 13110011001"],
  [3551, "会背唐诗吗", "中东区 (region=2)", "8578702", "+86 19521222228"],
  [3552, "英语区自由结算", "英语区 (region=0)", "8539314", "+86 13110011022"],
  [3558, "Yoww", "中东区 (region=2)", "8595978", "+86 13800138034"],
  [3560, "Yowwn", "中东区 (region=2)", "8532988", "+86 13800138033"],
  [3562, "Yowwwww", "中东区 (region=2)", "8549370", "+86 13800138031"],
  [3569, "新中东区公会长自由结算", "中东区 (region=2)", "8523877", "+86 13800138035"],
  [3575, "Yomwe", "英语区 (region=0)", "8536064", "+86 13800138018"],
];

const members = [
  [3493, "公会test", "英语区 (region=0)", 15668, "8520365", "双周政策", 0.02, 0, "已确认", ""],
  [3512, "记得记得", "中东区 (region=2)", 16425, "8503012", "自由政策", 0.04, 0, "已确认", ""],
  [3525, "测试", "英语区 (region=0)", 15636, "8573893", "自由政策", 0.02, 0, "已确认", ""],
  [3529, "leon guild", "英语区 (region=0)", 15672, "8501168", "自由政策", 84.35, 0, "待复核", "本期 gain_coin 为负，公会长分成待复核"],
  [3529, "leon guild", "英语区 (region=0)", 15686, "8514466", "双周政策", 89.11, 0, "待复核", "本期 gain_coin 为负，公会长分成待复核"],
  [3529, "leon guild", "英语区 (region=0)", 15687, "8558717", "自由政策", 84.35, 0, "待复核", "本期 gain_coin 为负，公会长分成待复核"],
  [3529, "leon guild", "英语区 (region=0)", 15688, "8597570", "双周政策", 89.11, 0, "待复核", "本期 gain_coin 为负，公会长分成待复核"],
  [3529, "leon guild", "英语区 (region=0)", 15689, "8526429", "自由政策", 73.07, 0, "已确认", ""],
  [3529, "leon guild", "英语区 (region=0)", 15692, "8596889", "自由政策", 84.35, 0, "待复核", "本期 gain_coin 为负，公会长分成待复核"],
  [3541, "英语区自由政策", "英语区 (region=0)", 16418, "8511452", "自由政策", 84.35, 0, "待复核", "本期 gain_coin 为负，公会长分成待复核"],
  [3541, "英语区自由政策", "英语区 (region=0)", 16422, "8540644", "双周政策", 89.11, 0, "待复核", "本期 gain_coin 为负，公会长分成待复核"],
  [3541, "英语区自由政策", "英语区 (region=0)", 16423, "8587411", "自由政策", 84.35, 0, "待复核", "本期 gain_coin 为负，公会长分成待复核"],
  [3541, "英语区自由政策", "英语区 (region=0)", 16424, "8588336", "双周政策", 89.11, 0, "待复核", "本期 gain_coin 为负，公会长分成待复核"],
  [3541, "英语区自由政策", "英语区 (region=0)", 16426, "8557287", "自由政策", 84.35, 0, "待复核", "本期 gain_coin 为负，公会长分成待复核"],
  [3551, "会背唐诗吗", "中东区 (region=2)", 15682, "8588564", "双周政策", 51.53, 10.5, "已确认", ""],
  [3552, "英语区自由结算", "英语区 (region=0)", 16448, "8502216", "双周政策", 89.11, 0, "待复核", "本期 gain_coin 为负，公会长分成待复核"],
  [3552, "英语区自由结算", "英语区 (region=0)", 16459, "8539314", "自由政策", 84.35, 0, "待复核", "本期 gain_coin 为负，公会长分成待复核"],
  [3558, "Yoww", "中东区 (region=2)", 15770, "8595978", "双周政策", 96.04, 0, "待复核", "本期 gain_coin 为负，公会长分成待复核"],
  [3560, "Yowwn", "中东区 (region=2)", 15769, "8532988", "双周政策", 959, 315, "已确认", ""],
  [3562, "Yowwwww", "中东区 (region=2)", 15767, "8549370", "自由政策", 1434, 483, "已确认", ""],
  [3569, "新中东区公会长自由结算", "中东区 (region=2)", 15771, "8523877", "自由政策", 1434, 483, "已确认", ""],
  [3575, "Yomwe", "英语区 (region=0)", 15754, "8536064", "双周政策", 89.11, 0, "待复核", "本期 gain_coin 为负，公会长分成待复核"],
];

const wb = Workbook.create();
const summary = wb.worksheets.add("公会汇总");
const detail = wb.worksheets.add("成员薪资");
const notes = wb.worksheets.add("口径说明");
const moneyFormat = "$#,##0.00;[Red]($#,##0.00);-";
const dark = "#0F766E";
const mid = "#DDF4EE";
const pale = "#F4FAF8";
const amber = "#FFF3CD";
const border = { preset: "inside", style: "thin", color: "#D6E4E0" };

summary.showGridLines = false;
summary.getRange("A1:I1").merge();
summary.getRange("A1").values = [["本周期公会薪资汇总（含所属地区）"]];
summary.getRange("A1:I1").format = { fill: dark, font: { bold: true, color: "#FFFFFF", size: 16 }, horizontalAlignment: "center", verticalAlignment: "center" };
summary.getRange("A1:I1").format.rowHeight = 30;
summary.getRange("A2:I2").merge();
summary.getRange("A2").values = [["周期：2026-08-01 00:00:00 至 2026-08-16 00:00:00  |  数据源：stay 测试库  |  币种：USD"]];
summary.getRange("A2:I2").format = { fill: "#E8F5F1", font: { color: "#24564D", italic: true }, horizontalAlignment: "center" };
summary.getRange("A4:I4").values = [["公会ID", "公会名称", "所属地区", "公会长用户编号", "公会长手机号", "主播薪资", "已确认公会长分成", "已确认总薪资", "待复核成员数"]];
summary.getRange("A4:I4").format = { fill: dark, font: { bold: true, color: "#FFFFFF" }, horizontalAlignment: "center", verticalAlignment: "center", wrapText: true, borders: border };
summary.getRange("A4:I4").format.rowHeight = 28;
summary.getRange("A5:E16").values = guilds;
summary.getRange("F5").formulas = [["=SUMIF('成员薪资'!$A$5:$A$26,A5,'成员薪资'!$G$5:$G$26)"]];
summary.getRange("F5:F16").fillDown();
summary.getRange("G5").formulas = [["=SUMIF('成员薪资'!$A$5:$A$26,A5,'成员薪资'!$H$5:$H$26)"]];
summary.getRange("G5:G16").fillDown();
summary.getRange("H5").formulas = [["=F5+G5"]];
summary.getRange("H5:H16").fillDown();
summary.getRange("I5").formulas = [["=COUNTIFS('成员薪资'!$A$5:$A$26,A5,'成员薪资'!$J$5:$J$26,\"待复核\")"]];
summary.getRange("I5:I16").fillDown();
summary.getRange("A5:I16").format = { borders: border, verticalAlignment: "center" };
summary.getRange("A5:I16").format.rowHeight = 22;
summary.getRange("F5:H16").format.numberFormat = moneyFormat;
summary.getRange("F5:I16").format.horizontalAlignment = "right";
summary.getRange("A17:E17").merge();
summary.getRange("A17").values = [["合计"]];
summary.getRange("F17").formulas = [["=SUM(F5:F16)"]];
summary.getRange("G17").formulas = [["=SUM(G5:G16)"]];
summary.getRange("H17").formulas = [["=SUM(H5:H16)"]];
summary.getRange("I17").formulas = [["=SUM(I5:I16)"]];
summary.getRange("A17:I17").format = { fill: "#C6E9DF", font: { bold: true, color: "#134E4A" }, borders: { preset: "doubleBottom", style: "medium", color: "#0F766E" } };
summary.getRange("F17:H17").format.numberFormat = moneyFormat;
summary.getRange("F17:I17").format.horizontalAlignment = "right";
summary.getRange("A19:I19").merge();
summary.getRange("A19").values = [["说明：待复核成员的本期 gain_coin 为负，其公会长分成未纳入“已确认总薪资”。"]];
summary.getRange("A19:I19").format = { fill: amber, font: { color: "#7A4A00" }, wrapText: true };
summary.getRange("A19:I19").format.rowHeight = 28;
summary.getRange("A:A").format.columnWidth = 11;
summary.getRange("B:B").format.columnWidth = 23;
summary.getRange("C:C").format.columnWidth = 19;
summary.getRange("D:D").format.columnWidth = 16;
summary.getRange("E:E").format.columnWidth = 20;
summary.getRange("F:H").format.columnWidth = 18;
summary.getRange("I:I").format.columnWidth = 14;
summary.freezePanes.freezeRows(4);

detail.showGridLines = false;
detail.getRange("A1:K1").merge();
detail.getRange("A1").values = [["本周期公会成员薪资明细（含所属地区）"]];
detail.getRange("A1:K1").format = { fill: dark, font: { bold: true, color: "#FFFFFF", size: 16 }, horizontalAlignment: "center", verticalAlignment: "center" };
detail.getRange("A1:K1").format.rowHeight = 30;
detail.getRange("A2:K2").merge();
detail.getRange("A2").values = [["仅列出本周期存在正向主播薪资的成员；金额单位：USD"]];
detail.getRange("A2:K2").format = { fill: "#E8F5F1", font: { color: "#24564D", italic: true }, horizontalAlignment: "center" };
detail.getRange("A4:K4").values = [["公会ID", "公会名称", "所属地区", "用户ID", "用户编号", "结算政策", "主播薪资", "已确认公会长分成", "已确认总薪资", "分成状态", "备注"]];
detail.getRange("A4:K4").format = { fill: dark, font: { bold: true, color: "#FFFFFF" }, horizontalAlignment: "center", verticalAlignment: "center", wrapText: true, borders: border };
detail.getRange("A4:K4").format.rowHeight = 28;
detail.getRange("A5:H26").values = members.map((row) => row.slice(0, 8));
detail.getRange("J5:K26").values = members.map((row) => row.slice(8, 10));
detail.getRange("I5").formulas = [["=G5+H5"]];
detail.getRange("I5:I26").fillDown();
detail.getRange("A5:K26").format = { borders: border, verticalAlignment: "center" };
detail.getRange("A5:K26").format.rowHeight = 22;
detail.getRange("G5:I26").format.numberFormat = moneyFormat;
detail.getRange("G5:I26").format.horizontalAlignment = "right";
detail.getRange("A27:F27").merge();
detail.getRange("A27").values = [["合计"]];
detail.getRange("G27").formulas = [["=SUM(G5:G26)"]];
detail.getRange("H27").formulas = [["=SUM(H5:H26)"]];
detail.getRange("I27").formulas = [["=SUM(I5:I26)"]];
detail.getRange("A27:K27").format = { fill: "#C6E9DF", font: { bold: true, color: "#134E4A" }, borders: { preset: "doubleBottom", style: "medium", color: "#0F766E" } };
detail.getRange("G27:I27").format.numberFormat = moneyFormat;
detail.getRange("G27:I27").format.horizontalAlignment = "right";
detail.getRange("A5:K26").conditionalFormats.add("Custom", { formula: "=$J5=\"待复核\"", format: { fill: "#FFF7E0", font: { color: "#7A4A00" } } });
detail.getRange("A:A").format.columnWidth = 11;
detail.getRange("B:B").format.columnWidth = 23;
detail.getRange("C:C").format.columnWidth = 19;
detail.getRange("D:E").format.columnWidth = 14;
detail.getRange("F:F").format.columnWidth = 12;
detail.getRange("G:I").format.columnWidth = 18;
detail.getRange("J:J").format.columnWidth = 12;
detail.getRange("K:K").format.columnWidth = 34;
detail.getRange("K5:K26").format.wrapText = true;
detail.freezePanes.freezeRows(4);

notes.showGridLines = false;
notes.getRange("A1:D1").merge();
notes.getRange("A1").values = [["计算口径与数据说明"]];
notes.getRange("A1:D1").format = { fill: dark, font: { bold: true, color: "#FFFFFF", size: 16 }, horizontalAlignment: "center", verticalAlignment: "center" };
notes.getRange("A1:D1").format.rowHeight = 30;
notes.getRange("A3:D3").values = [["项目", "取值 / 规则", "来源", "备注"]];
notes.getRange("A3:D3").format = { fill: dark, font: { bold: true, color: "#FFFFFF" }, horizontalAlignment: "center", borders: border };
notes.getRange("A4:D9").values = [
  ["结算周期", "2026-08-01 00:00:00 至 2026-08-16 00:00:00", "当前周期", "上半月周期"],
  ["数据环境", "stay 测试库", "MySQL MCP", "未查询生产库"],
  ["主播薪资基数", "gain_diamond + send_gain_diamond", "app_user_account", "实时薪资口径"],
  ["公会长分成基数", "本周期 coin_type=1 的 SUM(coin)", "app_user_coin_detail", "负值分成待复核，不计入已确认总薪资"],
  ["双周政策", "达标比率 1；未达标比率 0.7；首周期免罚", "app_live_user_site_daily_summary", "本次成员按已计算比例汇总"],
  ["预支薪资", "0.00 USD", "app_user_account.advance_salary_total_amount", "本次列出的成员均无预支"],
];
notes.getRange("A4:D9").format = { borders: border, verticalAlignment: "center", wrapText: true };
notes.getRange("A4:D9").format.rowHeight = 32;
notes.getRange("A4:A9").format = { fill: pale, font: { bold: true, color: "#134E4A" }, borders: border, verticalAlignment: "center", wrapText: true };
notes.getRange("A:A").format.columnWidth = 18;
notes.getRange("B:B").format.columnWidth = 36;
notes.getRange("C:C").format.columnWidth = 33;
notes.getRange("D:D").format.columnWidth = 38;

const checks = await Promise.all([
  wb.inspect({ kind: "table", range: "公会汇总!A1:I19", include: "values,formulas", tableMaxRows: 20, tableMaxCols: 10 }),
  wb.inspect({ kind: "table", range: "成员薪资!A1:K27", include: "values,formulas", tableMaxRows: 28, tableMaxCols: 12 }),
  wb.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 50 }, summary: "formula error scan" }),
]);
for (const check of checks) console.log(check.ndjson);

for (const [sheetName, fileName] of [["公会汇总", "preview_summary.png"], ["成员薪资", "preview_members.png"], ["口径说明", "preview_notes.png"]]) {
  const preview = await wb.render({ sheetName, autoCrop: "all", scale: 1.25, format: "png" });
  await fs.writeFile(`${outputDir}/${fileName}`, new Uint8Array(await preview.arrayBuffer()));
}

const output = await SpreadsheetFile.exportXlsx(wb);
await output.save(reportPath);
console.log(JSON.stringify({ reportPath }));
