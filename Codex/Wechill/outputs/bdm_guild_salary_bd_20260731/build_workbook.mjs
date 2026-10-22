import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = "E:/Codex/Wechill/outputs/bdm_guild_salary_bd_20260731";
const outputPath = `${outputDir}/test_guild_salary_with_bd_202607.xlsx`;

const text = {
  sheet: "\u516c\u4f1a\u85aa\u8d44BD",
  title: "202607 \u6d4b\u8bd5\u73af\u5883\u516c\u4f1a\u85aa\u8d44\u4e0e\u7ed1\u5b9a BD \u6e05\u5355",
  source: "\u6570\u636e\u6e90\uff1a\u6d4b\u8bd5\u5e93 bd_realtime_guild_salary\uff1b\u7ed1\u5b9a\u5173\u7cfb\uff1a\u85aa\u8d44\u884c bind_id \u5173\u8054 bd_agency_bind",
  trial: "\u8bd5\u7528",
  regular: "\u8f6c\u6b63",
  active: "\u6709\u6548",
};

const rows = [
  [202607, 3529, "leon guild", 4098.56, 8197.12, 278, 8517682, "u15761", 23, "uBD\u516d\u53f7", "BD", text.trial, text.active],
  [202607, 3541, "\u82f1\u8bed\u533a\u81ea\u7531\u653f\u7b56", 1357.10, 0, 272, 8558958, "u15752", 24, "BD\u4e09\u53f7", "BD", text.trial, text.active],
  [202607, 3552, "\u82f1\u8bed\u533a\u81ea\u7531\u7ed3\u7b97", 556.55, 0, 274, 8558958, "u15752", 24, "BD\u4e09\u53f7", "BD", text.trial, text.active],
  [202607, 3558, "Yoww", 312.76, 625.52, 233, 8524370, "u15880", 6, "Lee", "BD+BDM", text.trial, text.active],
  [202607, 3575, "Yomwe", 312.55, 625.10, 267, 8558958, "u15752", 24, "BD\u4e09\u53f7", "BD", text.trial, text.active],
  [202607, 3581, "1155555555", 312.55, 625.10, 264, 8517682, "u15761", 23, "uBD\u516d\u53f7", "BD", text.trial, text.active],
  [202607, 3584, "Lastly", 312.55, 0, 273, 8558958, "u15752", 24, "BD\u4e09\u53f7", "BD", text.trial, text.active],
  [202607, 3587, "Thgfgfg", 312.55, 625.10, 279, 8590613, "\u82f1\u8bed\u533aBDM", 19, "leo", "BD+BDM", text.regular, text.active],
  [202607, 3551, "\u4f1a\u80cc\u5510\u8bd7\u5417", 134.80, 269.60, 253, 8594890, "bug\u6ee1\u5929\u98de", 10, "bug\u6ee1\u5929\u98de", "BD", text.regular, text.active],
  [202607, 3533, "Saudi Arabia", 13.25, 0, 281, 8577097, "u16453", 25, "kocekid", "BD+BDM", text.trial, text.active],
];

const workbook = Workbook.create();
const sheet = workbook.worksheets.add(text.sheet);
sheet.showGridLines = false;

sheet.mergeCells("A1:M1");
sheet.getRange("A1").values = [[text.title]];
sheet.getRange("A1").format = {
  fill: "#0B4F6C",
  font: { bold: true, color: "#FFFFFF", size: 16 },
  horizontalAlignment: "center",
  verticalAlignment: "center",
};
sheet.getRange("A1").format.rowHeight = 30;

sheet.mergeCells("A2:M2");
sheet.getRange("A2").values = [[text.source]];
sheet.getRange("A2").format = {
  fill: "#E8F1F5",
  font: { color: "#35515E", italic: true, size: 10 },
  horizontalAlignment: "left",
  verticalAlignment: "center",
};
sheet.getRange("A2").format.rowHeight = 22;

