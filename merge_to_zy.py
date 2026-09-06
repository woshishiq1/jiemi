import os
import json  # 保持使用标准库 json 进行导出
import json5 # 仅用于读取带有注释的源文件
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

    # 1. 正常合并
    merged_sites = tvbox_sites + moyu_sites + xiaoyu_sites
    output_data = {"sites": merged_sites}

    # 2. 使用标准 json 生成标准的格式化文本（保留所有双引号，不会标红）
    json_text = json.dumps(output_data, ensure_ascii=False, indent=2)

    # 3. 找到各段第一个 site 的 key/name，在对应位置前面插入 // 注释
    def add_comment(content, site_list, comment_title):
        if not site_list:
            return content
        first_site = site_list[0]
        # 优先使用 key 作为定位锚点
        if "key" in first_site and first_site["key"]:
            target = f'"key": "{first_site["key"]}"'
        elif "name" in first_site and first_site["name"]:
            target = f'"name": "{first_site["name"]}"'
        else:
            return content

        # 在匹配到的第一个 key/name 前面加一行注释
        replacement = f'// {comment_title}\n    {target}'
        return content.replace(target, replacement, 1)

    # 依次插入三组配置的注释标识
    json_text = add_comment(json_text, tvbox_sites, "tvbox_config.json")
    json_text = add_comment(json_text, moyu_sites, "moyu.json")
    json_text = add_comment(json_text, xiaoyu_sites, "xiaoyu.json")

    # 4. 写入文件
    encoding = detect_encoding(TVBOX_FILE)
    try:
        with open(OUTPUT_FILE, 'w', encoding=encoding) as f:
            f.write(json_text)
        print(f"[+] 成功生成标准带注释文件: {OUTPUT_FILE}")
    except Exception as e:
        print(f"[-] 写入 {OUTPUT_FILE} 失败: {e}")

if __name__ == "__main__":
    merge_sites()
