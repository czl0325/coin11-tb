import time

import uiautomator2 as u2
from uiautomator2 import xpath

from utils import check_chars_exist, get_current_app, select_device, task_loop, check_verify, start_app, TB_APP, \
    check_popup, print_error, start_watcher, ALIPAY_APP

unclick_btn = []
have_clicked = dict()
is_end = False
error_count = 0
time1 = time.time()
selected_device = select_device()
d = u2.connect(selected_device)
print(f"已成功连接设备：{selected_device}")
start_app(d, ALIPAY_APP, init=True)
screen_width, screen_height = d.window_size()
ctx = start_watcher(d)
ctx.when(xpath='//android.app.Dialog//android.widget.Button[@text="关闭"]').click()
time.sleep(3)
hint_view = d(className="android.widget.TextView",
              resourceId="com.alipay.android.phone.openplatform.app:id/home_title_search_hint")
if hint_view.exists:
    print("点击搜索框")
    hint_view.click()
    time.sleep(3)
edit_view = d(className="android.widget.EditText", resourceId="com.alipay.mobile.antui:id/search_input_box")
if edit_view.exists:
    edit_view.send_keys("玩赚支付宝")
    time.sleep(2)
search_btn = d(className="android.widget.TextView", text="搜索")
if search_btn.exists:
    print("点击搜索")
    search_btn.click()
    time.sleep(3)
result_view = d(className="android.widget.FrameLayout",
                resourceId="com.alipay.android.phone.businesscommon.globalsearch:id/list_container")
if result_view.exists:
    print("进入玩赚支付宝")
    result_view.click()
    time.sleep(3)
sign_btn = d(className="android.widget.TextView", text="立即签到")
if sign_btn.exists:
    print("点击立即签到")
    sign_btn.click()
    time.sleep(5)


def check_in_task():
    package_name, activity_name = get_current_app(d)
    if package_name == ALIPAY_APP:
        title_view = d(className="android.widget.TextView",
                       resourceId="com.alipay.multiplatform.phone.xriver_integration:id/textView_title",
                       text="玩赚支付宝")
        if title_view.exists:
            return True
    return False


def back_to_task():
    print("开始返回任务页面")
    while True:
        try:
            temp_package, temp_activity = get_current_app(d)
            if temp_package is None or temp_activity is None or "Ext2ContainerActivity" in temp_activity:
                continue
            print(f"{temp_package}--{temp_activity}")
            if ALIPAY_APP not in temp_package:
                print(f"回到原始APP,{ALIPAY_APP}")
                start_app(d, ALIPAY_APP)
            else:
                check_popup(d)
                if check_in_task():
                    print("当前是任务列表画面，不能继续返回")
                    break
                else:
                    close_btn1 = d.xpath(
                        "//android.widget.FrameLayout[@resource-id='com.alipay.multiplatform.phone.xriver_integration:id/frameLayout_rightButton1']/android.widget.LinearLayout/android.widget.RelativeLayout/android.widget.RelativeLayout/android.widget.FrameLayout[2]")
                    if close_btn1.exists:
                        print("点击关闭小程序按钮")
                        close_btn1.click()
                        time.sleep(1)
                        continue
                    task_view = d.xpath('//android.widget.TextView[contains(@text, "限时下单任务")]')
                    if task_view.exists:
                        close_btn2 = d.xpath(
                            '//android.widget.TextView[contains(@text, "限时下单任务")]/preceding-sibling::android.view.View[1]')
                        if close_btn2.exists:
                            print("点击关闭限时下单任务按钮")
                            close_btn2.click()
                            time.sleep(1)
                            continue
                    print("点击后退")
                    d.press("back")
                    time.sleep(0.3)
        except Exception:
            print_error()


while True:
    time.sleep(4)
    print("开始查找任务。。。")
    to_btn = d(className="android.widget.Button", textMatches=r"去完成|去逛逛")
    if to_btn.exists:
        to_btn.click()
        time.sleep(3)
        task_loop(d, back_func=back_to_task, duration=18)
    else:
        print("任务全部做完了")
        break
ctx.close()
d.shell("settings put system accelerometer_rotation 0")
print("关闭手机自动旋转")
