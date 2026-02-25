import subprocess
import sys
import os


def run_scripts(script_paths):
    python_executable = sys.executable
    for script in script_paths:
        if not os.path.exists(script):
            print(f"警告: 脚本文件 '{script}' 不存在，跳过执行")
            continue
        print(f"开始执行: {script}")
        try:
            # 执行脚本，等待完成后再执行下一个
            result = subprocess.run(
                [python_executable, script],
                check=True,
                stdout=sys.stdout,  # 子进程stdout直接指向当前进程的stdout
                stderr=sys.stderr,  # 子进程stderr直接指向当前进程的stderr
                text=True
            )
            # 打印脚本输出
            if result.stdout:
                print(f"输出:{result.stdout}")
            print(f"执行成功: {script}")
        except subprocess.CalledProcessError as e:
            print(f"执行失败: {script}")
            print(f"错误信息: {e.stderr}")


if __name__ == "__main__":
    scripts_to_run = [
        # "支付宝农场.py",
        "闲鱼任务.py",
        "淘宝芭芭农场.py",
        "淘金币任务.py",
    ]

    run_scripts(scripts_to_run)
