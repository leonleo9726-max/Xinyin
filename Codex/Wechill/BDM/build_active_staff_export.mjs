import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = "E:/Codex/Wechill/outputs/bdm_active_staff_20260724";
const outputPath = `${outputDir}/BDM_BD_Active_Staff_20260724.xlsx`;

const records = [
  [6, "8524370", "Lee", "BDM+BD", "\u8BD5\u7528", "86", "13710011054", null, "\u4E2D\u4E1C\u533A", "Lee", "BDM+BD", "\u5426", "\u672A\u9A8C\u8BC1", "\u5426", "\u6709", "\u6709", null, new Date("2026-08-01T20:59:59Z"), 9, 7, new Date("2026-06-03T02:58:06Z"), new Date("2026-07-07T10:27:27Z")],
  [8, "8561551", "eat", "BDM+BD", "\u8BD5\u7528", "86", "19521222229", null, "\u4E2D\u4E1C\u533A", "eat", "BD", "\u662F", "\u672A\u9A8C\u8BC1", "\u5426", "\u65E0", "\u65E0", 30, new Date("2026-08-01T20:59:59Z"), 1, 2, new Date("2026-06-04T06:30:52Z"), new Date("2026-06-10T08:16:56Z")],
  [25, "8577097", "kocekid", "BDM+BD", "\u8BD5\u7528", "86", "13342866059", null, "\u4E2D\u4E1C\u533A", "kocekid", "BDM+BD", "\u5426", "\u672A\u9A8C\u8BC1", "\u5426", "\u6709", "\u6709", null, new Date("2026-09-01T20:59:59Z"), 1, 2, new Date("2026-06-23T02:19:04Z"), new Date("2026-06-24T03:55:28Z")],
  [4, "3728", "Gonfe", "BDM+BD", "\u8F6C\u6B63", "86", "18825113723", null, "\u4E2D\u4E1C\u533A", "Gonfe", "BDM+BD", "\u5426", "\u672A\u9A8C\u8BC1", "\u5426", "\u6709", "\u6709", null, new Date("2026-08-01T20:59:59Z"), 6, 2, new Date("2026-05-28T04:14:52Z"), new Date("2026-06-10T08:16:54Z")],
  [19, "8590613", "leo", "BDM+BD", "\u8F6C\u6B63", "86", "13710011066", null, "\u82F1\u8BED\u533A", "leo", "BDM+BD", "\u5426", "\u672A\u9A8C\u8BC1", "\u5426", "\u6709", "\u6709", null, new Date("2026-08-01T20:59:59Z"), 9, 7, new Date("2026-06-08T02:11:26Z"), new Date("2026-07-01T00:00:00Z")],
  [27, "8562905", "\u9AD8", "BDM+BD", "\u8F6C\u6B63", null, null, "0139haris@gmail.com", "\u4E2D\u4E1C\u533A", "\u9AD8", "BD", "\u5426", "\u672A\u9A8C\u8BC1", "\u5426", "\u6709", "\u6709", null, null, 9, 2, new Date("2026-06-23T15:38:53Z"), new Date("2026-06-23T15:47:16Z")],
  [31, "8532766", "peterzhong", "BDM+BD", "\u8F6C\u6B63", "86", "17728140845", null, "\u82F1\u8BED\u533A", "peterzhong", "BDM+BD", "\u5426", "\u672A\u9A8C\u8BC1", "\u5426", "\u6709", "\u6709", null, null, 9, 2, new Date("2026-07-10T07:20:40Z"), new Date("2026-07-22T12:50:43Z")],
  [5, "8539901", "Ginxxer", "BD", "\u8BD5\u7528", "86", "18825113722", null, "\u82F1\u8BED\u533A", "Gonfe", "BDM", "\u5426", "\u672A\u9A8C\u8BC1", "\u5426", "\u65E0", "\u6709", null, new Date("2026-08-01T20:59:59Z"), 6, null, new Date("2026-06-01T02:58:17Z"), new Date("2026-06-25T03:13:39Z")],
  [7, "8565914", "uBD\u4E00\u53F7", "BD", "\u8BD5\u7528", "86", "13710011059", null, "\u4E2D\u4E1C\u533A", "wechill(\u5B98\u65B9bd bdm)", "BDM", "\u5426", "\u672A\u9A8C\u8BC1", "\u5426", "\u65E0", "\u65E0", null, new Date("2026-08-01T20:59:59Z"), 1, null, new Date("2026-06-04T02:53:08Z"), new Date("2026-06-24T10:19:07Z")],
  [11, "8583449", "gonXXiao", "BD", "\u8BD5\u7528", "86", "18825113721", null, "\u82F1\u8BED\u533A", "Gonfe", "BD", "\u5426", "\u672A\u9A8C\u8BC1", "\u5426", "\u6709", "\u6709", 34, new Date("2026-08-01T20:59:59Z"), 9, null, new Date("2026-06-04T10:39:11Z"), new Date("2026-06-10T08:16:59Z")],
  [20, "8549741", "uBD\u56DB\u53F7", "BD", "\u8BD5\u7528", "86", "13710011067", null, "\u4E2D\u4E1C\u533A", "leo", "BD", "\u5426", "\u672A\u9A8C\u8BC1", "\u5426", "\u65E0", "\u65E0", 1, new Date("2026-08-01T20:59:59Z"), 9, null, new Date("2026-06-09T06:24:44Z"), new Date("2026-06-10T08:17:02Z")],
  [22, "8585742", "\u72EC\u9493\u5BD2\u6C5F\u96EA", "BD", "\u8BD5\u7528", "86", "18825113720", null, "\u82F1\u8BED\u533A", "Gonfe", "BD", "\u5426", "\u672A\u9A8C\u8BC1", "\u5426", "\u6709", "\u6709", null, new Date("2026-08-01T20:59:59Z"), 1, null, new Date("2026-06-09T07:44:47Z"), new Date("2026-06-10T07:22:15Z")],
  [23, "8517682", "uBD\u516D\u53F7", "BD", "\u8BD5\u7528", "86", "13800138025", null, "\u82F1\u8BED\u533A", "leo", "BDM", "\u5426", "\u672A\u9A8C\u8BC1", "\u5426", "\u65E0", "\u65E0", null, new Date("2026-07-01T20:59:59Z"), 9, null, new Date("2026-06-16T09:35:14Z"), new Date("2026-06-24T11:35:04Z")],
  [24, "8558958", "BD\u4E09\u53F7", "BD", "\u8BD5\u7528", "86", "13800138016", null, "\u82F1\u8BED\u533A", "leo", "BD", "\u5426", "\u672A\u9A8C\u8BC1", "\u5426", "\u6709", "\u65E0", null, new Date("2026-07-01T20:59:59Z"), 9, null, new Date("2026-06-18T03:26:32Z"), new Date("2026-06-24T02:22:29Z")],
  [26, "8523263", "kocekid\u6210\u54581", "BD", "\u8BD5\u7528", "86", "13138077663", null, "\u4E2D\u4E1C\u533A", "kocekid", "BDM", "\u5426", "\u672A\u9A8C\u8BC1", "\u5426", "\u65E0", "\u65E0", null, new Date("2026-08-01T20:59:59Z"), 9, null, new Date("2026-06-23T12:22:06Z"), new Date("2026-07-06T06:46:50Z")],
  [28, "8554413", "123", "BD", "\u8BD5\u7528", "86", "13710011013", null, "\u4E2D\u4E1C\u533A", null, "BDM", "\u5426", "\u672A\u9A8C\u8BC1", "\u5426", "\u65E0", "\u65E0", null, new Date("2026-07-01T20:59:59Z"), 9, null, new Date("2026-06-30T08:45:50Z"), new Date("2026-06-30T08:45:50Z")],
  [29, "8546191", "oop", "BD", "\u8BD5\u7528", "86", "13800138073", null, "\u4E2D\u4E1C\u533A", null, "BDM", "\u5426", "\u672A\u9A8C\u8BC1", "\u5426", "\u65E0", "\u65E0", null, new Date("2026-08-01T20:59:59Z"), 9, null, new Date("2026-07-07T06:43:06Z"), new Date("2026-07-07T06:43:06Z")],
  [30, "8539215", "DZP2", "BD", "\u8BD5\u7528", "86", "13342866067", null, "\u4E2D\u4E1C\u533A", null, "BDM", "\u5426", "\u672A\u9A8C\u8BC1", "\u5426", "\u65E0", "\u65E0", null, new Date("2026-08-01T20:59:59Z"), 86, null, new Date("2026-07-10T02:56:10Z"), new Date("2026-07-10T02:56:10Z")],
  [10, "8594890", "bug\u6EE1\u5929\u98DE", "BD", "\u8F6C\u6B63", "86", "19520111111", null, "\u4E2D\u4E1C\u533A", "eat", "BDM", "\u662F", "\u672A\u9A8C\u8BC1", "\u5426", "\u65E0", "\u65E0", null, null, 1, null, new Date("2026-06-04T07:51:13Z"), new Date("2026-07-07T02:56:18Z")],
  [12, "8517614", "uBD\u4E09\u53F7", "BD", "\u8F6C\u6B63", "86", "13710011063", null, "\u4E2D\u4E1C\u533A", "Lee", "BDM", "\u5426", "\u672A\u9A8C\u8BC1", "\u5426", "\u65E0", "\u65E0", null, null, 9, null, new Date("2026-06-05T08:10:12Z"), new Date("2026-06-30T08:55:01Z")],
  [17, "8540258", "dzp", "BD", "\u8F6C\u6B63", "86", "13138077661", null, "\u4E2D\u4E1C\u533A", "kocekid", "BDM", "\u5426", "\u672A\u9A8C\u8BC1", "\u5426", "\u6709", "\u6709", null, null, 1, null, new Date("2026-06-05T08:37:18Z"), new Date("2026-06-24T09:10:51Z")],
];

