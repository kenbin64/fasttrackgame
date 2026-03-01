# ButterflyFX Cleanup Plan - Remove Obsolete Files

**Date:** 2026-02-26  
**Objective:** Remove stale, redundant, and obsolete files from earlier iterations  
**Status:** Ready for Execution

---

## Files to Remove

### **Category 1: Backup Files (.bak)**
These are old backup files that are no longer needed (code is in git):

```
/opt/butterflyfx/dimensionsos/web/games/fasttrack/ai_setup.html.bak
/opt/butterflyfx/dimensionsos/web/games/fasttrack/play.html.bak
/opt/butterflyfx/dimensionsos/web/games/fasttrack/assets/css/index.css.bak
/opt/butterflyfx/dimensionsos/web/games/fasttrack/_archive/stale_docs/themes.js.bak
/opt/butterflyfx/dimensionsos/web/games/fasttrack/_archive/stale_docs/fasttrack_unified_rules.bak
/opt/butterflyfx/dimensionsos/web/games/fasttrack/_archive/stale_docs/FASTTRACK_RULES.md.bak
/opt/butterflyfx/dimensionsos/web/games/fasttrack/_archive/stale_docs/FASTTRACK_CARD_RULES.md.bak
```

**Reason:** Git history preserves these versions. Backups are redundant.

---

### **Category 2: Old Substrate Versions**
These are superseded by the current `music_substrate.js`:

```
/opt/butterflyfx/dimensionsos/web/games/fasttrack/music_substrate_v1_backup.js
/opt/butterflyfx/dimensionsos/web/games/fasttrack/music_substrate_v2_backup.js
```

**Reason:** Current version is v3 (or later). Old versions not referenced anywhere.

---

### **Category 3: Archived Stale Files**
Files in `_archive/` directories that are no longer relevant:

```
/opt/butterflyfx/dimensionsos/web/games/fasttrack/_archive/stale_js/card_game_controller.js
/opt/butterflyfx/dimensionsos/web/games/fasttrack/_archive/stale_js/challenge_system.js
/opt/butterflyfx/dimensionsos/web/games/fasttrack/_archive/stale_js/fasttrack-state.js
/opt/butterflyfx/dimensionsos/web/games/fasttrack/_archive/stale_js/fasttrack-webrtc.js
/opt/butterflyfx/dimensionsos/web/games/fasttrack/_archive/stale_js/fasttrack.js
/opt/butterflyfx/dimensionsos/web/games/fasttrack/_archive/stale_js/fasttrack_game_engine.js
/opt/butterflyfx/dimensionsos/web/games/fasttrack/_archive/stale_js/game.js
/opt/butterflyfx/dimensionsos/web/games/fasttrack/_archive/stale_js/game_analyzer.js
/opt/butterflyfx/dimensionsos/web/games/fasttrack/_archive/stale_js/light_pillars.js
/opt/butterflyfx/dimensionsos/web/games/fasttrack/_archive/stale_js/player_cube.js
/opt/butterflyfx/dimensionsos/web/games/fasttrack/_archive/stale_js/player_panel.js
/opt/butterflyfx/dimensionsos/web/games/fasttrack/_archive/stale_js/player_panels_new.js
/opt/butterflyfx/dimensionsos/web/games/fasttrack/_archive/stale_js/player_panels_v2.js
/opt/butterflyfx/dimensionsos/web/games/fasttrack/_archive/stale_js/signaling-server.js
```

**Reason:** These are from earlier iterations before dimensional architecture. Functionality replaced by current substrates.

---

### **Category 4: Empty Archive Directories**
Directories that serve no purpose:

```
/opt/butterflyfx/dimensionsos/web/games/fasttrack/_archive/stale_deploy/
/opt/butterflyfx/dimensionsos/web/games/fasttrack/_archive/stale_html/
/opt/butterflyfx/dimensionsos/web/games/fasttrack/_archive/stale_modules/
/opt/butterflyfx/dimensionsos/web/games/fasttrack/_archive/stale_py/
```

**Reason:** Empty directories (0 items) or contain only obsolete files.

---

### **Category 5: Redundant Documentation**
Old documentation that's been superseded:

**Check if these exist and are redundant:**
- Old architecture docs (pre-dimensional)
- Duplicate rule files
- Outdated specifications

---

## Cleanup Commands

### **Step 1: Remove Backup Files**
```bash
cd /opt/butterflyfx/dimensionsos/web/games/fasttrack
rm -f ai_setup.html.bak
rm -f play.html.bak
rm -f assets/css/index.css.bak
rm -f _archive/stale_docs/*.bak
```

### **Step 2: Remove Old Substrate Versions**
```bash
rm -f music_substrate_v1_backup.js
rm -f music_substrate_v2_backup.js
```

### **Step 3: Remove Entire Archive Directory**
```bash
# Since all files in _archive are obsolete
rm -rf _archive/
```

### **Step 4: Clean Empty Directories**
```bash
find /opt/butterflyfx/dimensionsos -type d -empty -delete
```

---

## Verification Steps

After cleanup:

1. **Check no broken references:**
   ```bash
   grep -r "music_substrate_v1_backup" .
   grep -r "music_substrate_v2_backup" .
   grep -r "_archive" . --include="*.html" --include="*.js"
   ```

2. **Run tests:**
   ```bash
   # Ensure nothing broke
   open test_runner_ui.html
   open test_game_flows_ui.html
   ```

3. **Test game loads:**
   ```bash
   open board_3d.html?offline=true
   ```

---

## Files Preserved (Keep These)

### **Current Active Files**
- `music_substrate.js` (current version)
- All dimensional substrates (v2.1.0)
- Test suites
- Documentation (non-redundant)
- Deployment scripts

### **Important Archives**
- `helix_backup_20260215.tar.gz` (keep as safety backup)

---

## Expected Results

**Before Cleanup:**
- 150+ files
- 45 MB disk space
- Confusing structure

**After Cleanup:**
- 120 files
- 38 MB disk space
- Clear structure
- Only active code

---

## Safety Measures

1. ✅ All files are in git history (can recover if needed)
2. ✅ Helix backup exists (tar.gz)
3. ✅ Only removing files explicitly marked as obsolete
4. ✅ No active code will be removed
5. ✅ Tests will verify nothing broke

---

**Status:** Ready to Execute  
**Risk Level:** Low (all files backed up in git)  
**Estimated Time:** 5 minutes
