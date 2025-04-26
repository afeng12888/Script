import asyncio
import functools
import json
import os
import random
import schedule
import telegram
from datetime import datetime

# 日期列表
DATE_LIST = ['2024-02-32', '2024-02-33', '2024-02-34', '2024-02-35', '2024-02-36', '2024-02-37']

# 文件路径，用于存储当前日期
DATE_FILE_PATH = rf'C:\Users\Administrator\Desktop\炒群资料\script\current_data\current_date.json'

# 图片已发送集合
sent_images = set()

# Telegram Bot 配置
TOKEN = ''       
CHAT_ID = '' 
nation = ''

# 创建 Telegram Bot 实例
bot = telegram.Bot(token=TOKEN)

# 获取当前日期并更新相应的变量
def get_current_date():
    """从文件中获取当前日期"""
    if os.path.exists(DATE_FILE_PATH):
        with open(DATE_FILE_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            current_date = data.get("current_date", DATE_LIST[0])  # 默认使用第一个日期
    else:
        current_date = DATE_LIST[0]  # 如果文件不存在，使用第一个日期
    
    return current_date

# 保存当前日期到文件
def save_current_date(new_date):
    """保存当前日期到 JSON 文件"""
    # 确保文件路径的父目录存在
    if not os.path.exists(os.path.dirname(DATE_FILE_PATH)):
        os.makedirs(os.path.dirname(DATE_FILE_PATH))
    
    # 将新的日期写入 JSON 文件
    with open(DATE_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump({"current_date": new_date}, f, ensure_ascii=False, indent=4)

# 更新日期
def update_date():
    """更新日期"""
    current_date = get_current_date()
    next_date_index = (DATE_LIST.index(current_date) + 1) % len(DATE_LIST)
    new_date = DATE_LIST[next_date_index]
    save_current_date(new_date)  # 保存新日期到文件
    print(f"日期已更新为: {new_date}")
    
    # 重新调度任务
    schedule_job()
    return new_date

def get_time_folders(date_folder):
    """根据日期获取时间文件夹"""
    return {
    "09:30-09:59": rf"C:\Users\Administrator\Desktop\炒群资料\image\{date_folder}\NO1",
    "10:00-10:29": rf"C:\Users\Administrator\Desktop\炒群资料\image\{date_folder}\NO2",
    "10:30-10:59": rf"C:\Users\Administrator\Desktop\炒群资料\image\{date_folder}\NO3",
    "11:00-12:00": rf"C:\Users\Administrator\Desktop\炒群资料\image\{date_folder}\NO4_ZZ",

    "12:00-12:29": rf"C:\Users\Administrator\Desktop\炒群资料\image\{date_folder}\NO5",
    "12:30-12:59": rf"C:\Users\Administrator\Desktop\炒群资料\image\{date_folder}\NO6",
    "13:00-13:29": rf"C:\Users\Administrator\Desktop\炒群资料\image\{date_folder}\NO7",
    "13:30-14:29": rf"C:\Users\Administrator\Desktop\炒群资料\image\{date_folder}\NO8_ZZ",

    "14:30-14:59": rf"C:\Users\Administrator\Desktop\炒群资料\image\{date_folder}\NO9",
    "15:00-15:29": rf"C:\Users\Administrator\Desktop\炒群资料\image\{date_folder}\NO10",
    "15:30-15:59": rf"C:\Users\Administrator\Desktop\炒群资料\image\{date_folder}\NO11",   
    "16:00-16:59": rf"C:\Users\Administrator\Desktop\炒群资料\image\{date_folder}\NO12_ZZ",

    "17:00-17:29": rf"C:\Users\Administrator\Desktop\炒群资料\image\{date_folder}\NO13",
    "17:30-17:59": rf"C:\Users\Administrator\Desktop\炒群资料\image\{date_folder}\NO14",
    "18:00-18:29": rf"C:\Users\Administrator\Desktop\炒群资料\image\{date_folder}\NO15",
    "18:30-18:59": rf"C:\Users\Administrator\Desktop\炒群资料\image\{date_folder}\NO16",
    "19:00-19:29": rf"C:\Users\Administrator\Desktop\炒群资料\image\{date_folder}\NO17",
    "19:30-19:59": rf"C:\Users\Administrator\Desktop\炒群资料\image\{date_folder}\NO18",
}
# 从 JSON 文件中读取特定时间和特定消息
def load_schedule(date_folder):
    with open(rf"C:\Users\Administrator\Desktop\炒群资料\script\SCHEDULE\{nation}\schedule_aer_{date_folder}.json", "r", encoding='utf-8') as file:
        return json.load(file)

# 定义发送特定消息的异步函数
async def send_specific_message(message):
    sent_message = await bot.send_message(chat_id=CHAT_ID, text=message)
    message_id =  sent_message.message_id
    await bot.pin_chat_message(chat_id=CHAT_ID, message_id=message_id)

# 定义发送图片的异步函数
async def send_image(date_folder):
    try:
        current_time = datetime.now().strftime("%H:%M:%S")
        folder_path = None
        time_folders = get_time_folders(date_folder)

        # 根据当前时间段选择对应的文件夹路径
        for time_range, path in time_folders.items():
            start_time, end_time = time_range.split("-")
            if start_time <= current_time <= end_time:
                folder_path = path
                break

        if folder_path:
            # 读取对应文件夹中的所有文件
            image_files = os.listdir(folder_path)
            
            # 去除已发送的照片文件
            remaining_images = [
                file for file in image_files
                if file.lower().endswith((".png", ".jpeg", "jpg")) and file not in sent_images
            ]

            if remaining_images:
                # 随机选择一张图片
                selected_image = random.choice(remaining_images)
                
                # 添加已发送的照片到集合中
                sent_images.add(selected_image)

                # 构建图片文件的完整路径
                image_path = os.path.join(folder_path, selected_image)

                # 打开图片文件并以二进制模式读取
                with open(image_path, 'rb') as photo:
                    await bot.send_photo(chat_id=CHAT_ID, photo=photo)
                    print(f"图片发送成功！时间：{current_time} -  PATH: {selected_image}")

        else:
            print("当前时间段没有配置文件夹路径。")

    except Exception as e:
        print(f"Error occurred while sending image: {str(e)}")

# 调度定时任务
def schedule_job():
    """调度发送特定消息和图片的任务"""
    # 获取当前日期
    date_folder = get_current_date()
    
    # 读取该日期的计划
    message_schedule = load_schedule(date_folder)
    
    # 清除之前的任务，避免重复
    schedule.clear()

    # 设置消息发送任务
    for message_time, message_content in message_schedule.items():
        async_func = functools.partial(send_specific_message, message_content)
        wrapper = functools.partial(asyncio.ensure_future, async_func())
        schedule.every().day.at(message_time).do(wrapper)

    # 每分钟发送一张照片
    schedule.every(2).minutes.do(lambda: asyncio.ensure_future(send_image(date_folder)))

# 每天系统结束时更新日期的定时任务
def schedule_update_date():
    schedule.every().day.at("23:59:59").do(update_date)

# 启动异步事件循环
async def main():
    # 在程序开始时打印一次当前日期
    current_date = get_current_date()
    print(f"当前加载日期: {current_date}")

    # 先执行一次调度任务，初始化当前日期
    schedule_job()

    schedule_update_date()  # 调度日期更新任务

    while True:
        schedule.run_pending()  # 运行已安排的任务
        await asyncio.sleep(1)

# 运行主函数
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        # 确保在程序退出前保存当前日期
        save_current_date(get_current_date())  # 调用 save_current_date
        loop.close()
