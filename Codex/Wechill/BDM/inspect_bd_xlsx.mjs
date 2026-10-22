import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = "E:/Codex/Wechill/outputs/bdm_active_staff_20260724/BD.xlsx";
const outputDir = "E:/Codex/Wechill/outputs/bdm_active_staff_20260724";
const input = await FileBlob.load(inputPath);
const workbook = await SpreadsheetFile.importXlsx(input);
const overview = await workbook.inspect({ kind: "workbook,sheet,table", maxChars: 8000, tableMaxRows: 30, tableMaxCols: 20 });
console.log(overview.ndjson);

for (const sheet of workbook.worksheets) {
  const preview = await workbook.render({ sheetName: sheet.name, autoCrop: "all", scale: 1, format: "png" });
  await fs.writeFile(`${outputDir}/bd_before_${sheet.index}.png`, new Uint8Array(await preview.arrayBuffer()));
  console.log(`SHEET:${sheet.index}:${sheet.name}`);
}
