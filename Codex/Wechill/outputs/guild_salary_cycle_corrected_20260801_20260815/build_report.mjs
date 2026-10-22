import fs from "node:fs/promises";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const outputDir = "E:/Codex/Wechill/outputs/guild_salary_cycle_corrected_20260801_20260815";
const reportPath = `${outputDir}/本周期公会实时薪资_修正分成口径_20260801_20260815.xlsx`;
const data = JSON.parse(await fs.readFile(`${outputDir}/salary_data.json`, "utf8"));
const members = data.members;
const agencies = [...new Map(members.map((m) => [m.agency_id, m])).values()];
const firstDetailRow = 5;
const lastDetailRow = firstDetailRow + members.length - 1;
const firstSummaryRow = 5;
const lastSummaryRow = firstSummaryRow + agencies.length - 1;
const moneyFormat = "$#,##0.00;[Red]($#,##0.00);-";
const numberFormat = "#,##0;[Red](#,##0);-";
const dark = "#0F766E";
const subhead = "#E7F4F0";
const totalFill = "#C7E9DF";
const warningFill = "#FFF7E0";
const grid = { preset: "inside", style: "thin", color: "#D6E4E0" };

const workbook = Workbook.create();
const summary = workbook.worksheets.add("公会汇总");
const detail = workbook.worksheets.add("成员明细");
const notes = workbook.worksheets.add("口径说明");

