import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = "E:/Codex/Wechill/outputs/bdm_salary_20260724";
const outputPath = `${outputDir}/BDM_BD_Test_Salary_20260724.xlsx`;

const staffRows = [
  [9, "8517682", "uBD\u516D\u53F7", "BD", "\u8BD5\u7528", "BD\u4E2A\u4EBA\u85AA\u8D44", 5, 4197.44, 500, 4197.44, 1259.23, 1, 879.61, 1759.23, 879.62, 4197.44, 8394.88, 2, new Date("2026-07-24T06:35:00.758Z")],
  [18, "8524370", "Lee", "BDM+BD", "\u8BD5\u7528", "BD\u4E2A\u4EBA\u85AA\u8D44", 5, 2905, 500, 2905, 871.5, 0, 685.75, 1371.5, 685.75, 2905, 5810, 1, new Date("2026-07-24T06:35:00.758Z")],
  [8, "8558958", "BD\u4E09\u53F7", "BD", "\u8BD5\u7528", "BD\u4E2A\u4EBA\u85AA\u8D44", 4, 312.55, 200, 312.55, 62.51, 0, 131.25, 262.51, 131.26, 2538.75, 625.1, 1, new Date("2026-07-24T06:35:00.758Z")],
  [12, "8590613", "leo", "BDM+BD", "\u8F6C\u6B63", "BD\u4E2A\u4EBA\u85AA\u8D44", 2, 312.55, 200, 312.55, 62.51, 1, 131.25, 262.51, 131.26, 312.55, 625.1, 1, new Date("2026-07-24T06:35:00.758Z")],
  [25, "8590613", "leo", "BDM+BD", "\u8F6C\u6B63", "BDM\u56E2\u961F\u7BA1\u7406\u85AA\u8D44", 5, 4822.54, 500, 4822.54, 964.5, 2, 0, 1464.5, 1464.5, 7048.74, 4822.54, 4, new Date("2026-07-24T06:35:00.758Z")],
  [27, "8524370", "Lee", "BDM+BD", "\u8BD5\u7528", "BDM\u56E2\u961F\u7BA1\u7406\u85AA\u8D44", 5, 2905, 500, 2905, 581, 0, 0, 1081, 1081, 2905, 2905, 1, new Date("2026-07-24T06:35:00.758Z")],
];

