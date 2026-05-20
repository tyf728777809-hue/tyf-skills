# rg 维护说明

## 根因

Codex App 自带的 `rg` 位于 `C:\Program Files\WindowsApps\OpenAI.Codex_...\app\resources\rg.exe`。该路径受 WindowsApps 应用包权限保护，在当前 PowerShell/Codex 进程中可能被 `CreateProcess` 拒绝，表现为：

```powershell
Program 'rg.exe' failed to run: Access is denied
```

这不是审核目录、管道或参数问题；显式执行 WindowsApps 下的 `rg.exe --version` 也会失败。

## 已采用修复

使用 Scoop 安装用户级 ripgrep，并让 Scoop shim 优先于 WindowsApps 版本：

```powershell
$env:ProgramFiles='C:\Program Files'; $env:ProgramData='C:\ProgramData'; $env:ALLUSERSPROFILE='C:\ProgramData'; $env:SystemDrive='C:'; $env:LOCALAPPDATA='C:\Users\N30846\AppData\Local'
scoop install ripgrep
```

当前期望的优先路径：

```text
E:\CLI\scoop\shims\rg.exe
```

## 健康检查

每次遇到 `rg` 异常时先运行：

```powershell
Get-Command rg -All
rg --version
rg --files | Select-Object -First 10
```

验收标准：`Get-Command rg -All` 的第一项应为 `E:\CLI\scoop\shims\rg.exe`，`rg --version` 退出码为 0。

## fallback 命令

如果 `rg` 再次不可用，不要阻塞审核；用 PowerShell 原生命令替代。

列文件：

```powershell
Get-ChildItem -Recurse -File -Force -ErrorAction SilentlyContinue | Select-Object -ExpandProperty FullName
```

按文件名搜索：

```powershell
Get-ChildItem -Recurse -File -Force -ErrorAction SilentlyContinue | Where-Object { $_.Name -match '<pattern>' }
```

按内容搜索：

```powershell
Get-ChildItem -Recurse -File -Force -ErrorAction SilentlyContinue |
  Where-Object { $_.Length -lt 2000000 } |
  Select-String -Pattern '<pattern>' -ErrorAction SilentlyContinue
```

## 重新修复

如果 Scoop shim 不在 PATH 第一位，优先重新打开终端；仍不生效时检查用户 PATH 是否包含：

```text
E:\CLI\scoop\shims
```

如 Scoop 不可用，再使用 winget 安装：

```powershell
winget install --id BurntSushi.ripgrep --source winget --accept-source-agreements --accept-package-agreements
```