summary.showGridLines = false;
summary.getRange("A1:O1").merge();
summary.getRange("A1").values = [["本周期公会实时薪资汇总"]];
summary.getRange("A1:O1").format = {
  fill: dark,
  font: { bold: true, color: "#FFFFFF", size: 16 },
  horizontalAlignment: "center",
  verticalAlignment: "center",
};
summary.getRange("A1:O1").format.rowHeight = 30;
summary.getRange("A2:O2").merge();
summary.getRange("A2").values = [[`周期：${data.period_start} 至 ${data.period_end_exclusive}（不含结束时点） | 数据环境：stay 测试库 | 币种：USD`]];
summary.getRange("A2:O2").format = {
  fill: subhead,
  font: { color: "#24564D", italic: true },
  horizontalAlignment: "center",
};
summary.getRange("A4:O4").values = [[
  "公会ID", "公会名称", "所属地区", "公会长用户编号", "公会长手机号",
  "主播薪资", "主播TG奖励", "公会长分成", "公会总薪资", "预支薪资",
  "薪资余额", "公会借支薪资", "可借支薪资", "有薪资成员数", "分成待复核数",
]];
summary.getRange("A4:O4").format = {
  fill: dark,
  font: { bold: true, color: "#FFFFFF" },
  horizontalAlignment: "center",
  verticalAlignment: "center",
  wrapText: true,
  borders: grid,
};
summary.getRange("A4:O4").format.rowHeight = 32;
summary.getRange(`A${firstSummaryRow}:E${lastSummaryRow}`).values = agencies.map((m) => [
  m.agency_id,
  m.agency_name,
  `${m.region} (region=${m.region_code})`,
  m.owner_user_number,
  m.owner_phone,
]);
summary.getRange(`L${firstSummaryRow}:M${lastSummaryRow}`).values = agencies.map((m) => [
  Number(m.agency_borrowed_amount),
  Number(m.borrowable_amount),
]);
summary.getRange(`F${firstSummaryRow}`).formulas = [[`=SUMIF('成员明细'!$A$${firstDetailRow}:$A$${lastDetailRow},A${firstSummaryRow},'成员明细'!$S$${firstDetailRow}:$S$${lastDetailRow})`]];
summary.getRange(`F${firstSummaryRow}:F${lastSummaryRow}`).fillDown();
summary.getRange(`G${firstSummaryRow}`).formulas = [[`=SUMIF('成员明细'!$A$${firstDetailRow}:$A$${lastDetailRow},A${firstSummaryRow},'成员明细'!$T$${firstDetailRow}:$T$${lastDetailRow})`]];
summary.getRange(`G${firstSummaryRow}:G${lastSummaryRow}`).fillDown();
summary.getRange(`H${firstSummaryRow}`).formulas = [[`=SUMIF('成员明细'!$A$${firstDetailRow}:$A$${lastDetailRow},A${firstSummaryRow},'成员明细'!$V$${firstDetailRow}:$V$${lastDetailRow})`]];
summary.getRange(`H${firstSummaryRow}:H${lastSummaryRow}`).fillDown();
summary.getRange(`I${firstSummaryRow}`).formulas = [[`=SUMIF('成员明细'!$A$${firstDetailRow}:$A$${lastDetailRow},A${firstSummaryRow},'成员明细'!$W$${firstDetailRow}:$W$${lastDetailRow})`]];
summary.getRange(`I${firstSummaryRow}:I${lastSummaryRow}`).fillDown();
summary.getRange(`J${firstSummaryRow}`).formulas = [[`=SUMIF('成员明细'!$A$${firstDetailRow}:$A$${lastDetailRow},A${firstSummaryRow},'成员明细'!$X$${firstDetailRow}:$X$${lastDetailRow})`]];
summary.getRange(`J${firstSummaryRow}:J${lastSummaryRow}`).fillDown();
summary.getRange(`K${firstSummaryRow}`).formulas = [[`=I${firstSummaryRow}-J${firstSummaryRow}`]];
summary.getRange(`K${firstSummaryRow}:K${lastSummaryRow}`).fillDown();
summary.getRange(`N${firstSummaryRow}`).formulas = [[`=COUNTIF('成员明细'!$A$${firstDetailRow}:$A$${lastDetailRow},A${firstSummaryRow})`]];
summary.getRange(`N${firstSummaryRow}:N${lastSummaryRow}`).fillDown();
summary.getRange(`O${firstSummaryRow}`).formulas = [[`=COUNTIFS('成员明细'!$A$${firstDetailRow}:$A$${lastDetailRow},A${firstSummaryRow},'成员明细'!$Y$${firstDetailRow}:$Y$${lastDetailRow},"待复核")`]];
summary.getRange(`O${firstSummaryRow}:O${lastSummaryRow}`).fillDown();
summary.getRange(`A${firstSummaryRow}:O${lastSummaryRow}`).format = { borders: grid, verticalAlignment: "center" };
summary.getRange(`A${firstSummaryRow}:O${lastSummaryRow}`).format.rowHeight = 22;
summary.getRange(`F${firstSummaryRow}:M${lastSummaryRow}`).format.numberFormat = moneyFormat;
summary.getRange(`F${firstSummaryRow}:O${lastSummaryRow}`).format.horizontalAlignment = "right";
const summaryTotalRow = lastSummaryRow + 1;
summary.getRange(`A${summaryTotalRow}:E${summaryTotalRow}`).merge();
summary.getRange(`A${summaryTotalRow}`).values = [["合计"]];
summary.getRange(`F${summaryTotalRow}`).formulas = [[`=SUM(F${firstSummaryRow}:F${lastSummaryRow})`, `=SUM(G${firstSummaryRow}:G${lastSummaryRow})`, `=SUM(H${firstSummaryRow}:H${lastSummaryRow})`, `=SUM(I${firstSummaryRow}:I${lastSummaryRow})`, `=SUM(J${firstSummaryRow}:J${lastSummaryRow})`, `=SUM(K${firstSummaryRow}:K${lastSummaryRow})`, `=SUM(L${firstSummaryRow}:L${lastSummaryRow})`, `=SUM(M${firstSummaryRow}:M${lastSummaryRow})`, `=SUM(N${firstSummaryRow}:N${lastSummaryRow})`, `=SUM(O${firstSummaryRow}:O${lastSummaryRow})`]];
summary.getRange(`A${summaryTotalRow}:O${summaryTotalRow}`).format = {
  fill: totalFill,
  font: { bold: true, color: "#134E4A" },
  borders: { preset: "doubleBottom", style: "medium", color: "#0F766E" },
};
summary.getRange(`F${summaryTotalRow}:M${summaryTotalRow}`).format.numberFormat = moneyFormat;
summary.getRange(`F${summaryTotalRow}:O${summaryTotalRow}`).format.horizontalAlignment = "right";
summary.getRange(`A${summaryTotalRow + 2}:O${summaryTotalRow + 2}`).merge();
summary.getRange(`A${summaryTotalRow + 2}`).values = [["分成口径：周期开始后 10 分钟内的历史 host salary 清算扣减已从本期 gain_coin 基数中排除；其他负向流水未被排除。"]];
summary.getRange(`A${summaryTotalRow + 2}:O${summaryTotalRow + 2}`).format = { fill: warningFill, font: { color: "#7A4A00" }, wrapText: true };
summary.getRange(`A${summaryTotalRow + 2}:O${summaryTotalRow + 2}`).format.rowHeight = 30;
for (const [range, width] of [[`A1:A${summaryTotalRow}`, 11], [`B1:B${summaryTotalRow}`, 23], [`C1:C${summaryTotalRow}`, 19], [`D1:D${summaryTotalRow}`, 16], [`E1:E${summaryTotalRow}`, 20], [`F1:M${summaryTotalRow}`, 16], [`N1:O${summaryTotalRow}`, 14]]) {
  summary.getRange(range).format.columnWidth = width;
}
summary.freezePanes.freezeRows(4);