const workbook = Workbook.create();
const roster = workbook.worksheets.add("\u5728\u804C\u6210\u5458");
const issues = workbook.worksheets.add("\u6570\u636E\u8D28\u91CF\u5F02\u5E38");

roster.showGridLines = false;
roster.mergeCells("A1:V1");
roster.getRange("A1").values = [["\u5728\u804C BDM \u4E0E BD \u6210\u5458\u6E05\u5355"]];
roster.getRange("A2:V2").merge();
roster.getRange("A2").values = [["\u6570\u636E\u6E90\uFF1Abd_staff\u3001app_user\u3001app_user_flag\uFF5C\u63D0\u53D6\u65E5\u671F\uFF1A2026-07-24\uFF5C\u5728\u804C\u53E3\u5F84\uFF1A\u6B63\u5E38\u4EBA\u4E8B\u8BB0\u5F55\u4E14\u72B6\u6001\u4E3A\u8BD5\u7528\u6216\u8F6C\u6B63"]];
roster.getRange("A1:V1").format = { fill: "#17365D", font: { bold: true, color: "#FFFFFF", size: 16 }, horizontalAlignment: "center", verticalAlignment: "center" };
roster.getRange("A2:V2").format = { fill: "#D9EAF7", font: { color: "#1F2937", italic: true }, horizontalAlignment: "left" };
roster.getRange("A1:V1").format.rowHeight = 28;
roster.getRange("A2:V2").format.rowHeight = 20;

