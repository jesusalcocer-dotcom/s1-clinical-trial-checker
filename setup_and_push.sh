#!/bin/bash
# Run this from your Mac terminal
# Moves the 5 framework docs + implementation instructions to your project,
# then pushes everything to git so Claude Code can access it.

PROJECT_DIR="/Users/jalcosan/Desktop/s1-clinical-trial-checker"
DOWNLOADS="/Users/jalcosan/Downloads"

echo "=== Step 1: Copy framework docs to project root ==="
cp "$DOWNLOADS/legal_brief.md" "$PROJECT_DIR/"
cp "$DOWNLOADS/study_specific_output.md" "$PROJECT_DIR/"
cp "$DOWNLOADS/check2_phase_labels.md" "$PROJECT_DIR/"
cp "$DOWNLOADS/checks_3_4_5.md" "$PROJECT_DIR/"
cp "$DOWNLOADS/checks_6_7.md" "$PROJECT_DIR/"

echo "=== Step 2: Copy implementation instructions ==="
cp "$DOWNLOADS/claude_code_v5_implementation.md" "$PROJECT_DIR/"

echo "=== Step 3: Verify files landed ==="
echo "Files in project root:"
ls -la "$PROJECT_DIR"/*.md

echo ""
echo "=== Step 4: Git add, commit, push ==="
cd "$PROJECT_DIR"
git add -A
git commit -m "Add v5 framework docs: legal brief, study output spec, check deep-dives (2,3,4,5,6,7), implementation instructions

New files:
- legal_brief.md (802 lines) — lawyer-auditable legal framework
- study_specific_output.md (914 lines) — Step 2 output format spec
- check2_phase_labels.md (473 lines) — Check 2 deep-dive with 3 comparison pairs
- checks_3_4_5.md (1469 lines) — Checks 3,4,5 deep-dive with 7+ comparison pairs
- checks_6_7.md (1128 lines) — Checks 6,7 deep-dive with 7 comparison pairs
- claude_code_v5_implementation.md — implementation instructions for Claude Code

31 placeholder slots for S-1 text tracked but intentionally unfilled."

git push origin main

echo ""
echo "=== Done! ==="
echo "Now open Claude Code in the project directory and paste:"
echo ""
echo "  Read claude_code_v5_implementation.md and execute all steps in order."
echo ""
