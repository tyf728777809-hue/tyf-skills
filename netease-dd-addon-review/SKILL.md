---
name: netease-dd-addon-review
description: 网易 DD / 魔兽插件审核、自动下载、后台编辑信息审核、人工确认后后台通过/拒绝、飞书总台账同步工作流。Use when the user asks to audit NetEase DD addons, 自动下载待审插件, 有爱插件库审核, 魔兽插件审核, 网易DD插件审核, 审核今天插件, 跑今日批次, 审核 MMDD 批次, addon zip review, 后台编辑信息审核, 确认后通过拒绝, 同步飞书台账, 图片多模态审核, 外链复审, or update the long-running NetEase DD addon review ledger.
---

# 网易 DD 插件审核

## 固定边界

- 默认自动获取待审清单、下载 zip、审核 zip 内容和后台编辑信息，生成建议结论。
- 不抽样；检查有爱插件库 5 个适配游戏版本 × `待审核/init`、`机审失败/niv_failed` 全部组合和分页。
- 所有审核必须由 `download_manifest.json` 限定本轮 zip；同一天目录可复用，但不得让历史 zip 混入本轮。
- 所有插件包图片和后台编辑图片都必须进入 `image_review_queue`；配置 `AIGW_API_KEY` 时自动调用 `doubao-seed-2.0-mini` 做图片模型审核，未配置时回退人工/原生多模态审图。
- “执行本地审核”是导出/下载/审核/生成 `backend_decisions`；“执行后台处置”是提交已确认的 `pass/reject`。
- 后台通过/拒绝必须读取 `confirmed_action=pass/reject`；不要把 `suggested_action` 当确认，除非用户明确说“按建议执行”。
- 不在回复、文档或日志中暴露密码、cookie、token；Playwright state 只本机使用。
- 默认不启用音频 ASR；除非用户明确要求，不加 `--audio-asr`。
- 飞书使用长期 Base `网易DD插件审核总台账`；同步前必须确认用户允许写入飞书。

## 入口目录

- 审核工程根目录：`E:\今天又是美好的一天\网易dd\插件审核`
- 有爱插件下载根目录：`E:\今天又是美好的一天\网易dd\插件审核\有爱插件审核`
- 每日批次目录：`<有爱插件下载根目录>\MMDD`，例如 `0512`；同一天多次下载复用同一目录。
- 登录态：`<审核工程根目录>\.playwright-cli\netease-dd-df-state.json`
- 规范文档：`E:\今天又是美好的一天\网易dd\插件审核\审核规范.md`

## 实战运行清单

1. 预检登录态：如后台跳登录页，用 Playwright 让用户登录并保存 `state-save .playwright-cli\netease-dd-df-state.json`。
   - 导出或探测 `/addon-api/list` 时必须确认接口业务返回正常：`code=0` 且不是 `用户未登录`。任何 `code!=0`、`用户未登录`、无权限、非 JSON 或登录页响应都必须停止，让用户重新登录并保存 state。
   - “无待审”只有在 5 个游戏版本 × `待审核/init`、`机审失败/niv_failed` 10 个组合都正常返回，且总数均为 0 时才可信。
2. 端到端本地审核优先使用封装脚本：
   ```cmd
   py -3 tools\run_end_to_end_review.py --batch MMDD
   ```
3. 如需拆分执行，必须按顺序运行：
   ```cmd
   py -3 tools\export_pending_addons.py --batch MMDD
   py -3 tools\download_addon_zips.py --manifest 有爱插件审核\MMDD\addon_download_manifest.json --output-dir 有爱插件审核\MMDD --report-name download_manifest.json
   py -3 tools\run_daily_audit.py --root 有爱插件审核 --batch MMDD --zip-manifest 有爱插件审核\MMDD\download_manifest.json
   ```
4. 下载后校验：`downloaded == addon_download_manifest.json 中有 download_url 的数量`。
5. 审核后校验：`batch_summary.插件总数 == download_manifest.json 中 status=downloaded 的数量`。
6. 检查 `_audit_output_v4-final`：`batch_summary`、`plugin_reviews`、`evidence_details`、`image_review_manifest`、`image_review_queue`、`image_multimodal_review`、`image_model_review`、`image_model_review_calls`、`external_link_review`、`attention_notes`、`backend_decisions`。
7. 若 `image_review_queue` 非空且无 `AIGW_API_KEY`，打开 contact sheet/单图预览逐图审核，并把结论写回 `image_multimodal_review.csv/json`；已启用模型时必须核对 `image_model_review.json` 与 `image_model_review_calls.json`。
8. 图片结论写回后重跑本地审核时，必须读取当前 `batch_summary.json` 的 `批次ID`，并固定同一个批次 ID，避免新轮次导致 `image_id` 失效：
   ```cmd
   py -3 tools\run_daily_audit.py --root 有爱插件审核 --batch MMDD --zip-manifest 有爱插件审核\MMDD\download_manifest.json --batch-id <原批次ID>
   ```
