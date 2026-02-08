#!/bin/bash
# cleanup_repo.sh - Clean up bulletproof-video-playback repository

set -e

echo "🧹 Bulletproof Video Playback - Repository Cleanup"
echo "=================================================="
echo ""

# ==============================================================================
# PART 1: DELETE OLD/REDUNDANT FILES
# ==============================================================================

echo "📄 Step 1: Removing obsolete documentation files..."

# These are temporary/working documents that are now superseded by CHANGELOG
FILES_TO_DELETE=(
    "DOCS-UPDATE-SUMMARY.md"           # Temporary doc update notes
    "LINUX_PORT_SUMMARY.md"            # Info now in CHANGELOG
    "PHASE_2_4_COMPLETE.md"            # Phase 2.4 is done, in CHANGELOG
    "TIER-1-FIX-SHIP.md"               # Working document, no longer needed
    "RELEASE_STATUS.html"              # HTML status page (not needed in repo)
    "test_keyframes.py"                # Test script in root (should be in tests/ or scripts/)
    "test_monitor.yaml"                # Test config in root (move to examples/)
    "monitor.json"                     # Test config in root (move to examples/)
)

for file in "${FILES_TO_DELETE[@]}"; do
    if [ -f "$file" ]; then
        echo "  ❌ Deleting: $file"
        git rm "$file"
    fi
done

echo ""
echo "📁 Step 2: Moving test files to proper locations..."

# Move test configs to examples folder
if [ -f "test_monitor.yaml" ]; then
    echo "  📦 Moving test_monitor.yaml → examples/"
    git mv test_monitor.yaml examples/
fi

if [ -f "monitor.json" ]; then
    echo "  📦 Moving monitor.json → examples/"
    git mv monitor.json examples/
fi

if [ -f "test_keyframes.py" ]; then
    echo "  📦 Moving test_keyframes.py → scripts/"
    git mv test_keyframes.py scripts/
fi

echo ""

# ==============================================================================
# PART 2: REORGANIZE PHASE 3.1 DOCS INTO SUBFOLDER
# ==============================================================================

echo "📚 Step 3: Organizing Phase 3.1 documentation..."

if [ ! -d "docs/phase-3.1" ]; then
    mkdir -p docs/phase-3.1
fi

PHASE_DOCS=(
    "PHASE-3.1-OVERVIEW.md"
    "PHASE-3.1-QUICKSTART.md"
    "PHASE-3.1-RESOURCES.md"
    "PHASE-3.1-START-HERE.md"
    "PHASE-3.1-TECH-DECISIONS.md"
    "PHASE-3.1-WEB-DASHBOARD.md"
)

for doc in "${PHASE_DOCS[@]}"; do
    if [ -f "$doc" ]; then
        echo "  📦 Moving $doc → docs/phase-3.1/"
        git mv "$doc" "docs/phase-3.1/"
    fi
done

echo ""

# ==============================================================================
# PART 3: MOVE OTHER ROOT-LEVEL DOCS TO docs/ FOLDER
# ==============================================================================

echo "📚 Step 4: Moving other documentation to docs/ folder..."

DOCS_TO_MOVE=(
    "KEYFRAME_FEATURE.md:docs/features/"
    "TESTING_KEYFRAMES.md:docs/testing/"
    "SCRIPTS_STRUCTURE.md:docs/"
    "ROADMAP.md:docs/"
)

for item in "${DOCS_TO_MOVE[@]}"; do
    file="${item%%:*}"
    dest="${item##*:}"
    
    if [ -f "$file" ]; then
        mkdir -p "$dest"
        echo "  📦 Moving $file → $dest"
        git mv "$file" "$dest"
    fi
done

echo ""

# ==============================================================================
# PART 4: DELETE MERGED BRANCHES
# ==============================================================================

echo "🌳 Step 5: Checking branches for cleanup..."

# feature/folder-monitor - MERGED into main (Phase 2.4 complete)
echo "  🗑️  Deleting feature/folder-monitor (merged)"
git push origin --delete feature/folder-monitor 2>/dev/null || echo "    (already deleted)"

# linux-port-dev - MERGED into main (v0.2.0)
echo "  🗑️  Deleting linux-port-dev (merged)"
git push origin --delete linux-port-dev 2>/dev/null || echo "    (already deleted)"

echo ""
echo "  ⚠️  KEEPING these branches:"
echo "     • feature/dashboard - Future work (Phase 3.1)"
echo "     • feature/textual-tui - Experimental TUI rewrite"

echo ""

# ==============================================================================
# PART 5: CREATE ARCHIVE FOLDER FOR HISTORICAL DOCS
# ==============================================================================

echo "📦 Step 6: Creating archive for historical documents..."

mkdir -p docs/archive

# Nothing to archive yet, but structure is ready

echo ""

# ==============================================================================
# PART 6: COMMIT CLEANUP
# ==============================================================================

echo "💾 Step 7: Committing cleanup changes..."

git add .
git commit -m "chore: Repository cleanup and documentation reorganization

- Remove obsolete working documents (TIER-1, PHASE_2_4_COMPLETE, etc.)
- Move Phase 3.1 docs to docs/phase-3.1/
- Move feature docs to docs/features/
- Move test configs to examples/
- Move test scripts to scripts/
- Delete merged branches (folder-monitor, linux-port-dev)
- Organize documentation structure for easier navigation
"

echo ""
echo "✅ Cleanup complete! Summary:"
echo ""
echo "Files deleted:"
for file in "${FILES_TO_DELETE[@]}"; do
    echo "  ❌ $file"
done
echo ""
echo "Documentation reorganized:"
echo "  📁 docs/phase-3.1/       - Phase 3.1 planning docs"
echo "  📁 docs/features/        - Feature documentation"
echo "  📁 docs/testing/         - Testing guides"
echo "  📁 examples/             - Example configs"
echo "  📁 scripts/              - Utility scripts"
echo ""
echo "Branches deleted:"
echo "  🗑️  feature/folder-monitor (merged)"
echo "  🗑️  linux-port-dev (merged)"
echo ""
echo "🚀 Ready to push! Run: git push origin main"
