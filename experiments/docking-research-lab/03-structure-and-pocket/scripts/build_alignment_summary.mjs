import fs from "node:fs/promises";
import path from "node:path";
import { SpreadsheetFile, Workbook } from "@oai/artifact-tool";

const projectRoot = "/Users/yangruoxi/Projects/Docking-Research-Lab";
const alignmentRoot = path.join(projectRoot, "alignment");
const resultsDir = path.join(alignmentRoot, "results");
const validationDir = "/private/tmp/alignment_summary_artifact";

const comparisons = [
  ["01", "core_gprc", "TWF154_Gpr2", "Aflagrans_GprC", "01_TWF154_Gpr2_vs_GprC"],
  ["02", "core_gprc", "TWF154_Gpr3", "Aflagrans_GprC", "02_TWF154_Gpr3_vs_GprC"],
  ["03", "core_srbc64", "TWF154_Gpr2", "Celegans_N2_SRBC64", "03_TWF154_Gpr2_vs_SRBC64"],
  ["04", "core_srbc64", "TWF154_Gpr3", "Celegans_N2_SRBC64", "04_TWF154_Gpr3_vs_SRBC64"],
  ["05", "strain_control", "TWF154_Gpr2", "ATCC24927_Gpr2", "05_TWF154_Gpr2_vs_ATCC24927_Gpr2"],
  ["06", "strain_control", "TWF154_Gpr3", "ATCC24927_Gpr3", "06_TWF154_Gpr3_vs_ATCC24927_Gpr3"],
];

const headers = [
  "comparison_id",
  "analysis_role",
  "mobile_receptor",
  "reference_receptor",
  "mobile_length",
  "reference_length",
  "aligned_length",
  "mobile_coverage",
  "reference_coverage",
  "rmsd_A",
  "sequence_identity",
  "tm_score_mobile_normalized",
  "tm_score_reference_normalized",
  "tm_score_average_normalized",
  "stderr_bytes",
  "run_status",
  "stdout_path",
  "rotation_matrix_path",
];

function requiredMatch(text, regex, label, sourcePath) {
  const match = text.match(regex);
  if (!match) throw new Error(`Missing ${label} in ${sourcePath}`);
  return match;
}

const rows = [];
for (const [id, role, mobile, reference, directory] of comparisons) {
  const relativeDir = path.join("alignments", directory);
  const stdoutRelative = path.join(relativeDir, "tmalign.stdout.txt");
  const stderrRelative = path.join(relativeDir, "tmalign.stderr.txt");
  const matrixRelative = path.join(relativeDir, "rotation_matrix.txt");
  const stdoutPath = path.join(alignmentRoot, stdoutRelative);
  const stderrPath = path.join(alignmentRoot, stderrRelative);
  const matrixPath = path.join(alignmentRoot, matrixRelative);

  const text = await fs.readFile(stdoutPath, "utf8");
  const length1 = Number(requiredMatch(text, /Length of Chain_1:\s*(\d+) residues/, "Chain_1 length", stdoutPath)[1]);
  const length2 = Number(requiredMatch(text, /Length of Chain_2:\s*(\d+) residues/, "Chain_2 length", stdoutPath)[1]);
  const alignment = requiredMatch(
    text,
    /Aligned length=\s*(\d+), RMSD=\s*([0-9.]+), Seq_ID=n_identical\/n_aligned=\s*([0-9.]+)/,
    "alignment summary",
    stdoutPath,
  );
  const alignedLength = Number(alignment[1]);
  const rmsd = Number(alignment[2]);
  const sequenceIdentity = Number(alignment[3]);
  const tmMobile = Number(requiredMatch(text, /TM-score=\s*([0-9.]+).*normalized by length of Chain_1/, "mobile-normalized TM-score", stdoutPath)[1]);
  const tmReference = Number(requiredMatch(text, /TM-score=\s*([0-9.]+).*normalized by length of Chain_2/, "reference-normalized TM-score", stdoutPath)[1]);
  const tmAverage = Number(requiredMatch(text, /TM-score=\s*([0-9.]+).*normalized by average length/, "average-normalized TM-score", stdoutPath)[1]);
  const stderrBytes = (await fs.stat(stderrPath)).size;
  await fs.access(matrixPath);

  rows.push([
    id,
    role,
    mobile,
    reference,
    length1,
    length2,
    alignedLength,
    alignedLength / length1,
    alignedLength / length2,
    rmsd,
    sequenceIdentity,
    tmMobile,
    tmReference,
    tmAverage,
    stderrBytes,
    stderrBytes === 0 ? "pass" : "review_stderr",
    stdoutRelative,
    matrixRelative,
  ]);
}

function tsvCell(value) {
  return String(value).replaceAll("\t", " ").replaceAll("\r", " ").replaceAll("\n", " ");
}

const tsv = [headers, ...rows].map((row) => row.map(tsvCell).join("\t")).join("\n") + "\n";
await fs.mkdir(resultsDir, { recursive: true });
await fs.writeFile(path.join(resultsDir, "alignment_summary.tsv"), tsv, "utf8");

const workbook = Workbook.create();
const sheet = workbook.worksheets.add("Alignment Summary");
sheet.getRangeByIndexes(0, 0, rows.length + 1, headers.length).values = [headers, ...rows];
sheet.freezePanes.freezeRows(1);
sheet.showGridLines = false;
sheet.getRangeByIndexes(0, 0, 1, headers.length).format = {
  fill: "#1F4E78",
  font: { bold: true, color: "#FFFFFF" },
};
sheet.getRange("E2:G7").format.numberFormat = "0";
sheet.getRange("H2:I7").format.numberFormat = "0.000";
sheet.getRange("J2:N7").format.numberFormat = "0.00000";
sheet.getRange("O2:O7").format.numberFormat = "0";
sheet.getUsedRange().format.autofitColumns();
sheet.getRange("Q:R").format.columnWidth = 42;

const inspected = await workbook.inspect({
  kind: "table",
  range: "'Alignment Summary'!A1:R7",
  include: "values,formulas",
  tableMaxRows: 8,
  tableMaxCols: 18,
  maxChars: 12000,
});

const errors = await workbook.inspect({
  kind: "match",
  searchTerm: "#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A",
  options: { useRegex: true, maxResults: 100 },
  summary: "alignment summary error scan",
});

await fs.mkdir(validationDir, { recursive: true });
const preview = await workbook.render({
  sheetName: "Alignment Summary",
  range: "A1:R7",
  scale: 1,
  format: "png",
});
await fs.writeFile(path.join(validationDir, "preview.png"), new Uint8Array(await preview.arrayBuffer()));
const xlsx = await SpreadsheetFile.exportXlsx(workbook);
await xlsx.save(path.join(validationDir, "alignment_summary_validation.xlsx"));

console.log(JSON.stringify({
  output: path.join(resultsDir, "alignment_summary.tsv"),
  rowCount: rows.length,
  inspected: inspected.ndjson,
  errors: errors.ndjson,
}));
