import time

import uiautomator2 as u2
from uiautomator2 import Direction
from utils import check_chars_exist


unclick_btn = []
is_end = False
error_count = 0
in_other_app = False
d = u2.connect()
d.app_start("com.eg.android.AlipayGphone", stop=True, use_monkey=True)
time.sleep(5)


def operate_task():
    start_time = time.time()
    while True:
        if time.time() - start_time > 16:
            break
        d.swipe_ext(Direction.FORWARD)
        time.sleep(3)
        d.swipe_ext(Direction.BACKWARD)
        time.sleep(3)
    while True:
        if d(text="做任务集肥料").exists:
            print("当前是任务列表画面，不能继续返回")
            break
        else:
            d.press("back")
            time.sleep(0.5)


d.watcher.when("O1CN012qVB9n1tvZ8ATEQGu_!!6000000005964-2-tps-144-144").click()
d.watcher.when(xpath="//android.app.Dialog//android.widget.Button[@text='关闭']").click()
d.watcher.start()
while True:
    farm_btn = d(resourceId="com.alipay.android.phone.openplatform:id/app_text", className="android.widget.TextView", text="芭芭农场")
    if farm_btn.exists:
        d.click(farm_btn[0].center()[0], farm_btn[0].center()[1])
        time.sleep(5)
    task_btn = d(className="android.widget.Button", text="任务列表")
    if task_btn.exists:
        break
while True:
    task_btn = d(className="android.widget.Button", text="任务列表")
    if task_btn.exists:
        d.click(task_btn[0].center()[0], task_btn[0].center()[1])
        time.sleep(5)
    if d(text="做任务集肥料").exists:
        break
finish_count = 0
while True:
    try:
        time.sleep(3)
        get_btn = d(className="android.widget.Button", text="领取")
        if get_btn.exists:
            get_btn.click()
            time.sleep(2)
        to_btn = d(className="android.widget.Button", textMatches="去完成|去浏览|去逛逛")
        if to_btn.exists:
            need_click_view = None
            need_click_index = 0
            task_name = None
            for index, view in enumerate(to_btn):
                text_div = view.left(className="android.widget.TextView")
                if text_div.exists:
                    if check_chars_exist(text_div.get_text(), ["5次", "购买", "分享", "今日头条"]):
                        if view not in unclick_btn:
                            unclick_btn.append(view)
                        continue
                    task_name = text_div.get_text()
                    need_click_index = index
                    need_click_view = view
                    break
            if need_click_view:
                print("点击按钮", task_name)
                need_click_view.click()
                time.sleep(2)
                search_view = d(className="android.view.View", text="搜索有福利")
                search_edit = d(resourceId="com.taobao.taobao:id/searchEdit")
                search_btn = d(resourceId="com.taobao.taobao:id/searchbtn")
                if search_view.exists:
                    d(className="android.widget.EditText", instance=0).send_keys("笔记本电脑")
                    d(className="android.widget.Button", text="搜索").click()
                    time.sleep(2)
                elif search_edit.exists and search_btn.exists:
                    search_edit.send_keys("笔记本电脑")
                    search_btn.click()
                    time.sleep(2)
                operate_task()
            else:
                error_count += 1
                print("未找到可点击按钮", error_count)
                if error_count > 3:
                    break
    except Exception as e:
        print(e)
        continue
d.watcher.remove()
