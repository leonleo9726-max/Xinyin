import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";
import { fileURLToPath } from "node:url";

const workbookPath = fileURLToPath(new URL("./Guild_Salary_20260601_20260615.xlsx", import.meta.url));
const blob = await FileBlob.load(workbookPath);
const workbook = await SpreadsheetFile.importXlsx(blob);
const sheets = await workbook.inspect({ kind: "sheet", include: "name" });
console.log(sheets.ndjson);
