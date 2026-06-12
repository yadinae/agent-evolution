// solidify-state.js — 进化状态持久化
// Extracted from solidify.js for modularity.
const fs = require("fs");
const path = require("path");
const { getMemoryDir, getEvolutionDir } = require("./paths");

function readStateForSolidify() {
  var p = path.join(getEvolutionDir(), "evolution_solidify_state.json");
  try {
    if (!fs.existsSync(p)) return { last_run: null };
    return JSON.parse(fs.readFileSync(p, "utf8"));
  } catch (e) {
    return { last_run: null };
  }
}

function writeStateForSolidify(state) {
  var dir = getMemoryDir();
  var p = path.join(getEvolutionDir(), "evolution_solidify_state.json");
  try { if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true }); } catch (e) {}
  var tmp = p + ".tmp";
  fs.writeFileSync(tmp, JSON.stringify(state, null, 2) + "\n", "utf8");
  fs.renameSync(tmp, p);
}

module.exports = { readStateForSolidify, writeStateForSolidify };
