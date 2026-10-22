import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outDir = "E:/Codex/Wechill/outputs/bdm_salary_members_20260729_0705";
const outFile = `${outDir}/BDM_BD_Salary_Members_20260729.xlsx`;
const month = 202607;
const snapshot = "2026-07-29 07:05:00 UTC";

const rows = [
  [9, "8517682", "uBD\u516d\u53f7", "BD", "\u8bd5\u7528", "\u7981\u7528", "BD\u4e2a\u4eba\u85aa\u8d44", 5, 4411.11, 4411.11, 500, 1323.33, 1, 911.66, 1823.33, 911.67, 4411.11, 8822.22, 2, "\u5426", "\u672a\u9a8c\u8bc1", "\u5426", snapshot],
  [18, "8524370", "Lee", "BDM+BD", "\u8bd5\u7528", "\u542f\u7528", "BD\u4e2a\u4eba\u85aa\u8d44", 2, 312.76, 312.76, 200, 62.55, 0, 131.27, 262.55, 131.28, 312.76, 625.52, 1, "\u5426", "\u672a\u9a8c\u8bc1", "\u5426", snapshot],
  [8, "8558958", "BD\u4e09\u53f7", "BD", "\u8bd5\u7528", "\u542f\u7528", "BD\u4e2a\u4eba\u85aa\u8d44", 4, 312.55, 312.55, 200, 62.51, 0, 131.25, 262.51, 131.26, 2538.75, 625.1, 1, "\u5426", "\u672a\u9a8c\u8bc1", "\u5426", snapshot],
  [12, "8590613", "leo", "BDM+BD", "\u8f6c\u6b63", "\u7981\u7528", "BD\u4e2a\u4eba\u85aa\u8d44", 2, 312.55, 312.55, 200, 62.51, 1, 131.25, 262.51, 131.26, 312.55, 625.1, 1, "\u5426", "\u672a\u9a8c\u8bc1", "\u5426", snapshot],
  [25, "8590613", "leo", "BDM+BD", "\u8f6c\u6b63", "\u7981\u7528", "BDM\u56e2\u961f\u7ba1\u7406\u85aa\u8d44", 5, 5036.21, 5036.21, 500, 1007.24, 2, 0, 1507.24, 1507.24, 7262.41, 5036.21, 4, "\u5426", "\u672a\u9a8c\u8bc1", "\u5426", snapshot],
  [27, "8524370", "Lee", "BDM+BD", "\u8bd5\u7528", "\u542f\u7528", "BDM\u56e2\u961f\u7ba1\u7406\u85aa\u8d44", 1, 312.76, 312.76, 100, 62.55, 0, 0, 162.55, 162.55, 312.76, 312.76, 1, "\u5426", "\u672a\u9a8c\u8bc1", "\u5426", snapshot],
];

const wb = Workbook.create();
const detail = wb.worksheets.add("\u85aa\u8d44\u6210\u5458\u660e\u7ec6");
const summary = wb.worksheets.add("\u85aa\u8d44\u6c47\u603b");
const quality = wb.worksheets.add("\u6570\u636e\u8d28\u91cf\u63d0\u793a");

const navy = "#163E6C";
const teal = "#0F6E8C";
const paleBlue = "#EAF2F8";
const orange = "#D95D18";
const paleOrange = "#FFF0E7";
const lightBorder = { preset: "all", style: "thin", color: "#C7D6E5" };
const money = "#,##0.00";

