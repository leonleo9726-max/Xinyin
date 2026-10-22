import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = "E:/Codex/Wechill/outputs/bdm_active_staff_20260724/BDM_BD_Active_Staff_20260724.xlsx";
const outputDir = "E:/Codex/Wechill/outputs/bdm_active_staff_20260724";
const input = await FileBlob.load(inputPath);
const workbook = await SpreadsheetFile.importXlsx(input);

const summary = await workbook.inspect({ kind: "workbook,sheet,table", maxChars: 6000, tableMaxRows: 40, tableMaxCols: 24 });
const data = await workbook.inspect({ kind: "table", range: "\u5728\u804c\u6210\u5458!A1:V60", include: "values,formulas", tableMaxRows: 60, tableMaxCols: 22 });
const styles = await workbook.inspect({ kind: "computedStyle", sheetId: "\u5728\u804c\u6210\u5458", range: "A7:V10", maxChars: 5000 });
console.log(summary.ndjson);
console.log(data.ndjson);
console.log(styles.ndjson);

const rosterPreview = await workbook.render({ sheetName: "\u5728\u804c\u6210\u5458", range: "A1:V60", scale: 1, format: "png" });
await fs.writeFile(`${outputDir}/manual_roster_before_guilds.png`, new Uint8Array(await rosterPreview.arrayBuffer()));