detail.showGridLines = false;
detail.getRange("A1:Y1").merge();
detail.getRange("A1").values = [["本周期有薪资成员明细（修正后分成口径）"]];
detail.getRange("A1:Y1").format = {
  fill: dark,
  font: { bold: true, color: "#FFFFFF", size: 16 },
  horizontalAlignment: "center",
  verticalAlignment: "center",
};
detail.getRange("A1:Y1").format.rowHeight = 30;
detail.getRange("A2:Y2").merge();
detail.getRange("A2").values = [["金额单位：USD；借支为公会实时 borrowed_amount，预支为成员实时 advance_salary_total_amount。"]];
detail.getRange("A2:Y2").format = { fill: subhead, font: { color: "#24564D", italic: true }, horizontalAlignment: "center" };
detail.getRange("A4:Y4").values = [[
  "公会ID", "公会名称", "所属地区", "公会长用户编号", "公会长手机号", "用户ID", "用户编号", "昵称", "角色", "政策",
  "主播钻石基数", "原始本期金币", "已排除起始清算扣减", "调整后本期金币", "流水记录数", "有效天数", "总时长(小时)", "薪资比例",
  "主播薪资", "主播TG奖励", "主播总薪资", "公会长分成", "成员总薪资", "预支薪资", "薪资余额",
]];
detail.getRange("A4:Y4").format = {
  fill: dark,
  font: { bold: true, color: "#FFFFFF" },
  horizontalAlignment: "center",
  verticalAlignment: "center",
  wrapText: true,
  borders: grid,
};
detail.getRange("A4:Y4").format.rowHeight = 38;
detail.getRange(`A${firstDetailRow}:R${lastDetailRow}`).values = members.map((m) => [
  m.agency_id, m.agency_name, `${m.region} (region=${m.region_code})`, m.owner_user_number, m.owner_phone,
  m.user_id, m.user_number, m.nickname, m.role, m.policy, m.host_diamond_base, m.raw_period_gain_coin,
  m.excluded_cycle_start_settlement_debit, m.period_gain_coin, m.coin_record_count, m.effective_days,
  Number(m.total_hours), Number(m.salary_ratio),
]);
detail.getRange(`S${firstDetailRow}:Y${lastDetailRow}`).values = members.map((m) => [
  Number(m.host_salary), Number(m.host_tg_reward), Number(m.host_total_salary), Number(m.president_commission),
  Number(m.member_total_salary), Number(m.advance_salary), Number(m.member_salary_balance),
]);
detail.getRange(`A${firstDetailRow}:Y${lastDetailRow}`).format = { borders: grid, verticalAlignment: "center" };
detail.getRange(`A${firstDetailRow}:Y${lastDetailRow}`).format.rowHeight = 22;
detail.getRange(`K${firstDetailRow}:P${lastDetailRow}`).format.numberFormat = numberFormat;
detail.getRange(`Q${firstDetailRow}:Q${lastDetailRow}`).format.numberFormat = "0.00";
detail.getRange(`R${firstDetailRow}:R${lastDetailRow}`).format.numberFormat = "0.00%";
detail.getRange(`S${firstDetailRow}:Y${lastDetailRow}`).format.numberFormat = moneyFormat;
detail.getRange(`K${firstDetailRow}:Y${lastDetailRow}`).format.horizontalAlignment = "right";
detail.getRange(`A${firstDetailRow}:Y${lastDetailRow}`).conditionalFormats.add("Custom", { formula: `=$M${firstDetailRow}<0`, format: { fill: warningFill, font: { color: "#7A4A00" } } });
const detailTotalRow = lastDetailRow + 1;
detail.getRange(`A${detailTotalRow}:R${detailTotalRow}`).merge();
detail.getRange(`A${detailTotalRow}`).values = [["合计"]];
detail.getRange(`S${detailTotalRow}`).formulas = [[`=SUM(S${firstDetailRow}:S${lastDetailRow})`, `=SUM(T${firstDetailRow}:T${lastDetailRow})`, `=SUM(U${firstDetailRow}:U${lastDetailRow})`, `=SUM(V${firstDetailRow}:V${lastDetailRow})`, `=SUM(W${firstDetailRow}:W${lastDetailRow})`, `=SUM(X${firstDetailRow}:X${lastDetailRow})`, `=SUM(Y${firstDetailRow}:Y${lastDetailRow})`]];
detail.getRange(`A${detailTotalRow}:Y${detailTotalRow}`).format = {
  fill: totalFill,
  font: { bold: true, color: "#134E4A" },
  borders: { preset: "doubleBottom", style: "medium", color: "#0F766E" },
};
detail.getRange(`S${detailTotalRow}:Y${detailTotalRow}`).format.numberFormat = moneyFormat;
detail.getRange(`S${detailTotalRow}:Y${detailTotalRow}`).format.horizontalAlignment = "right";
for (const [range, width] of [[`A1:A${detailTotalRow}`, 10], [`B1:B${detailTotalRow}`, 22], [`C1:C${detailTotalRow}`, 18], [`D1:D${detailTotalRow}`, 15], [`E1:E${detailTotalRow}`, 19], [`F1:F${detailTotalRow}`, 11], [`G1:G${detailTotalRow}`, 13], [`H1:H${detailTotalRow}`, 20], [`I1:J${detailTotalRow}`, 11], [`K1:Q${detailTotalRow}`, 15], [`R1:R${detailTotalRow}`, 10], [`S1:Y${detailTotalRow}`, 16]]) {
  detail.getRange(range).format.columnWidth = width;
}
detail.freezePanes.freezeRows(4);

