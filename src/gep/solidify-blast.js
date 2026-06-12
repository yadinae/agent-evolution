// solidify-blast.js — 爆破半径分析与约束检查
// Extracted from solidify.js for modularity.
var path = require("path");
var fs = require("fs");

var BLAST_RADIUS_HARD_CAP_FILES = Number(process.env.EVOLVER_HARD_CAP_FILES) || 60;
var BLAST_RADIUS_HARD_CAP_LINES = Number(process.env.EVOLVER_HARD_CAP_LINES) || 20000;

function isForbiddenPath(relPath, forbiddenPaths) {
  var r = String(relPath || "");
  for (var i = 0; i < forbiddenPaths.length; i++) {
    var f = String(forbiddenPaths[i]);
    if (f === r) return true;
    if (r.startsWith(f + "/") || r.startsWith(f + "\\")) return true;
  }
  return false;
}

function classifyBlastSeverity(blast, maxFiles) {
  var files = Number(blast.files) || 0;
  var lines = Number(blast.lines) || 0;
  var warnRatio = 0.8;
  if (files > BLAST_RADIUS_HARD_CAP_FILES || lines > BLAST_RADIUS_HARD_CAP_LINES) {
    return { severity: "hard_cap_breach", message: "HARD CAP BREACH: " + files + " files / " + lines + " lines" };
  }
  if (maxFiles > 0 && files > maxFiles * 2) {
    return { severity: "critical_overrun", message: "CRITICAL: " + files + " files exceeds 2x max (" + maxFiles + ")" };
  }
  if (maxFiles > 0 && files > maxFiles) {
    return { severity: "exceeded", message: files + " files exceeds max " + maxFiles };
  }
  if (maxFiles > 0 && files > maxFiles * warnRatio) {
    return { severity: "approaching_limit", message: files + " / " + maxFiles + " files (approaching limit)" };
  }
  return { severity: "within_limit", message: files + " files / " + lines + " lines" };
}

function analyzeBlastRadiusBreakdown(changedFiles, topN) {
  if (!Array.isArray(changedFiles)) return [];
  var n = Math.max(1, Number(topN) || 10);
  var exts = {};
  for (var i = 0; i < changedFiles.length; i++) {
    var ext = path.extname(String(changedFiles[i] || "")).toLowerCase() || "(no_ext)";
    exts[ext] = (exts[ext] || 0) + 1;
  }
  var sorted = Object.keys(exts).sort(function(a, b) { return exts[b] - exts[a]; });
  var top = [];
  for (var j = 0; j < Math.min(n, sorted.length); j++) {
    top.push({ ext: sorted[j], count: exts[sorted[j]] });
  }
  return top;
}

function compareBlastEstimate(estimate, actual) {
  if (!estimate) return { status: "no_estimate" };
  var estF = Number(estimate.files) || 0;
  var actF = Number(actual.files) || 0;
  if (estF <= 0) return { status: "no_estimate" };
  var ratio = actF / estF;
  if (ratio <= 1.2) return { status: "accurate" };
  if (ratio <= 2.0) return { status: "underestimated_2x" };
  return { status: "severely_underestimated" };
}

function isCriticalProtectedPath(relPath) {
  var p = String(relPath || "").replace(/\\/g, "/");
  var critical = ["package.json", "package-lock.json", "mcp_server.js", "src/gep/", "src/evolve.js"];
  for (var i = 0; i < critical.length; i++) {
    if (p === critical[i] || p.startsWith(critical[i])) return true;
  }
  return false;
}

function detectDestructiveChanges(opts) {
  var changed = Array.isArray(opts.changedFiles) ? opts.changedFiles : [];
  var violations = [];
  for (var i = 0; i < changed.length; i++) {
    if (isCriticalProtectedPath(changed[i])) {
      violations.push("Destructive change to protected path: " + changed[i]);
    }
  }
  return violations;
}

module.exports = {
  classifyBlastSeverity, analyzeBlastRadiusBreakdown, compareBlastEstimate,
  isCriticalProtectedPath, isForbiddenPath, detectDestructiveChanges,
  BLAST_RADIUS_HARD_CAP_FILES, BLAST_RADIUS_HARD_CAP_LINES,
};
