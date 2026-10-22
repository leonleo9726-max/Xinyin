import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = "E:/Codex/Wechill/outputs/bdm_bd_salary_20260731";
const workbook = Workbook.create();
const sheet = workbook.worksheets.add("BD\u85aa\u8d44");
sheet.showGridLines = false;

const data = [
  [202607, "8517682", "uBD\u516d\u53f7", "BD", "\u8bd5\u7528", 5, 4411.11, 4411.11, 500.00, 1323.33, 1, 1, 911.66, 911.66, 1823.33, 911.67, 50000, 500000, 500.00, 1000.00, 1000.00, 0.00],
  [202607, "8524370", "Lee", "BD+BDM", "\u8bd5\u7528", 2, 312.76, 312.76, 200.00, 62.55, 0, 0, 131.27, 131.27, 262.55, 131.28, 20000, 200000, 200.00, 100.00, 1000.00, 900.00],
  [202607, "8558958", "BD\u4e09\u53f7", "BD", "\u8bd5\u7528", 4, 312.55, 312.55, 200.00, 62.51, 0, 0, 131.25, 131.25, 262.51, 131.26, 20000, 200000, 131.00, 420.00, 1000.00, 580.00],
  [202607, "8590613", "leo", "BD+BDM", "\u8f6c\u6b63", 2, 312.55, 312.55, 200.00, 62.51, 1, 1, 131.25, 131.25, 262.51, 131.26, 20000, 200000, 100.00, 1000.00, 2000.00, 1000.00],
];

const headers = [[
  "\u7ed3\u7b97\u6708", "\u7528\u6237\u7f16\u53f7", "BD\u5c55\u793a\u540d", "\u8eab\u4efd", "\u5728\u804c\u72b6\u6001", "\u7b49\u7ea7",
  "\u5e95\u85aa\u6709\u6548\u6d41\u6c34", "Bonus\u6709\u6548\u6d41\u6c34", "\u5e95\u85aa", "\u516c\u4f1a\u63d0\u6210",
  "\u65b0\u589e\u516c\u4f1a\u6570", "\u6709\u6548\u65b0\u589e\u516c\u4f1a\u6570", "\u65b0\u589e\u516c\u4f1a\u672a\u8fbe\u6807\u6263\u6b3e", "\u6709\u6548\u65b0\u589e\u516c\u4f1a\u672a\u8fbe\u6807\u6263\u6b3e",
  "\u603b\u85aa\u8d44", "\u603b\u85aa\u8d44\u4f59\u989d", "\u5956\u52b1\u91d1\u5e01", "\u6e38\u620f\u5e01\u5956\u52b1",
  "\u9884\u652f\u91d1\u989d", "\u501f\u652f\u91d1\u989d", "\u501f\u652f\u989d\u5ea6", "\u53ef\u501f\u652f\u91d1\u989d"
]];

sheet.mergeCells("A1:V1");
sheet.getRange("A1").values = [["202607 \u5f53\u524d\u6708 BD \u85aa\u8d44\u4e0e\u9884\u652f\u501f\u652f\u6c47\u603b"]];
sheet.mergeCells("A2:V2");
sheet.getRange("A2").values = [["\u6570\u636e\u6765\u6e90\uff1a\u6d4b\u8bd5\u5e93\u5b9e\u65f6\u85aa\u8d44\u8868 + \u5f53\u524d\u503a\u52a1\u6c47\u603b\u8868\u3002\u603b\u85aa\u8d44\u4f59\u989d\u4e0e\u9884\u652f\u91d1\u989d/\u501f\u652f\u91d1\u989d\u4e3a\u72ec\u7acb\u5feb\u7167\uff0c\u4e0d\u4f5c\u4e8c\u6b21\u6263\u51cf\u3002"]];

