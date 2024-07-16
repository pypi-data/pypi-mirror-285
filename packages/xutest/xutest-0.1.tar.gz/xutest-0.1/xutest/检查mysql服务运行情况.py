
def check_mysql_status():
    import subprocess
    try:
        # 使用 sc query 命令检查 MySQL 服务状态
        result = subprocess.run(["sc", "query", "MySQL80"], capture_output=True, text=True, timeout=10)
        if "RUNNING" in result.stdout.upper():
            print("MySQL 服务正在运行。")
        else:
            print("MySQL 服务未运行。")
            # 启动 MySQL 服务
            try:
                # 使用 net start 命令启动 MySQL 服务
                result = subprocess.run(["net", "start", "MySQL80"], capture_output=True, text=True, timeout=30)
                if "SERVICE_NAME: MySQL" in result.stdout:
                    print("MySQL 服务启动成功。")
                else:
                    print("MySQL 服务启动失败。")
            except subprocess.TimeoutExpired:
                print("启动 MySQL 服务超时。")
            except Exception as e:
                print(f"启动 MySQL 服务时发生错误：{str(e)}")
    except subprocess.TimeoutExpired:
        print("检查 MySQL 服务状态超时。")
    except Exception as e:
        print(f"检查 MySQL 服务状态时发生错误：{str(e)}")

if __name__ == '__main__':
    check_mysql_status()
