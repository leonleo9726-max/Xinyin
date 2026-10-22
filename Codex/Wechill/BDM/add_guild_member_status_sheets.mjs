import fs from "node:fs/promises";
import { FileBlob, SpreadsheetFile } from "@oai/artifact-tool";

const inputPath = "E:/Codex/Wechill/outputs/bdm_active_staff_20260724/BD.xlsx";
const outputDir = "E:/Codex/Wechill/outputs/bdm_active_staff_20260724";
const outputPath = `${outputDir}/BD_with_guild_member_status.xlsx`;

const guilds = [
  { id: 3529, name: "leon guild", status: "\u6b63\u5e38", members: [
    [1404, "8501168", "leon", 0, 1, 0, 2, "2026-03-16T04:11:23.140Z", null],
    [1421, "8597570", "u15688", 1, 1, 1, 1, "2026-03-20T01:54:18.793Z", null],
    [1416, "8526429", "u15689", 2, 1, 2, 2, "2026-03-18T06:44:15.637Z", null],
    [1419, "8514466", "\u0639\u0644\u062a\u0627\u0646\u0646 \u062a\u064a\u0646\u062a\u064a\u0646\u062a \u0646\u064a\u062a\u0628\u0646\u0628\u062a \u062a\u064a\u0646\u062a\u064a\u0646\u062a", 1, 1, 2, 1, "2026-03-20T01:54:12.896Z", null],
    [1420, "8558717", "u15687", 1, 1, 2, 2, "2026-03-20T01:54:15.706Z", null],
    [1422, "8596889", "u15692", 1, 1, 2, 2, "2026-03-20T01:54:21.375Z", null],
    [1439, "8583889", "testleemxkdkdkdks", 0, 1, 2, 2, "2026-04-22T03:58:06.956Z", null],
    [1443, "8554210", "u15677-7134", 1, 1, 2, 2, "2026-04-28T10:09:02.722Z", null],
    [1406, "8589519", "U15648", 1, 0, 2, 1, "2026-03-16T10:30:19.761Z", "2026-03-17T04:09:55Z"],
    [1415, "8520731", "Lee", 0, 0, 2, 1, "2026-03-17T08:03:59.204Z", "2026-03-17T08:05:41Z"],
    [1447, "8514908", "u16401", 0, 0, 2, 2, "2026-05-06T03:10:31.720Z", "2026-06-20T19:10:47Z"],
    [1450, "8563167", "u16407", 2, 0, 2, 1, "2026-06-05T07:00:00Z", "2026-07-15T10:45:49Z"],
    [1499, "8577097", "u16453", 0, 0, 2, 2, "2026-05-22T03:26:59.433Z", "2026-06-09T07:41:08Z"],
    [1554, "8514908", "u16401", 0, 0, 2, 2, "2026-06-25T03:22:23.609Z", "2026-07-15T04:11:13Z"],
  ] },
  { id: 3540, name: "\u4e2d\u4e1c\u516c\u4f1a\u957f\u53cc\u5468\u653f\u7b56", status: "\u5df2\u89e3\u6563", members: [
    [1466, "8501913", "u15861", 1, 0, 0, 1, "2026-05-14T08:43:48.755Z", "2026-07-07T02:36:38Z"],
    [1467, "8515667", "u15898", 0, 0, 2, 1, "2026-05-14T08:45:33.760Z", "2026-07-07T02:36:39Z"],
    [1468, "8575805", "u15862", 0, 0, 2, 2, "2026-05-14T11:52:21.196Z", "2026-07-07T02:36:39Z"],
    [1481, "8554413", "u15900", 0, 0, 2, 2, "2026-05-16T03:13:07.316Z", "2026-05-16T03:21:17Z"],
    [1482, "8588149", "u15865", 0, 0, 2, 2, "2026-05-16T03:22:21.208Z", "2026-07-07T02:36:39Z"],
  ] },
  { id: 3541, name: "\u82f1\u8bed\u533a\u81ea\u7531\u653f\u7b56", status: "\u6b63\u5e38", members: [
    [1469, "8511452", "u16418", 1, 1, 0, 2, "2026-05-15T03:17:09.610Z", null],
    [1470, "8593132", "u16421", 0, 1, 2, 2, "2026-05-15T03:17:51.142Z", null],
    [1471, "8540644", "u16422", 1, 1, 2, 1, "2026-05-15T03:24:38.001Z", null],
    [1472, "8587411", "u16423", 1, 1, 2, 2, "2026-05-15T03:51:58.793Z", null],
    [1473, "8588336", "u16424", 1, 1, 2, 1, "2026-05-15T04:29:55.225Z", null],
    [1484, "8557287", "u16426", 1, 1, 2, 2, "2026-05-16T10:05:25.557Z", null],
  ] },
  { id: 3544, name: "\u82f1\u8bed\u533a\u516c\u4f1a\u957f\u81ea\u7531\u653f\u7b56", status: "\u6b63\u5e38", members: [
    [1485, "8578423", "u16435", 0, 1, 0, 2, "2026-05-18T02:14:33.823Z", null],
    [1486, "8517892", "u16436", 0, 1, 2, 1, "2026-05-18T02:15:13.815Z", null],
    [1492, "8546504", "u16444", 0, 1, 2, 2, "2026-05-20T02:08:06.639Z", null],
  ] },
  { id: 3552, name: "\u82f1\u8bed\u533a\u81ea\u7531\u7ed3\u7b97", status: "\u6b63\u5e38", members: [
    [1505, "8539314", "u16459", 1, 1, 0, 2, "2026-05-25T02:33:40.748Z", null],
    [1507, "8502216", "u16448", 1, 1, 2, 1, "2026-05-25T07:44:11.572Z", null],
    [1511, "8573401", "u16464", 0, 1, 2, 2, "2026-05-26T06:16:19.482Z", null],
    [1506, "8564242", "u16460", 1, 0, 2, 2, "2026-05-25T02:36:14.061Z", "2026-05-25T12:50:21Z"],
  ] },
  { id: 3558, name: "Yoww", status: "\u6b63\u5e38", members: [[1517, "8595978", "u15770", 1, 1, 0, 1, "2026-06-04T11:18:23.147Z", null]] },
  { id: 3572, name: "\u0647\u062b\u0647\u064a\u062a\u0628\u062a\u0628\u0647 \u0628\u0647\u0628\u0646", status: "\u6b63\u5e38", members: [[1541, "8542665", "u15751", 0, 1, 0, 2, "2026-06-18T03:11:24.123Z", null]] },
  { id: 3575, name: "Yomwe", status: "\u6b63\u5e38", members: [[1544, "8536064", "u15754", 1, 1, 0, 1, "2026-06-18T07:52:09.573Z", null]] },
  { id: 3581, name: "1155555555", status: "\u6b63\u5e38", members: [[1550, "8574607", "u16496", 1, 1, 0, 1, "2026-06-23T12:08:28.851Z", null]] },
  { id: 3584, name: "Lastly", status: "\u6b63\u5e38", members: [[1553, "8584657", "u15758", 1, 1, 0, 1, "2026-06-24T12:00:41.969Z", null]] },
  { id: 3587, name: "Thgfgfg", status: "\u6b63\u5e38", members: [[1558, "8558307", "u15755", 1, 1, 0, 1, "2026-07-08T02:55:43.730Z", null]] },
];

