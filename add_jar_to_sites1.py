import os
import json
import hashlib

INPUT_JSON = "tvbox_config1.json"
OUTPUT_JSON = "tvbox_modified1.json"
TARGET_IMAGE = "moyu.jar"          # 用于计算 MD5 的图片

JAR_KEY = "jar"
BASE_JAR_URL = "https://ghfast.top/https://raw.githubusercontent.com/woshishiq1/jiemi/main/moyu.jar"


def get_file_md5(file_path):
    """计算本地文件的 MD5 值"""
    if not os.path.exists(file_path):
        print(f"[-] 未找到图片 {file_path}，将使用无 MD5 链接")
        return None
    try:
        hasher = hashlib.md5()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        md5 = hasher.hexdigest()
        print(f"[+] 成功计算 aowu.png MD5: {md5}")
        return md5
    except Exception as e:
        print(f"[-] 计算 MD5 失败: {e}")
        return None


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

    # 计算最新 MD5
    img_md5 = get_file_md5(TARGET_IMAGE)
    if img_md5:
        final_jar_value = f"{BASE_JAR_URL};md5;{img_md5}"
    else:
        final_jar_value = BASE_JAR_URL

    print(f"[+] 准备注入 Jar 地址 → {final_jar_value[:80]}...")

    updated_count = 0
    skipped_count = 0

    for site in sites_list:
        if isinstance(site, dict):
            site_name = site.get("name", "未知站点")
            current_jar = site.get(JAR_KEY)

            # 智能判断：已有有效 jar 地址则跳过
            if current_jar and isinstance(current_jar, str) and current_jar.strip():
                print(f"[~] 跳过已有 Jar 的站点: {site_name}")
                skipped_count += 1
                continue

            # 没有 jar 或 jar 为空 → 注入
            site[JAR_KEY] = final_jar_value
            print(f"[+] 已为站点注入 Jar: {site_name}")
            updated_count += 1

    if updated_count == 0 and skipped_count == 0:
        print("[-] sites 列表为空或格式异常")
        return

    try:
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)
        print(f"\n[+] 操作完成！")
        print(f"   • 新增/更新 Jar 的站点: {updated_count} 个")
        print(f"   • 跳过（已有 Jar）的站点: {skipped_count} 个")
        print(f"   • 输出文件: {OUTPUT_JSON}")
    except Exception as e:
        print(f"[-] 保存新 JSON 失败: {e}")


if __name__ == "__main__":
    add_jar_to_sites()
