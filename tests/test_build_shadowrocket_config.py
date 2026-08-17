import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).parents[1] / "scripts" / "build_shadowrocket_config.py"
WORKFLOW = Path(__file__).parents[1] / ".github" / "workflows" / "publish.yml"
SPEC = importlib.util.spec_from_file_location("builder", SCRIPT)
builder = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(builder)


class TransformTests(unittest.TestCase):
    def test_adds_groups_and_routes_proxy_policies(self):
        source = """[General]\nfoo = bar\n[Rule]\nDOMAIN-SUFFIX,t.me,Proxy\nDOMAIN-SUFFIX,qq.com,Direct\nFINAL,PROXY\n[URL Rewrite]\nexample 302\n"""

        result = builder.transform(source)

        self.assertIn("AI-JP-SG-Auto = url-test", result)
        self.assertIn("OpenAI-JP-SG-Auto = url-test", result)
        self.assertIn("Gemini-JP-SG-Auto = url-test", result)
        self.assertIn("HK-Auto = url-test", result)
        self.assertLess(result.index("DOMAIN-SUFFIX,google.com,Gemini-JP-SG-Auto"), result.index("DOMAIN-SUFFIX,t.me,HK-Auto"))
        self.assertIn("DOMAIN-SUFFIX,qq.com,Direct", result)
        self.assertIn("FINAL,HK-Auto", result)
        self.assertIn("[URL Rewrite]\nexample 302", result)

    def test_rejects_upstream_without_rule_section(self):
        with self.assertRaisesRegex(ValueError, r"no \[Rule\] section"):
            builder.transform("[General]\n")

    def test_rejects_already_patched_source(self):
        with self.assertRaisesRegex(ValueError, "already contains"):
            builder.transform("# BEGIN local routing patch\n[Rule]\n")

    def test_routes_chatgpt_with_the_existing_openai_rule_set(self):
        result = builder.transform("[General]\n[Rule]\nFINAL,PROXY\n")

        self.assertIn(
            "RULE-SET,https://raw.githubusercontent.com/blackmatrix7/ios_rule_script/master/rule/Shadowrocket/OpenAI/OpenAI.list,OpenAI-JP-SG-Auto",
            result,
        )
        self.assertNotIn("/Shadowrocket/AI/AI.list", result)

    def test_workflow_stages_generated_file_before_diff_check(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")
        self.assertLess(
            workflow.index("git add published/shadowrocket-custom.conf"),
            workflow.index("git diff --cached --quiet"),
        )
