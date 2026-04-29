You are given an OpenClaw skill installer script. Add a `--dry-run` mode that simulates all file writes and prints a unified diff of what would change, without actually modifying any files.

```bash
#!/usr/bin/env bash
# OpenClaw Skill Installer v2
# Installs a skill package into the OpenClaw skills directory.
# Usage: install-skill.sh <skill-archive.tar.gz> [--force]
set -euo pipefail

SKILLS_DIR="${OPENCLAW_HOME:-$HOME/.openclaw}/skills"
CONFIG_DIR="${OPENCLAW_HOME:-$HOME/.openclaw}/config"
LOG_FILE="${OPENCLAW_HOME:-$HOME/.openclaw}/logs/skill-install.log"
MANIFEST_FILE="$SKILLS_DIR/.manifest.json"

log() { echo "[$(date -u +%Y-%m-%dT%H:%M:%SZ)] $*" | tee -a "$LOG_FILE"; }
die() { log "ERROR: $*"; exit 1; }

ARCHIVE=""
FORCE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --force) FORCE=true; shift ;;
        --help|-h)
            echo "Usage: $0 <skill-archive.tar.gz> [--force]"
            echo "  --force    Overwrite existing skill"
            exit 0 ;;
        *) ARCHIVE="$1"; shift ;;
    esac
done

[[ -z "$ARCHIVE" ]] && die "No archive specified"
[[ -f "$ARCHIVE" ]] || die "Archive not found: $ARCHIVE"

# Create directories
mkdir -p "$SKILLS_DIR" "$CONFIG_DIR" "$(dirname "$LOG_FILE")"

# Extract to temp dir
TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

log "Extracting $ARCHIVE..."
tar xzf "$ARCHIVE" -C "$TMPDIR" || die "Failed to extract archive"

# Validate skill structure
SKILL_META="$TMPDIR/skill.json"
[[ -f "$SKILL_META" ]] || die "Missing skill.json in archive"

SKILL_NAME=$(python3 -c "import json; print(json.load(open('$SKILL_META'))['name'])" 2>/dev/null)
SKILL_VERSION=$(python3 -c "import json; print(json.load(open('$SKILL_META'))['version'])" 2>/dev/null)
SKILL_AUTHOR=$(python3 -c "import json; print(json.load(open('$SKILL_META')).get('author', 'unknown'))" 2>/dev/null)

[[ -z "$SKILL_NAME" ]] && die "Cannot read skill name from skill.json"
log "Installing skill: $SKILL_NAME v$SKILL_VERSION by $SKILL_AUTHOR"

DEST_DIR="$SKILLS_DIR/$SKILL_NAME"

# Check existing
if [[ -d "$DEST_DIR" ]]; then
    if [[ "$FORCE" == "true" ]]; then
        log "Removing existing skill: $SKILL_NAME"
        rm -rf "$DEST_DIR"
    else
        EXISTING_VER=$(python3 -c "import json; print(json.load(open('$DEST_DIR/skill.json'))['version'])" 2>/dev/null || echo "unknown")
        die "Skill $SKILL_NAME already installed (v$EXISTING_VER). Use --force to overwrite."
    fi
fi

# Copy files
log "Copying files to $DEST_DIR..."
cp -r "$TMPDIR" "$DEST_DIR"
chmod -R u+rw "$DEST_DIR"

# Run post-install hooks
if [[ -f "$DEST_DIR/hooks/post-install.sh" ]]; then
    log "Running post-install hook..."
    chmod +x "$DEST_DIR/hooks/post-install.sh"
    bash "$DEST_DIR/hooks/post-install.sh" "$DEST_DIR" || log "WARNING: post-install hook failed"
fi

# Install dependencies
if [[ -f "$DEST_DIR/requirements.txt" ]]; then
    log "Installing Python dependencies..."
    pip3 install -r "$DEST_DIR/requirements.txt" --quiet || log "WARNING: pip install failed"
fi

if [[ -f "$DEST_DIR/package.json" ]]; then
    log "Installing Node dependencies..."
    (cd "$DEST_DIR" && npm install --production --quiet 2>/dev/null) || log "WARNING: npm install failed"
fi

# Update manifest
log "Updating manifest..."
if [[ -f "$MANIFEST_FILE" ]]; then
    # Add/update entry in manifest
    python3 -c "
import json, os
manifest = json.load(open('$MANIFEST_FILE'))
manifest['skills'] = [s for s in manifest.get('skills', []) if s['name'] != '$SKILL_NAME']
manifest['skills'].append({
    'name': '$SKILL_NAME',
    'version': '$SKILL_VERSION',
    'author': '$SKILL_AUTHOR',
    'installed_at': '$(date -u +%Y-%m-%dT%H:%M:%SZ)',
    'path': '$DEST_DIR'
})
with open('$MANIFEST_FILE', 'w') as f:
    json.dump(manifest, f, indent=2)
"
else
    python3 -c "
import json
manifest = {
    'skills': [{
        'name': '$SKILL_NAME',
        'version': '$SKILL_VERSION',
        'author': '$SKILL_AUTHOR',
        'installed_at': '$(date -u +%Y-%m-%dT%H:%M:%SZ)',
        'path': '$DEST_DIR'
    }]
}
with open('$MANIFEST_FILE', 'w') as f:
    json.dump(manifest, f, indent=2)
"
fi

# Register with OpenClaw config
SKILLS_CONFIG="$CONFIG_DIR/skills.json"
if [[ -f "$SKILLS_CONFIG" ]]; then
    python3 -c "
import json
config = json.load(open('$SKILLS_CONFIG'))
config.setdefault('enabled', [])
if '$SKILL_NAME' not in config['enabled']:
    config['enabled'].append('$SKILL_NAME')
with open('$SKILLS_CONFIG', 'w') as f:
    json.dump(config, f, indent=2)
"
else
    python3 -c "
import json
config = {'enabled': ['$SKILL_NAME']}
with open('$SKILLS_CONFIG', 'w') as f:
    json.dump(config, f, indent=2)
"
fi

# Verify installation
if [[ -f "$DEST_DIR/skill.json" ]]; then
    log "✅ Skill $SKILL_NAME v$SKILL_VERSION installed successfully"
    log "  Path: $DEST_DIR"
    FILE_COUNT=$(find "$DEST_DIR" -type f | wc -l | tr -d ' ')
    log "  Files: $FILE_COUNT"
else
    die "Installation verification failed"
fi

# Print skill info
echo ""
echo "Skill: $SKILL_NAME"
echo "Version: $SKILL_VERSION"
echo "Author: $SKILL_AUTHOR"
echo "Path: $DEST_DIR"
echo ""
echo "To use: openclaw skill enable $SKILL_NAME"
```

Requirements for `--dry-run`:
1. Parse `--dry-run` flag alongside existing flags
2. No files are created, modified, or deleted when `--dry-run` is active
3. For each file that would be written/modified, print a unified diff:
   - New files: show `--- /dev/null` → `+++ <path>` with all lines as additions
   - Modified files: show actual diff against existing content
   - Deleted files (from --force): show removal
4. Show the manifest.json and skills.json changes as diffs
5. Print summary: "Dry run complete. N files would be written, M modified, K deleted."
6. Post-install hooks and dependency installs should be listed but NOT executed

Return the complete modified script.