9. 生成 Markdown 审核报告：`有爱插件审核\MMDD\_audit_output_v4-final\审核报告.md`。
10. 汇总给用户：3-5 行摘要、审核报告路径、待确认处置表路径；后台已提交时还要给提交日志路径和复查清零结果。

## 红线停止条件

- `downloaded` 与有效清单数不一致：停止，不运行审核。
- 导出接口返回 `code!=0`、`用户未登录`、无权限、非 JSON、登录页或 10 组合不完整：停止，不允许报告“无待审”。
- `zip_count=0` 但 `downloaded>0`：停止，优先检查 `--zip-manifest` 路径解析。
- `zip_count` 与 `downloaded` 不一致：停止，不允许继续后台处置。
- `download_manifest.json` 丢失 `backend_text` 或 `backend_image_urls`：停止，重新下载报告或修字段透传。
- 后台编辑字段数全为 0 且清单中有后台字段：停止，说明编辑信息未纳入审核。
- `image_review_queue` 非空但 `image_multimodal_review` 未全部 `review_status=reviewed`：停止，含图片插件不得建议通过；未配置 AIGW 时这是正常人工门禁。
- contact sheet 缺格、图片无法打开、GIF/WebP/长图/小图或模型证据不足未单图复核：停止，对应插件进入人工复审；透明图不再单独构成单图复核条件。
- 任何 `download_failed`、`not_zip`、`zero_size`：停止，列失败项重试。
- 提交后台后 10 组合复查未清零：停止，列未清零组合和后台 ID。

## 后台编辑信息审核

- `addon_download_manifest.json` 与 `download_manifest.json` 必须保留：`backend_text`、`backend_image_urls`、`detail_url`、`download_url`。
- 审核脚本会把后台字段纳入证据：名称、描述、HTML 说明、更新说明、来源链接、logo、详情图等。
- 后台文字命中政治、色情、赌博诈骗、外挂黑灰产、账号交易、台独/分裂一个中国表达时，写入 `evidence_details` 并影响插件结论。
- 后台图片 URL 要下载到 `_review_v2\backend_images`，写入 `image_review_manifest` 与 `image_review_queue`，并进入 AIGW/人工图片审核；下载失败写 `后台图片无法下载` 证据并进入人工复审。

## AIGW 图片模型审核

- `image_review_queue.json/csv` 是图片必审队列；每个 `image_id` 必须对应一条 `image_multimodal_review` 结论。
- 审图来源包括：插件包图片、后台 logo/详情图、转换后的 PNG、带编号 contact sheet、异常图片的单图预览。
- 配置：
  ```cmd
  set AIGW_API_KEY=<your-aigw-api-key>
  set AIGW_BASE_URL=https://aigw.ds.163.com
  set AIGW_IMAGE_REVIEW_MODEL=doubao-seed-2.0-mini
  ```
- 默认 endpoint 为 `https://aigw.ds.163.com/v1/chat/completions`；如网关变化，用 `AIGW_IMAGE_REVIEW_URL` 覆盖。
- 模型按默认 8 张一批生成 `image_model_batches\model_contact_sheet_*.jpg` 初筛；`reject/uncertain`、调用失败、证据不足、小图、长图、GIF/WebP、疑似小字/二维码/联系方式/水印/广告导流会进入单图复核。
- 单图复核超时或网络失败会自动重试 1 次；重试前压缩为 RGB JPEG 并限制尺寸/体积。
- 输出 `image_model_review.json` 与 `image_model_review_calls.json`；调用审计只记录 call id、endpoint、model、mode、覆盖图片、HTTP status、response id、耗时、结果数和错误摘要，不得包含 API key、Authorization 或 base64。
- 如果同目录已有完整 `image_model_review.json` 与 `image_model_review_calls.json` 且覆盖当前 `image_review_queue`，会 resume，不重复调用 AIGW。
- 已有人工 `review_status=reviewed` 结果优先复用，不被模型覆盖；相同图片内容的历史 reviewed 结论可按 SHA1 复用，pending 不复用。
- 审图时逐格记录：`review_status`、`risk_level`、`risk_type`、`visual_description`、`evidence_summary`、`suggested_action`、`needs_recheck`。
- 高风险图片写入 `evidence_details` 并影响插件结论；不确定、模型失败、证据为空或描述跑偏写入人工复审，不允许自动通过。
- 模型全量可信 pass 时图片可放行，但文字、外链、音频、后台字段仍按原规则审核。
- 图片结论回写后重跑必须使用原 `批次ID`；不要让 `run_daily_audit.py` 自动生成新批次 ID。

