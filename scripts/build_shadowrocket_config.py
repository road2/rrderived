#!/usr/bin/env python3
"""Build a daily-updated Shadowrocket configuration from Johnshall's source."""

from __future__ import annotations

import re
import sys
from pathlib import Path


MARKER = "# BEGIN local routing patch"
GROUPS = """# BEGIN local routing patch
[Proxy Group]
AI-JP-SG-Auto = url-test,policy-regex-filter=🇯🇵|JP|Japan|日本|东京|Tokyo|大阪|Osaka|🇸🇬|SG|Singapore|新加坡,url=http://www.gstatic.com/generate_204,interval=600,tolerance=50,timeout=5
OpenAI-JP-SG-Auto = url-test,policy-regex-filter=🇯🇵|JP|Japan|日本|东京|Tokyo|大阪|Osaka|🇸🇬|SG|Singapore|新加坡,url=https://chatgpt.com,interval=600,tolerance=50,timeout=5
Gemini-JP-SG-Auto = url-test,policy-regex-filter=🇯🇵|JP|Japan|日本|东京|Tokyo|大阪|Osaka|🇸🇬|SG|Singapore|新加坡,url=https://gemini.google.com,interval=600,tolerance=50,timeout=5
HK-Auto = url-test,policy-regex-filter=🇭🇰|HK|Hong Kong|HongKong|香港,url=http://www.gstatic.com/generate_204,interval=600,tolerance=50,timeout=5
# END local routing patch

"""
RULES = """# BEGIN local routing patch
# AI and Google search homepage: only Japan/Singapore URL-test nodes.
RULE-SET,https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Shadowrocket/OpenAI/OpenAI.list,OpenAI-JP-SG-Auto
RULE-SET,https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Shadowrocket/Claude/Claude.list,AI-JP-SG-Auto
RULE-SET,https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Shadowrocket/Gemini/Gemini.list,Gemini-JP-SG-Auto
DOMAIN-SUFFIX,google.com,Gemini-JP-SG-Auto
DOMAIN-SUFFIX,google.com.hk,Gemini-JP-SG-Auto
DOMAIN-SUFFIX,googleapis.com,Gemini-JP-SG-Auto
DOMAIN-SUFFIX,gstatic.com,Gemini-JP-SG-Auto
DOMAIN-SUFFIX,googleusercontent.com,Gemini-JP-SG-Auto
DOMAIN-SUFFIX,google.ai,Gemini-JP-SG-Auto
# END local routing patch

"""


def transform(source: str) -> str:
    """Return the upstream configuration with the local routing policy applied."""
    if MARKER in source:
        raise ValueError("source already contains the local routing patch")
    if "[Rule]" not in source:
        raise ValueError("upstream configuration has no [Rule] section")

    source = source.replace("[Rule]\n", f"{GROUPS}[Rule]\n", 1)
    rule_start = source.index("[Rule]\n") + len("[Rule]\n")
    next_section = re.search(r"^\[[^\]]+\]\s*$", source[rule_start:], re.MULTILINE)
    rule_end = rule_start + next_section.start() if next_section else len(source)

    before = source[:rule_start]
    rule_section = source[rule_start:rule_end]
    after = source[rule_end:]
    rule_section = re.sub(r",(?:Proxy|PROXY)(?=,|\s*$)", ",HK-Auto", rule_section, flags=re.MULTILINE)
    return before + RULES + rule_section + after


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: build_shadowrocket_config.py INPUT.conf OUTPUT.conf", file=sys.stderr)
        return 2

    source_path, output_path = (Path(value) for value in sys.argv[1:])
    try:
        output = transform(source_path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as error:
        print(f"Build failed: {error}", file=sys.stderr)
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
