#!/usr/bin/env node
/**
 * Fill-safety audit entry point (from kml/tools/ambient).
 *
 *   node tools/audit-fill-safety.js lesson_02_vocabulary
 *   node tools/audit-fill-safety.js lesson_02_vocabulary --dry-run
 */

import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import path from "node:path";

const ambientRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const pyScript = path.join(ambientRoot, "scripts", "audit_fill_safety.py");
const args = process.argv.slice(2);

if (args.length === 0 || args.includes("-h") || args.includes("--help")) {
  console.log(`Usage: node tools/audit-fill-safety.js <collection_id> [--dry-run] [--samples N]`);
  process.exit(args.length === 0 ? 1 : 0);
}

const result = spawnSync("python3", [pyScript, ...args], {
  cwd: ambientRoot,
  stdio: "inherit",
});

process.exit(result.status ?? 1);
