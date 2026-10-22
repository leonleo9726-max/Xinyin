import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outDir = "E:/Codex/Wechill/outputs/bdm_bd_test_salary_20260724_1050";
const outFile = `${outDir}/BDM_BD_Test_Salary_20260724_1050.xlsx`;
const month = 202607;
const snapshot = "2026-07-24 10:50:00";
const c = (text) => text;

const staffRows = [
  [9, "8517682", "uBD\u516d\u53f7", "BD", "\u8bd5\u7528", "BD\u4e2a\u4eba\u85aa\u8d44", 5, 4411.11, 500, 4411.11, 1323.33, 1, 911.66, 1823.33, 911.67, 4411.11, 8822.22, 2, snapshot],
  [18, "8524370", "Lee", "BDM+BD", "\u8bd5\u7528", "BD\u4e2a\u4eba\u85aa\u8d44", 2, 312.76, 200, 312.76, 62.55, 0, 131.27, 262.55, 131.28, 312.76, 625.52, 1, snapshot],
  [8, "8558958", "BD\u4e09\u53f7", "BD", "\u8bd5\u7528", "BD\u4e2a\u4eba\u85aa\u8d44", 4, 312.55, 200, 312.55, 62.51, 0, 131.25, 262.51, 131.26, 2538.75, 625.1, 1, snapshot],
  [12, "8590613", "leo", "BDM+BD", "\u8f6c\u6b63", "BD\u4e2a\u4eba\u85aa\u8d44", 2, 312.55, 200, 312.55, 62.51, 1, 131.25, 262.51, 131.26, 312.55, 625.1, 1, snapshot],
  [25, "8590613", "leo", "BDM+BD", "\u8f6c\u6b63", "BDM\u56e2\u961f\u7ba1\u7406\u85aa\u8d44", 5, 5036.21, 500, 5036.21, 1007.24, 2, 0, 1507.24, 1507.24, 7262.41, 5036.21, 4, snapshot],
  [27, "8524370", "Lee", "BDM+BD", "\u8bd5\u7528", "BDM\u56e2\u961f\u7ba1\u7406\u85aa\u8d44", 1, 312.76, 100, 312.76, 62.55, 0, 0, 162.55, 162.55, 312.76, 312.76, 1, snapshot],
];

