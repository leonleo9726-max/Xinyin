import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = "E:/Codex/Wechill/outputs/bdm_bd_salary_20260806";
const outputPath = `${outputDir}/current_period_bd_salary_20260806.xlsx`;

const salaryRows = [
  [202608, "2026-08-01 00:00:00", "2026-08-16 00:00:00", "8524370", "Lee", "BD+BDM", "\u8bd5\u7528\u671f", 2, 122.22, 122.22, 100.00, 24.44, 124.44, 62.22, 0, 0, 62.22, 62.22, 10000, 100000, 0.00, 0.00, 1000.00, null, 122.22, 244.44, 1, "2026-08-06T01:05:00.684Z"],
  [202608, "2026-08-01 00:00:00", "2026-08-16 00:00:00", "8535700", "BD", "BD", "\u8f6c\u6b63", 4, 5108.00, 5108.00, 250.00, 204.32, 454.32, 363.46, 0, 0, 90.86, 90.86, 40, 80, 0.00, 0.00, 1000.00, null, 5108.00, 10216.00, 3, "2026-08-06T01:05:00.684Z"],
  [202608, "2026-08-01 00:00:00", "2026-08-16 00:00:00", "8558958", "BD\u4e09\u53f7", "BD", "\u8bd5\u7528\u671f", 2, 110.11, 110.11, 100.00, 22.02, 122.02, 61.01, 0, 0, 61.01, 61.01, 10000, 100000, 0.00, 409.77, 1000.00, null, 862.28, 220.22, 1, "2026-08-06T01:05:00.684Z"],
];

const guildRows = [
  ["8524370", "Lee", 3558, "Yoww", "\u4e2d\u4e1c\u533a", "\u53cc\u5468\u653f\u7b56", "\u7ed1\u5b9a\u4e2d", 233, "2026-06-04T06:18:23.000Z", "2026-08-31T15:59:59.000Z", "2026-08-31T15:59:59.000Z", 122.22, 122.22, 122.22, 244.44, 122.22, 122.22, "\u8ba1\u5165", "\u8ba1\u5165", "\u8fbe\u6807", "\u5426", "2026-08-06T01:05:00.684Z"],
  ["8535700", "BD", 3560, "Yowwn", "\u4e2d\u4e1c\u533a", "\u53cc\u5468\u653f\u7b56", "\u7ed1\u5b9a\u4e2d", 283, "2026-07-31T11:00:00.000Z", "2027-01-15T15:59:59.000Z", "2027-01-15T15:59:59.000Z", 1274.00, 1274.00, 1274.00, 2548.00, 1274.00, 1274.00, "\u8ba1\u5165", "\u8ba1\u5165", "\u8fbe\u6807", "\u5426", "2026-08-06T01:05:00.684Z"],
  ["8535700", "BD", 3562, "Yowwwww", "\u4e2d\u4e1c\u533a", "\u81ea\u7531\u653f\u7b56", "\u7ed1\u5b9a\u4e2d", 284, "2026-07-31T11:00:00.000Z", "2027-01-15T15:59:59.000Z", "2027-01-15T15:59:59.000Z", 1917.00, 1917.00, 1917.00, 3834.00, 1917.00, 1917.00, "\u8ba1\u5165", "\u8ba1\u5165", "\u8fbe\u6807", "\u5426", "2026-08-06T01:05:00.684Z"],
  ["8535700", "BD", 3569, "\u65b0\u4e2d\u4e1c\u533a\u516c\u4f1a\u957f\u81ea\u7531\u7ed3\u7b97", "\u4e2d\u4e1c\u533a", "\u81ea\u7531\u653f\u7b56", "\u7ed1\u5b9a\u4e2d", 282, "2026-07-31T11:00:00.000Z", "2027-01-15T15:59:59.000Z", "2027-01-15T15:59:59.000Z", 1917.00, 1917.00, 1917.00, 3834.00, 1917.00, 1917.00, "\u8ba1\u5165", "\u8ba1\u5165", "\u8fbe\u6807", "\u5426", "2026-08-06T01:05:00.684Z"],
  ["8558958", "BD\u4e09\u53f7", 3541, "\u82f1\u8bed\u533a\u81ea\u7531\u653f\u7b56", "\u82f1\u8bed\u533a", "\u53cc\u5468\u653f\u7b56", "\u7ed1\u5b9a\u4e2d", 272, "2026-06-24T06:46:28.000Z", "2026-07-15T15:59:59.000Z", "2026-07-15T15:59:59.000Z", 0.00, 0.00, 536.60, 0.00, 0.00, 0.00, "\u4e0d\u8ba1\u5165", "\u4e0d\u8ba1\u5165", "\u672a\u8fbe\u6807", "\u5426", "2026-08-06T01:05:00.684Z"],
  ["8558958", "BD\u4e09\u53f7", 3552, "\u82f1\u8bed\u533a\u81ea\u7531\u7ed3\u7b97", "\u82f1\u8bed\u533a", "\u81ea\u7531\u653f\u7b56", "\u7ed1\u5b9a\u4e2d", 274, "2026-06-30T03:52:55.000Z", "2026-07-15T15:59:59.000Z", "2026-07-15T15:59:59.000Z", 0.00, 0.00, 215.57, 0.00, 0.00, 0.00, "\u4e0d\u8ba1\u5165", "\u4e0d\u8ba1\u5165", "\u672a\u8fbe\u6807", "\u5426", "2026-08-06T01:05:00.684Z"],
  ["8558958", "BD\u4e09\u53f7", 3575, "Yomwe", "\u82f1\u8bed\u533a", "\u53cc\u5468\u653f\u7b56", "\u7ed1\u5b9a\u4e2d", 267, "2026-06-23T21:39:09.000Z", "2026-09-15T15:59:59.000Z", "2026-09-15T15:59:59.000Z", 110.11, 110.11, 110.11, 220.22, 110.11, 110.11, "\u8ba1\u5165", "\u8ba1\u5165", "\u8fbe\u6807", "\u5426", "2026-08-06T01:05:00.684Z"],
  ["8558958", "BD\u4e09\u53f7", 3584, "Lastly", "\u82f1\u8bed\u533a", "\u53cc\u5468\u653f\u7b56", "\u7ed1\u5b9a\u4e2d", 273, "2026-06-24T07:00:42.000Z", "2026-07-15T15:59:59.000Z", "2026-07-15T15:59:59.000Z", 0.00, 0.00, 0.00, 0.00, 0.00, 0.00, "\u4e0d\u8ba1\u5165", "\u4e0d\u8ba1\u5165", "\u672a\u8fbe\u6807", "\u5426", "2026-08-06T01:05:00.684Z"],
];

