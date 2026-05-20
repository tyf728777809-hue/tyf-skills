---
name: netease-dd-share-wa-review
description: Use when auditing NetEase DD configuration shares or WA library items on df.cc.163.com, including 配置分享库审核, WA库审核, 配置/WA每日审核, 跑一下审核, or recurring review reports for pending and machine-review-failed items.
---

# 网易 DD 配置分享库 & WA 库审核

## 默认边界

- 默认只生成报告，不点击后台按钮；只有用户明确说“执行审核/直接审核/提交审核”才运行执行脚本。
- 覆盖 40 组：5 个游戏版本 × 公开/私密 × 待审核/机审失败；WA 固定 `source=用户发布`。
- 不保存、不打印账号密码、cookie、token；登录优先复用 Chrome/Playwright 会话，失效时自动尝试恢复。
- 图片审核可接入公司 AIGW：通过环境变量 `AIGW_API_KEY` 调用 `doubao-seed-2.0-mini`，不把 key 写入脚本、报告或日志。
- 输出默认写入 `E:\今天又是美好的一天\网易dd\插件审核\output\share-wa-review\<YYYYMMDD-HHMM>`。

## 快速命令

在工作目录 `E:\今天又是美好的一天\网易dd\插件审核` 执行：

```powershell
$env:ProgramFiles='C:\Program Files'; $env:LOCALAPPDATA='C:\Users\N30846\AppData\Local'; $env:SystemDrive='C:'
node C:\Users\N30846\.agents\skills\netease-dd-share-wa-review\scripts\run_review.js --mode report
```

如需搜索文件或日志，先做 `rg` 健康检查；若不可用，按 `references/rg-maintenance.md` 使用 PowerShell fallback，不要因为 `rg` 失败中断审核。

```powershell
rg --version
rg --files | Select-Object -First 10
```

明确获准执行后台审核时：

```powershell
$env:ProgramFiles='C:\Program Files'; $env:LOCALAPPDATA='C:\Users\N30846\AppData\Local'; $env:SystemDrive='C:'
node C:\Users\N30846\.agents\skills\netease-dd-share-wa-review\scripts\run_review.js --mode execute --input <report-json-path>
node C:\Users\N30846\.agents\skills\netease-dd-share-wa-review\scripts\run_review.js --mode rescan
```

如果报告里 `imageManifestCount > 0`：

- 已配置 `AIGW_API_KEY` 时，`report` 会自动生成分批模型图册并调用 `doubao-seed-2.0-mini` 审图，输出 `image_model_review.json`。
- 同时输出 `image_model_review_calls.json`，用于核对每次模型调用的 `callId`、endpoint、model、mode、覆盖图片、HTTP status、response id、耗时、结果数量和错误摘要；不得包含 API key、Authorization header 或图片 base64。
- `summary.json` 的 `imageReview.status` 为 `model_passed` 时，执行可不带 `--images-reviewed`；`model_passed` 要求图片结果数等于图片清单数、每张图都有成功调用覆盖、且无 reject/uncertain/error。
- 模型返回 `reject` 会改写关联条目为拒绝；`uncertain`、模型失败、图片不可读会改写为 `manualConfirm`，仍需人工处理。
- 模型返回 `pass` 但缺少可核查证据、或证据明显偏离魔兽/DD/WA/配置分享上下文（如误识别成其他游戏/产品），会降级为 `uncertain`。
- 单图复核超时或网络失败会自动重试 1 次；重试前会压缩为 RGB JPEG 并限制尺寸/体积，审计日志只记录压缩文件路径，不记录 base64 或 Authorization。
- 透明图不再一律单图复核；只有图册证据不足、疑似二维码/联系方式/小字/水印/广告/引流、机审失败、长图/小图、GIF/WebP 等场景才进入单图复核。
- 如果同目录已有完整 `image_model_review.json` 与 `image_model_review_calls.json`，且覆盖当前图片清单，`report` 会 resume，不重复调用 AIGW。
- 未配置 `AIGW_API_KEY` 或模型未全量通过时，必须先查看同目录 `contact_sheet_visual.png`；未带 `--images-reviewed` 时脚本会拒绝执行。

可选环境变量：

```powershell
$env:AIGW_API_KEY='<your-aigw-api-key>'
$env:AIGW_BASE_URL='https://aigw.ds.163.com'
$env:AIGW_IMAGE_REVIEW_MODEL='doubao-seed-2.0-mini'
$env:AIGW_IMAGE_REVIEW_BATCH_SIZE='8'
```

默认调用 `https://aigw.ds.163.com/v1/chat/completions`；如网关调整，可用 `AIGW_IMAGE_REVIEW_URL` 覆盖完整地址。
`report` 会在终端打印阶段进度：扫描、下载图片、图册审核、单图复核、写报告。

如用户明确改判某些 SN 为通过，执行时使用 `--approve-id`，多个 SN 用英文逗号分隔；脚本会保留原始 `summary.json`，另写 `summary.execute.json` 后提交。

```powershell
node C:\Users\N30846\.agents\skills\netease-dd-share-wa-review\scripts\run_review.js --mode execute --input <report-json-path> --images-reviewed --approve-id <sn1>,<sn2>
```