## 高风险文本语境复核

- `P0/P1` 文本命中后必须查看上下文，不能只凭关键词建议拒绝。
- 游戏怪物名、任务文本、技能名、本地化字段、词库/过滤词表、库代码注释、许可证或第三方库说明默认先标记为“需语境复核”。
- 只有确认命中内容是现实违法违规表达、色情低俗传播、赌博诈骗、外挂黑灰产、账号交易、台独/分裂一个中国表达等，才可建议拒绝。
- 若复核后属于游戏语境或机翻误报，应降级为通过或人工复审，并在报告中说明“关键词命中但语境不构成违规”。

## 用户确认后后台处置

1. 审核后打开 `_audit_output_v4-final\backend_decisions.csv` 给用户确认。
2. 用户可修改：`confirmed_action=pass/reject/skip/空`，`reject_reason` 为拒绝理由。
3. 用户明确“按建议执行”时，才可把空 `confirmed_action` 批量填为 `suggested_action`。
4. 提交命令优先复用登录态：
   ```cmd
   py -3 tools\submit_backend_decisions.py --decisions 有爱插件审核\MMDD\_audit_output_v4-final\backend_decisions.csv --state .playwright-cli\netease-dd-df-state.json
   ```
5. 只提交 `confirmed_action=pass/reject` 的行；`skip` 或空值不提交。
6. 提交后检查 `backend_submission_log.json`，并复查 10 组合待审核数量是否清零。

## Markdown 审核报告

每轮审核后生成 `有爱插件审核\MMDD\_audit_output_v4-final\审核报告.md`，报告必须包含：

- 批次概览：批次 ID、日期、执行轮次、审核口径、开始/完成时间。
- 待审矩阵：5 个游戏版本 × `待审核/机审失败` 数量。
- 下载统计：清单总数、有效下载 URL、下载成功/失败、zip 审核数量、批次目录。
- 审核结论：建议通过、人工复审、建议拒绝、已后台提交/未提交。
- 后台编辑信息：文字字段数、图片 URL 数、图片下载失败数。
- 图片多模态：图片总数、已审数、未审数、无法审阅数、风险图片数、contact sheet 总览路径。
- 风险与证据：按风险类型汇总；列出人工复审/建议拒绝插件的原因、证据文件、关键片段；`P0/P1` 必须写明语境复核结论。
- 关注提醒：台湾服务器/地区标识等关注项，并说明是否影响通过。
- 后台处置：`confirmed_action` 数量、提交成功/失败/跳过、提交后 10 组合复查结果。
- 遗留问题：未处理插件、失败命令、需要人工判断的项；如果无遗留，写“无”。

## v4-final 口径

- 游戏术语、服务器地区、本地化字段默认放宽。
- 广告导流、作者社区、赞助链接不单独拦截，除非同时包含违法违规内容。
- 台湾服务器/地区/本地化语境可通过，但必须写入 `关注提醒` 并说明插件内作用。
- 把台湾描述为国家、与中国并列为主权国家、台独/独立/主权/建国/政治口号、分裂一个中国原则表达，进入复审或拒绝。
- 政治人物、政党标识、色情裸露、赌博诈骗、外挂黑灰产、账号交易、现实敏感政治表达从严。

## 飞书同步

- 默认表：`批次`、`插件审核`、`证据明细`、`图片审核`、`音频审核`、`外链确认`、`关注提醒`、`尺度规则`。
- 同步前先确认用户允许写入飞书；本地审核和后台下载不需要飞书确认。
- 同步命令：
  ```cmd
  py -3 tools\feishu_sync.py --output-dir <批次输出目录> --chunk-size 10
  ```
- 若只验证命令，不写入飞书，加 `--dry-run`。
