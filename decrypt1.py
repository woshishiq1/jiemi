import requests
import re
import json
import base64
import os

def decrypt_tvbox_config():
    url = "http://我不是.摸鱼儿.top"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    print(f"正在访问: {url}")
    res = requests.get(url, headers=headers, timeout=20)
    print(f"状态码: {res.status_code} | 内容长度: {len(res.text)}")
    
    content = res.text

    # 方法1：增强 Base64 提取
    print("尝试方法1：增强Base64提取...")
    blocks = re.findall(r'[A-Za-z0-9+/=]{250,}', content)
    for block in sorted(blocks, key=len, reverse=True):
        try:
            cleaned = re.sub(r'[^A-Za-z0-9+/=]', '', block)
            if len(cleaned) < 200: continue
            padding = len(cleaned) % 4
            if padding:
                cleaned += "=" * (4 - padding)
            decoded = base64.b64decode(cleaned).decode('utf-8', errors='ignore')
            if '"sites"' in decoded or '"spider"' in decoded:
                match = re.search(r'\{[\s\S]*"sites"[\s\S]*?\}', decoded, re.DOTALL)
                if match:
                    config = json.loads(match.group(0))
                    print("🎉 方法1 解密成功！")
                    return config
        except:
            continue

    # 方法2：调用 2015888 在线解密接口（更稳）
    print("尝试方法2：调用在线解密接口...")
    try:
        api_url = "https://master.2015888.xyz/jiemi/"
        payload = {"url": url, "content": content[:80000]}  # 截取避免过长
        api_res = requests.post(api_url, data=payload, headers=headers, timeout=25)
        
        # 提取 textarea 中的内容
        match = re.search(r'<textarea[^>]*>([\s\S]*?)</textarea>', api_res.text, re.I)
        if match:
            json_text = match.group(1).strip()
            config = json.loads(json_text)
            print("🎉 方法2（在线接口）解密成功！")
            return config
    except Exception as e:
        print(f"在线接口失败: {e}")

    print("❌ 两种方法均失败")
    return None

if __name__ == "__main__":
    config = decrypt_tvbox_config()
    if config:
        with open("tvbox_config1.json", "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print("✅ tvbox_config1.json 已生成")
        
        # 自动提取spider并下载
        spider = config.get("spider", "")
        if spider:
            jar_url = spider.split(";")[0]
            print(f"发现最新jar: {jar_url}")
            try:
                r = requests.get(jar_url, headers=headers, timeout=30)
                with open("moyu.jar", "wb") as f:
                    f.write(r.content)
                print(f"✅ moyu.jar 下载完成 ({len(r.content)/1024/1024:.1f} MB)")
            except:
                print("jar下载失败")
    else:
        print("❌ 自动解密失败")
