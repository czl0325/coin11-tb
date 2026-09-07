import time
import uiautomator2 as u2
from utils import select_device, start_app, ALIPAY_APP, start_watcher, check_chars_exist, task_loop, get_current_app

no_clicked = ["斗地主", "完成助力", "许愿星", "浏览广告"]
selected_device = select_device()
d = u2.connect(selected_device)
print(f"已成功连接设备：{selected_device}")
start_app(d, ALIPAY_APP, init=True)
screen_width, screen_height = d.window_size()
ctx = start_watcher(d)
ctx.when("退出评价").click()
ctx.when(xpath='//android.app.Dialog//android.widget.Button[@text="关闭"]').click()
time.sleep(3)


def check_in_task():
    package_name, activity_name = get_current_app(d)
    if package_name != ALIPAY_APP:
        return False
    if d(className="android.widget.TextView", text="完成打卡").exists():
        return True
    return False


def back_to_task():
    print("开始返回任务页面")
    while True:
        if check_in_task():
            print("已返回任务页面")
            break
        d.press("back")
        time.sleep(0.5)


search_view = d(className="android.widget.TextView", resourceId="com.alipay.android.phone.businesscommon.globalsearch:id/text", text="玻弦打卡")
if search_view.exists:
    print("进入玻弦打卡")
    search_view.click()
    time.sleep(3)
else:
    hint_view = d(className="android.widget.TextView", resourceId="com.alipay.android.phone.openplatform.app:id/home_title_search_hint")
    if hint_view.exists:
        print("点击搜索框")
        hint_view.click()
        time.sleep(3)
    edit_view = d(className="android.widget.EditText", resourceId="com.alipay.mobile.antui:id/search_input_box")
    if edit_view.exists:
        edit_view.send_keys("玻弦打卡")
        time.sleep(2)
    search_btn = d(className="android.widget.TextView", text="搜索")
    if search_btn.exists:
        print("点击搜索")
        search_btn.click()
        time.sleep(3)
result_view = d(className="android.widget.FrameLayout", resourceId="com.alipay.android.phone.businesscommon.globalsearch:id/list_container")
if result_view.exists:
    print("进入玻弦打卡")
    result_view.click()
    time.sleep(3)
    d.swipe(100, screen_height - 300, 130, screen_height - 1200, 1)
    time.sleep(2)
    while True:
        time.sleep(5)
        has_task = False
        to_btn = d.xpath('//android.widget.Button[@text="去完成"]')
        if to_btn.exists:
            for index, view in enumerate(to_btn.all()):
                title_view = d.xpath(f'(//android.widget.Button[@text="去完成"])[{index+1}]/../../preceding-sibling::android.view.View[1]/android.view.View[1]/android.widget.TextView')
                if title_view.exists:
                    title_text = title_view.text
                    print(f"查找到任务：{title_text}")
                    if check_chars_exist(title_text, no_clicked):
                        continue
                    print(f"点击任务：{title_text}")
                    has_task = True
                    d.click(view.bounds[0] + 30, view.center()[1])
                    time.sleep(5)
                    task_loop(d, back_to_task, origin_app=ALIPAY_APP, only_scroll=True)
                    time.sleep(2)
                    break
        if not has_task:
            print("任务全部做完了，退出循环")
            break
ctx.close()