const input = await FileBlob.load(inputPath);
const workbook = await SpreadsheetFile.importXlsx(input);
const roleLabels = { 0: "\u516c\u4f1a\u957f", 1: "\u7ba1\u7406\u5458", 2: "\u4e3b\u64ad" };
const policyLabels = { 1: "\u53cc\u5468", 2: "\u81ea\u7531" };

for (const guild of guilds) {
  const sheetName = `\u6210\u5458\u72b6\u6001_${guild.id}`;
  const sheet = workbook.worksheets.add(sheetName);
  sheet.showGridLines = false;
  sheet.mergeCells("A1:I1");
  sheet.getRange("A1").values = [[`\u516c\u4f1a\u6210\u5458\u72b6\u6001 | ${guild.id} | ${guild.name}`]];
  sheet.mergeCells("A2:I2");
  sheet.getRange("A2").values = [[`\u516c\u4f1a\u72b6\u6001\uff1a${guild.status} | \u6210\u5458\u72b6\u6001\u4ee5 app_user_agency_member.status \u4e3a\u51c6 | \u6570\u636e\u63d0\u53d6\uff1a2026-07-24`]];
  sheet.getRange("A1:I1").format = { fill: "#1F4E78", font: { bold: true, color: "#FFFFFF", size: 14 }, horizontalAlignment: "center", verticalAlignment: "center" };
  sheet.getRange("A2:I2").format = { fill: guild.status === "\u5df2\u89e3\u6563" ? "#FCE4D6" : "#D9EAF7", font: { italic: true, color: "#1F2937" }, horizontalAlignment: "left" };
  sheet.getRange("A1:I1").format.rowHeight = 26;
  sheet.getRange("A2:I2").format.rowHeight = 20;

  const lastRow = 6 + guild.members.length;
  sheet.getRange("A4:F4").values = [["\u6210\u5458\u603b\u6570", null, "\u6709\u6548\u6210\u5458", null, "\u5df2\u9000\u51fa", null]];
  sheet.getRange("B4").formulas = [[`=COUNTA(A7:A${lastRow})`]];
  sheet.getRange("D4").formulas = [[`=COUNTIF(D7:D${lastRow},\"\u6709\u6548\")`]];
  sheet.getRange("F4").formulas = [[`=COUNTIF(D7:D${lastRow},\"\u5df2\u9000\u51fa\")`]];
  sheet.getRange("A4:F4").format = { fill: "#EAF2F8", font: { bold: true, color: "#17365D" }, horizontalAlignment: "center", borders: { preset: "outside", style: "thin", color: "#9EB6CE" } };
  sheet.getRange("B4,D4,F4").format = { fill: "#FFFFFF", font: { bold: true, color: "#17365D", size: 12 }, horizontalAlignment: "center", borders: { preset: "outside", style: "thin", color: "#9EB6CE" } };

  const headers = [["\u6210\u5458\u5173\u7cfb ID", "\u7528\u6237\u7f16\u53f7", "\u6635\u79f0", "\u6210\u5458\u72b6\u6001", "\u6210\u5458\u89d2\u8272", "\u7ed3\u7b97\u653f\u7b56", "\u52a0\u5165\u65f6\u95f4", "\u9000\u51fa\u65f6\u95f4", "\u8d26\u53f7\u72b6\u6001\uff08\u539f\u503c\uff09"]];
  const rows = guild.members.map((member) => [
    member[0], member[1], member[2], member[4] === 1 ? "\u6709\u6548" : "\u5df2\u9000\u51fa", roleLabels[member[5]], policyLabels[member[6]], new Date(member[7]), member[8] ? new Date(member[8]) : null, member[3],
  ]);
  sheet.getRange(`A6:I${lastRow}`).values = [...headers, ...rows];
  const table = sheet.tables.add(`A6:I${lastRow}`, true, `GuildMemberStatus${guild.id}`);
  table.style = "TableStyleMedium2";
  table.showFilterButton = true;
  sheet.getRange(`B7:B${lastRow}`).format.numberFormat = "@";
  sheet.getRange(`G7:H${lastRow}`).format.numberFormat = "yyyy-mm-dd hh:mm";
  sheet.getRange(`A6:I${lastRow}`).format.wrapText = true;
  sheet.getRange("A6:I6").format.rowHeight = 28;
  sheet.getRange(`A7:I${lastRow}`).format.rowHeight = 22;
  sheet.getRange(`D7:D${lastRow}`).conditionalFormats.add("containsText", { text: "\u6709\u6548", format: { fill: "#D9EAD3", font: { color: "#274E13" } } });
  sheet.getRange(`D7:D${lastRow}`).conditionalFormats.add("containsText", { text: "\u5df2\u9000\u51fa", format: { fill: "#F4CCCC", font: { color: "#990000" } } });
  const widths = [13, 13, 30, 13, 13, 12, 20, 20, 16];
  for (let index = 0; index < widths.length; index += 1) {
    sheet.getRangeByIndexes(0, index, lastRow, 1).format.columnWidth = widths[index];
  }
  sheet.freezePanes.freezeRows(6);
}

await fs.mkdir(outputDir, { recursive: true });
const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(outputPath);

const sheetCheck = await workbook.inspect({ kind: "sheet", include: "id,name", maxChars: 6000 });
const check3529 = await workbook.inspect({ kind: "table", range: "\u6210\u5458\u72b6\u6001_3529!A1:I20", include: "values,formulas", tableMaxRows: 20, tableMaxCols: 9 });
const check3540 = await workbook.inspect({ kind: "table", range: "\u6210\u5458\u72b6\u6001_3540!A1:I11", include: "values,formulas", tableMaxRows: 12, tableMaxCols: 9 });
const formulaErrors = await workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 100 }, summary: "formula errors" });
console.log(sheetCheck.ndjson);
console.log(check3529.ndjson);
console.log(check3540.ndjson);
console.log(formulaErrors.ndjson);

for (const guild of guilds) {
  const preview = await workbook.render({ sheetName: `\u6210\u5458\u72b6\u6001_${guild.id}`, autoCrop: "all", scale: 1, format: "png" });
  await fs.writeFile(`${outputDir}/member_status_${guild.id}.png`, new Uint8Array(await preview.arrayBuffer()));
}
console.log(outputPath);
