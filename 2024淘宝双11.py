import time

import uiautomator2 as u2
from uiautomator2 import Direction
from utils import check_chars_exist, other_app

d = u2.connect()
d.app_start("com.taobao.taobao", stop=True, use_monkey=True)
# d.debug = True
screen_width = d.info['displayWidth']
screen_height = d.info['displayHeight']
time.sleep(2)
in_search = False
in_other_app = False
have_clicked = []


def check_close():
    d(className="android.widget.Button", text="关闭")


def operate_task():
    global in_search
    global in_other_app
    start_time = time.time()
    taolive_btn = d(resourceId="com.taobao.taobao:id/taolive_close_btn")
    if taolive_btn.exists and not in_other_app:
        time.sleep(20)
        while True:
            taolive_btn = d(resourceId="com.taobao.taobao:id/taolive_close_btn")
            if not taolive_btn.exists:
                break
            d.press("back")
            time.sleep(5)
    elif in_other_app:
        time.sleep(10)
        print("当前包名: ", d.app_current()["package"])
        d.app_stop(d.app_current()["package"])
        in_other_app = False
    else:
        while True:
            if time.time() - start_time > 20:
                break
            d.swipe_ext(Direction.FORWARD)
            time.sleep(3)
            d.swipe_ext(Direction.BACKWARD)
            time.sleep(3)
        d.press("back")
        if in_search:
            time.sleep(2)
            in_search = False
            d.press("back")


ctx = d.watch_context()
ctx.when("O1CN012qVB9n1tvZ8ATEQGu_!!6000000005964-2-tps-144-144").click()
ctx.when("O1CN01TkBa3v1zgLfbNmfp7_!!6000000006743-2-tps-72-72").click()
ctx.when(xpath="//android.app.Dialog//android.widget.Button[@text='关闭']").click()
# d.watcher.when(xpath="//android.widget.Button[@text='关闭']").click()
# d.watcher.when("关闭").click()
ctx.when(xpath="//android.widget.TextView[@package='com.eg.android.AlipayGphone']").click()
ctx.start()
# close_btn = d(className="android.widget.ImageView", description="关闭按钮")
# if close_btn.exists:
#     close_btn.click()
print("检查弹窗开始")
ctx.wait_stable()
print("检查弹窗结束")
coin_btn = d(className="android.widget.FrameLayout", description="金币双11", clickable=True)
if coin_btn.exists(timeout=10):
    d.click(coin_btn[0].center()[0], coin_btn[0].center()[1])
    time.sleep(2)
else:
    raise Exception("没有找到金币双11按钮")
# task_btn = d.xpath('//android.widget.TextView[@text="做任务攒钱"]')
while True:
    time.sleep(2)
    underway_btn = d(text="进行中")
    if underway_btn.exists:
        continue
    task_btn = d(text="做任务攒钱")
    if task_btn.exists:
        break
# task_btn = d(resourceId="eva-canvas")
error_count = 0
if task_btn.click_exists(timeout=10):
    print("点击了做任务攒钱按钮")
    # left, bottom, right = task_btn.info['bounds']['left'], task_btn.info['bounds']['bottom'], task_btn.info['bounds']['right']
    # d.click((right - left) // 2, bottom - 10)
    time.sleep(8)
    sign_btn = d(text="签到")
    if sign_btn.exists:
        sign_btn.click()
        time.sleep(2)
    # list_view = d(className="android.widget.ListView", instance=0)
    # print("检查list_view")
    # if list_view.exists:
    #     print("list_view存在")
    unclick_btn = []
    is_end = False
    while True:
        to_btn = d(className="android.widget.Button", text="去完成")
        if to_btn.exists:
            need_click_view = None
            need_click_index = 0
            task_name = None
            for index, view in enumerate(to_btn):
                text_div = view.sibling(className="android.view.View", instance=0).child(className="android.widget.TextView", instance=0)
                if text_div.exists:
                    if check_chars_exist(text_div.get_text()):
                        if view not in unclick_btn:
                            unclick_btn.append(view)
                        continue
                    task_name = text_div.get_text()
                    if task_name in have_clicked:
                        continue
                    need_click_index = index
                    need_click_view = view
                    break
            if need_click_view:
                print("点击按钮", task_name)
                if task_name not in have_clicked:
                    have_clicked.append(task_name)
                need_click_view.click()
                time.sleep(2)
                search_view = d(className="android.view.View", text="搜索有福利")
                if search_view.exists:
                    d(className="android.widget.EditText", instance=0).send_keys("笔记本电脑")
                    d(className="android.widget.Button", text="搜索").click()
                    in_search = True
                    time.sleep(2)
                if check_chars_exist(task_name, other_app):
                    in_other_app = True
                    operate_task()
                else:
                    web_view = d(className="android.webkit.WebView")
                    if web_view.exists(timeout=5):
                        operate_task()
            else:
                if not is_end:
                    d.swipe_ext(Direction.FORWARD)
                    d(scrollable=True).scroll.toEnd()
                    is_end = True
                else:
                    error_count += 1
                    print("未找到可点击按钮", error_count)
                    if error_count > 6:
                        break
        else:
            print("没有找到去完成按钮")
            break
        time.sleep(6)
else:
    print("未找到做任务按钮")
draw_down_btn = d(className="android.widget.Button", text="立即领取")
while True:
    if draw_down_btn.exists:
        draw_down_btn.click()
        time.sleep(2)
    else:
        break
ctx.stop()
ctx.close()
d.watcher.remove()