const guildRows = [
  [8, "8558958", "BD\u4E09\u53F7", "BD\u4E2A\u4EBA\u85AA\u8D44", 3541, "\u82F1\u8BED\u533A\u81EA\u7531\u653F\u7B56", 272, new Date("2026-06-24T11:46:28Z"), new Date("2026-07-15T20:59:59Z"), new Date("2026-07-15T20:59:59Z"), 0, 0, 1357.1, 0, 0, 0, "\u662F", "\u662F", "\u5426", "\u5426", new Date("2026-07-24T06:35:00.758Z")],
  [8, "8558958", "BD\u4E09\u53F7", "BD\u4E2A\u4EBA\u85AA\u8D44", 3552, "\u82F1\u8BED\u533A\u81EA\u7531\u7ED3\u7B97", 274, new Date("2026-06-30T08:52:55Z"), new Date("2026-07-15T20:59:59Z"), new Date("2026-07-15T20:59:59Z"), 0, 0, 556.55, 0, 0, 0, "\u662F", "\u662F", "\u5426", "\u5426", new Date("2026-07-24T06:35:00.758Z")],
  [8, "8558958", "BD\u4E09\u53F7", "BD\u4E2A\u4EBA\u85AA\u8D44", 3575, "Yomwe", 267, new Date("2026-06-24T02:39:09Z"), new Date("2026-09-15T20:59:59Z"), new Date("2026-09-15T20:59:59Z"), 312.55, 312.55, 312.55, 625.1, 312.55, 312.55, "\u662F", "\u662F", "\u662F", "\u5426", new Date("2026-07-24T06:35:00.758Z")],
  [8, "8558958", "BD\u4E09\u53F7", "BD\u4E2A\u4EBA\u85AA\u8D44", 3584, "Lastly", 273, new Date("2026-06-24T12:00:42Z"), new Date("2026-07-15T20:59:59Z"), new Date("2026-07-15T20:59:59Z"), 0, 0, 312.55, 0, 0, 0, "\u662F", "\u662F", "\u5426", "\u5426", new Date("2026-07-24T06:35:00.758Z")],
  [9, "8517682", "uBD\u516D\u53F7", "BD\u4E2A\u4EBA\u85AA\u8D44", 3529, "leon guild", 278, new Date("2026-07-06T21:00:00Z"), new Date("2026-07-31T20:59:59Z"), new Date("2026-07-31T20:59:59Z"), 3884.89, 3884.89, 3884.89, 7769.78, 3884.89, 3884.89, "\u662F", "\u662F", "\u662F", "\u662F", new Date("2026-07-24T06:35:00.758Z")],
  [9, "8517682", "uBD\u516D\u53F7", "BD\u4E2A\u4EBA\u85AA\u8D44", 3581, "1155555555", 264, new Date("2026-06-23T12:08:29Z"), new Date("2026-09-15T20:59:59Z"), new Date("2026-09-15T20:59:59Z"), 312.55, 312.55, 312.55, 625.1, 312.55, 312.55, "\u662F", "\u662F", "\u662F", "\u5426", new Date("2026-07-24T06:35:00.758Z")],
  [9, "8517682", "uBD\u516D\u53F7", "BD\u4E2A\u4EBA\u85AA\u8D44", 3572, "\u0647\u062B\u0647\u064A\u062A\u0628\u062A\u0628\u0647 \u0628\u0647\u0628\u0646", 256, new Date("2026-06-18T03:11:24Z"), new Date("2026-09-15T20:59:59Z"), new Date("2026-09-15T20:59:59Z"), 0, 0, 0, 0, 0, 0, "\u662F", "\u662F", "\u5426", "\u5426", new Date("2026-07-24T06:35:00.758Z")],
  [12, "8590613", "leo", "BD\u4E2A\u4EBA\u85AA\u8D44", 3587, "Thgfgfg", 279, new Date("2026-07-08T02:55:44Z"), new Date("2026-07-31T20:59:59Z"), new Date("2026-07-31T20:59:59Z"), 312.55, 312.55, 312.55, 625.1, 312.55, 312.55, "\u662F", "\u662F", "\u662F", "\u662F", new Date("2026-07-24T06:35:00.758Z")],
  [12, "8590613", "leo", "BD\u4E2A\u4EBA\u85AA\u8D44", 3544, "\u82F1\u8BED\u533A\u516C\u4F1A\u957F\u81EA\u7531\u653F\u7B56", 251, new Date("2026-06-09T04:27:11Z"), new Date("2026-08-31T20:59:59Z"), new Date("2026-08-31T20:59:59Z"), 0, 0, 0, 0, 0, 0, "\u662F", "\u662F", "\u5426", "\u5426", new Date("2026-07-24T06:35:00.758Z")],
  [18, "8524370", "Lee", "BD\u4E2A\u4EBA\u85AA\u8D44", 3558, "Yoww", 233, new Date("2026-06-04T11:18:23Z"), new Date("2026-08-31T20:59:59Z"), new Date("2026-08-31T20:59:59Z"), 2905, 2905, 2905, 5810, 2905, 2905, "\u662F", "\u662F", "\u662F", "\u5426", new Date("2026-07-24T06:35:00.758Z")],
];

