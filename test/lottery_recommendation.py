import random
from datetime import datetime

def get_lottery_type():
    """判断今日开奖类型"""
    today = datetime.now().weekday()
    # 大乐透：周一、三、六开奖
    # 双色球：周二、四、日开奖
    if today in [0, 2, 5]:  # 周一、三、六
        return "大乐透"
    else:
        return "双色球"

def generate_numbers(lottery_type):
    """生成推荐号码"""
    if lottery_type == "大乐透":
        # 前区5个号码(1-35)，后区2个号码(1-12)
        front_numbers = sorted(random.sample(range(1, 36), 5))
        back_numbers = sorted(random.sample(range(1, 13), 2))
        return f"前区：{', '.join(map(str, front_numbers))}，后区：{', '.join(map(str, back_numbers))}"
    else:
        # 双色球：6个红球(1-33)，1个蓝球(1-16)
        red_numbers = sorted(random.sample(range(1, 34), 6))
        blue_number = random.randint(1, 16)
        return f"红球：{', '.join(map(str, red_numbers))}，蓝球：{blue_number}"

def main():
    print("开始生成推荐号码...")
    lottery_type = get_lottery_type()
    print(f"今日开奖类型：{lottery_type}")
    
    numbers = generate_numbers(lottery_type)
    print(f"\n推荐号码：\n{numbers}")
    print("\n程序执行完成")

if __name__ == "__main__":
    main() 