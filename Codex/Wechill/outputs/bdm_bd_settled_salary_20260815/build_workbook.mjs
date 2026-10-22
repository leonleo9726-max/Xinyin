import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = "E:/Codex/Wechill/outputs/bdm_bd_settled_salary_20260815";
const workbook = Workbook.create();

const bdRows = [
  [284, 3728, "Gonfe", "转正", 0, 0, 0, 0, 0, 0, 0, 0, 0, 200, 0, 200, 0],
  [277, 8517614, "uBD三号", "转正", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  [272, 8517682, "uBD六号", "试用", 0, 0, 0, 0, 0, 0, 0, 0, 0, 537.97, 0, 537.97, 0],
  [269, 8523263, "kocekid成员1", "试用", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  [260, 8523877, "BD七号", "转正", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  [282, 8524370, "Lee", "试用", 163.38, 100, 163.38, 32.67, 132.67, 66.33, 0, 0, 0, 900, 66.34, 833.66, 0],
  [263, 8528701, "test", "转正", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  [264, 8532766, "peterzhong", "转正", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  [261, 8535700, "BD", "转正", 6440.87, 250, 6440.87, 257.63, 507.63, 101.52, 0, 0, 0, 800, 406.11, 393.89, 0],
  [265, 8539215, "DZP2", "试用", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  [283, 8539901, "Ginxxer", "试用", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  [276, 8540258, "dzp", "转正", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  [266, 8546191, "oop", "试用", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  [274, 8549741, "uBD四号", "试用", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  [267, 8554413, "123", "试用", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  [271, 8558958, "BD三号", "试用", 148.3, 100, 148.3, 29.66, 129.66, 64.83, 0, 0, 0, 409.77, 64.83, 344.94, 0],
  [280, 8561551, "eat", "试用", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  [268, 8562905, "高", "转正", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  [281, 8565914, "uBD一号", "试用", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  [262, 8568697, "SABDM", "转正", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  [270, 8577097, "kocekid", "试用", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  [278, 8583449, "gonXXiao", "试用", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  [273, 8585742, "独钓寒江雪", "试用", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  [275, 8590613, "leo", "转正", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
  [279, 8594890, "bug满天飞", "转正", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
];

const memberRows = [
  [770, "2026-08-15 23:59:59", 8517682, "uBD六号", 3529, "leon guild", 8501168, "leon", "自由", 2700000, 67, 8, 9.35, 16.11, 5, 84.35, 84.35, 1, 0, 0],
  [772, "2026-08-15 23:59:59", 8517682, "uBD六号", 3529, "leon guild", 8514466, "علتانن تينتينت نيتبنبت تينتينت", "双周", 2700000, 89.3, 10, 28, 21, 0, 127.3, 89.11, 0.7, 0, 0],
  [773, "2026-08-15 23:59:59", 8517682, "uBD六号", 3529, "leon guild", 8558717, "u15687", "自由", 2700000, 67, 8, 9.35, 16.11, 5, 84.35, 84.35, 1, 0, 0],
  [774, "2026-08-15 23:59:59", 8517682, "uBD六号", 3529, "leon guild", 8597570, "u15688", "双周", 2700000, 89.3, 10, 28, 21, 0, 127.3, 89.11, 0.7, 0, 0],
  [775, "2026-08-15 23:59:59", 8517682, "uBD六号", 3529, "leon guild", 8596889, "u15692", "自由", 2700000, 67, 8, 9.35, 16.11, 5, 84.35, 84.35, 1, 0, 0],
  [779, "2026-08-15 23:59:59", 8524370, "Lee", 3558, "Yoww", 8595978, "u15770", "双周", 2700000, 112.2, 5, 20, 26.18, 0, 137.2, 96.04, 0.7, 0, 0],
  [778, "2026-08-15 23:59:59", 8535700, "BD", 3560, "Yowwn", 8532988, "u15769", "双周", 30000000, 1350, 20, 0, 315, 0, 1370, 959, 0.7, 0, 0],
  [777, "2026-08-15 23:59:59", 8535700, "BD", 3562, "Yowwwww", 8549370, "u15767", "自由", 30000000, 1404, 30, 0, 468, 15, 1434, 1434, 1, 0, 0],
  [780, "2026-08-15 23:59:59", 8535700, "BD", 3569, "新中东区公会长自由结算", 8523877, "uBD七号", "自由", 30000000, 1404, 30, 0, 468, 15, 1434, 1434, 1, 0, 553],
  [781, "2026-08-15 23:59:59", 8535700, "BD", 3569, "新中东区公会长自由结算", 8504072, "u15773", "双周", 5000000, 213.3, 10, 20, 71.1, 0, 243.3, 243.3, 1, 0, 0],
  [782, "2026-08-15 23:59:59", 8535700, "BD", 3569, "新中东区公会长自由结算", 8598038, "u15774", "双周", 5000000, 213.3, 10, 20, 71.1, 0, 243.3, 243.3, 1, 0, 0],
  [783, "2026-08-15 23:59:59", 8535700, "BD", 3569, "新中东区公会长自由结算", 8573918, "u15776", "双周", 5000000, 213.3, 10, 20, 49.77, 0, 243.3, 170.31, 0.7, 0, 0],
  [784, "2026-08-15 23:59:59", 8558958, "BD三号", 3541, "英语区自由政策", 8511452, "u16418", "自由", 2700000, 67, 8, 9.35, 16.11, 5, 84.35, 84.35, 1, 0, 0],
  [785, "2026-08-15 23:59:59", 8558958, "BD三号", 3541, "英语区自由政策", 8540644, "u16422", "双周", 2700000, 89.3, 10, 28, 21, 0, 127.3, 89.11, 0.7, 0, 0],
  [786, "2026-08-15 23:59:59", 8558958, "BD三号", 3541, "英语区自由政策", 8587411, "u16423", "自由", 2700000, 67, 8, 9.35, 16.11, 5, 84.35, 84.35, 1, 0, 0],
  [787, "2026-08-15 23:59:59", 8558958, "BD三号", 3541, "英语区自由政策", 8588336, "u16424", "双周", 2700000, 89.3, 10, 28, 21, 0, 127.3, 89.11, 0.7, 0, 0],
  [788, "2026-08-15 23:59:59", 8558958, "BD三号", 3541, "英语区自由政策", 8557287, "u16426", "自由", 2700000, 67, 8, 9.35, 16.11, 5, 84.35, 84.35, 1, 0, 0],
  [789, "2026-08-15 23:59:59", 8558958, "BD三号", 3552, "英语区自由结算", 8502216, "u16448", "双周", 2700000, 89.3, 10, 28, 21, 0, 127.3, 89.11, 0.7, 0, 0],
  [790, "2026-08-15 23:59:59", 8558958, "BD三号", 3552, "英语区自由结算", 8539314, "u16459", "自由", 2700000, 67, 8, 9.35, 16.11, 5, 84.35, 84.35, 1, 0, 84.35],
  [776, "2026-08-15 23:59:59", 8558958, "BD三号", 3575, "Yomwe", 8536064, "u15754", "双周", 2700000, 89.3, 10, 28, 21, 0, 127.3, 89.11, 0.7, 0, 0],
  [771, "2026-08-15 23:59:59", 8594890, "bug满天飞", 3551, "会背唐诗吗", 8588564, "u15682", "双周", 1190563, 66, 4, 3.62, 10.5, 0, 73.62, 51.53, 0.7, 0, 0],
];

const colors = {
  navy: "#1F4E78",
  teal: "#0F766E",
  lightBlue: "#D9EAF7",
  lightTeal: "#DDEFEA",
  warning: "#FFF2CC",
  border: "#D0D7DE",
  white: "#FFFFFF",
  gray: "#F6F8FA",
};

function styleTitle(sheet, range, color) {
  sheet.getRange(range).format = {
    fill: color,
    font: { bold: true, color: colors.white, size: 15 },
    horizontalAlignment: "left",
    verticalAlignment: "center",
  };
}

function styleHeader(sheet, range, color) {
  sheet.getRange(range).format = {
    fill: color,
    font: { bold: true, color: colors.white },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
    borders: { preset: "all", style: "thin", color: colors.border },
  };
}

function styleBody(sheet, range) {
  sheet.getRange(range).format = {
    verticalAlignment: "center",
    borders: { preset: "inside", style: "thin", color: colors.border },
  };
}

const summary = workbook.worksheets.add("汇总");
summary.showGridLines = false;
summary.getRange("A1:H1").merge();
summary.getRange("A1").values = [["202608 已结算 BD 薪资与绑定公会成员结算汇总"]];
styleTitle(summary, "A1:H1", colors.navy);
summary.getRange("A2:H2").merge();
summary.getRange("A2").values = [["数据来源：stay 测试库；BD 月结表 bd_staff_monthly_salary；成员已打款表 app_payer_host_salary_detail_v2。"]];
summary.getRange("A2:H2").format = { fill: colors.gray, font: { italic: true, color: "#374151" } };
summary.getRange("A4:B8").values = [
  ["指标", "数值"],
  ["BD 角色月结记录数", null],
  ["BD 总薪资", null],
  ["BD 实发薪资", null],
  ["成员已打款记录数", null],
];
summary.getRange("A4:B4").format = { fill: colors.teal, font: { bold: true, color: colors.white }, horizontalAlignment: "center" };
summary.getRange("B5:B8").formulas = [
  ["=COUNTA('BD月结'!A5:A29)"],
  ["=SUM('BD月结'!I5:I29)"],
  ["=SUM('BD月结'!Q5:Q29)"],
  ["=COUNTA('成员结算'!A5:A25)"],
];
summary.getRange("D4:E8").values = [
  ["成员结算指标", "数值"],
  ["绑定公会数", null],
  ["结算成员数", null],
  ["成员应发薪资", null],
  ["成员实发薪资", null],
];
summary.getRange("D4:E4").format = { fill: colors.teal, font: { bold: true, color: colors.white }, horizontalAlignment: "center" };
summary.getRange("E5:E8").formulas = [
  ["=COUNTA(UNIQUE('成员结算'!E5:E25))"],
  ["=COUNTA('成员结算'!G5:G25)"],
  ["=SUM('成员结算'!P5:P25)"],
  ["=SUM('成员结算'!Q5:Q25)"],
];
summary.getRange("A4:B8").format.borders = { preset: "all", style: "thin", color: colors.border };
summary.getRange("D4:E8").format.borders = { preset: "all", style: "thin", color: colors.border };
summary.getRange("B6:B7").format.numberFormat = "#,##0.00";
summary.getRange("E7:E8").format.numberFormat = "#,##0.00";
summary.getRange("A10:H10").merge();
summary.getRange("A10").values = [["数据质量声明：成员明细结算时间为 2026-08-15 23:59:59，晚于导出时系统日期 2026-08-06，属于测试库预生成的未来结算数据。"]];
summary.getRange("A10:H10").format = { fill: colors.warning, font: { bold: true, color: "#7F6000" }, wrapText: true, verticalAlignment: "center" };
summary.getRange("A1:H10").format.rowHeight = 22;
summary.getRange("A1:H1").format.rowHeight = 28;
summary.getRange("A10:H10").format.rowHeight = 36;
summary.getRange("A:A").format.columnWidth = 26;
summary.getRange("B:B").format.columnWidth = 16;
summary.getRange("D:D").format.columnWidth = 24;
summary.getRange("E:E").format.columnWidth = 16;

const bdSheet = workbook.worksheets.add("BD月结");
bdSheet.showGridLines = false;
bdSheet.getRange("A1:Q1").merge();
bdSheet.getRange("A1").values = [["202608 BD 角色月结薪资明细"]];
styleTitle(bdSheet, "A1:Q1", colors.navy);
bdSheet.getRange("A2:Q2").merge();
bdSheet.getRange("A2").values = [["salary_role=1（BD 个人薪资）；金额单位：美元。预支、借支均为该次月结快照值。"]];
bdSheet.getRange("A2:Q2").format = { fill: colors.gray, font: { italic: true, color: "#374151" } };
const bdHeaders = [["月结ID", "BD用户ID", "姓名", "雇佣状态", "底薪有效流水", "底薪", "Bonus有效流水", "提成", "总薪资", "未达标扣款", "预支结算前", "预支抵扣", "预支结余", "借支结算前", "借支抵扣", "借支结余", "实发薪资"]];
bdSheet.getRange("A4:Q4").values = bdHeaders;
styleHeader(bdSheet, "A4:Q4", colors.teal);
bdSheet.getRange("A5:Q29").values = bdRows;
styleBody(bdSheet, "A5:Q29");
bdSheet.getRange("E5:Q29").format.numberFormat = "#,##0.00";
bdSheet.getRange("A4:Q29").format.rowHeight = 21;
bdSheet.getRange("A:A").format.columnWidth = 12;
bdSheet.getRange("B:B").format.columnWidth = 14;
bdSheet.getRange("C:C").format.columnWidth = 18;
bdSheet.getRange("D:D").format.columnWidth = 12;
bdSheet.getRange("E:Q").format.columnWidth = 14;
bdSheet.freezePanes.freezeRows(4);
bdSheet.tables.add("A4:Q29", true, "BdMonthlySalaryTable");
bdSheet.getRange("I5:I29").conditionalFormats.add("dataBar", { color: "#4F81BD", gradient: true });

const memberSheet = workbook.worksheets.add("成员结算");
memberSheet.showGridLines = false;
memberSheet.getRange("A1:T1").merge();
memberSheet.getRange("A1").values = [["202608 BD 绑定公会成员已打款结算明细"]];
styleTitle(memberSheet, "A1:T1", colors.navy);
memberSheet.getRange("A2:T2").merge();
memberSheet.getRange("A2").values = [["status=2（已打款），金额单位：美元；成员应发 = 主播薪资 + 主播TG奖励 + 超额奖励。公会长分成字段不计入成员应发。"]];
memberSheet.getRange("A2:T2").format = { fill: colors.gray, font: { italic: true, color: "#374151" } };
const memberHeaders = [["明细ID", "结算时间", "BD用户ID", "BD姓名", "公会ID", "公会名称", "成员ID", "成员昵称", "成员政策", "钻石", "主播薪资", "主播TG奖励", "超额奖励", "公会长薪资", "公会长TG奖励", "成员应发", "成员实发", "实发比例", "成员预支字段", "成员借支字段"]];
memberSheet.getRange("A4:T4").values = memberHeaders;
styleHeader(memberSheet, "A4:T4", colors.teal);
memberSheet.getRange("A5:T25").values = memberRows;
styleBody(memberSheet, "A5:T25");
memberSheet.getRange("J5:Q25").format.numberFormat = "#,##0.00";
memberSheet.getRange("R5:R25").format.numberFormat = "0.00";
memberSheet.getRange("S5:T25").format.numberFormat = "#,##0.00";
memberSheet.getRange("A4:T25").format.rowHeight = 21;
memberSheet.getRange("A:A").format.columnWidth = 11;
memberSheet.getRange("B:B").format.columnWidth = 21;
memberSheet.getRange("C:C").format.columnWidth = 14;
memberSheet.getRange("D:D").format.columnWidth = 14;
memberSheet.getRange("E:E").format.columnWidth = 10;
memberSheet.getRange("F:F").format.columnWidth = 26;
memberSheet.getRange("G:G").format.columnWidth = 14;
memberSheet.getRange("H:H").format.columnWidth = 20;
memberSheet.getRange("I:I").format.columnWidth = 11;
memberSheet.getRange("J:T").format.columnWidth = 14;
memberSheet.freezePanes.freezeRows(4);
memberSheet.tables.add("A4:T25", true, "MemberSettlementTable");
memberSheet.getRange("Q5:Q25").conditionalFormats.add("dataBar", { color: "#2E8B57", gradient: true });

const notes = workbook.worksheets.add("口径说明");
notes.showGridLines = false;
notes.getRange("A1:B1").merge();
notes.getRange("A1").values = [["导出口径与校验说明"]];
styleTitle(notes, "A1:B1", colors.navy);
notes.getRange("A3:B8").values = [
  ["项目", "说明"],
  ["BD 月结来源", "bd_staff_monthly_salary，筛选 salary_month=202608、salary_role=1。"],
  ["BD 实发", "total_salary_balance；月结时已扣除有效新公会未达标扣款及当次债务抵扣。"],
  ["成员结算来源", "app_payer_host_salary_detail_v2，筛选 status=2，并按结算时点关联 BD-公会绑定关系。"],
  ["成员应发公式", "host_salary + host_tg_reward + excess_diamonds_salary。"],
  ["成员实发", "actual_salary；双周未达标时可因 salary_ratio=0.70 低于应发。"],
];
styleHeader(notes, "A3:B3", colors.teal);
notes.getRange("A4:B8").format = { wrapText: true, verticalAlignment: "center", borders: { preset: "all", style: "thin", color: colors.border } };
notes.getRange("A10:B10").merge();
notes.getRange("A10").values = [["异常声明：测试库成员结算时间为 2026-08-15 23:59:59，晚于导出时系统日期 2026-08-06；本工作簿未对该时间异常进行修正。"]];
notes.getRange("A10:B10").format = { fill: colors.warning, font: { bold: true, color: "#7F6000" }, wrapText: true, verticalAlignment: "center" };
notes.getRange("A:A").format.columnWidth = 22;
notes.getRange("B:B").format.columnWidth = 88;
notes.getRange("A1:B10").format.rowHeight = 24;
notes.getRange("A1:F1").format.rowHeight = 28;
notes.getRange("A10:B10").format.rowHeight = 42;

const inspect = await workbook.inspect({ kind: "table", range: "BD月结!A1:Q10", include: "values,formulas", tableMaxRows: 10, tableMaxCols: 17 });
console.log(inspect.ndjson);
const errorScan = await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 100 }, summary: "formula errors" });
console.log(errorScan.ndjson);

for (const [sheetName, range, fileName] of [
  ["汇总", "A1:H10", "preview_summary.png"],
  ["BD月结", "A1:Q29", "preview_bd.png"],
  ["成员结算", "A1:T25", "preview_members.png"],
  ["口径说明", "A1:B10", "preview_notes.png"],
]) {
  const preview = await workbook.render({ sheetName, range, scale: 1.3, format: "png" });
  await fs.writeFile(`${outputDir}/${fileName}`, new Uint8Array(await preview.arrayBuffer()));
}

const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(`${outputDir}/bd_settled_salary_202608.xlsx`);
console.log("exported", `${outputDir}/bd_settled_salary_202608.xlsx`);
