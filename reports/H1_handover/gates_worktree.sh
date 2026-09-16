#!/bin/zsh
# T2 -- the seven-strain gate battery, run IN THE T1 WORKTREE so the option under test is the
# code exercised. Every exit code printed. CANDIDAS_ROOT unset.
cd "/Users/g.yvon-durocher/Library/CloudStorage/OneDrive-UniversityofExeter/Documents/work/MICROADAPT/etcGEMs-h1"
unset CANDIDAS_ROOT
E=../etcGEMs-venv/bin/etcgem; P=../etcGEMs-venv/bin/python
echo "tree $(pwd) HEAD $(git rev-parse --short HEAD) CANDIDAS_ROOT='${CANDIDAS_ROOT}'"
$E transfer --experiment transfer_candida_unpinned --quiet > /dev/null 2>&1; echo "transfer_candida_unpinned rc=$?"
$E transfer --experiment transfer_candida --quiet > /dev/null 2>&1; echo "transfer_candida rc=$?"
$E fba --strain cauris_iRV973 --experiment candida_pool_unconstrained --temp 30 > /dev/null 2>&1; echo "fba unconstrained rc=$?"
$E fba --strain cauris_iRV973 --experiment candida_pool_binding --temp 30 > /dev/null 2>&1; echo "fba binding rc=$?"
$P reports/candida_thermal_limit/gate_table.py > /tmp/h1_gate_table.out 2>&1; echo "gate_table rc=$?"; grep -E "comparisons" /tmp/h1_gate_table.out | tail -1
$P reports/P1_parsa_port/gate.py > /tmp/h1_gate_p1.out 2>&1; echo "P1 gate rc=$?"; grep -E "comparisons" /tmp/h1_gate_p1.out | tail -1
$E tpc --strain eciML1515 > /dev/null 2>&1; echo "tpc eciML1515 rc=$?"; $E tpc --strain mmaripaludis > /dev/null 2>&1; echo "tpc mmaripaludis rc=$?"; $E tpc --strain syn6803 --experiment syn6803_ecmodel > /dev/null 2>&1; echo "tpc syn6803 rc=$?"
echo "=====git status strains/ outputs/ (byte-identity; must be empty or only untracked png)"; git status --short strains/ outputs/; echo "status rc=$?"
echo "BATTERY DONE"
