import os
import json
import hashlib

INPUT_JSON = "tvbox_config.json"
OUTPUT_JSON = "tvbox_modified.json"
TARGET_IMAGE = "aowu.png"  # 依赖刚刚下载好的最新图片来计算MD5

JAR_KEY = "jar"
# 基础链接（去掉了末尾，留给脚本动态拼接MD5）
BASE_JAR_URL = "https://ghfast.top/https://raw.githubusercontent.com/woshishiq1/jiemi/main/aowu.png"

def get_file_md5(file_path):
    """计算本地文件的 MD5 值"""
    if not os.path.exists(file_path):
        return ""
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    return hasher.hexdigest()

def add_jar_to_sites():
    if not os.path.exists(INPUT_JSON):
        print(f"[-] 未找到源文件 {INPUT_JSON}")
        return

    try:
        with open(INPUT_JSON, "r", encoding="utf-8") as f:
            config_data = json.load(f)
    except Exception as e:
        print(f"[-] 解析 JSON 失败: {e}")
        return

    sites_list = config_data.get("sites", [])
    if not sites_list or not isinstance(sites_list, list):
        print("[-] 未找到有效的 'sites' 列表。")
        return

    # 核心改动：实时计算最新下载的 aowu.png 的 MD5
    img_md5 = get_file_md5(TARGET_IMAGE)
    if img_md5:
        # 拼接成 TVBox 标配的带有 MD5 强刷尾巴的链接
        # 变成：https://.../aowu.png;md5;xxxxxx
        final_jar_value = f"{BASE_JAR_URL};md5;{img_md5}"
        print(f"[+] 成功计算最新图片 MD5: {img_md5}")
    else:
        # 如果图片还没下载完，作为保底使用原链接
        final_jar_value = BASE_JAR_URL
        print("[-] 未找到 aowu.png，使用无MD5的默认链接。")

    print(f"[+] 开始为 {len(sites_list)} 个站点注入最新的 Jar 地址...")

    for site in sites_list:
        if isinstance(site, dict):
            site[JAR_KEY] = final_jar_value

    try:
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        print(f"[+] 成功生成完美配置: {OUTPUT_JSON} (已自动挂载MD5缓存刷新机制)")
    except Exception as e:
        print(f"[-] 保存新 JSON 失败: {e}")

if __name__ == "__main__":
    add_jar_to_sites()