detail.showGridLines = false;
detail.getRange("A1:X1").merge();
detail.getRange("A1").values = [["\u6d4b\u8bd5\u73af\u5883 BD / BDM \u6709\u85aa\u8d44\u6210\u5458\u660e\u7ec6"]];
detail.getRange("A1:X1").format = { fill: navy, font: { bold: true, color: "#FFFFFF", size: 16 }, horizontalAlignment: "center" };
detail.getRange("A2:X2").merge();
detail.getRange("A2").values = [[`\u6570\u636e\u6e90\uff1a\u6d4b\u8bd5\u5e93 mysql | \u7ed3\u7b97\u6708\uff1a${month} | \u7b5b\u9009\u6761\u4ef6\uff1a\u5b9e\u65f6\u603b\u85aa\u8d44\u975e\u96f6 | \u5feb\u7167\uff1a${snapshot}`]];
detail.getRange("A2:X2").format = { fill: paleBlue, font: { italic: true, color: "#4F6476" } };
const headers = [["\u5b9e\u65f6\u85aa\u8d44 ID", "\u7528\u6237\u7f16\u53f7", "\u59d3\u540d", "\u8eab\u4efd", "\u5728\u804c\u72b6\u6001", "\u8d26\u53f7\u72b6\u6001", "\u85aa\u8d44\u7c7b\u578b", "\u7b49\u7ea7", "\u5e95\u85aa\u6709\u6548\u6d41\u6c34", "Bonus \u6709\u6548\u6d41\u6c34", "\u5e95\u85aa", "\u516c\u4f1a\u63d0\u6210", "\u65b0\u589e\u516c\u4f1a\u6570", "\u65b0\u516c\u4f1a\u6263\u6b3e", "\u603b\u85aa\u8d44", "\u85aa\u8d44\u4f59\u989d", "\u516c\u4f1a\u85aa\u8d44\u603b\u548c", "\u6709\u6548\u516c\u4f1a\u85aa\u8d44\u603b\u548c", "\u6709\u6548\u516c\u4f1a\u6570", "\u5ba1\u6838\u6807\u8bb0", "\u5ba1\u6838\u9a8c\u8bc1", "\u5b98\u65b9\u8d26\u53f7", "\u5feb\u7167\u65f6\u95f4", "\u8d26\u53f7\u4e0e\u85aa\u8d44\u6821\u9a8c"]];
detail.getRange("A4:X4").values = headers;
detail.getRange("A5:W10").values = rows;
detail.getRange("X5").formulas = [["=IF(AND(E5<>\"\u79bb\u804c\",F5=\"\u7981\u7528\"),\"\u5f85\u6838\u5bf9\",\"\u6b63\u5e38\")"]];
detail.getRange("X5:X10").fillDown();
detail.getRange("A4:X4").format = { fill: teal, font: { bold: true, color: "#FFFFFF" }, horizontalAlignment: "center", wrapText: true };
detail.getRange("A5:X10").format = { borders: lightBorder };
detail.getRange("I5:R10").format.numberFormat = money;
detail.getRange("A4:X10").format.autofitColumns();
detail.getRange("B4:B10").format.columnWidth = 13;
detail.getRange("G4:G10").format.columnWidth = 19;
detail.getRange("W4:W10").format.columnWidth = 22;
detail.getRange("X4:X10").format.columnWidth = 16;
detail.getRange("A4:X10").format.rowHeight = 22;
detail.tables.add("A4:X10", true, "SalaryMemberTable");
detail.getRange("X5:X10").conditionalFormats.add("containsText", { text: "\u5f85\u6838\u5bf9", format: { fill: "#FADBD8", font: { color: "#B03A2E", bold: true } } });
detail.freezePanes.freezeRows(4);

