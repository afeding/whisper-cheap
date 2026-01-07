# Whisper Cheap Security - Remediation Checklist

**Project:** Whisper Cheap (Windows STT Application)
**Audit Date:** January 6, 2026
**Status:** Pre-Release Security Fixes Required

---

## Critical Issues (MUST FIX BEFORE RELEASE)

### Issue 1: Exposed OpenRouter API Key
- **Severity:** CRITICAL
- **File:** `config.json:29`
- **Effort:** 30 minutes

- [ ] **Step 1:** Rotate API key on OpenRouter account
  - Login to openrouter.ai
  - Delete or revoke the exposed key
  - Generate new API key
  - Note: Old key is `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`

- [ ] **Step 2:** Update config.json
  ```json
  "post_processing": {
    "enabled": false,
    "openrouter_api_key": "",  // Empty string instead of key
    ...
  }
  ```

- [ ] **Step 3:** Modify `src/main.py` (around line 525)
  - Read API key from environment variable `OPENROUTER_API_KEY`
  - Fall back to config.json if env var not set
  - Reference: See `SECURITY_FIXES.md` → Fix 1

- [ ] **Step 4:** Update README.md
  - Add section: "Using OpenRouter LLM Post-Processing"
  - Document how to set environment variable
  - Add to .gitignore: `config.json`

- [ ] **Step 5:** Verify
  ```bash
  # Ensure no API keys in repo
  git log -p --all -S "sk-or-v1" | head -5
  # Should show nothing (or only historical commits to redact)
  ```

- [ ] **Step 6:** Optional - Clean git history (only if repo not public yet)
  ```bash
  git filter-branch --force --index-filter \
    "git rm --cached --ignore-unmatch config.json" \
    --prune-empty --tag-name-filter cat -- --all
  git push origin --force --all
  ```

---

### Issue 2: Path Traversal Vulnerability
- **Severity:** CRITICAL
- **Files:** `src/ui/web_settings/api.py` (lines 386, 407, 429, 459)
- **Effort:** 2-3 hours

- [ ] **Step 1:** Create path validation utility
  - Create: `src/utils/path_validation.py`
  - Implement: `validate_filename()`, `safe_path_join()`, `validate_config_path()`
  - Reference: See `SECURITY_FIXES.md` → Fix 2

- [ ] **Step 2:** Update `SettingsAPI.get_history()`
  - Add filename validation
  - Use `safe_path_join()` for audio paths
  - Add path containment checks

- [ ] **Step 3:** Update `SettingsAPI.open_folder()`
  - Validate folder_type parameter
  - Use `validate_config_path()` for app_data
  - Only allow specific folder types

- [ ] **Step 4:** Update `SettingsAPI.play_audio()`
  - Only allow .wav files
  - Verify path within recordings_dir
  - Use subprocess instead of os.startfile()

- [ ] **Step 5:** Test path traversal scenarios
  ```python
  # Should be blocked:
  - "../etc/passwd"
  - "../../windows/system32"
  - "file/../traversal"
  - "C:\\evil.exe"
  - "\\\\unc\\path"
  ```

- [ ] **Step 6:** Run security tests
  ```bash
  pytest tests/test_security_fixes.py::TestPathValidation -v
  ```

---

### Issue 3: SQL Injection Risk
- **Severity:** CRITICAL
- **File:** `src/managers/history.py:88`
- **Effort:** 1 hour

- [ ] **Step 1:** Update `get_all()` method
  - Replace f-string SQL with parameterized queries
  - Use `?` placeholders for all variables
  - Pass values as tuple to `.execute()`

- [ ] **Step 2:** Add bounds validation
  - Limit: 0 < limit <= 1000
  - Offset: >= 0

- [ ] **Step 3:** Test with malicious inputs
  ```python
  # Should not cause injection:
  - limit=10 UNION SELECT ... --
  - limit=999999999
  - limit="string"
  ```

- [ ] **Step 4:** Run regression tests
  ```bash
  pytest tests/test_history.py -v
  ```

---

## High Issues (Fix Within 1 Week)

### Issue 4: Missing Update Verification
- **Severity:** HIGH
- **File:** `src/managers/updater.py:343-382`
- **Effort:** 2 hours

- [ ] **Step 1:** Make SHA256 verification mandatory
  - Remove fallback for missing SHA256
  - Raise error if hash not available
  - Reference: See `SECURITY_FIXES.md` → Fix 4

- [ ] **Step 2:** Prevent redirects in download
  - Set `allow_redirects=False` in requests.get()
  - Check for HTTP 3xx responses
  - Raise error if redirect detected

- [ ] **Step 3:** Implement update signature verification (Windows)
  - Create `_verify_installer_signature()` method
  - Check authenticode signature
  - Verify signed by known publisher

- [ ] **Step 4:** Test update verification
  ```bash
  # Simulate missing SHA256
  # Simulate corrupted download
  # Simulate redirect attack
  pytest tests/test_updater_security.py -v
  ```

- [ ] **Step 5:** Verify no bypasses exist
  ```bash
  # All code paths must verify signature
  grep -n "install_update\|download_update" src/managers/updater.py
  # Should see verification before installation
  ```

---

### Issue 5: Configuration Injection / No Input Validation
- **Severity:** HIGH
- **File:** `src/main.py:314-356`
- **Effort:** 1.5 hours

- [ ] **Step 1:** Create config validation utility
  - Create: `src/utils/config_validation.py`
  - Implement: `ConfigValidator` class
  - Add: `validate_audio_config()`, `validate_prompt_template()`, `validate_llm_model()`
  - Reference: See `SECURITY_FIXES.md` → Fix 3