const colors = {
  dark: "#0F4C5C",
  mid: "#167D9A",
  light: "#E7F4F7",
  accent: "#DDEFE1",
  border: "#B9CDD3",
  text: "#14313A",
};

function styleTitle(sheet, lastColumn, title, subtitle) {
  sheet.mergeCells(`A1:${lastColumn}1`);
  sheet.getRange("A1").values = [[title]];
  sheet.getRange(`A1:${lastColumn}1`).format = {
    fill: colors.dark,
    font: { bold: true, color: "#FFFFFF", size: 16 },
    horizontalAlignment: "center",
    verticalAlignment: "center",
  };
  sheet.getRange(`A1:${lastColumn}1`).format.rowHeight = 30;
  sheet.mergeCells(`A2:${lastColumn}2`);
  sheet.getRange("A2").values = [[subtitle]];
  sheet.getRange(`A2:${lastColumn}2`).format = {
    fill: colors.light,
    font: { color: colors.text, italic: true, size: 10 },
    horizontalAlignment: "left",
    verticalAlignment: "center",
  };
  sheet.getRange(`A2:${lastColumn}2`).format.rowHeight = 24;
}

function styleHeader(range) {
  range.format = {
    fill: colors.mid,
    font: { bold: true, color: "#FFFFFF", size: 10 },
    horizontalAlignment: "center",
    verticalAlignment: "center",
    wrapText: true,
    borders: { preset: "outside", style: "thin", color: colors.border },
  };
}

const workbook = Workbook.create();
const summary = workbook.worksheets.add("BD\u85aa\u8d44\u6c47\u603b");
const guilds = workbook.worksheets.add("\u7ed1\u5b9a\u516c\u4f1a\u660e\u7ec6");
const notes = workbook.worksheets.add("\u53e3\u5f84\u8bf4\u660e");

summary.showGridLines = false;
styleTitle(
  summary,
  "AB",
  "202608 \u5f53\u524d\u7ed3\u7b97\u5468\u671f BD \u5b9e\u65f6\u85aa\u8d44\u6c47\u603b",
  "\u5468\u671f\uff1a2026-08-01 00:00:00 \u81f3 2026-08-16 00:00:00\uff1b\u6570\u636e\u6e90\uff1a\u6d4b\u8bd5\u5e93\u5b9e\u65f6 BD \u85aa\u8d44\u3001\u5f53\u524d\u503a\u52a1\u4e0e\u516c\u4f1a\u7ed1\u5b9a\u6570\u636e\u3002"
);