summary.showGridLines = false;
summary.getRange("A1:H1").merge();
summary.getRange("A1").values = [["\u6d4b\u8bd5\u73af\u5883 BD / BDM \u85aa\u8d44\u6c47\u603b"]];
summary.getRange("A1:H1").format = { fill: navy, font: { bold: true, color: "#FFFFFF", size: 16 }, horizontalAlignment: "center" };
summary.getRange("A2:H2").merge();
summary.getRange("A2").values = [[`\u5bf9\u5e94\u660e\u7ec6\u5feb\u7167\uff1a${snapshot}`]];
summary.getRange("A2:H2").format = { fill: paleBlue, font: { italic: true, color: "#4F6476" } };
summary.getRange("A4:H4").values = [["\u85aa\u8d44\u8bb0\u5f55\u6570", null, "BD\u4e2a\u4eba\u85aa\u8d44", null, "BDM\u56e2\u961f\u85aa\u8d44", null, "\u603b\u85aa\u8d44", null]];
summary.getRange("B4").formulas = [["=COUNTA('\u85aa\u8d44\u6210\u5458\u660e\u7ec6'!A5:A10)"]];
summary.getRange("D4").formulas = [["=SUMIF('\u85aa\u8d44\u6210\u5458\u660e\u7ec6'!G5:G10,\"BD\u4e2a\u4eba\u85aa\u8d44\",'\u85aa\u8d44\u6210\u5458\u660e\u7ec6'!O5:O10)"]];
summary.getRange("F4").formulas = [["=SUMIF('\u85aa\u8d44\u6210\u5458\u660e\u7ec6'!G5:G10,\"BDM\u56e2\u961f\u7ba1\u7406\u85aa\u8d44\",'\u85aa\u8d44\u6210\u5458\u660e\u7ec6'!O5:O10)"]];
summary.getRange("H4").formulas = [["=SUM(D4,F4)"]];
summary.getRange("A4:H4").format = { fill: paleBlue, font: { bold: true, color: navy }, borders: lightBorder, horizontalAlignment: "center" };
summary.getRange("B4").format.numberFormat = "#,##0";
summary.getRange("D4,F4,H4").format.numberFormat = money;
summary.getRange("A4:H4").format.columnWidth = 17;
summary.getRange("A6:C6").values = [["\u85aa\u8d44\u7c7b\u578b", "\u8bb0\u5f55\u6570", "\u603b\u85aa\u8d44"]];
summary.getRange("A7:A8").values = [["BD\u4e2a\u4eba\u85aa\u8d44"], ["BDM\u56e2\u961f\u7ba1\u7406\u85aa\u8d44"]];
summary.getRange("B7").formulas = [["=COUNTIF('\u85aa\u8d44\u6210\u5458\u660e\u7ec6'!G5:G10,A7)"]];
summary.getRange("B7:B8").fillDown();
summary.getRange("C7").formulas = [["=SUMIF('\u85aa\u8d44\u6210\u5458\u660e\u7ec6'!G5:G10,A7,'\u85aa\u8d44\u6210\u5458\u660e\u7ec6'!O5:O10)"]];
summary.getRange("C7:C8").fillDown();
summary.getRange("A6:C8").format = { borders: lightBorder };
summary.getRange("A6:C6").format = { fill: teal, font: { bold: true, color: "#FFFFFF" }, horizontalAlignment: "center" };
summary.getRange("B7:B8").format.numberFormat = "#,##0";
summary.getRange("C7:C8").format.numberFormat = money;
summary.getRange("E6:H6").merge();
summary.getRange("E6").values = [["\u6570\u636e\u8d28\u91cf\u7edf\u8ba1"]];
summary.getRange("E6:H6").format = { fill: orange, font: { bold: true, color: "#FFFFFF" }, horizontalAlignment: "center" };
summary.getRange("E7:G7").values = [["\u5f53\u6708\u5f85\u5904\u7406\u85aa\u8d44\u5f02\u5e38", "\u7981\u7528\u8d26\u53f7\u85aa\u8d44\u8bb0\u5f55", "\u8d26\u53f7\u6821\u9a8c\u5f85\u6838\u5bf9"]];
summary.getRange("E8").values = [[0]];
summary.getRange("F8").formulas = [["=COUNTIF('\u85aa\u8d44\u6210\u5458\u660e\u7ec6'!F5:F10,\"\u7981\u7528\")"]];
summary.getRange("G8").formulas = [["=COUNTIF('\u85aa\u8d44\u6210\u5458\u660e\u7ec6'!X5:X10,\"\u5f85\u6838\u5bf9\")"]];
summary.getRange("E7:G8").format = { fill: paleOrange, borders: { preset: "all", style: "thin", color: "#E2B195" }, horizontalAlignment: "center", wrapText: true };
summary.getRange("E7:G7").format.font = { bold: true, color: "#8E4A14" };
summary.getRange("E6:H8").format.columnWidth = 18;
summary.getRange("E7:G7").format.rowHeight = 35;