如用户明确改判某些 SN 为“转私密后通过”，执行时使用 `--transfer-private-id`，多个 SN 用英文逗号分隔。

```powershell
node C:\Users\N30846\.agents\skills\netease-dd-share-wa-review\scripts\run_review.js --mode execute --input <report-json-path> --images-reviewed --transfer-private-id <sn1>,<sn2>
```

如用户明确改判某些 SN 为拒绝或继续人工确认，执行时可使用 `--reject-id` 或 `--manual-confirm-id`。如改判项较多，也可以写 JSON 文件：

```json
{"approveIds":["<sn1>"],"transferPrivateIds":["<sn2>"],"rejectIds":["<sn3>"],"manualConfirmIds":["<sn4>"]}
```

```powershell
node C:\Users\N30846\.agents\skills\netease-dd-share-wa-review\scripts\run_review.js --mode execute --input <report-json-path> --images-reviewed --override <override-json-path>
```

改判执行会生成 `override_preview.json` 和 `override_learnings.json`。执行前核对其中 SN、标题、原动作和新动作；若 SN 不在输入报告中，脚本会失败且不提交。后续报告命中相似历史改判时只标记 `reviewed_by_prior_override` 作为参考，不直接覆盖当前硬风险结论。

明确要求自动执行闭环时，可使用 `cycle`：它会执行当前可执行项、复扫、继续执行复扫中仍可执行的项，直到清空、只剩人工确认或出现失败，并输出 `cycle_summary.json`。

```powershell
node C:\Users\N30846\.agents\skills\netease-dd-share-wa-review\scripts\run_review.js --mode cycle --input <report-json-path> --override <override-json-path> --images-reviewed
```

## 工作流

1. 先读 `references/review-policy.md` 确认最新口径。
2. 运行 `report`，检查 `summary.json`、`review_report.md`、`scan_raw.json`、`manual_confirm.json`。如有图片，检查 `image_model_review.json` 与 `image_model_review_calls.json`；模型审图未全量通过时，必须查看 `contact_sheet_visual.png`。
3. 给用户汇总新增待审、建议通过/拒绝/转私密/人工确认数量。
4. 只有用户明确要求执行时，运行 `execute --input summary.json`；如果图片模型未全量通过，需先人工看图并追加 `--images-reviewed`。若用户改判，附加 `--approve-id`、`--transfer-private-id`、`--reject-id`、`--manual-confirm-id` 或 `--override`，并先核对 `override_preview.json`。
5. 执行后必须 `rescan`，并汇总 `execute_result.json`、每轮 byAction、失败数、跳过数和复扫剩余数；若复扫仍有可执行项，即使同时存在人工确认项，也继续执行可执行项并再次复扫。可用 `--mode cycle` 自动完成这段闭环；复扫目录如果有图片且模型审图未全量通过，必须重新查看该目录的 `contact_sheet_visual.png`，再带 `--images-reviewed` 执行，直到只剩人工确认、清空或出现失败。
6. 定时任务只使用 `report`，不自动执行后台审核。

## 结果判断

- `autoPass`：字段有意义、无违规，图片/素材无明显问题。
- 公开配置分享如果名称、描述、介绍详细且内容有意义，没有配置分享日志/更新日志也可 `autoPass`。
- `transferPrivateThenPass`：公开分享内容简单且有自用/专用/专供/朋友分享/给朋友分享/分享给朋友/给朋友用/好友分享意图时转私密后通过；配置分享即使写了自用，只要有具体安装、功能、适用版本、插件组成或更新说明，也可 `autoPass`。
- WA 库口径保持：名称、简介、字符串内容需有具体内容；字符串详情可简略或没有。
- 明确“分享出来/供大家/给别人用”等公开外向分享，且说明充分，仍可 `autoPass`。
- `reject`：纯占位、明显无意义、无自用说明，或违规内容。
- `manualConfirm`：图片/素材无法判断、接口异常、机审失败图文未能完整识别、边界口径不稳。

## 登录和凭据

- Chrome 会话名：`df-cms-chrome-default`。
- 认证状态保存：`output\share-wa-review\df-cms-auth-state.json`。
- 自动登录优先读取环境变量 `DF_CMS_USER` / `DF_CMS_PASS`；缺失时尝试 Windows Credential Manager 目标名 `df-cms-review/tongyifeng`。
- 如果登录态失效且无法读取凭据，报告“需配置凭据或人工登录”，不要要求用户在聊天中重复发送密码。
- 不要在命令示例、日志、临时脚本或报告中写入真实密码、cookie 或 token。

## 本地工具维护

- `rg` 长期修复与 fallback：见 `references/rg-maintenance.md`。
- `execute` 支持 UTF-8 BOM 的 JSON；PowerShell 生成的执行副本不应再触发 `Unexpected token '﻿'`。
- `execute` 保留 sidecar input JSON 供审计；生成的 Playwright 脚本不得使用 `require` 或动态 `import`，也不得嵌入明文 SN/记录内容，避免 runner 不兼容和日志暴露。
