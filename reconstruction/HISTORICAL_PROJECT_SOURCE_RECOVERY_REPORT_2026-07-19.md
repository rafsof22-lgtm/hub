# Historical Project Source Recovery Report — 2026-07-19

## Executive outcome

Project-source evidence was used to recover and formalize a substantial historical workspace denominator without pretending that references equal original archive bytes.

### Proven recovered evidence

- Full archive header and file inventory: **4,070 entries**.
- Stream files: **3,314**.
- Directories: **667**.
- Compression folders: **2**.
- File names, sizes, folder assignments, substream positions and available CRC32 values are preserved in `source_inventory.csv`.
- A preserved **75,000,000-byte** partial decompression stream exists for folder 0.
- Historical extraction logic proves folder 0 is the principal application/source folder.
- Folder 1's largest files are compiled NVIDIA/CUDA/NCCL/shared-library artifacts rather than unique Jarvis requirements.
- Historical project knowledge includes a **4,852,187-byte** `PROJECT_001_AUTO_PARTS/knowledge_base/EXTRACTED_DOCUMENTS.txt` source.
- Historical module and API structure is visible in the inventory, including agents, AI models, automation, chat, cost, crypto, health, income, integrations, intelligence, knowledgebase, market, MCP, modules, notifications, patents, payments, PC automation, property, security and trading.

## Recovery implementation

Files added:

- `reconstruction/historical_project_source_recovery_manifest.json`
- `reconstruction/recover_project_sources.py`
- `tests/test_recover_project_sources.py`
- `.github/workflows/historical-project-source-recovery-ci.yml`

The recovery pipeline:

1. Reads the preserved archive inventory.
2. Reconstructs folder-0 stream offsets deterministically.
3. Splits available partial raw bytes according to the original substream sizes.
4. Verifies recovered streams against CRC32 where available.
5. Writes SHA-256 evidence for every recovered stream.
6. Extracts text candidates only.
7. Rejects absolute paths and traversal components.
8. Records the exact truncation boundary instead of inventing missing bytes.
9. Produces a machine-readable recovery manifest.

## Correct completion classifications

| Scope | Status |
|---|---|
| Archive existence and denominator | `DONE_VERIFIED_FROM_PROJECT_SOURCES` |
| Archive file-tree inventory | `DONE_VERIFIED_FROM_PROJECT_SOURCES` |
| Folder/substream mapping | `DONE_VERIFIED_FROM_PROJECT_SOURCES` |
| Historical module/feature denominator | `SUBSTANTIALLY_RECOVERED` |
| Partial folder-0 raw data | `PARTIAL_RAW_RECOVERY_PROVEN` |
| Project 001 knowledgebase evidence | `DONE_VERIFIED_FROM_PROJECT_SOURCES` |
| Missing compiled dependency binaries | `NON_SEMANTIC_FOR_REQUIREMENTS` |
| Full original archive SHA-256 | `BLOCKED_ORIGINAL_ARCHIVE_BYTES` |
| Full folder-0 120,258,421-byte extraction | `BLOCKED_AFTER_75,000,000_BYTES` |
| Full folder-1 618,810,210-byte extraction | `BLOCKED_ORIGINAL_ARCHIVE_BYTES` |
| Full raw ChatGPT conversation tree | `BLOCKED_ORIGINAL_EXPORT_BYTES` |
| Global byte-for-byte no-gaps certificate | `NOT_PROVEN` |

## Supersession rule

Historical reports claiming `100%`, `zero gaps`, `production ready`, `313 modules`, `320+ modules`, `371 modules`, `373 modules` or similar totals are retained as historical assertions. They do not override the current source inventory, repository state, CI evidence or live-runtime evidence.

## Exact next input for byte-exact closure

Either of the following closes the remaining raw-source proof boundary:

- the original `KIMI_WORKSPACE_RAW.7z`, or
- the remaining decompressed folder-0 bytes plus complete folder-1 bytes with original inventory/CRC alignment.

For conversation-level closure, supply the original ChatGPT export ZIP/7Z or `conversations.json`.
