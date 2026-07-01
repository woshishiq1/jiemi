import base64
import json
import re
import requests

def decrypt_tvbox_config(webp_url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"
    }
    
    print(f"正在访问: {webp_url}")
    try:
        session = requests.Session()
        res = session.get(webp_url, headers=headers, timeout=20, allow_redirects=True)
        print(f"最终状态码: {res.status_code}，最终URL: {res.url}")
        content = res.text
        print(f"内容长度: {len(content)} 字符")
    except Exception as e:
        print(f"请求失败: {e}")
        return None

    # 增强版 Base64 提取（处理拆分、换行、干扰字符）
    print("正在尝试增强 Base64 提取...")
    # 更宽松的模式，允许中间有少量干扰
    base64_blocks = re.findall(r'[A-Za-z0-9+/=]{200,}', content)
    
    for i, block in enumerate(sorted(base64_blocks, key=len, reverse=True)):
        try:
            # 清理可能的干扰
            cleaned = re.sub(r'[^A-Za-z0-9+/=]', '', block)
            if len(cleaned) < 100:
                continue
                
            # 补全 padding
            padding = len(cleaned) % 4
            if padding:
                cleaned += "=" * (4 - padding)
            
            decoded_bytes = base64.b64decode(cleaned, validate=False)
            decoded_str = decoded_bytes.decode('utf-8', errors='ignore')
            
            # 查找 JSON 对象
            json_match = re.search(r'(\{[\s\S]*?\})', decoded_str, re.DOTALL)
            if json_match:
                json_str = json_match.group(1)
                config = json.loads(json_str)
                print(f"🎉 第 {i+1} 个块解密成功！")
                return config
        except:
            continue

    # 兜底：尝试找最大的 {} 结构
    print("尝试兜底 JSON 提取...")
    try:
        full_match = re.search(r'(\{[\s\S]{1000,}?)\}', content, re.DOTALL)
        if full_match:
            possible = full_match.group(1) + '}'
            # 尝试清理后解析
            possible = re.sub(r'[^ -~]', '', possible)  # 移除不可见字符
            config = json.loads(possible)
            return config
    except:
        pass

    print("❌ 本地所有解密方法失败")
    return None


if __name__ == "__main__":
    target_url = "http://我不是.摸鱼儿.top"
    config = decrypt_tvbox_config(target_url)
    
    if config:
        with open("tvbox_config1.json", "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        print(f"✅ 解密成功！已保存到 tvbox_config1.json")
        print(f"站点数量: {len(config.get('sites', []))}")
    else:
        print("❌ 解密失败")