const guildRows = [
  [8, "8558958", "BD\u4e09\u53f7", "BD\u4e2a\u4eba\u85aa\u8d44", 3541, "\u82f1\u8bed\u533a\u81ea\u7531\u653f\u7b56", 272, "2026-06-24 11:46:28", "2026-07-15 20:59:59", "2026-07-15 20:59:59", 0, 0, 1357.1, 0, 0, 0, "\u662f", "\u662f", "\u5426", "\u5426", snapshot],
  [8, "8558958", "BD\u4e09\u53f7", "BD\u4e2a\u4eba\u85aa\u8d44", 3552, "\u82f1\u8bed\u533a\u81ea\u7531\u7ed3\u7b97", 274, "2026-06-30 08:52:55", "2026-07-15 20:59:59", "2026-07-15 20:59:59", 0, 0, 556.55, 0, 0, 0, "\u662f", "\u662f", "\u5426", "\u5426", snapshot],
  [8, "8558958", "BD\u4e09\u53f7", "BD\u4e2a\u4eba\u85aa\u8d44", 3575, "Yomwe", 267, "2026-06-24 02:39:09", "2026-09-15 20:59:59", "2026-09-15 20:59:59", 312.55, 312.55, 312.55, 625.1, 312.55, 312.55, "\u662f", "\u662f", "\u662f", "\u5426", snapshot],
  [8, "8558958", "BD\u4e09\u53f7", "BD\u4e2a\u4eba\u85aa\u8d44", 3584, "Lastly", 273, "2026-06-24 12:00:42", "2026-07-15 20:59:59", "2026-07-15 20:59:59", 0, 0, 312.55, 0, 0, 0, "\u662f", "\u662f", "\u5426", "\u5426", snapshot],
  [9, "8517682", "uBD\u516d\u53f7", "BD\u4e2a\u4eba\u85aa\u8d44", 3529, "leon guild", 278, "2026-07-06 21:00:00", "2026-07-31 20:59:59", "2026-07-31 20:59:59", 4098.56, 4098.56, 4098.56, 8197.12, 4098.56, 4098.56, "\u662f", "\u662f", "\u662f", "\u662f", snapshot],
  [9, "8517682", "uBD\u516d\u53f7", "BD\u4e2a\u4eba\u85aa\u8d44", 3572, "\u0647\u062b\u0647\u064a\u062a\u0628\u062a\u0628\u0647 \u0628\u0647\u0628\u0646", 256, "2026-06-18 03:11:24", "2026-09-15 20:59:59", "2026-09-15 20:59:59", 0, 0, 0, 0, 0, 0, "\u662f", "\u662f", "\u5426", "\u5426", snapshot],
  [9, "8517682", "uBD\u516d\u53f7", "BD\u4e2a\u4eba\u85aa\u8d44", 3581, "1155555555", 264, "2026-06-23 12:08:29", "2026-09-15 20:59:59", "2026-09-15 20:59:59", 312.55, 312.55, 312.55, 625.1, 312.55, 312.55, "\u662f", "\u662f", "\u662f", "\u5426", snapshot],
  [12, "8590613", "leo", "BD\u4e2a\u4eba\u85aa\u8d44", 3544, "\u82f1\u8bed\u533a\u516c\u4f1a\u957f\u81ea\u7531\u653f\u7b56", 251, "2026-06-09 04:27:11", "2026-08-31 20:59:59", "2026-08-31 20:59:59", 0, 0, 0, 0, 0, 0, "\u662f", "\u662f", "\u5426", "\u5426", snapshot],
  [12, "8590613", "leo", "BD\u4e2a\u4eba\u85aa\u8d44", 3587, "Thgfgfg", 279, "2026-07-08 02:55:44", "2026-07-31 20:59:59", "2026-07-31 20:59:59", 312.55, 312.55, 312.55, 625.1, 312.55, 312.55, "\u662f", "\u662f", "\u662f", "\u662f", snapshot],
  [18, "8524370", "Lee", "BD\u4e2a\u4eba\u85aa\u8d44", 3558, "Yoww", 233, "2026-06-04 11:18:23", "2026-08-31 20:59:59", "2026-08-31 20:59:59", 312.76, 312.76, 312.76, 625.52, 312.76, 312.76, "\u662f", "\u662f", "\u662f", "\u5426", snapshot],
];

const qualityRows = [
  [25, "8590613", "leo", "BDM\u56e2\u961f\u7ba1\u7406\u85aa\u8d44", 1507.24, 7262.41, 0, 7262.41, "\u5f85\u6838\u5bf9", "\u4eba\u5458\u85aa\u8d44\u6c47\u603b\u5b58\u5728\u516c\u4f1a\u85aa\u8d44\u603b\u548c\uff0c\u4f46\u672a\u627e\u5230\u5173\u8054 bd_realtime_guild_salary \u660e\u7ec6"],
  [27, "8524370", "Lee", "BDM\u56e2\u961f\u7ba1\u7406\u85aa\u8d44", 162.55, 312.76, 0, 312.76, "\u5f85\u6838\u5bf9", "\u4eba\u5458\u85aa\u8d44\u6c47\u603b\u5b58\u5728\u516c\u4f1a\u85aa\u8d44\u603b\u548c\uff0c\u4f46\u672a\u627e\u5230\u5173\u8054 bd_realtime_guild_salary \u660e\u7ec6"],
];

const workbook = Workbook.create();
const staffSheet = workbook.worksheets.add("\u85aa\u8d44\u4eba\u5458\u6c47\u603b");
const guildSheet = workbook.worksheets.add("\u7ed1\u5b9a\u516c\u4f1a\u85aa\u8d44\u660e\u7ec6");
const qualitySheet = workbook.worksheets.add("\u6570\u636e\u8d28\u91cf\u5f02\u5e38");

const navy = "#163E6C";
const blue = "#0F6E8C";
const lightBlue = "#D9EEF7";
const orange = "#D95D18";
const lightOrange = "#FFF0E7";
const border = { preset: "all", style: "thin", color: "#C7D6E5" };
const moneyFormat = "#,##0.00";

