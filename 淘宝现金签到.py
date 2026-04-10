import time

import uiautomator2 as u2
from utils import check_chars_exist, other_app, get_current_app, select_device, task_loop, check_verify, start_app, TB_APP

unclick_btn = []
have_clicked = dict()
is_end = False
error_count = 0
in_other_app = False
time1 = time.time()
selected_device = select_device()
d = u2.connect(selected_device)
print(f"已成功连接设备：{selected_device}")
start_app(d, TB_APP, init=True)
ctx = d.watch_context()
ctx.when("O1CN012qVB9n1tvZ8ATEQGu_!!6000000005964-2-tps-144-144").click()
ctx.when("O1CN01sORayC1hBVsDQRZoO_!!6000000004239-2-tps-426-128.png_").click()
ctx.when("领取今日奖励").click()
ctx.when("确认").click()
ctx.when("确定").click()
ctx.when("刷新").click()
ctx.when("点击刷新").click()
ctx.when(xpath="//android.app.Dialog//android.widget.Button[contains(text(), '-tps-')]").click()
ctx.when(xpath="//android.app.Dialog//android.widget.Button[@text='关闭']").click()
ctx.when(xpath="//android.widget.FrameLayout[@resource-id='com.taobao.taobao:id/poplayer_native_state_center_layout_frame_id']//android.widget.ImageView[@content-desc='关闭按钮']").click()
# ctx.when(xpath="//android.widget.TextView[@package='com.eg.android.AlipayGphone']").click()
ctx.start()
time.sleep(3)

coin_btn = d(className="android.view.View", description="红包签到")
if coin_btn.exists:
    print("点击红包签到按钮")
    coin_btn.click()
    time.sleep(8)
sign_btn = d(className="android.widget.Button", text="立即签到")
if sign_btn.exists:
    print("点击立即签到")
    sign_btn.click()
    time.sleep(5)
get_btn = d(className="android.widget.Button", resourceId="TIMER_REWARD_BUTTON", textContains="点击领取")
if get_btn.exists:
    print("点击立即领取")
    get_btn.click()
    time.sleep(5)
earn_btn = d(className="android.widget.Button", resourceId="EARN_YUANBAO_BUTTON", textContains="赚元宝")
if earn_btn.exists:
    print("点击赚元宝")
    earn_btn.click()
    time.sleep(3)
    ctx.close()
d.shell("settings put system accelerometer_rotation 0")
print("关闭手机自动旋转")
time2 = time.time()
minutes, seconds = divmod(int(time2 - time1), 60)
print(f"共耗时: {minutes} 分钟 {seconds} 秒")