const anomalyRows = [
  [25, "8590613", "leo", "BDM\u56E2\u961F\u7BA1\u7406\u85AA\u8D44", 1464.5, 7048.74, 0, 7048.74, "\u5F85\u6838\u5BF9", "\u4EBA\u5458\u85AA\u8D44\u6C47\u603B\u5B58\u5728\u516C\u4F1A\u85AA\u8D44\u603B\u548C\uFF0C\u4F46\u672A\u627E\u5230\u5173\u8054 bd_realtime_guild_salary \u660E\u7EC6"],
  [27, "8524370", "Lee", "BDM\u56E2\u961F\u7BA1\u7406\u85AA\u8D44", 1081, 2905, 0, 2905, "\u5F85\u6838\u5BF9", "\u4EBA\u5458\u85AA\u8D44\u6C47\u603B\u5B58\u5728\u516C\u4F1A\u85AA\u8D44\u603B\u548C\uFF0C\u4F46\u672A\u627E\u5230\u5173\u8054 bd_realtime_guild_salary \u660E\u7EC6"],
];

const workbook = Workbook.create();
const staffSheet = workbook.worksheets.add("\u85AA\u8D44\u4EBA\u5458\u6C47\u603B");
const guildSheet = workbook.worksheets.add("\u7ED1\u5B9A\u516C\u4F1A\u85AA\u8D44\u660E\u7EC6");
const qualitySheet = workbook.worksheets.add("\u6570\u636E\u8D28\u91CF\u5F02\u5E38");

staffSheet.showGridLines = false;
staffSheet.mergeCells("A1:S1");
staffSheet.getRange("A1").values = [["\u6D4B\u8BD5\u73AF\u5883 BD / BDM \u5B9E\u65F6\u85AA\u8D44\u5BFC\u51FA"]];
staffSheet.mergeCells("A2:S2");
staffSheet.getRange("A2").values = [["\u6570\u636E\u6E90\uFF1A\u6D4B\u8BD5\u73AF\u5883 mysql\uFF5C\u7ED3\u7B97\u6708\uFF1A202607\uFF5C\u53E3\u5F84\uFF1Abd_realtime_staff_salary.total_salary \u975E\u96F6\uFF5C\u5FEB\u7167\u65F6\u95F4\uFF1A2026-07-24 06:35"]];
staffSheet.getRange("A1:S1").format = { fill: "#17365D", font: { bold: true, color: "#FFFFFF", size: 16 }, horizontalAlignment: "center" };
staffSheet.getRange("A2:S2").format = { fill: "#D9EAF7", font: { italic: true, color: "#1F2937" } };
staffSheet.getRange("A1:S1").format.rowHeight = 28;
staffSheet.getRange("A2:S2").format.rowHeight = 20;
staffSheet.getRange("A4:H4").values = [["\u85AA\u8D44\u8BB0\u5F55\u6570", null, "BD\u4E2A\u4EBA\u85AA\u8D44", null, "BDM\u56E2\u961F\u85AA\u8D44", null, "\u5173\u8054\u516C\u4F1A\u660E\u7EC6", null]];
staffSheet.getRange("B4").formulas = [["=COUNTA(A8:A13)"]];
staffSheet.getRange("D4").formulas = [["=SUMIF(F8:F13,\"BD\u4E2A\u4EBA\u85AA\u8D44\",N8:N13)"]];
staffSheet.getRange("F4").formulas = [["=SUMIF(F8:F13,\"BDM\u56E2\u961F\u7BA1\u7406\u85AA\u8D44\",N8:N13)"]];
staffSheet.getRange("H4").formulas = [["=COUNTA('\u7ED1\u5B9A\u516C\u4F1A\u85AA\u8D44\u660E\u7EC6'!A5:A14)"]];
staffSheet.getRange("A4:H4").format = { fill: "#EAF2F8", font: { bold: true, color: "#17365D" }, horizontalAlignment: "center", borders: { preset: "outside", style: "thin", color: "#9EB6CE" } };
staffSheet.getRange("B4,D4,F4,H4").format = { fill: "#FFFFFF", font: { bold: true, color: "#17365D", size: 12 }, horizontalAlignment: "center", borders: { preset: "outside", style: "thin", color: "#9EB6CE" } };
staffSheet.getRange("D4,F4").format.numberFormat = "#,##0.00";