quality.showGridLines = false;
quality.getRange("A1:G1").merge();
quality.getRange("A1").values = [["\u6570\u636e\u8d28\u91cf\u5f85\u6838\u5bf9\u9879"]];
quality.getRange("A1:G1").format = { fill: orange, font: { bold: true, color: "#FFFFFF", size: 16 }, horizontalAlignment: "center" };
quality.getRange("A2:G2").merge();
quality.getRange("A2").values = [["\u5f53\u524d\u6709\u85aa\u8d44\u7684\u5728\u804c\u6210\u5458\u4e2d\uff0c\u8d26\u53f7\u72b6\u6001\u4e3a\u7981\u7528\u7684\u7528\u6237\u9700\u8981\u786e\u8ba4\u4e1a\u52a1\u4e00\u81f4\u6027"]];
quality.getRange("A2:G2").format = { fill: paleOrange, font: { italic: true, color: "#8E4A14" } };
quality.getRange("A4:G4").values = [["\u7528\u6237\u7f16\u53f7", "\u59d3\u540d", "\u5728\u804c\u72b6\u6001", "\u8d26\u53f7\u72b6\u6001", "\u85aa\u8d44\u8bb0\u5f55\u6570", "\u72b6\u6001", "\u8bf4\u660e"]];
quality.getRange("A5:D6").values = [["8517682", "uBD\u516d\u53f7", "\u8bd5\u7528", "\u7981\u7528"], ["8590613", "leo", "\u8f6c\u6b63", "\u7981\u7528"]];
quality.getRange("E5").formulas = [["=COUNTIF('\u85aa\u8d44\u6210\u5458\u660e\u7ec6'!B$5:B$10,A5)"]];
quality.getRange("E5:E6").fillDown();
quality.getRange("F5:F6").values = [["\u5f85\u6838\u5bf9"], ["\u5f85\u6838\u5bf9"]];
quality.getRange("G5:G6").values = [["\u5728\u804c\u4e14\u6709\u85aa\u8d44\uff0c\u4f46\u8d26\u53f7\u72b6\u6001\u4e3a\u7981\u7528"], ["\u5728\u804c\u4e14\u6709\u85aa\u8d44\uff0c\u4f46\u8d26\u53f7\u72b6\u6001\u4e3a\u7981\u7528"]];
quality.getRange("A4:G4").format = { fill: orange, font: { bold: true, color: "#FFFFFF" }, horizontalAlignment: "center" };
quality.getRange("A5:G6").format = { fill: paleOrange, borders: { preset: "all", style: "thin", color: "#E2B195" } };
quality.getRange("F5:F6").conditionalFormats.add("containsText", { text: "\u5f85\u6838\u5bf9", format: { fill: "#FADBD8", font: { color: "#B03A2E", bold: true } } });
quality.getRange("A4:G6").format.autofitColumns();
quality.getRange("G4:G6").format.columnWidth = 38;
quality.getRange("G5:G6").format.wrapText = true;
quality.getRange("A4:G6").format.rowHeight = 26;
quality.getRange("G5:G6").format.rowHeight = 36;
quality.tables.add("A4:G6", true, "SalaryQualityTable");

const summaryCheck = await wb.inspect({ kind: "table", range: "\u85aa\u8d44\u6c47\u603b!A1:H8", include: "values,formulas", tableMaxRows: 10, tableMaxCols: 8 });
const detailCheck = await wb.inspect({ kind: "table", range: "\u85aa\u8d44\u6210\u5458\u660e\u7ec6!A4:X10", include: "values,formulas", tableMaxRows: 8, tableMaxCols: 24 });
const errors = await wb.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 100 }, summary: "formula error scan" });
console.log(summaryCheck.ndjson);
console.log(detailCheck.ndjson);
console.log(errors.ndjson);

for (const [sheetName, fileName] of [["\u85aa\u8d44\u6210\u5458\u660e\u7ec6", "detail_preview.png"], ["\u85aa\u8d44\u6c47\u603b", "summary_preview.png"], ["\u6570\u636e\u8d28\u91cf\u63d0\u793a", "quality_preview.png"]]) {
  const image = await wb.render({ sheetName, autoCrop: "all", scale: 1, format: "png" });
  await fs.writeFile(`${outDir}/${fileName}`, new Uint8Array(await image.arrayBuffer()));
}

const xlsx = await SpreadsheetFile.exportXlsx(wb);
await xlsx.save(outFile);
console.log(outFile);