notes.showGridLines = false;
notes.getRange("A1:D1").merge();
notes.getRange("A1").values = [["计算口径与数据说明"]];
notes.getRange("A1:D1").format = { fill: dark, font: { bold: true, color: "#FFFFFF", size: 16 }, horizontalAlignment: "center", verticalAlignment: "center" };
notes.getRange("A1:D1").format.rowHeight = 30;
notes.getRange("A3:D3").values = [["项目", "取值 / 规则", "来源", "备注"]];
notes.getRange("A3:D3").format = { fill: dark, font: { bold: true, color: "#FFFFFF" }, horizontalAlignment: "center", borders: grid };
notes.getRange("A4:D10").values = [
  ["结算周期", `${data.period_start} 至 ${data.period_end_exclusive}`, "当前周期", "结束时点不含在内"],
  ["数据环境", "stay 测试库", "MySQL MCP", "未查询生产库"],
  ["主播薪资基数", "gain_diamond + send_gain_diamond", "app_user_account", "实时薪资，不使用历史结算明细"],
  ["公会长分成基数", "调整后的本期 period_gain_coin", "app_user_coin_detail", "按成员独立匹配地区与政策档位"],
  ["起始清算扣减", "source_type=18, option_type=203, remark=host salary, coin<0", "app_user_coin_detail", "仅周期开始后 10 分钟内排除"],
  ["借支薪资", "agency.borrowed_amount", "app_user_agency", "公会实时借支金额，USD"],
  ["预支薪资", "SUM(member.advance_salary_total_amount)", "app_user_account", "当前结果中的成员预支均为 0"],
];
notes.getRange("A4:D10").format = { borders: grid, verticalAlignment: "center", wrapText: true };
notes.getRange("A4:D10").format.rowHeight = 32;
notes.getRange("A4:A10").format = { fill: "#F4FAF8", font: { bold: true, color: "#134E4A" }, borders: grid, verticalAlignment: "center", wrapText: true };
notes.getRange("A1:A10").format.columnWidth = 20;
notes.getRange("B1:B10").format.columnWidth = 41;
notes.getRange("C1:C10").format.columnWidth = 31;
notes.getRange("D1:D10").format.columnWidth = 38;

const checks = await Promise.all([
  workbook.inspect({ kind: "table", range: `公会汇总!A1:O${summaryTotalRow}`, include: "values,formulas", tableMaxRows: 25, tableMaxCols: 16 }),
  workbook.inspect({ kind: "table", range: `成员明细!A1:Y${detailTotalRow}`, include: "values,formulas", tableMaxRows: 30, tableMaxCols: 26 }),
  workbook.inspect({ kind: "match", searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A", options: { useRegex: true, maxResults: 50 }, summary: "formula error scan" }),
]);
for (const check of checks) console.log(check.ndjson);

for (const [sheetName, fileName] of [["公会汇总", "preview_summary.png"], ["成员明细", "preview_members.png"], ["口径说明", "preview_notes.png"]]) {
  const preview = await workbook.render({ sheetName, autoCrop: "all", scale: 1.15, format: "png" });
  await fs.writeFile(`${outputDir}/${fileName}`, new Uint8Array(await preview.arrayBuffer()));
}

const output = await SpreadsheetFile.exportXlsx(workbook);
await output.save(reportPath);
console.log(JSON.stringify({ reportPath, memberCount: members.length, agencyCount: agencies.length }));
