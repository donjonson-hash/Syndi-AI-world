# Legacy Cleanup Guide

## Problem
Duplicate brain modules in core/:
- brain_core.py (5.4KB) — deprecated
- brain_integration.py (4.5KB) — deprecated
- brain_llm_integration.py (11.2KB) — deprecated
- brain_agents_freelance_integrated.py (11.2KB) — deprecated
- brain_unified.py (22.7KB) — CURRENT

## Steps
1. Check imports: `grep -r "from brain_" core/ --include="*.py"`
2. Backup: `cp -r core/ core-backup-$(date +%Y%m%d)`
3. Remove duplicates after redirecting imports to brain_unified
4. Test: `python -c "import brain_unified; print('OK')"`

## Files to delete (after verification)
- brain_core.py
- brain_integration.py
- brain_llm_integration.py
- brain_agents_freelance_integrated.py

## Keep
- brain_unified.py (22.7KB)
