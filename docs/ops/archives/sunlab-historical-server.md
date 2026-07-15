# Sunlab 历史文件查询服务器

> 归档边界：本文件只记录 `10.40.4.2` 的历史文件查询入口和本机免密登录状态。该服务器不是当前活跃计算服务器，也不作为新 MD、docking、ODE 或生产任务入口。新远程计算任务仍默认使用 [NKULiulab E2 共享云服务器](../nkuliulab-e2-cloud-server.md)。

## 服务器用途

| 项目 | 值 |
|---|---|
| 登录地址 | `zhangzn@10.40.4.2` |
| SSH 端口 | `22` |
| 本机 SSH alias | `drylab-10-40-4-2` |
| 2026-06-25 验证 hostname | `sunlab` |
| 使用边界 | 仅供某些历史文件查询；不作为当前活跃计算路线 |

## 本机 SSH config

2026-06-25 已在本机 `~/.ssh/config` 增加:

```sshconfig
Host drylab-10-40-4-2
    HostName 10.40.4.2
    User zhangzn
    Port 22
    IdentityFile ~/.ssh/id_ed25519
    IdentitiesOnly yes
    ServerAliveInterval 30
    ServerAliveCountMax 4
```

## 免密登录状态

2026-06-25 用户在本机执行:

```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub -p 22 zhangzn@10.40.4.2
ssh -o BatchMode=yes -p 22 zhangzn@10.40.4.2 'hostname && whoami'
ssh -o BatchMode=yes drylab-10-40-4-2 'hostname && whoami'
```

验证输出:

```text
sunlab
zhangzn
```

结论：本机到 `zhangzn@10.40.4.2:22` 的 SSH 公钥登录已生效。

## 使用注意

- 不要把该服务器写入当前活跃远程计算路线。
- 查询历史文件前先确认目标路径，避免猜测文件名。
- 不要在仓库、日志或服务器共享目录中记录密码、私钥、token 或 API key。
- 如需把服务器文件同步回 repo，先明确文件来源和用途；服务器端文件不是 repo 源头。