const staffHeaders = [["\u5B9E\u65F6\u85AA\u8D44 ID", "\u7528\u6237\u7F16\u53F7", "\u59D3\u540D", "\u8EAB\u4EFD", "\u5728\u804C\u72B6\u6001", "\u85AA\u8D44\u7C7B\u578B", "\u7B49\u7EA7", "\u5E95\u85AA\u6709\u6548\u6D41\u6C34", "\u5E95\u85AA", "Bonus \u6709\u6548\u6D41\u6C34", "\u516C\u4F1A\u63D0\u6210", "\u65B0\u589E\u516C\u4F1A\u6570", "\u65B0\u516C\u4F1A\u6263\u6B3E", "\u603B\u85AA\u8D44", "\u85AA\u8D44\u4F59\u989D", "\u516C\u4F1A\u85AA\u8D44\u603B\u548C", "\u6709\u6548\u516C\u4F1A\u85AA\u8D44\u603B\u548C", "\u6709\u6548\u516C\u4F1A\u6570", "\u5FEB\u7167\u65F6\u95F4"]];
staffSheet.getRange("A7:S7").values = staffHeaders;
staffSheet.getRange("A8:S13").values = staffRows;
const staffTable = staffSheet.tables.add("A7:S13", true, "TestSalaryStaffTable");
staffTable.style = "TableStyleMedium2";
staffTable.showFilterButton = true;
staffSheet.getRange("B8:B13").format.numberFormat = "@";
staffSheet.getRange("H8:Q13").format.numberFormat = "#,##0.00";
staffSheet.getRange("S8:S13").format.numberFormat = "yyyy-mm-dd hh:mm";
staffSheet.getRange("A7:S13").format.wrapText = true;
staffSheet.getRange("A7:S7").format.rowHeight = 30;
staffSheet.getRange("A8:S13").format.rowHeight = 22;
staffSheet.getRange("F8:F13").conditionalFormats.add("containsText", { text: "BDM\u56E2\u961F\u7BA1\u7406\u85AA\u8D44", format: { fill: "#E4DFEC", font: { color: "#60497A" } } });
const staffWidths = [13, 13, 16, 12, 12, 18, 8, 16, 12, 16, 13, 13, 14, 12, 12, 16, 20, 13, 20];
for (let index = 0; index < staffWidths.length; index += 1) staffSheet.getRangeByIndexes(0, index, 13, 1).format.columnWidth = staffWidths[index];
staffSheet.freezePanes.freezeRows(7);
staffSheet.freezePanes.freezeColumns(3);

