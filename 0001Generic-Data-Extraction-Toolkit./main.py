# ==========================================
# 1. 怎麼發送請求 (環境準備與匯入)
# 指令: pip install requests lxml
# ==========================================
import requests
from lxml import etree
import time
import random

# ==========================================
# 2. 發送給誰 (設定目標與偽裝)
# ==========================================
# 建立會話，維持連線效率與 Cookie
session = requests.Session()

# 基礎網址與首頁網址
base_url = 'https://sto55.com'
# 使用者輸入目標
target_url = input("請輸入小說第一章網址: ").strip()
save_file = input("請輸入儲存檔案名稱: ").strip() + ".txt"

# 偽裝自己
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    '接受-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
    'Referer': base_url
})

# ==========================================
# 3. 發送請求 (循環抓取邏輯)
# ==========================================
current_url = target_url

while current_url:
    try:
        # 發送 GET 請求
        response = session.get(current_url, timeout=15)
        
        # 設置編碼防止亂碼
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"請求失敗，錯誤代碼: {response.status_code}")
            break

        # ==========================================
        # 4. 響應信息 (解析內容)
        # ==========================================
        html_tree = etree.HTML(response.text)
        
        # 提取標題
        title = html_tree.xpath('//h1/text()')
        title_text = title[0].strip() if title else "未知章節"
        
        # 提取內文 (適配 sto55 的 class 結構)
        paragraphs = html_tree.xpath('//div[@class="article-content"]//p/text()')
        content = '\n'。join([p.strip() for p in paragraphs if p.strip()])

        # ==========================================
        # 5. 保存 (檔案寫入與翻頁)
        # ==========================================
        # 使用 'a' (追加模式) 寫入檔案
        with open(save_file, 'a', encoding='utf-8') as f:
            f.write(f"\n\n{title_text}\n" + "="*20 + "\n")
            f.write(content + "\n")
        
        print(f"已成功保存: {title_text}")

        # 找尋下一章網址
        next_path = html_tree.xpath('//a[contains(text(), "下一章")]/@href')
        if next_path:
            path = next_path[0]
            # 拼接完整 URL
            current_url = path if path.startswith('http') else base_url + path
            
            # 動態更新 Referer 偽裝行為
            session.headers.update({'Referer': response.url})
            
            # 隨機延時，保護 IP 不被封鎖
            time.sleep(random.uniform(1.5, 3.5))
        else:
            print("--- 全書下載完成 ---")
            break

    except Exception as e:
        print(f"發生意外錯誤: {e}")
        break