- [ ] **Step 2:** Update RecordingConfig
  - Add bounds to all parameters
  - Validate in __post_init__() method
  - Raise ValueError on invalid config

- [ ] **Step 3:** Update main.py to use validation
  - Replace direct config access with validated versions
  - Add fallback to safe defaults
  - Log warnings for invalid values

- [ ] **Step 4:** Test invalid configurations
  ```python
  # Should be rejected or corrected:
  - sample_rate: -1, 0, 1, 1000000
  - channels: 0, 3, 100
  - chunk_size: -1, 0, 1GB
  - vad_threshold: -1, 2, "string"
  - prompt_template: missing ${output}, >5000 chars
  - device_id: -2, 1000, "invalid"
  ```

- [ ] **Step 5:** Run validation tests
  ```bash
  pytest tests/test_security_fixes.py::TestConfigValidation -v
  ```

---

## Medium Issues (Plan for Next Release)

### Issue 6: API Key Exposed in Logs
- **Severity:** MEDIUM
- **Files:** `src/main.py:872`, `src/ui/web_settings/api.py:182`
- **Effort:** 1 hour

- [ ] **Step 1:** Create security utility
  - Create: `src/utils/security.py`
  - Implement: `mask_api_key()`, `mask_sensitive_config()`
  - Reference: See `SECURITY_FIXES.md` → Fix 5

- [ ] **Step 2:** Update logging calls
  - Replace full API keys with masked versions
  - Update exception handling to not log secrets

- [ ] **Step 3:** Test that logs don't contain keys
  ```bash
  # Verify logs never contain full API key
  grep -r "sk-or-v1-[a-f0-9]" logs/
  # Should return nothing
  ```

---

## Low Issues (Recommended)

### Issue 7: Clipboard Content Retained on Crash
- **Severity:** LOW
- **File:** `src/utils/paste.py:107-114`
- **Effort:** 30 minutes

- [ ] **Step 1:** Add try/finally to paste_text()
  - Ensure clipboard always restored
  - Wrap critical section in try block
  - Restore in finally block
  - Reference: See `SECURITY_FIXES.md` → Fix 6

- [ ] **Step 2:** Test clipboard safety
  ```python
  # Verify original content restored even if exception
  pytest tests/test_security_fixes.py::test_clipboard_restored_on_exception -v
  ```

---

## Testing & Verification

### Create Security Test Suite
- [ ] Create: `tests/test_security_fixes.py`
- [ ] Run all tests:
  ```bash
  pytest tests/test_security_fixes.py -v --tb=short
  ```
- [ ] Verify all tests pass:
  - Path traversal tests
  - Configuration validation tests
  - API key masking tests
  - Clipboard safety tests
  - SQL injection prevention tests
  - Update verification tests

### Manual Testing
- [ ] Test recording workflow (record → transcribe → paste)
- [ ] Test settings window (open → modify config → save)
- [ ] Test LLM post-processing (if enabled)
- [ ] Test update checking (verify SHA256 validation)
- [ ] Test with malicious config.json (should handle gracefully)

### Integration Testing
- [ ] Run full application through normal workflow
- [ ] Check logs for any exposed secrets:
  ```bash
  grep -i "api.key\|openrouter\|sk-or" logs/app.log
  # Should return nothing or only masked values
  ```

---

## Code Review Checklist

- [ ] **Path Validation**
  - No ".." in paths
  - No "/" or "\" in filenames
  - All paths validated before use
  - Containment checks in place

- [ ] **Input Validation**
  - All config values bounded
  - Invalid values use safe defaults
  - Type checking before use
  - Length limits enforced

- [ ] **Secret Management**
  - No API keys in config.json
  - Environment variables used
  - Logs don't contain keys
  - Masking function applied

- [ ] **Update Security**
  - SHA256 verification mandatory
  - Signature verification added
  - Redirects prevented
  - Error handling comprehensive

- [ ] **Clipboard Safety**
  - Try/finally wraps critical section
  - Original content restored on error
  - No transcriptions left behind

---

## Pre-Release Checklist

### Before Tagging Release
- [ ] All CRITICAL fixes implemented & tested
- [ ] All HIGH fixes implemented & tested
- [ ] Security test suite passes (100%)
- [ ] Manual testing completed
- [ ] Code review passed
- [ ] No hardcoded secrets in repo
- [ ] No debug logging enabled
- [ ] Documentation updated
- [ ] README.md updated with security notes

### Before Publishing to Users
- [ ] Security audit report reviewed
- [ ] All vulnerabilities addressed
- [ ] Update system verification working
- [ ] ZIP/installer tested on clean Windows VM
- [ ] No crashes or hangs during normal use
- [ ] Performance acceptable
- [ ] Error handling covers edge cases

---

## Documentation Updates

- [ ] **README.md**
  - Add "Security" section
  - Document LLM setup with env variables
  - Link to security policy

- [ ] **config.json (template)**
  - Remove hardcoded API key
  - Add comments about environment variables
  - Document safe configuration ranges

- [ ] **CONTRIBUTING.md** (if exists)
  - Add security guidelines
  - Document threat model
  - Reference audit reports

---

## Sign-Off

- [ ] **Security Audit:** Completed (January 6, 2026)
- [ ] **Remediation:** In Progress
- [ ] **Testing:** Pending
- [ ] **Code Review:** Pending
- [ ] **Release Approval:** Pending

**Estimated Completion:** 6-9 hours of development + 2-3 hours testing

---

## Reference Documents

- `SECURITY_AUDIT_REPORT.md` - Full audit findings
- `SECURITY_FIXES.md` - Exact code patches
- `SECURITY_SUMMARY.txt` - Executive summary

**DO NOT RELEASE without completing CRITICAL and HIGH sections.**