sheet.getRange("A4:F4").values = [[
  "\u6709\u85aa\u8d44BD\u6570", "\u603b\u85aa\u8d44", "\u603b\u85aa\u8d44\u4f59\u989d", "\u9884\u652f\u91d1\u989d", "\u501f\u652f\u91d1\u989d", "\u53ef\u501f\u652f\u91d1\u989d"
]];
sheet.getRange("A5:F5").formulas = [[
  "=COUNTA(B9:B12)", "=SUM(O9:O12)", "=SUM(P9:P12)", "=SUM(S9:S12)", "=SUM(T9:T12)", "=SUM(V9:V12)"
]];

sheet.getRange("A8:V8").values = headers;
sheet.getRange("A9:V12").values = data;
const table = sheet.tables.add("A8:V12", true, "BdSalaryTable");
table.showFilterButton = true;
table.showBandedColumns = false;

sheet.getRange("A1:V1").format = {
  fill: "#0F766E",
  font: { bold: true, color: "#FFFFFF", size: 16 },
  horizontalAlignment: "center",
  verticalAlignment: "center",
};
sheet.getRange("A2:V2").format = {
  fill: "#E6FFFB",
  font: { color: "#134E4A", italic: true, size: 10 },
  horizontalAlignment: "left",
  verticalAlignment: "center",
};
sheet.getRange("A4:F4").format = {
  fill: "#D1FAE5",
  font: { bold: true, color: "#065F46" },
  horizontalAlignment: "center",
  verticalAlignment: "center",
  borders: { preset: "outside", style: "thin", color: "#99F6E4" },
};
sheet.getRange("A5:F5").format = {
  fill: "#F0FDFA",
  font: { bold: true, color: "#115E59", size: 12 },
  horizontalAlignment: "right",
  verticalAlignment: "center",
  borders: { preset: "outside", style: "thin", color: "#99F6E4" },
  numberFormat: "#,##0.00",
};
sheet.getRange("A5").format.numberFormat = "#,##0";
sheet.getRange("A8:V8").format = {
  fill: "#115E59",
  font: { bold: true, color: "#FFFFFF", size: 10 },
  horizontalAlignment: "center",
  verticalAlignment: "center",
  wrapText: true,
};
sheet.getRange("A9:V12").format = {
  verticalAlignment: "center",
  borders: { preset: "insideHorizontal", style: "thin", color: "#D1D5DB" },
};
sheet.getRange("A9:F12").format.horizontalAlignment = "center";
sheet.getRange("G9:V12").format.horizontalAlignment = "right";
sheet.getRange("G9:J12").format.numberFormat = "#,##0.00";
sheet.getRange("K9:L12").format.numberFormat = "#,##0";
sheet.getRange("M9:P12").format.numberFormat = "#,##0.00";
sheet.getRange("Q9:R12").format.numberFormat = "#,##0";
sheet.getRange("S9:V12").format.numberFormat = "#,##0.00";

const widths = [10, 13, 16, 11, 11, 8, 15, 15, 12, 13, 13, 16, 19, 21, 13, 15, 12, 14, 13, 13, 13, 15];
for (let index = 0; index < widths.length; index += 1) {
  sheet.getRangeByIndexes(0, index, 12, 1).format.columnWidth = widths[index];
}
sheet.getRange("A1:V1").format.rowHeight = 30;
sheet.getRange("A2:V2").format.rowHeight = 24;
sheet.getRange("A4:F5").format.rowHeight = 24;
sheet.getRange("A8:V8").format.rowHeight = 34;
sheet.getRange("A9:V12").format.rowHeight = 21;
sheet.freezePanes.freezeRows(8);
sheet.freezePanes.freezeColumns(2);

const check = await workbook.inspect({
  kind: "table",
  range: "BD\u85aa\u8d44!A1:V12",
  include: "values,formulas",
  tableMaxRows: 12,
  tableMaxCols: 22,
});
console.log(check.ndjson);
const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "formula error scan",
});
console.log(errors.ndjson);

const preview = await workbook.render({ sheetName: "BD\u85aa\u8d44", range: "A1:V12", scale: 1, format: "png" });
await fs.writeFile(`${outputDir}/preview.png`, new Uint8Array(await preview.arrayBuffer()));
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(`${outputDir}/test_bd_salary_with_debt_202607.xlsx`);
