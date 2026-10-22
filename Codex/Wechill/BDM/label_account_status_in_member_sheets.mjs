import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = "E:/Codex/Wechill/outputs/bdm_active_staff_20260724/BD_with_guild_member_status.xlsx";
const outputDir = "E:/Codex/Wechill/outputs/bdm_active_staff_20260724";
const outputPath = `${outputDir}/BD_with_guild_member_status_account_labels.xlsx`;
const guildIds = [3529, 3540, 3541, 3544, 3552, 3558, 3572, 3575, 3581, 3584, 3587];
const labels = { 0: "\u7981\u7528 (0)", 1: "\u542f\u7528 (1)", 2: "\u6ce8\u9500 (2)" };

const input = await FileBlob.load(inputPath);
const workbook = await SpreadsheetFile.importXlsx(input);

for (const guildId of guildIds) {
  const sheet = workbook.worksheets.getItem(`\u6210\u5458\u72b6\u6001_${guildId}`);
  const used = sheet.getUsedRange(true);
  const rowCount = used.values.length;
  const lastRow = rowCount;
  const existingNote = sheet.getRange("A2").values[0][0];
  const originalValues = sheet.getRange(`I7:I${lastRow}`).values;
  sheet.getRange("A2").values = [[`${existingNote} | app_user.status\uff1a0=\u7981\u7528\u30011=\u542f\u7528\u30012=\u6ce8\u9500`]];
  sheet.getRange("I6").values = [["\u8d26\u53f7\u72b6\u6001"]];
  sheet.getRange(`I7:I${lastRow}`).values = originalValues.map(([value]) => [labels[value] ?? `\u672a\u77e5 (${value})`]);
  sheet.getRange("A2:I2").format.wrapText = true;
  sheet.getRange("A2:I2").format.rowHeight = 30;
  sheet.getRange("I1").format.columnWidth = 16;
}

await fs.mkdir(outputDir, { recursive: true });
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);

const check3529 = await workbook.inspect({ kind: "table", range: "\u6210\u5458\u72b6\u6001_3529!A1:I20", include: "values,formulas", tableMaxRows: 20, tableMaxCols: 9 });
const formulaErrors = await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 100 }, summary: "formula errors" });
console.log(check3529.ndjson);
console.log(formulaErrors.ndjson);

const preview = await workbook.render({ sheetName: "\u6210\u5458\u72b6\u6001_3529", autoCrop: "all", scale: 1, format: "png" });
await fs.writeFile(`${outputDir}/account_status_labels_preview.png`, new Uint8Array(await preview.arrayBuffer()));
console.log(outputPath);