guildSheet.showGridLines = false;
guildSheet.mergeCells("A1:U1");
guildSheet.getRange("A1").values = [["\u6D4B\u8BD5\u73AF\u5883\u7ED1\u5B9A\u516C\u4F1A\u85AA\u8D44\u660E\u7EC6"]];
guildSheet.mergeCells("A2:U2");
guildSheet.getRange("A2").values = [["\u4EC5\u5305\u542B\u603B\u85AA\u8D44\u975E\u96F6\u7684\u5B9E\u65F6\u4EBA\u5458\u85AA\u8D44\u6240\u5173\u8054\u7684 bd_realtime_guild_salary \u8BB0\u5F55\uFF5C\u7ED3\u7B97\u6708\uFF1A202607"]];
guildSheet.getRange("A1:U1").format = { fill: "#17365D", font: { bold: true, color: "#FFFFFF", size: 16 }, horizontalAlignment: "center" };
guildSheet.getRange("A2:U2").format = { fill: "#D9EAF7", font: { italic: true, color: "#1F2937" } };
guildSheet.getRange("A1:U1").format.rowHeight = 28;
guildSheet.getRange("A2:U2").format.rowHeight = 20;
const guildHeaders = [["\u5B9E\u65F6\u85AA\u8D44 ID", "\u7528\u6237\u7F16\u53F7", "\u59D3\u540D", "\u85AA\u8D44\u7C7B\u578B", "\u516C\u4F1A ID", "\u516C\u4F1A\u540D\u79F0", "\u7ED1\u5B9A ID", "\u7ED1\u5B9A\u65F6\u95F4", "\u5E95\u85AA\u622A\u6B62", "Bonus \u622A\u6B62", "\u5E95\u85AA\u7C7B\u6D41\u6C34", "Bonus \u7C7B\u6D41\u6C34", "\u516C\u4F1A\u85AA\u8D44\u603B\u989D", "\u6709\u6548\u516C\u4F1A\u85AA\u8D44", "\u5E95\u85AA\u6709\u6548\u6D41\u6C34", "Bonus \u6709\u6548\u6D41\u6C34", "\u672C\u6708\u8BA1\u5E95\u85AA", "\u672C\u6708\u8BA1 Bonus", "Bonus \u8FBE\u6807", "\u672C\u6708\u65B0\u589E", "\u5FEB\u7167\u65F6\u95F4"]];
guildSheet.getRange("A4:U4").values = guildHeaders;
guildSheet.getRange("A5:U14").values = guildRows;
const guildTable = guildSheet.tables.add("A4:U14", true, "TestSalaryGuildTable");
guildTable.style = "TableStyleMedium2";
guildTable.showFilterButton = true;
guildSheet.getRange("B5:B14").format.numberFormat = "@";
guildSheet.getRange("H5:J14").format.numberFormat = "yyyy-mm-dd hh:mm";
guildSheet.getRange("K5:P14").format.numberFormat = "#,##0.00";
guildSheet.getRange("U5:U14").format.numberFormat = "yyyy-mm-dd hh:mm";
guildSheet.getRange("A4:U14").format.wrapText = true;
guildSheet.getRange("A4:U4").format.rowHeight = 30;
guildSheet.getRange("A5:U14").format.rowHeight = 22;
const guildWidths = [13, 13, 16, 16, 11, 28, 11, 20, 20, 20, 13, 13, 15, 15, 15, 15, 12, 13, 12, 12, 20];
for (let index = 0; index < guildWidths.length; index += 1) guildSheet.getRangeByIndexes(0, index, 14, 1).format.columnWidth = guildWidths[index];
guildSheet.freezePanes.freezeRows(4);
guildSheet.freezePanes.freezeColumns(4);