function setTitle(sheet, range, title, source, titleColor) {
  sheet.showGridLines = false;
  sheet.getRange(range).merge();
  sheet.getRange(range.split(":")[0]).values = [[title]];
  sheet.getRange(range).format = { fill: titleColor, font: { bold: true, color: "#FFFFFF", size: 16 }, horizontalAlignment: "center", verticalAlignment: "center" };
  sheet.getRange("A2:S2").merge();
  sheet.getRange("A2").values = [[source]];
  sheet.getRange("A2:S2").format = { fill: "#EAF2F8", font: { italic: true, color: "#4F6476" }, verticalAlignment: "center" };
  sheet.getRange("1:1").format.rowHeight = 28;
  sheet.getRange("2:2").format.rowHeight = 20;
}

setTitle(staffSheet, "A1:S1", "\u6d4b\u8bd5\u73af\u5883 BD / BDM \u5b9e\u65f6\u85aa\u8d44\u5bfc\u51fa", `\u6570\u636e\u6e90\uff1a\u6d4b\u8bd5\u5e93 mysql | \u7ed3\u7b97\u6708\uff1a${month} | \u53e3\u5f84\uff1abd_realtime_staff_salary.total_salary \u975e\u96f6 | \u5feb\u7167\u65f6\u95f4\uff1a${snapshot}`, navy);
staffSheet.getRange("A4:H4").values = [["\u85aa\u8d44\u8bb0\u5f55\u6570", null, "BD\u4e2a\u4eba\u85aa\u8d44", null, "BDM\u56e2\u961f\u85aa\u8d44", null, "\u5173\u8054\u516c\u4f1a\u660e\u7ec6", null]];
staffSheet.getRange("B4").formulas = [["=COUNTA(A8:A13)"]];
staffSheet.getRange("D4").formulas = [["=SUMIF(F8:F13,\"BD\u4e2a\u4eba\u85aa\u8d44\",N8:N13)"]];
staffSheet.getRange("F4").formulas = [["=SUMIF(F8:F13,\"BDM\u56e2\u961f\u7ba1\u7406\u85aa\u8d44\",N8:N13)"]];
staffSheet.getRange("H4").formulas = [["=COUNTA('\u7ed1\u5b9a\u516c\u4f1a\u85aa\u8d44\u660e\u7ec6'!A5:A14)"]];
staffSheet.getRange("A4:H4").format = { fill: "#E7F0F8", font: { bold: true, color: navy }, borders: border, horizontalAlignment: "center" };
staffSheet.getRange("B4,H4").format.numberFormat = "#,##0";
staffSheet.getRange("D4,F4").format.numberFormat = moneyFormat;
staffSheet.getRange("A4").format.columnWidth = 15;
staffSheet.getRange("B4").format.columnWidth = 10;
staffSheet.getRange("C4").format.columnWidth = 16;
staffSheet.getRange("D4").format.columnWidth = 14;
staffSheet.getRange("E4").format.columnWidth = 17;
staffSheet.getRange("F4").format.columnWidth = 14;
staffSheet.getRange("G4").format.columnWidth = 17;
staffSheet.getRange("H4").format.columnWidth = 10;