summary.getRange("A4:G4").values = [[
  "\u6709\u85aa\u8d44BD\u6570", "\u603b\u85aa\u8d44", "\u603b\u85aa\u8d44\u4f59\u989d", "\u9884\u652f\u91d1\u989d", "\u501f\u652f\u91d1\u989d", "\u53ef\u501f\u652f\u91d1\u989d", "\u6709\u6548\u516c\u4f1a\u6570"
]];
summary.getRange("A5:G5").formulas = [[
  "=COUNTA(D9:D11)", "=SUM(M9:M11)", "=SUM(N9:N11)", "=SUM(U9:U11)", "=SUM(V9:V11)", "=SUM(X9:X11)", "=SUM(AA9:AA11)"
]];
styleHeader(summary.getRange("A4:G4"));
summary.getRange("A5:G5").format = {
  fill: colors.accent,
  font: { bold: true, color: colors.text, size: 12 },
  horizontalAlignment: "right",
  verticalAlignment: "center",
  borders: { preset: "outside", style: "thin", color: colors.border },
};
summary.getRange("A5").format.numberFormat = "#,##0";
summary.getRange("B5:F5").format.numberFormat = "#,##0.00";
summary.getRange("G5").format.numberFormat = "#,##0";
summary.getRange("A4:G5").format.rowHeight = 24;

const summaryHeaders = [[
  "\u7ed3\u7b97\u6708", "\u5468\u671f\u5f00\u59cb", "\u5468\u671f\u7ed3\u675f", "\u7528\u6237\u7f16\u53f7", "BD\u663e\u793a\u540d", "\u8eab\u4efd", "\u5728\u804c\u72b6\u6001", "\u7b49\u7ea7", "\u5e95\u85aa\u6709\u6548\u6d41\u6c34", "Bonus\u6709\u6548\u6d41\u6c34", "\u5e95\u85aa", "\u516c\u4f1a\u63d0\u6210", "\u603b\u85aa\u8d44", "\u603b\u85aa\u8d44\u4f59\u989d", "\u65b0\u589e\u516c\u4f1a\u6570", "\u6709\u6548\u65b0\u589e\u516c\u4f1a\u6570", "\u65b0\u589e\u516c\u4f1a\u672a\u8fbe\u6807\u6263\u6b3e", "\u6709\u6548\u65b0\u589e\u516c\u4f1a\u672a\u8fbe\u6807\u6263\u6b3e", "\u91d1\u5e01\u5956\u52b1", "\u6e38\u620f\u5e01\u5956\u52b1", "\u9884\u652f\u91d1\u989d", "\u501f\u652f\u91d1\u989d", "\u501f\u652f\u989d\u5ea6", "\u53ef\u501f\u652f\u91d1\u989d", "\u516c\u4f1a\u85aa\u8d44\u603b\u548c", "\u516c\u4f1a\u6709\u6548\u85aa\u8d44\u603b\u548c", "\u6709\u6548\u516c\u4f1a\u6570", "\u5feb\u7167\u65f6\u95f4"
]];
summary.getRange("A8:AB8").values = summaryHeaders;
styleHeader(summary.getRange("A8:AB8"));
summary.getRange("A8:AB8").format.rowHeight = 36;
summary.getRange("A9:W11").values = salaryRows.map((row) => row.slice(0, 23));
summary.getRange("X9:X11").formulas = [["=W9-V9"], ["=W10-V10"], ["=W11-V11"]];
summary.getRange("Y9:AB11").values = salaryRows.map((row) => row.slice(24));
summary.tables.add("A8:AB11", true, "BdSalaryTable").showFilterButton = true;
summary.getRange("A9:AB11").format = {
  verticalAlignment: "center",
  borders: { preset: "insideHorizontal", style: "thin", color: "#D7E2E6" },
};
summary.getRange("A9:H11").format.horizontalAlignment = "center";
summary.getRange("I9:AB11").format.horizontalAlignment = "right";
summary.getRange("I9:N11").format.numberFormat = "#,##0.00";
summary.getRange("O9:P11").format.numberFormat = "#,##0";
summary.getRange("Q9:R11").format.numberFormat = "#,##0.00";
summary.getRange("S9:T11").format.numberFormat = "#,##0";
summary.getRange("U9:Z11").format.numberFormat = "#,##0.00";
summary.getRange("AA9:AA11").format.numberFormat = "#,##0";
summary.getRange("AB9:AB11").format.horizontalAlignment = "left";
summary.getRange("AB9:AB11").format.numberFormat = "yyyy-mm-dd hh:mm:ss";
const summaryWidths = [10, 20, 20, 13, 16, 10, 10, 8, 15, 15, 12, 13, 13, 15, 13, 16, 19, 22, 12, 14, 13, 13, 13, 15, 15, 18, 13, 27];
summaryWidths.forEach((width, index) => {
  summary.getRangeByIndexes(0, index, 11, 1).format.columnWidth = width;
});
summary.getRange("A9:AB11").format.rowHeight = 22;
summary.freezePanes.freezeRows(8);
summary.freezePanes.freezeColumns(4);