roster.getRange("A4:J4").values = [["\u5728\u804C\u603B\u4EBA\u6570", null, "BDM+BD", null, "BD", null, "\u8BD5\u7528", null, "\u8F6C\u6B63", null]];
roster.getRange("B4").formulas = [["=COUNTA(A8:A28)"]];
roster.getRange("D4").formulas = [["=COUNTIF(D8:D28,\"BDM+BD\")"]];
roster.getRange("F4").formulas = [["=COUNTIF(D8:D28,\"BD\")"]];
roster.getRange("H4").formulas = [["=COUNTIF(E8:E28,\"\u8BD5\u7528\")"]];
roster.getRange("J4").formulas = [["=COUNTIF(E8:E28,\"\u8F6C\u6B63\")"]];
roster.getRange("A4:J4").format = { fill: "#EAF2F8", font: { bold: true, color: "#17365D" }, horizontalAlignment: "center", borders: { preset: "outside", style: "thin", color: "#9EB6CE" } };
roster.getRange("B4,D4,F4,H4,J4").format = { fill: "#FFFFFF", font: { bold: true, color: "#17365D", size: 13 }, horizontalAlignment: "center", borders: { preset: "outside", style: "thin", color: "#9EB6CE" } };

const headers = [["\u5458\u5DE5 ID", "\u7528\u6237\u7F16\u53F7", "\u59D3\u540D", "\u8EAB\u4EFD\uFF08\u6743\u5A01\uFF09", "\u5728\u804C\u72B6\u6001", "\u533A\u53F7", "\u624B\u673A\u53F7", "\u90AE\u7BB1", "\u5730\u533A", "\u76F4\u5C5E BDM", "\u5C97\u4F4D\u5C55\u793A", "\u5BA1\u6838\u6807\u8BB0", "\u5BA1\u6838\u9A8C\u8BC1", "\u5B98\u65B9\u6807\u8BB0", "\u516C\u4F1A\u5BA1\u6838\u6743\u9650", "\u91D1\u5E01\u63D0\u73B0\u6743\u9650", "\u8BD5\u7528\u5929\u6570", "\u9884\u8BA1\u8F6C\u6B63\u65F6\u95F4", "BD \u653F\u7B56 ID", "BDM \u653F\u7B56 ID", "\u521B\u5EFA\u65F6\u95F4", "\u66F4\u65B0\u65F6\u95F4"]];
roster.getRange("A7:V7").values = headers;
roster.getRange("A8:V28").values = records;
const table = roster.tables.add("A7:V28", true, "ActiveStaffTable");
table.style = "TableStyleMedium2";
table.showFilterButton = true;

