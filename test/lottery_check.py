import requests
from bs4 import BeautifulSoup
from datetime import datetime

def get_lottery_type():
    """判断今日开奖类型"""
    today = datetime.now().weekday()
    print(f"今天是星期{today + 1}")
    if today in [0, 2, 5]:  # 周一、三、六
        print("今天开大乐透")
        return "大乐透"
    else:
        print("今天开双色球")
        return "双色球"

def get_lottery_result(lottery_type):
    """获取开奖结果"""
    try:
        if lottery_type == "大乐透":
            url = "https://datachart.500.com/dlt/history/newinc/history.php"
        else:
            url = "https://datachart.500.com/ssq/history/newinc/history.php"
            
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        print(f"正在获取{lottery_type}开奖结果，URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.encoding = 'gb2312'  # 500彩票网使用gb2312编码
        print(f"响应状态码: {response.status_code}")
        
        if response.status_code != 200:
            print(f"请求失败，状态码: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        print("成功解析HTML")

        # 查找开奖表格
        tbody = soup.find('tbody', id='tdata')
        if tbody:
            print("找到开奖表格")
            first_tr = tbody.find('tr')
            if first_tr:
                tds = first_tr.find_all('td')
                if len(tds) >= 8:
                    # 第2到8个td（索引1到7）
                    numbers = [td.text.strip() for td in tds[1:8]]
                    print(f"找到开奖号码: {' '.join(numbers)}")
                    return ' '.join(numbers)
                else:
                    print("td数量不足，无法提取开奖号码")
                    return None
            else:
                print("未找到第一个tr")
                return None
        else:
            print("未找到id为tdata的tbody")
            return None

    except requests.exceptions.Timeout:
        print("请求超时")
        return None
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {str(e)}")
        return None
    except Exception as e:
        print(f"获取开奖结果失败: {str(e)}")
        return None

def main():
    print("开始执行开奖查询...")
    lottery_type = get_lottery_type()
    result = get_lottery_result(lottery_type)
    
    if result:
        print(f"\n今日{lottery_type}开奖结果：")
        print(result)
    else:
        print(f"\n今日{lottery_type}开奖结果获取失败")
    
    print("\n程序执行完成")

if __name__ == "__main__":
    main() 