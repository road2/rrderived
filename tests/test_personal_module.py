import re
import unittest
from pathlib import Path


ROOT = Path(__file__).parents[1]
MODULE = ROOT / "modules" / "personal.module"


class PersonalModuleTests(unittest.TestCase):
    def test_module_is_renamed_and_self_contained(self):
        self.assertTrue(MODULE.is_file())
        self.assertFalse((ROOT / "modules" / "personal-direct.module").exists())

        content = MODULE.read_text(encoding="utf-8")
        self.assertIn("[Proxy Group]", content)
        self.assertIn("[Rule]", content)

        defined_groups = set(
            re.findall(r"^(Personal-[^=\n]+?)\s*=", content, flags=re.MULTILINE)
        )
        referenced_groups = set(
            re.findall(r",(Personal-[^,\n]+)(?:,|$)", content, flags=re.MULTILINE)
        )
        self.assertFalse(referenced_groups - defined_groups)

    def test_specialized_rules_precede_direct_overrides(self):
        content = MODULE.read_text(encoding="utf-8")
        self.assertLess(
            content.index("DOMAIN-SUFFIX,yfsp.tv,Personal-YFSP"),
            content.index("DOMAIN-SUFFIX,qq.com,DIRECT"),
        )

    def test_ai_policy_falls_back_to_builtin_proxy(self):
        content = MODULE.read_text(encoding="utf-8")
        self.assertIn(
            "Personal-AI = fallback,Personal-JP-SG-Auto,PROXY,",
            content,
        )
        self.assertIn("OpenAI/OpenAI.list,Personal-AI", content)
        self.assertNotIn("OpenAI/OpenAI.list,Personal-JP-SG-Auto", content)

    def test_module_contains_no_home_network_or_credentials(self):
        content = MODULE.read_text(encoding="utf-8")
        self.assertNotRegex(content, r"192\.168\.5\.")
        self.assertNotRegex(content, r"(?im)^\s*(secret|password|token)\s*[:=]")


if __name__ == "__main__":
    unittest.main()
