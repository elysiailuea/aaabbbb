import argparse
import time
from datetime import datetime

import paramiko


def try_login(host: str, port: int, username: str, password: str, timeout: float = 3.0) -> bool:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            hostname=host,
            port=port,
            username=username,
            password=password,
            timeout=timeout,
            banner_timeout=timeout,
            auth_timeout=timeout,
            allow_agent=False,
            look_for_keys=False,
        )
        return True
    except Exception:
        return False
    finally:
        try:
            client.close()
        except Exception:
            pass


def main():
    ap = argparse.ArgumentParser(description="对本地 Cowrie(2222) 进行可控的失败登录模拟（用于答辩演示）")
    ap.add_argument("--host", default="localhost")
    ap.add_argument("--port", type=int, default=2222)
    ap.add_argument("--rounds", type=int, default=30, help="总尝试次数")
    ap.add_argument("--sleep", type=float, default=0.2, help="每次尝试间隔秒数")
    args = ap.parse_args()

    users = ["root", "admin", "test", "oracle"]
    pwds = ["123456", "password", "admin123", "root", "qwerty", "123123"]

    ok = 0
    fail = 0
    print(f"[{datetime.now()}] 开始模拟 SSH 登录：{args.host}:{args.port} rounds={args.rounds}")
    for i in range(args.rounds):
        u = users[i % len(users)]
        p = pwds[i % len(pwds)]
        success = try_login(args.host, args.port, u, p)
        if success:
            ok += 1
            print(f"  [{i+1}/{args.rounds}] 成功登录（罕见，取决于 Cowrie 配置）：{u}/{p}")
        else:
            fail += 1
            print(f"  [{i+1}/{args.rounds}] 失败登录：{u}/{p}")
        time.sleep(args.sleep)

    print(f"完成：成功={ok} 失败={fail}")
    print("提示：稍等 30 秒让聚合任务更新画像/告警，然后去前端看板与事件查询查看效果。")


if __name__ == "__main__":
    main()