roster.getRange("A7:V28").format.wrapText = true;
roster.getRange("A7:V7").format = { fill: "#1F4E78", font: { bold: true, color: "#FFFFFF" }, horizontalAlignment: "center", verticalAlignment: "center", wrapText: true };
roster.getRange("A8:V28").format = { verticalAlignment: "center", borders: { preset: "insideHorizontal", style: "thin", color: "#D9E2F3" } };
roster.getRange("A8:A28").format.horizontalAlignment = "right";
roster.getRange("B8:B28").format = { numberFormat: "@", horizontalAlignment: "left" };
roster.getRange("G8:G28").format = { numberFormat: "@", horizontalAlignment: "left" };
roster.getRange("Q8:Q28").format.numberFormat = "#,##0";
roster.getRange("R8:R28").format.numberFormat = "yyyy-mm-dd hh:mm";
roster.getRange("U8:V28").format.numberFormat = "yyyy-mm-dd hh:mm";
roster.getRange("E8:E28").conditionalFormats.add("containsText", { text: "\u8BD5\u7528", format: { fill: "#FFF2CC", font: { color: "#7F6000" } } });
roster.getRange("J8:J28").conditionalFormats.add("containsBlanks", { format: { fill: "#FCE4D6", font: { color: "#C00000" } } });

const widths = [10, 13, 20, 19, 12, 10, 15, 27, 14, 25, 17, 11, 15, 10, 21, 25, 14, 21, 13, 14, 19, 19];
for (let index = 0; index < widths.length; index += 1) {
  roster.getRangeByIndexes(0, index, 28, 1).format.columnWidth = widths[index];
}
roster.getRange("A7:V7").format.rowHeight = 30;
roster.getRange("A8:V28").format.rowHeight = 22;
roster.freezePanes.freezeRows(7);
roster.freezePanes.freezeColumns(3);