const staffHeaders = [["\u5b9e\u65f6\u85aa\u8d44 ID", "\u7528\u6237\u7f16\u53f7", "\u59d3\u540d", "\u8eab\u4efd", "\u5728\u804c\u72b6\u6001", "\u85aa\u8d44\u7c7b\u578b", "\u7b49\u7ea7", "\u5e95\u85aa\u6709\u6548\u6d41\u6c34", "\u5e95\u85aa", "Bonus \u6709\u6548\u6d41\u6c34", "\u516c\u4f1a\u63d0\u6210", "\u65b0\u589e\u516c\u4f1a\u6570", "\u65b0\u516c\u4f1a\u6263\u6b3e", "\u603b\u85aa\u8d44", "\u85aa\u8d44\u4f59\u989d", "\u516c\u4f1a\u85aa\u8d44\u603b\u548c", "\u6709\u6548\u516c\u4f1a\u85aa\u8d44\u603b\u548c", "\u6709\u6548\u516c\u4f1a\u6570", "\u5feb\u7167\u65f6\u95f4"]];
staffSheet.getRange("A7:S7").values = staffHeaders;
staffSheet.getRange("A8:S13").values = staffRows;
staffSheet.getRange("A7:S7").format = { fill: blue, font: { bold: true, color: "#FFFFFF" }, horizontalAlignment: "center", wrapText: true };
staffSheet.getRange("A8:S13").format = { borders: border };
staffSheet.getRange("A8:S13").format.wrapText = false;
staffSheet.getRange("H8:Q13").format.numberFormat = moneyFormat;
staffSheet.getRange("A7:S13").format.autofitColumns();
staffSheet.getRange("A4").format.columnWidth = 15;
staffSheet.getRange("B4").format.columnWidth = 10;
staffSheet.getRange("C4").format.columnWidth = 16;
staffSheet.getRange("D4").format.columnWidth = 14;
staffSheet.getRange("E4").format.columnWidth = 17;
staffSheet.getRange("F4").format.columnWidth = 18;
staffSheet.getRange("G4").format.columnWidth = 17;
staffSheet.getRange("H4").format.columnWidth = 10;
staffSheet.getRange("B7:B13").format.columnWidth = 14;
staffSheet.getRange("F7:F13").format.columnWidth = 18;
staffSheet.getRange("S7:S13").format.columnWidth = 20;
staffSheet.getRange("A7:S13").format.rowHeight = 22;
staffSheet.tables.add("A7:S13", true, "TestSalaryStaffTable");
staffSheet.freezePanes.freezeRows(7);

guildSheet.showGridLines = false;
guildSheet.getRange("A1:U1").merge();
guildSheet.getRange("A1").values = [["\u6d4b\u8bd5\u73af\u5883\u7ed1\u5b9a\u516c\u4f1a\u85aa\u8d44\u660e\u7ec6"]];
guildSheet.getRange("A1:U1").format = { fill: navy, font: { bold: true, color: "#FFFFFF", size: 16 }, horizontalAlignment: "center" };
guildSheet.getRange("A2:U2").merge();
guildSheet.getRange("A2").values = [[`\u4ec5\u5305\u542b\u603b\u85aa\u8d44\u975e\u96f6\u5b9e\u65f6\u4eba\u5458\u85aa\u8d44\u7684\u5173\u8054 bd_realtime_guild_salary \u8bb0\u5f55 | \u7ed3\u7b97\u6708\uff1a${month}`]];
guildSheet.getRange("A2:U2").format = { fill: "#EAF2F8", font: { italic: true, color: "#4F6476" } };
const guildHeaders = [["\u5b9e\u65f6\u85aa\u8d44 ID", "\u7528\u6237\u7f16\u53f7", "\u59d3\u540d", "\u85aa\u8d44\u7c7b\u578b", "\u516c\u4f1a ID", "\u516c\u4f1a\u540d\u79f0", "\u7ed1\u5b9a ID", "\u7ed1\u5b9a\u65f6\u95f4", "\u5e95\u85aa\u622a\u6b62", "Bonus \u622a\u6b62", "\u5e95\u85aa\u7c7b\u6d41\u6c34", "Bonus \u7c7b\u6d41\u6c34", "\u516c\u4f1a\u85aa\u8d44\u603b\u989d", "\u6709\u6548\u516c\u4f1a\u85aa\u8d44", "\u5e95\u85aa\u6709\u6548\u6d41\u6c34", "Bonus \u6709\u6548\u6d41\u6c34", "\u672c\u6708\u8ba1\u5e95\u85aa", "\u672c\u6708\u8ba1 Bonus", "Bonus \u8fbe\u6807", "\u672c\u6708\u65b0\u589e", "\u5feb\u7167\u65f6\u95f4"]];
guildSheet.getRange("A4:U4").values = guildHeaders;
guildSheet.getRange("A5:U14").values = guildRows;
guildSheet.getRange("A4:U4").format = { fill: blue, font: { bold: true, color: "#FFFFFF" }, horizontalAlignment: "center", wrapText: true };
guildSheet.getRange("A5:U14").format = { borders: border };
guildSheet.getRange("K5:P14").format.numberFormat = moneyFormat;
guildSheet.getRange("A4:U14").format.autofitColumns();
guildSheet.getRange("D4:D14").format.columnWidth = 18;
guildSheet.getRange("F4:F14").format.columnWidth = 24;
guildSheet.getRange("H4:J14").format.columnWidth = 20;
guildSheet.getRange("U4:U14").format.columnWidth = 20;
guildSheet.getRange("A4:U14").format.rowHeight = 22;
guildSheet.tables.add("A4:U14", true, "TestSalaryGuildTable");
guildSheet.freezePanes.freezeRows(4);

