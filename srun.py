import subprocess
import elevate
import time
import logging
import os
import locale
from datetime import datetime, timedelta

# 申请管理员权限
elevate.elevate()

# 日志文件路径
log_file = "network_monitor.log"
log_retention_days = 7  # 保留日志的天数

# 配置日志
logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger()

# 获取 Windows 默认编码（避免乱码）
default_encoding = locale.getpreferredencoding()


# 清理过期日志
def clean_old_logs():
    if os.path.exists(log_file):
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            if not lines:
                return
            # 解析日志中的日期并过滤 7 天内的日志
            threshold_date = datetime.now() - timedelta(days=log_retention_days)
            new_lines = []
            for line in lines:
                try:
                    log_date_str = line.split(" - ")[0]  # 提取日志时间
                    log_date = datetime.strptime(log_date_str, "%Y-%m-%d %H:%M:%S")
                    if log_date >= threshold_date:
                        new_lines.append(line)
                except ValueError:
                    new_lines.append(line)  # 格式错误，保留原行

            with open(log_file, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

            logger.info("Old logs cleaned successfully.")
        except Exception as e:
            logger.error(f"Error cleaning logs: {e}")


# 运行日志清理
clean_old_logs()

# 设置执行命令的时间间隔（单位：秒）
interval = 60


# 运行子进程的函数（隐藏窗口）
def run_command(command):
    try:
        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                       creationflags=subprocess.CREATE_NO_WINDOW)
        logger.info(f"Executed command: {' '.join(command)}")
    except Exception as e:
        logger.error(f"Error executing command: {' '.join(command)}, Error: {e}")


# 退出当前登录
logger.info("Logging out...")
run_command(['.\\srun.exe', 'logout', '-c', '.\\config.txt'])

while True:
    # 执行ping命令
    response = subprocess.run(['ping', 'www.baidu.com', '-n', '1'], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                              creationflags=subprocess.CREATE_NO_WINDOW)

    # 检查ping命令的返回码
    if response.returncode == 0:
        logger.info("Ping successful, continue monitoring...")
    else:
        logger.warning("Ping failed, executing login command...")
        # 执行登录命令
        run_command(['.\\srun.exe', 'login', '-c', '.\\config.txt'])

    # 每天 00:00 清理日志
    if datetime.now().hour == 0 and datetime.now().minute == 0:
        clean_old_logs()

    # 等待指定的时间间隔
    time.sleep(interval)