sheet.getRange("A4:E4").values = [[
  "\u6709\u85aa\u8d44\u516c\u4f1a\u6570",
  "\u516c\u4f1a\u85aa\u8d44\u5408\u8ba1",
  "\u6709\u6548\u85aa\u8d44\u5408\u8ba1",
  "\u85aa\u8d44\u6708\u4efd",
  "\u6570\u636e\u6765\u6e90",
]];
sheet.getRange("A5:E5").values = [[null, null, null, null, "\u6d4b\u8bd5\u5e93\u5b9e\u65f6\u85aa\u8d44\u8868"]];
sheet.getRange("A5").formulas = [["=COUNTA(A9:A18)"]];
sheet.getRange("B5").formulas = [["=SUM(D9:D18)"]];
sheet.getRange("C5").formulas = [["=SUM(E9:E18)"]];
sheet.getRange("D5").formulas = [["=MIN(A9:A18)"]];
sheet.getRange("A4:E4").format = {
  fill: "#DCEAF0",
  font: { bold: true, color: "#0B4F6C" },
  horizontalAlignment: "center",
  verticalAlignment: "center",
  borders: { preset: "outside", style: "thin", color: "#9DBCC9" },
};
sheet.getRange("A5:E5").format = {
  fill: "#F7FBFC",
  font: { bold: true, color: "#1F2933" },
  horizontalAlignment: "center",
  verticalAlignment: "center",
  borders: { preset: "outside", style: "thin", color: "#9DBCC9" },
};
sheet.getRange("B5:C5").format.numberFormat = "#,##0.00";
sheet.getRange("A4:E5").format.rowHeight = 22;

const headers = [[
  "\u85aa\u8d44\u6708\u4efd", "\u516c\u4f1aID", "\u516c\u4f1a\u540d\u79f0", "\u516c\u4f1a\u85aa\u8d44", "\u6709\u6548\u85aa\u8d44", "\u7ed1\u5b9aID", "BD\u7528\u6237\u53f7", "BD\u6635\u79f0", "BD\u5458\u5de5ID", "BD\u663e\u793a\u540d", "BD\u8eab\u4efd", "\u5728\u804c\u72b6\u6001", "\u7ed1\u5b9a\u72b6\u6001",
]];
sheet.getRange("A8:M8").values = headers;
sheet.getRange("A9:M18").values = rows;
sheet.getRange("A8:M8").format = {
  fill: "#146C94",
  font: { bold: true, color: "#FFFFFF" },
  horizontalAlignment: "center",
  verticalAlignment: "center",
  wrapText: true,
  borders: { preset: "outside", style: "thin", color: "#0B4F6C" },
};
sheet.getRange("A9:M18").format = {
  verticalAlignment: "center",
  borders: { preset: "insideHorizontal", style: "thin", color: "#DCE6EB" },
};
sheet.getRange("A9:B18").format.horizontalAlignment = "center";
sheet.getRange("D9:E18").format.numberFormat = "#,##0.00";
sheet.getRange("D9:E18").format.horizontalAlignment = "right";
sheet.getRange("F9:G18").format.horizontalAlignment = "center";
sheet.getRange("I9:M18").format.horizontalAlignment = "center";
sheet.getRange("A8:M18").format.rowHeight = 21;

const table = sheet.tables.add("A8:M18", true, "GuildSalaryBdTable");
table.showFilterButton = true;
sheet.freezePanes.freezeRows(8);

const widths = [15, 15, 20, 15, 15, 10, 13, 14, 11, 16, 12, 12, 12];
for (let index = 0; index < widths.length; index += 1) {
  sheet.getRangeByIndexes(0, index, 18, 1).format.columnWidth = widths[index];
}

const inspected = await workbook.inspect({
  kind: "table",
  range: "\u516c\u4f1a\u85aa\u8d44BD!A1:M18",
  include: "values,formulas",
  tableMaxRows: 20,
  tableMaxCols: 13,
});
console.log(inspected.ndjson);

const formulaErrors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 50 },
  summary: "formula error scan",
});
console.log(formulaErrors.ndjson);

const preview = await workbook.render({
  sheetName: text.sheet,
  range: "A1:M18",
  scale: 1.5,
  format: "png",
});
await fs.writeFile(`${outputDir}/preview.png`, new Uint8Array(await preview.arrayBuffer()));

await fs.mkdir(outputDir, { recursive: true });
const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(outputPath);
console.log(outputPath);
