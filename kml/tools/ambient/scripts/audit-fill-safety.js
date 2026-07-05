#!/usr/bin/env node
/**
 * Node entry point for fill-safety audit (delegates to audit_fill_safety.py).
 *
 * Usage (from kml/tools/ambient):
 *   node scripts/audit-fill-safety.js lesson_02_vocabulary
 *   node scripts/audit-fill-safety.js lesson_02_vocabulary --dry-run
 */

import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";

const here = path.dirname(fileURLToPath(import.meta.url));
const pyScript = path.join(here, "audit_fill_safety.py");
const args = process.argv.slice(2);

if (args.length === 0 || args.includes("-h") || args.includes("--help")) {
  console.log(`Usage: node scripts/audit-fill-safety.js <collection_id> [--dry-run] [--samples N]`);
  process.exit(args.length === 0 ? 1 : 0);
}

const result = spawnSync("python3", [pyScript, ...args], {
  cwd: path.resolve(here, ".."),
  stdio: "inherit",
});

process.exit(result.status ?? 1);