guilds.showGridLines = false;
styleTitle(
  guilds,
  "V",
  "202608 \u5f53\u524d\u7ed3\u7b97\u5468\u671f\u7ed1\u5b9a\u516c\u4f1a\u4e0e\u516c\u4f1a\u85aa\u8d44\u660e\u7ec6",
  "\u4ec5\u5173\u8054\u5230\u672c\u5468\u671f\u6709\u85aa\u8d44 BD \u7684\u5b9e\u65f6\u516c\u4f1a\u85aa\u8d44\u660e\u7ec6\uff1b\u516c\u4f1a\u5730\u533a\u53d6\u81ea app_user_agency.region\u3002"
);
const guildHeaders = [[
  "\u7528\u6237\u7f16\u53f7", "BD\u663e\u793a\u540d", "\u516c\u4f1aID", "\u516c\u4f1a\u540d\u79f0", "BD\u5730\u533a", "\u7ed3\u7b97\u653f\u7b56", "\u7ed1\u5b9a\u72b6\u6001", "\u7ed1\u5b9aID", "\u7ed1\u5b9a\u65f6\u95f4", "\u5e95\u85aa\u5230\u671f\u65f6\u95f4", "Bonus\u5230\u671f\u65f6\u95f4", "\u5e95\u85aa\u516c\u4f1a\u85aa\u8d44", "Bonus\u516c\u4f1a\u85aa\u8d44", "\u516c\u4f1a\u85aa\u8d44\u603b\u548c", "\u516c\u4f1a\u6709\u6548\u85aa\u8d44", "\u5e95\u85aa\u6709\u6548\u6d41\u6c34", "Bonus\u6709\u6548\u6d41\u6c34", "\u5e95\u85aa\u7a97\u53e3", "Bonus\u7a97\u53e3", "Bonus\u8fbe\u6807", "\u672c\u6708\u65b0\u589e\u516c\u4f1a", "\u5feb\u7167\u65f6\u95f4"
]];
guilds.getRange("A4:V4").values = guildHeaders;
styleHeader(guilds.getRange("A4:V4"));
guilds.getRange("A4:V4").format.rowHeight = 36;
guilds.getRange("A5:V12").values = guildRows;
guilds.tables.add("A4:V12", true, "BoundGuildTable").showFilterButton = true;
guilds.getRange("A5:V12").format = {
  verticalAlignment: "center",
  borders: { preset: "insideHorizontal", style: "thin", color: "#D7E2E6" },
};
guilds.getRange("A5:C12").format.horizontalAlignment = "center";
guilds.getRange("D5:K12").format.horizontalAlignment = "left";
guilds.getRange("L5:Q12").format.numberFormat = "#,##0.00";
guilds.getRange("R5:U12").format.horizontalAlignment = "center";
guilds.getRange("V5:V12").format.horizontalAlignment = "left";
guilds.getRange("I5:K12").format.numberFormat = "yyyy-mm-dd hh:mm:ss";
guilds.getRange("V5:V12").format.numberFormat = "yyyy-mm-dd hh:mm:ss";
const guildWidths = [13, 16, 10, 26, 12, 12, 12, 10, 27, 27, 27, 15, 15, 15, 15, 16, 16, 12, 12, 12, 16, 27];
guildWidths.forEach((width, index) => {
  guilds.getRangeByIndexes(0, index, 12, 1).format.columnWidth = width;
});
guilds.getRange("A5:V12").format.rowHeight = 22;
guilds.freezePanes.freezeRows(4);
guilds.freezePanes.freezeColumns(3);

