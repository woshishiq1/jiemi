import os
import json5  # 支持带注释或不规范的 JSON 格式
import chardet

TVBOX_FILE = "tvbox_config.json"
MOYU_FILE = "moyu.json"
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

def write_json_file(file_path, data, reference_file):
    encoding = detect_encoding(reference_file)
    try:
        with open(file_path, 'w', encoding=encoding) as f:
            json5.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[+] 成功生成/更新文件: {file_path}")
    except Exception as e:
        print(f"[-] 写入 {file_path} 失败: {e}")

def merge_sites():
    print("[*] 开始读取文件并准备合并...")
    tvbox_data = read_json_file(TVBOX_FILE)
    moyu_data = read_json_file(MOYU_FILE)

    if tvbox_data is None or moyu_data is None:
        print("[-] 合并中止：源文件读取失败。")
        exit(1)

    tvbox_sites = tvbox_data.get("sites", [])
    moyu_sites = moyu_data.get("sites", [])

    if not isinstance(tvbox_sites, list) or not isinstance(moyu_sites, list):
        print("[-] 错误: 'sites' 字段不是列表格式！")
        exit(1)

    # 合并 sites
    merged_sites = tvbox_sites + moyu_sites

    # 以 tvbox 结构为模板，更新 sites 列表
    output_data = dict(tvbox_data)
    output_data["sites"] = merged_sites

    write_json_file(OUTPUT_FILE, output_data, TVBOX_FILE)
    print("[*] 合并完成！")

if __name__ == "__main__":
    merge_sites()
