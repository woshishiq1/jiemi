import os
import json5  # 读取和写入都使用 json5
import chardet

TVBOX_FILE = "tvbox_config.json"
MOYU_FILE = "moyu.json"
XIAOYU_FILE = "xiaoyu.json"
OUTPUT_FILE = "zy.json"

def detect_encoding(file_path):
    if not os.path.exists(file_path):
        return "utf-8"
    with open(file_path, 'rb') as f:
        raw_data = f.read(10000)
        result = chardet.detect(raw_data)
        return result['encoding'] or "utf-8"

def read_json_file(file_path):
    if not os.path.exists(file_path):
        print(f"[-] 未找到文件: {file_path}")
        return None
    encoding = detect_encoding(file_path)
    try:
        with open(file_path, 'r', encoding=encoding) as f:
            return json5.load(f)
    except Exception as e:
        print(f"[-] 读取 {file_path} 失败: {e}")
        return None

def merge_sites():
    print("[*] 开始读取文件并准备合并...")
    tvbox_data = read_json_file(TVBOX_FILE)
    moyu_data = read_json_file(MOYU_FILE)
    xiaoyu_data = read_json_file(XIAOYU_FILE)

    if tvbox_data is None or moyu_data is None or xiaoyu_data is None:
        print("[-] 合并中止：源文件读取失败。")
        exit(1)

    tvbox_sites = tvbox_data.get("sites", [])
    moyu_sites = moyu_data.get("sites", [])
    xiaoyu_sites = xiaoyu_data.get("sites", [])

    if not isinstance(tvbox_sites, list) or not isinstance(moyu_sites, list) or not isinstance(xiaoyu_sites, list):
        print("[-] 错误: 'sites' 字段不是列表格式！")
        exit(1)

    merged_sites = tvbox_sites + moyu_sites + xiaoyu_sites
    output_data = {"sites": merged_sites}

    # 1. 先用 json5 生成美化后的 JSON5 字符串
    json5_str = json5.dumps(output_data, ensure_ascii=False, indent=2)

    # 2. 通过文本替换，在列表项中对应接口前精准注入 // 注释
    if tvbox_sites and "key" in tvbox_sites[0]:
        first_tvbox_key = f'"key": "{tvbox_sites[0]["key"]}"'
        json5_str = json5_str.replace(first_tvbox_key, f'// tvbox_config.json\n    {first_tvbox_key}', 1)

    if moyu_sites and "key" in moyu_sites[0]:
        first_moyu_key = f'"key": "{moyu_sites[0]["key"]}"'
        json5_str = json5_str.replace(first_moyu_key, f'// moyu.json\n    {first_moyu_key}', 1)

    if xiaoyu_sites and "key" in xiaoyu_sites[0]:
        first_xiaoyu_key = f'"key": "{xiaoyu_sites[0]["key"]}"'
        json5_str = json5_str.replace(first_xiaoyu_key, f'// xiaoyu.json\n    {first_xiaoyu_key}', 1)

    # 3. 写入文件
    encoding = detect_encoding(TVBOX_FILE)
    try:
        with open(OUTPUT_FILE, 'w', encoding=encoding) as f:
            f.write(json5_str)
        print(f"[+] 成功生成带注释的文件: {OUTPUT_FILE}")
    except Exception as e:
        print(f"[-] 写入 {OUTPUT_FILE} 失败: {e}")

if __name__ == "__main__":
    merge_sites()
