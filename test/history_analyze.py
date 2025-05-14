import requests
from bs4 import BeautifulSoup
from collections import Counter

def fetch_dlt_history(n=100):
    """
    爬取最近n期大乐透历史开奖数据，返回前区和后区号码列表
    """
    url = "https://datachart.500.com/dlt/history/newinc/history.php"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.encoding = 'gb2312'
    soup = BeautifulSoup(response.text, 'html.parser')
    tbody = soup.find('tbody', id='tdata')
    front_all = []
    back_all = []
    if tbody:
        trs = tbody.find_all('tr')[:n]
        for tr in trs:
            tds = tr.find_all('td')
            if len(tds) >= 8:
                # 前区5个，后区2个
                front = [int(tds[i].text.strip()) for i in range(1, 6)]
                back = [int(tds[i].text.strip()) for i in range(6, 8)]
                front_all.extend(front)
                back_all.extend(back)
    return front_all, back_all

def analyze_hot_cold(numbers, pick_hot=3, pick_cold=2, pool=5):
    """
    numbers: 所有历史号码（前区或后区）
    pick_hot: 推荐中热号数量
    pick_cold: 推荐中冷号数量
    pool: 推荐号码总数
    返回：热号列表、冷号列表、推荐号码
    """
    counter = Counter(numbers)
    # 出现次数排序
    most_common = counter.most_common()
    hot = [num for num, _ in most_common[:pool]]
    cold = [num for num, _ in most_common[-pool:]]
    # 推荐号码：优先热号，补充冷号
    recommend = sorted(hot[:pick_hot] + cold[:pick_cold])
    return hot, cold, recommend

if __name__ == "__main__":
    front_all, back_all = fetch_dlt_history(100)
    hot_f, cold_f, rec_f = analyze_hot_cold(front_all, 3, 2, 5)
    hot_b, cold_b, rec_b = analyze_hot_cold(back_all, 1, 1, 2)
    print(f"前区热号: {hot_f}")
    print(f"前区冷号: {cold_f}")
    print(f"前区推荐: {rec_f}")
    print(f"后区热号: {hot_b}")
    print(f"后区冷号: {cold_b}")
    print(f"后区推荐: {rec_b}") 