qualitySheet.showGridLines = false;
qualitySheet.getRange("A1:J1").merge();
qualitySheet.getRange("A1").values = [["\u6570\u636e\u8d28\u91cf\u5f02\u5e38\u4e0e\u5f85\u6838\u5bf9\u9879"]];
qualitySheet.getRange("A1:J1").format = { fill: "#A8460B", font: { bold: true, color: "#FFFFFF", size: 16 }, horizontalAlignment: "center" };
qualitySheet.getRange("A2:J2").merge();
qualitySheet.getRange("A2").values = [["\u5f53\u524d\u7ed3\u7b97\u6708\u672a\u89e3\u51b3\u85aa\u8d44\u5f02\u5e38\u8bb0\u5f55\uff1a0 \u6761 | \u4ee5\u4e0b\u4e3a\u5b9e\u65f6\u4eba\u5458\u85aa\u8d44\u4e0e\u516c\u4f1a\u85aa\u8d44\u660e\u7ec6\u7684\u5173\u8054\u5dee\u5f02"]];
qualitySheet.getRange("A2:J2").format = { fill: "#FFF1E8", font: { italic: true, color: "#8E4A14" } };
const qualityHeaders = [["\u5b9e\u65f6\u85aa\u8d44 ID", "\u7528\u6237\u7f16\u53f7", "\u59d3\u540d", "\u85aa\u8d44\u7c7b\u578b", "\u603b\u85aa\u8d44", "\u4eba\u5458\u8868\u516c\u4f1a\u85aa\u8d44\u603b\u548c", "\u516c\u4f1a\u660e\u7ec6\u6570", "\u5dee\u5f02", "\u72b6\u6001", "\u8bf4\u660e"]];
qualitySheet.getRange("A4:J4").values = qualityHeaders;
qualitySheet.getRange("A5:J6").values = qualityRows;
qualitySheet.getRange("A4:J4").format = { fill: orange, font: { bold: true, color: "#FFFFFF" }, horizontalAlignment: "center", wrapText: true };
qualitySheet.getRange("A5:J6").format = { fill: lightOrange, borders: { preset: "all", style: "thin", color: "#E2B195" } };
qualitySheet.getRange("E5:H6").format.numberFormat = moneyFormat;
qualitySheet.getRange("A4:J6").format.autofitColumns();
qualitySheet.getRange("D4:D6").format.columnWidth = 20;
qualitySheet.getRange("J4:J6").format.columnWidth = 52;
qualitySheet.getRange("J5:J6").format.wrapText = true;
qualitySheet.getRange("A4:J6").format.rowHeight = 26;
qualitySheet.getRange("J5:J6").format.rowHeight = 42;
qualitySheet.tables.add("A4:J6", true, "TestSalaryQualityTable");
qualitySheet.getRange("I5:I6").conditionalFormats.add("containsText", { text: "\u5f85\u6838\u5bf9", format: { fill: "#FADBD8", font: { color: "#B03A2E", bold: true } } });
qualitySheet.freezePanes.freezeRows(4);

const summaryCheck = await workbook.inspect({ kind: "table", range: "\u85aa\u8d44\u4eba\u5458\u6c47\u603b!A4:S13", include: "values,formulas", tableMaxRows: 12, tableMaxCols: 19 });
const formulaErrors = await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 100 }, summary: "formula error scan" });
console.log(summaryCheck.ndjson);
console.log(formulaErrors.ndjson);

for (const [sheetName, fileName] of [["\u85aa\u8d44\u4eba\u5458\u6c47\u603b", "staff_preview.png"], ["\u7ed1\u5b9a\u516c\u4f1a\u85aa\u8d44\u660e\u7ec6", "guild_preview.png"], ["\u6570\u636e\u8d28\u91cf\u5f02\u5e38", "quality_preview.png"]]) {
  const image = await workbook.render({ sheetName, autoCrop: "all", scale: 1, format: "png" });
  await fs.writeFile(`${outDir}/${fileName}`, new Uint8Array(await image.arrayBuffer()));
}

const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(outFile);
console.log(outFile);
