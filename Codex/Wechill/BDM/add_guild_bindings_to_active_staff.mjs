import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = "E:/Codex/Wechill/outputs/bdm_active_staff_20260724/BDM_BD_Active_Staff_20260724.xlsx";
const outputDir = "E:/Codex/Wechill/outputs/bdm_active_staff_20260724";
const outputPath = `${outputDir}/BDM_BD_Active_Staff_20260724_with_guild_bindings.xlsx`;
const input = await FileBlob.load(inputPath);
const workbook = await SpreadsheetFile.importXlsx(input);
const roster = workbook.worksheets.getItem("\u5728\u804c\u6210\u5458");

const bindingRows = [
  ["8517682", "uBD\u516d\u53f7", 256, 3572, "\u0647\u062b\u0647\u064a\u062a\u0628\u062a\u0628\u0647 \u0628\u0647\u0628\u0646", null, "\u82f1\u8bed\u533a", "\u81ea\u7531", "\u6b63\u5e38", new Date("2026-06-18T03:11:24Z"), new Date("2026-09-15T20:59:59Z"), new Date("2026-09-15T20:59:59Z")],
  ["8517682", "uBD\u516d\u53f7", 264, 3581, "1155555555", null, "\u82f1\u8bed\u533a", "\u53cc\u5468", "\u6b63\u5e38", new Date("2026-06-23T12:08:29Z"), new Date("2026-09-15T20:59:59Z"), new Date("2026-09-15T20:59:59Z")],
  ["8517682", "uBD\u516d\u53f7", 278, 3529, "leon guild", null, "\u82f1\u8bed\u533a", "\u81ea\u7531", "\u6b63\u5e38", new Date("2026-07-06T21:00:00Z"), new Date("2026-07-31T20:59:59Z"), new Date("2026-07-31T20:59:59Z")],
  ["8524370", "Lee", 233, 3558, "Yoww", null, "\u4e2d\u4e1c\u533a", "\u53cc\u5468", "\u6b63\u5e38", new Date("2026-06-04T11:18:23Z"), new Date("2026-08-31T20:59:59Z"), new Date("2026-08-31T20:59:59Z")],
  ["8558958", "BD\u4e09\u53f7", 267, 3575, "Yomwe", null, "\u82f1\u8bed\u533a", "\u53cc\u5468", "\u6b63\u5e38", new Date("2026-06-24T02:39:09Z"), new Date("2026-09-15T20:59:59Z"), new Date("2026-09-15T20:59:59Z")],
  ["8558958", "BD\u4e09\u53f7", 272, 3541, "\u82f1\u8bed\u533a\u81ea\u7531\u653f\u7b56", null, "\u82f1\u8bed\u533a", "\u53cc\u5468", "\u6b63\u5e38", new Date("2026-06-24T11:46:28Z"), new Date("2026-07-15T20:59:59Z"), new Date("2026-07-15T20:59:59Z")],
  ["8558958", "BD\u4e09\u53f7", 273, 3584, "Lastly", null, "\u82f1\u8bed\u533a", "\u53cc\u5468", "\u6b63\u5e38", new Date("2026-06-24T12:00:42Z"), new Date("2026-07-15T20:59:59Z"), new Date("2026-07-15T20:59:59Z")],
  ["8558958", "BD\u4e09\u53f7", 274, 3552, "\u82f1\u8bed\u533a\u81ea\u7531\u7ed3\u7b97", null, "\u82f1\u8bed\u533a", "\u81ea\u7531", "\u6b63\u5e38", new Date("2026-06-30T08:52:55Z"), new Date("2026-07-15T20:59:59Z"), new Date("2026-07-15T20:59:59Z")],
  ["8565914", "uBD\u4e00\u53f7", 231, 3540, "\u4e2d\u4e1c\u516c\u4f1a\u957f\u53cc\u5468\u653f\u7b56", null, "\u4e2d\u4e1c\u533a", "\u53cc\u5468", "\u5df2\u89e3\u6563", new Date("2026-06-04T09:46:53Z"), new Date("2026-08-31T20:59:59Z"), new Date("2026-08-31T20:59:59Z")],
  ["8590613", "leo", 251, 3544, "\u82f1\u8bed\u533a\u516c\u4f1a\u957f\u81ea\u7531\u653f\u7b56", null, "\u82f1\u8bed\u533a", "\u81ea\u7531", "\u6b63\u5e38", new Date("2026-06-09T04:27:11Z"), new Date("2026-08-31T20:59:59Z"), new Date("2026-08-31T20:59:59Z")],
  ["8590613", "leo", 279, 3587, "Thgfgfg", null, "\u82f1\u8bed\u533a", "\u53cc\u5468", "\u6b63\u5e38", new Date("2026-07-08T02:55:44Z"), new Date("2026-07-31T20:59:59Z"), new Date("2026-07-31T20:59:59Z")],
];

const nameByUserNumber = new Map(bindingRows.map((row) => [row[0], row[1]]));
const bindingsByUserNumber = new Map();
for (const row of bindingRows) {
  const existing = bindingsByUserNumber.get(row[0]) ?? [];
  existing.push(row);
  bindingsByUserNumber.set(row[0], existing);
}