issues.showGridLines = false;
issues.mergeCells("A1:F1");
issues.getRange("A1").values = [["\u6570\u636E\u8D28\u91CF\u5F02\u5E38 - \u5728\u804C\u6210\u5458\u5BFC\u51FA"]];
issues.getRange("A1:F1").format = { fill: "#9E480E", font: { bold: true, color: "#FFFFFF", size: 14 }, horizontalAlignment: "center" };
issues.getRange("A3:F3").values = [["\u7EA7\u522B", "\u5F02\u5E38\u9879", "\u5F71\u54CD\u6210\u5458", "\u6765\u6E90\u5B57\u6BB5", "\u89E6\u53D1\u6761\u4EF6", "\u5904\u7406\u5EFA\u8BAE"]];
issues.getRange("A4:F7").values = [
  ["\u9AD8", "\u8EAB\u4EFD\u4E0E\u5C97\u4F4D\u5C55\u793A\u4E0D\u4E00\u81F4", "12 \u4EBA\uFF1Aeat\u3001\u9AD8\u3001Ginxxer\u3001uBD\u4E00\u53F7\u3001uBD\u516D\u53F7\u3001kocekid\u6210\u54581\u3001123\u3001oop\u3001DZP2\u3001bug\u6EE1\u5929\u98DE\u3001uBD\u4E09\u53F7\u3001dzp", "bd_staff.job_title_type \u4E0E role_bd/role_bdm", "\u5C97\u4F4D\u5C55\u793A\u4E0E\u6743\u5A01\u8EAB\u4EFD\u5B57\u6BB5\u51B2\u7A81", "\u6743\u9650\u548C\u8EAB\u4EFD\u5224\u65AD\u5FC5\u987B\u4EE5 role_bd\u3001role_bdm \u4E3A\u51C6\u3002"],
  ["\u9AD8", "\u9884\u8BA1\u8F6C\u6B63\u65F6\u95F4\u5DF2\u8FC7\u4F46\u4ECD\u4E3A\u8BD5\u7528", "3 \u4EBA\uFF1AuBD\u516D\u53F7\u3001BD\u4E09\u53F7\u3001123", "bd_staff.probation_regular_time\u3001employment_status", "\u9884\u8BA1\u8F6C\u6B63\u65F6\u95F4\u65E9\u4E8E 2026-07-24\uFF0C\u5F53\u524D\u72B6\u6001\u4ECD\u4E3A\u8BD5\u7528", "\u6838\u5B9E\u4EBA\u4E8B\u6D41\u7A0B\u6216\u5B9A\u65F6\u72B6\u6001\u8F6C\u6362\u4EFB\u52A1\u3002"],
  ["\u4E2D", "\u672A\u5206\u914D\u76F4\u5C5E BDM", "3 \u4EBA\uFF1A123\u3001oop\u3001DZP2", "bd_staff.supervisor_staff_id", "\u76F4\u5C5E\u4E0A\u7EA7\u4E3A NULL", "\u56E2\u961F\u85AA\u8D44\u8BA1\u7B97\u524D\u5E94\u5206\u914D\u6709\u6548\u5728\u804C BDM\u3002"],
  ["\u4E2D", "\u5BA1\u6838\u9A8C\u8BC1\u7F3A\u5931", "\u5168\u90E8 21 \u540D\u5728\u804C\u6210\u5458", "app_user_flag.verified_audit", "\u5B57\u6BB5\u503C\u4E3A NULL", "\u5B8C\u6210\u5BA1\u6838\u9A8C\u8BC1\u6216\u660E\u786E\u7CFB\u7EDF\u9ED8\u8BA4\u503C\u3002"],
];
issues.getRange("A3:F3").format = { fill: "#C65911", font: { bold: true, color: "#FFFFFF" }, horizontalAlignment: "center", wrapText: true };
issues.getRange("A4:F7").format = { verticalAlignment: "top", wrapText: true, borders: { preset: "all", style: "thin", color: "#E6B8AF" } };
issues.getRange("A4:A7").conditionalFormats.add("containsText", { text: "\u9AD8", format: { fill: "#F4CCCC", font: { bold: true, color: "#990000" } } });
issues.getRange("A4:A7").conditionalFormats.add("containsText", { text: "\u4E2D", format: { fill: "#FCE5CD", font: { bold: true, color: "#B45F06" } } });
const issueWidths = [12, 34, 64, 38, 52, 58];
for (let index = 0; index < issueWidths.length; index += 1) {
  issues.getRangeByIndexes(0, index, 7, 1).format.columnWidth = issueWidths[index];
}
issues.getRange("A3:F3").format.rowHeight = 28;
issues.getRange("A4:F7").format.rowHeight = 54;
issues.freezePanes.freezeRows(3);

await fs.mkdir(outputDir, { recursive: true });
const exported = await SpreadsheetFile.exportXlsx(workbook);
await exported.save(outputPath);

const rosterCheck = await workbook.inspect({ kind: "table", range: "\u5728\u804C\u6210\u5458!A4:V12", include: "values,formulas", tableMaxRows: 12, tableMaxCols: 22 });
const formulaErrors = await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 100 }, summary: "formula errors" });
console.log(rosterCheck.ndjson);
console.log(formulaErrors.ndjson);

const rosterPreview = await workbook.render({ sheetName: "\u5728\u804C\u6210\u5458", range: "A1:V15", scale: 1, format: "png" });
const issuesPreview = await workbook.render({ sheetName: "\u6570\u636E\u8D28\u91CF\u5F02\u5E38", range: "A1:F7", scale: 1, format: "png" });
await fs.writeFile(`${outputDir}/active_staff_preview.png`, new Uint8Array(await rosterPreview.arrayBuffer()));
await fs.writeFile(`${outputDir}/data_quality_preview.png`, new Uint8Array(await issuesPreview.arrayBuffer()));
console.log(outputPath);