qualitySheet.showGridLines = false;
qualitySheet.mergeCells("A1:J1");
qualitySheet.getRange("A1").values = [["\u6570\u636E\u8D28\u91CF\u5F02\u5E38\u4E0E\u5F85\u6838\u5BF9\u9879"]];
qualitySheet.mergeCells("A2:J2");
qualitySheet.getRange("A2").values = [["\u5F53\u524D\u7ED3\u7B97\u6708\u672A\u89E3\u51B3\u85AA\u8D44\u5F02\u5E38\u8BB0\u5F55\uFF1A0 \u6761\uFF5C\u4EE5\u4E0B\u4E3A\u5B9E\u65F6\u4EBA\u5458\u85AA\u8D44\u4E0E\u516C\u4F1A\u85AA\u8D44\u660E\u7EC6\u7684\u5173\u8054\u5DEE\u5F02"]];
qualitySheet.getRange("A1:J1").format = { fill: "#9E480E", font: { bold: true, color: "#FFFFFF", size: 15 }, horizontalAlignment: "center" };
qualitySheet.getRange("A2:J2").format = { fill: "#FCE4D6", font: { italic: true, color: "#7F6000" } };
qualitySheet.getRange("A1:J1").format.rowHeight = 26;
qualitySheet.getRange("A2:J2").format.rowHeight = 20;
const anomalyHeaders = [["\u5B9E\u65F6\u85AA\u8D44 ID", "\u7528\u6237\u7F16\u53F7", "\u59D3\u540D", "\u85AA\u8D44\u7C7B\u578B", "\u603B\u85AA\u8D44", "\u4EBA\u5458\u8868\u516C\u4F1A\u85AA\u8D44\u603B\u548C", "\u516C\u4F1A\u660E\u7EC6\u6570", "\u5DEE\u5F02", "\u72B6\u6001", "\u8BF4\u660E"]];
qualitySheet.getRange("A4:J4").values = anomalyHeaders;
qualitySheet.getRange("A5:J6").values = anomalyRows;
const anomalyTable = qualitySheet.tables.add("A4:J6", true, "TestSalaryQualityTable");
anomalyTable.style = "TableStyleMedium3";
anomalyTable.showFilterButton = true;
qualitySheet.getRange("B5:B6").format.numberFormat = "@";
qualitySheet.getRange("E5:H6").format.numberFormat = "#,##0.00";
qualitySheet.getRange("A4:J6").format.wrapText = true;
qualitySheet.getRange("A4:J4").format.rowHeight = 28;
qualitySheet.getRange("A5:J6").format.rowHeight = 40;
qualitySheet.getRange("I5:I6").conditionalFormats.add("containsText", { text: "\u5F85\u6838\u5BF9", format: { fill: "#F4CCCC", font: { bold: true, color: "#990000" } } });
const anomalyWidths = [14, 13, 16, 18, 12, 22, 13, 14, 12, 55];
for (let index = 0; index < anomalyWidths.length; index += 1) qualitySheet.getRangeByIndexes(0, index, 6, 1).format.columnWidth = anomalyWidths[index];
qualitySheet.freezePanes.freezeRows(4);

await fs.mkdir(outputDir, { recursive: true });
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);

const staffCheck = await workbook.inspect({ kind: "table", range: "\u85AA\u8D44\u4EBA\u5458\u6C47\u603B!A4:S13", include: "values,formulas", tableMaxRows: 15, tableMaxCols: 19 });
const guildCheck = await workbook.inspect({ kind: "table", range: "\u7ED1\u5B9A\u516C\u4F1A\u85AA\u8D44\u660E\u7EC6!A1:U14", include: "values,formulas", tableMaxRows: 15, tableMaxCols: 21 });
const qualityCheck = await workbook.inspect({ kind: "table", range: "\u6570\u636E\u8D28\u91CF\u5F02\u5E38!A1:J6", include: "values,formulas", tableMaxRows: 8, tableMaxCols: 10 });
const formulaErrors = await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 100 }, summary: "formula errors" });
console.log(staffCheck.ndjson);
console.log(guildCheck.ndjson);
console.log(qualityCheck.ndjson);
console.log(formulaErrors.ndjson);

const staffPreview = await workbook.render({ sheetName: "\u85AA\u8D44\u4EBA\u5458\u6C47\u603B", range: "A1:S13", scale: 1, format: "png" });
const guildPreview = await workbook.render({ sheetName: "\u7ED1\u5B9A\u516C\u4F1A\u85AA\u8D44\u660E\u7EC6", range: "A1:U14", scale: 1, format: "png" });
const qualityPreview = await workbook.render({ sheetName: "\u6570\u636E\u8D28\u91CF\u5F02\u5E38", range: "A1:J6", scale: 1, format: "png" });
await fs.writeFile(`${outputDir}/staff_salary_preview.png`, new Uint8Array(await staffPreview.arrayBuffer()));
await fs.writeFile(`${outputDir}/guild_salary_preview.png`, new Uint8Array(await guildPreview.arrayBuffer()));
await fs.writeFile(`${outputDir}/salary_quality_preview.png`, new Uint8Array(await qualityPreview.arrayBuffer()));
console.log(outputPath);