notes.showGridLines = false;
styleTitle(notes, "D", "\u6570\u636e\u53e3\u5f84\u4e0e\u5bfc\u51fa\u8bf4\u660e", "\u7528\u4e8e\u5ba1\u8ba1\u5f53\u524d\u7ed3\u7b97\u5468\u671f BD \u5b9e\u65f6\u85aa\u8d44\u6570\u636e\u3002");
notes.getRange("A4:D4").values = [["\u9879\u76ee", "\u53e3\u5f84", "\u6570\u636e\u6e90", "\u8bf4\u660e"]];
styleHeader(notes.getRange("A4:D4"));
notes.getRange("A5:D10").values = [
  ["\u7ed3\u7b97\u5468\u671f", "2026-08-01 00:00:00 \u81f3 2026-08-16 00:00:00", "BDM\u4e1a\u52a1\u89c4\u5219", "\u5f53\u524d\u4e3a\u4e0a\u534a\u6708\u7ed3\u7b97\u5468\u671f\u3002"],
  ["BD\u85aa\u8d44", "salary_role=1 \u4e14 total_salary>0", "bd_realtime_staff_salary", "\u4ec5\u5c55\u793a BD \u4e2a\u4eba\u85aa\u8d44\uff0c\u4e0d\u542b BDM \u56e2\u961f\u7ba1\u7406\u85aa\u8d44\u3002"],
  ["\u85aa\u8d44\u4f59\u989d", "\u76f4\u63a5\u5c55\u793a total_salary_balance", "bd_realtime_staff_salary", "\u5df2\u5e94\u7528\u65b0\u589e\u516c\u4f1a\u8003\u6838\u6263\u6b3e\u3002"],
  ["\u9884\u652f\u4e0e\u501f\u652f", "\u5f53\u524d\u672a\u8fd8\u91d1\u989d", "bd_staff_salary_debt", "\u72ec\u7acb\u4e8e\u5b9e\u65f6\u85aa\u8d44\u4f59\u989d\uff0c\u4e0d\u5728\u672c\u8868\u91cd\u590d\u6263\u51cf\u3002"],
  ["\u516c\u4f1a\u5730\u533a", "0=\u82f1\u8bed\u533a\uff1b2=\u4e2d\u4e1c\u533a", "app_user_agency", "\u4ee5\u7ed1\u5b9a\u516c\u4f1a\u5730\u533a\u4e3a\u51c6\u3002"],
  ["\u516c\u4f1a\u85aa\u8d44", "\u5b9e\u65f6\u516c\u4f1a\u7ef4\u5ea6\u85aa\u8d44", "bd_realtime_guild_salary", "\u5305\u542b\u7a97\u53e3\u3001\u8fbe\u6807\u4e0e\u6709\u6548\u6d41\u6c34\u6807\u8bb0\u3002"],
];
notes.tables.add("A4:D10", true, "NotesTable").showFilterButton = false;
notes.getRange("A5:D10").format = {
  verticalAlignment: "center",
  wrapText: true,
  borders: { preset: "insideHorizontal", style: "thin", color: "#D7E2E6" },
};
notes.getRange("A5:A10").format = { font: { bold: true, color: colors.text }, fill: "#F2F8F9", verticalAlignment: "center" };
[18, 34, 28, 54].forEach((width, index) => {
  notes.getRangeByIndexes(0, index, 10, 1).format.columnWidth = width;
});
notes.getRange("A5:D10").format.rowHeight = 32;
notes.freezePanes.freezeRows(4);

await fs.mkdir(outputDir, { recursive: true });
const inspection = await workbook.inspect({
  kind: "table",
  range: "BD\u85aa\u8d44\u6c47\u603b!A1:AB11",
  include: "values,formulas",
  tableMaxRows: 12,
  tableMaxCols: 28,
});
console.log(inspection.ndjson);
const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "formula error scan",
});
console.log(errors.ndjson);
for (const sheetName of ["BD\u85aa\u8d44\u6c47\u603b", "\u7ed1\u5b9a\u516c\u4f1a\u660e\u7ec6", "\u53e3\u5f84\u8bf4\u660e"]) {
  const preview = await workbook.render({ sheetName, autoCrop: "all", scale: 1, format: "png" });
  const fileName = sheetName.replaceAll("/", "_");
  await fs.writeFile(`${outputDir}/${fileName}.png`, new Uint8Array(await preview.arrayBuffer()));
}
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);
console.log(`EXPORTED=${outputPath}`);
