import os
import json
import requests

# 定义文件名
JSON_FILE = "tvbox_config1.json"   # 你解密后的JSON文件
TARGET_FILE = "moyu.jar"           # 下载后保存的名字

def download_spider():
    # 1. 检查 json 文件是否存在
    if not os.path.exists(JSON_FILE):
        print(f"[-] 未找到 {JSON_FILE}，请先运行解密脚本生成该文件！")
        return

    # 2. 读取 json 内容
    try:
        with open(JSON_FILE, "r", encoding="utf-8") as f:
            config_data = json.load(f)
    except Exception as e:
        print(f"[-] 读取 JSON 文件失败: {e}")
        return

    # 3. 提取 spider 字段
    spider_raw = config_data.get("spider", "")
    if not spider_raw:
        print("[-] JSON 中未找到 'spider' 字段，跳过下载。")
        return

    print(f"[+] 获取到原始 spider 字段: {spider_raw}")

    # 4. 解析实际下载链接（去掉 ;md5; 后面的部分）
    download_url = spider_raw.split(";")[0].strip()
   
    if not download_url.startswith("http"):
        print(f"[-] 解析出的地址非有效 HTTP 链接: {download_url}")
        return

    print(f"[+] 解析出最新下载链接: {download_url}")

    # 5. 下载并保存为 moyu.jar（强制覆盖）
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        
        print(f"[+] 开始下载最新 spider jar 文件...")
        response = requests.get(download_url, headers=headers, timeout=60)
        response.raise_for_status()
       
        with open(TARGET_FILE, "wb") as f:
            f.write(response.content)
           
        print(f"[+] ✅ 下载成功！")
        print(f"    文件名: {TARGET_FILE}")
        print(f"    大小: {len(response.content) / (1024*1024):.2f} MB")
       
    except Exception as e:
        print(f"[-] 下载或保存失败: {e}")

if __name__ == "__main__":
    download_spider()
