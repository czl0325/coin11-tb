import time

import uiautomator2 as u2
from uiautomator2 import xpath

from utils import check_chars_exist, get_current_app, select_device, task_loop, check_verify, start_app, TB_APP, check_popup, print_error, start_watcher, ALIPAY_APP

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
hint_view = d(className="android.widget.TextView", resourceId="com.alipay.android.phone.openplatform.app:id/home_title_search_hint")
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
result_view = d(className="android.widget.FrameLayout", resourceId="com.alipay.android.phone.businesscommon.globalsearch:id/list_container")
if result_view.exists:
    print("进入玩赚支付宝")
    result_view.click()
    time.sleep(3)
sign_btn = d(className="android.widget.TextView", text="立即签到")
if sign_btn.exists:
    print("点击立即签到")
    sign_btn.click()
    time.sleep(5)
ctx.close()