const rosterValues = roster.getRange("A2:I8").values;
const summaryValues = rosterValues.map((row) => {
  const userNumber = String(row[0]);
  const bindings = bindingsByUserNumber.get(userNumber) ?? [];
  const summary = bindings.length === 0
    ? "\u65e0\u7ed1\u5b9a\u4e2d\u516c\u4f1a"
    : bindings.map((binding) => `[${binding[3]}] ${binding[4]} (${binding[7]}/${binding[8]})`).join("\n");
  return [bindings.length, summary];
});

roster.getRange("J1:K1").values = [["\u7ed1\u5b9a\u4e2d\u516c\u4f1a\u6570", "\u7ed1\u5b9a\u4e2d\u516c\u4f1a\u6c47\u603b"]];
roster.getRange("J2:K8").values = summaryValues;
roster.getRange("J2:K8").format.wrapText = true;
roster.getRange("J1").format.columnWidth = 14;
roster.getRange("K1").format.columnWidth = 48;

for (let index = 0; index < summaryValues.length; index += 1) {
  const bindingCount = summaryValues[index][0];
  const rowHeight = bindingCount <= 1 ? 24 : bindingCount === 2 ? 40 : bindingCount === 3 ? 56 : 72;
  roster.getRange(`A${index + 2}:K${index + 2}`).format.rowHeight = rowHeight;
}

for (const table of roster.tables.items) {
  table.delete();
}
const rosterTable = roster.tables.add("A1:K8", true, "ActiveStaffGuildTable");
rosterTable.style = "TableStyleMedium2";
rosterTable.showFilterButton = true;

const details = workbook.worksheets.add("\u7ed1\u5b9a\u516c\u4f1a\u660e\u7ec6");
details.showGridLines = false;
const detailHeaders = [["\u7528\u6237\u7f16\u53f7", "\u59d3\u540d", "\u7ed1\u5b9a ID", "\u516c\u4f1a ID", "\u516c\u4f1a\u540d\u79f0", "\u516c\u4f1a\u9080\u8bf7\u7801", "\u516c\u4f1a\u5730\u533a", "\u7ed3\u7b97\u653f\u7b56", "\u516c\u4f1a\u72b6\u6001", "\u7ed1\u5b9a\u65f6\u95f4", "\u5e95\u85aa\u622a\u6b62\u65f6\u95f4", "Bonus \u622a\u6b62\u65f6\u95f4"]];
details.getRange("A1:L1").values = detailHeaders;
details.getRange("A2:L12").values = bindingRows;
const detailsTable = details.tables.add("A1:L12", true, "GuildBindingDetailsTable");
detailsTable.style = "TableStyleMedium2";
detailsTable.showFilterButton = true;
details.getRange("A2:A12").format.numberFormat = "@";
details.getRange("J2:L12").format.numberFormat = "yyyy-mm-dd hh:mm";
details.getRange("A1:L12").format.wrapText = true;
details.getRange("A1:L1").format.rowHeight = 30;
details.getRange("A2:L12").format.rowHeight = 24;
details.getRange("I2:I12").conditionalFormats.add("containsText", { text: "\u5df2\u89e3\u6563", format: { fill: "#F4CCCC", font: { bold: true, color: "#990000" } } });
const detailWidths = [13, 16, 11, 11, 32, 14, 13, 12, 12, 20, 20, 20];
for (let index = 0; index < detailWidths.length; index += 1) {
  details.getRangeByIndexes(0, index, 12, 1).format.columnWidth = detailWidths[index];
}
details.freezePanes.freezeRows(1);

await fs.mkdir(outputDir, { recursive: true });
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);

const rosterCheck = await workbook.inspect({ kind: "table", range: "\u5728\u804c\u6210\u5458!A1:K8", include: "values,formulas", tableMaxRows: 10, tableMaxCols: 12 });
const detailsCheck = await workbook.inspect({ kind: "table", range: "\u7ed1\u5b9a\u516c\u4f1a\u660e\u7ec6!A1:L12", include: "values,formulas", tableMaxRows: 15, tableMaxCols: 12 });
const formulaErrors = await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 100 }, summary: "formula errors" });
console.log(rosterCheck.ndjson);
console.log(detailsCheck.ndjson);
console.log(formulaErrors.ndjson);

const rosterPreview = await workbook.render({ sheetName: "\u5728\u804c\u6210\u5458", range: "A1:K8", scale: 1, format: "png" });
const detailsPreview = await workbook.render({ sheetName: "\u7ed1\u5b9a\u516c\u4f1a\u660e\u7ec6", range: "A1:L12", scale: 1, format: "png" });
await fs.writeFile(`${outputDir}/active_staff_with_guilds_preview.png`, new Uint8Array(await rosterPreview.arrayBuffer()));
await fs.writeFile(`${outputDir}/guild_binding_details_preview.png`, new Uint8Array(await detailsPreview.arrayBuffer()));
console.log(outputPath);
