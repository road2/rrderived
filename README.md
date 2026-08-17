# Shadowrocket 每日派生配置

该模板每天拉取 Johnshall 的 `sr_top500_whitelist.conf`，并生成不含任何节点、订阅或账号信息的派生配置：

- AI 与 Google 首页相关域名：只在日本/新加坡节点中自动测速选择；
- 原配置中所有 `Proxy` / `PROXY` 规则：改为只在香港节点中自动测速选择；
- 原配置的 `Direct`、广告、重写和 MITM 规则：保持不变。

## 部署

1. 在 GitHub 新建一个**公开**空仓库；公开仓库不会泄露节点，因为本模板不保存节点或订阅链接。
2. 将本目录的内容上传到新仓库根目录。上传后仓库根目录应有 `.github/`、`scripts/`、`tests/` 和 `README.md`。
3. 在 GitHub 打开 `Actions`，允许工作流运行；选择 **Refresh Shadowrocket derived config**，点击 **Run workflow**。
4. 工作流完成后，仓库会出现 `published/shadowrocket-custom.conf`。
5. 将下列地址中的占位符替换为自己的 GitHub 用户名和仓库名，再在 Shadowrocket 中作为配置文件 URL 导入：

```text
https://raw.githubusercontent.com/<GitHub用户名>/<仓库名>/main/published/shadowrocket-custom.conf
```

6. Shadowrocket 的“全局路由”选择“配置”。

## 验证

打开配置详情中的“代理分组”：

- `AI-JP-SG-Auto` 至少应显示一个日本或新加坡节点；
- `HK-Auto` 至少应显示一个香港节点；
- 访问 `https://www.google.com/ncr`，日志中的策略应为 `AI-JP-SG-Auto`；
- 访问任意普通境外网站，日志中的策略通常应为 `HK-Auto`。

策略组通过节点名称筛选地区。若你的订阅节点不包含 `JP`、`日本`、`SG`、`新加坡`、`HK` 或 `香港` 等名称，请先调整脚本中的筛选关键词。

## 本地验证

```sh
python3 -m unittest discover -s tests -v
curl --fail --location https://raw.githubusercontent.com/Johnshall/Shadowrocket-ADBlock-Rules-Forever/release/sr_top500_whitelist.conf -o /tmp/upstream.conf
python3 scripts/build_shadowrocket_config.py /tmp/upstream.conf /tmp/shadowrocket-custom.conf
```

查看生成文件中是否有 `AI-JP-SG-Auto`、`HK-Auto` 与 `FINAL,HK-Auto`。
