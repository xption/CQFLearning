#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Result.md 修复脚本
根据 Phase 4 修复方案执行所有修改
"""

import re

def fix_result_md():
    # 读取文件
    with open('Result.md', 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    fixes_count = 0

    print("Starting to fix Result.md...")
    print("=" * 60)

    # P1-1: 修正 Alpha 值
    if '0624' in content:
        content = content.replace('\\alpha=0\\.0624', '\\alpha=-0.6786')
        content = content.replace('= 0\\.0624 \\+', '= -0.6786 \\+')
        fixes_count += 1
        print("[OK] P1-1: Alpha value fixed (0.0624 -> -0.6786)")

    # P1-2: 修正 OU Sigma
    if '0126' in content:
        # 查找表格中的日波动率
        content = re.sub(r'\|日波动率σ\|0\\.0126\|', '|日波动率σ|0.003812|', content)
        fixes_count += 1
        print("[OK] P1-2: OU Sigma fixed (0.0126 -> 0.003812)")

    # P1-3: 修正动态策略收益率
    if '-0\\.61%' in content or '-0\\.53%' in content:
        content = content.replace('-0\\.61%', '+0.17%')
        content = content.replace('-0\\.53%', '+0.17%')
        fixes_count += 1
        print("[OK] P1-3: Dynamic strategy return fixed (-0.61%/-0.53% -> +0.17%)")

    # P1-4: 修正动态策略最大回撤
    if '12\\.36%' in content:
        content = content.replace('12\\.36%', '1.79%')
        fixes_count += 1
        print("[OK] P1-4: Dynamic strategy drawdown fixed (12.36% -> 1.79%)")

    # P2-1: 修正平均持仓天数
    if '19\\.6个交易日' in content or '19\\.6天' in content:
        content = content.replace('19\\.6个交易日', '14.25个交易日')
        content = content.replace('19\\.6天', '14.25天')
        fixes_count += 1
        print("[OK] P2-1: Average holding days fixed (19.6 -> 14.25)")

    # 写回文件
    if content != original_content:
        with open('Result.md', 'w', encoding='utf-8') as f:
            f.write(content)
        print("=" * 60)
        print(f"Fix completed! Total {fixes_count} issues fixed")
        print("Saved to Result.md")
    else:
        print("=" * 60)
        print("No changes needed")

    return fixes_count

if __name__ == '__main__':
    fix_result_md()
