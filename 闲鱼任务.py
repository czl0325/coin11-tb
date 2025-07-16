import time
import re

import ddddocr
import uiautomator2 as u2

from utils import get_current_app, find_button, close_xy_dialog

d = u2.connect()
# origin_timeout = d.shell("settings get system screen_off_timeout").output
# d.shell("settings put system screen_off_timeout 86400000")
d.app_start("com.taobao.idlefish", stop=True, use_monkey=True)
screen_width, screen_height = d.window_size()
ctx = d.watch_context()
ctx.when("暂不升级").click()
ctx.when("放弃").click()
ctx.when("确定").click()
ctx.start()
have_clicked = dict()
error_count = 0
ocr = ddddocr.DdddOcr(show_ad=False)
finish_count = 0
xy_task_name = ["领至高20元外卖红包", "浏览指定频道好物", "搜一搜推荐商品", "去浏览全新好物", "浏览推荐的国补商品", "去支付宝领积分", "去淘宝签到领红包", "去蚂蚁庄园逛一逛", "去逛一逛芭芭农场", "去支付宝农场领水果", "去蚂蚁森林逛一逛", "去百度逛一逛", "去饿了么果园领水果", "褥羊毛赚话费", "去天猫拿红包", "逛一逛淘宝人生", "去淘特领好礼", "上夸克天天领现金"]


def check_in_xy():
    home_view = d(className="android.webkit.WebView", text="闲鱼币首页")
    task_dialog = d(resourceId="taskWrap", className="android.view.View")
    if home_view.exists and task_dialog.exists:
        print("任务弹框存在")
        return True
    return False


def click_earn():
    while True:
        print("开始查找去赚钱按钮")
        if d(className="android.view.View", resourceId="taskWrap").exists:
            print("任务弹框存在")
            break
        throw_btn1 = d(className="android.view.View", resourceId="mapDiceBtn")
        if throw_btn1.exists:
            print("点击任务按钮")
            d.click(throw_btn1.bounds()[2] + 100, throw_btn1.center()[1] + 30)
        time.sleep(2)


def back_to_task():
    print("开始返回到闲鱼币首页。")
    try_count = 0
    while True:
        if check_in_xy():
            break
        else:
            back_btn = d.xpath('//android.view.View[@resource-id="root"]/android.view.View/android.view.View/android.view.View/android.view.View/android.widget.Image')
            if back_btn.exists and try_count % 4 == 0:
                print("点击后退按钮")
                back_btn.click()
                time.sleep(0.5)
            else:
                d.press("back")
                time.sleep(0.1)
            try_count += 1


def operate_task(task):
    _, activity = get_current_app(d)
    start_time = time.time()
    if task == "浏览指定频道好物":
        while True:
            if time.time() - start_time > 24:
                break
            d.swipe_ext("up", scale=0.3)
            time.sleep(0.5)
        d(scrollable=True).fling.vert.toBeginning(max_swipes=1000)
        time.sleep(2)
        click_earn()
    else:
        print("普通页面")
        search_view = d(className="android.view.View", text="搜索有福利")
        search_edit = d(resourceId="com.taobao.taobao:id/searchEdit")
        search_btn = d(resourceId="com.taobao.taobao:id/searchbtn")
        if search_view.exists and d(className="android.widget.Button", text="搜索").exists:
            d(className="android.widget.EditText", instance=0).send_keys("笔记本电脑")
            d(className="android.widget.Button", text="搜索").click()
            time.sleep(2)
        elif search_edit.exists and search_btn.exists:
            search_edit.send_keys("笔记本电脑")
            search_btn.click()
            time.sleep(2)
        time.sleep(3)
        print("开始上下滑动")
        start_time = time.time()
        tap_index = 0
        while True:
            if tap_index % 4 == 0 and tap_index > 0:
                d.swipe_ext("down", scale=0.4)
            else:
                d.swipe_ext("up", scale=0.4)
            time.sleep(0.3)
            tap_index += 1
            if time.time() - start_time > 25:
                break
        print("滑动完毕，开始退出")
        back_to_task()


time.sleep(5)
ctx.wait_stable()
while True:
    sign_btn1 = d(resourceId="com.taobao.idlefish:id/icon_entry_lottie", className="android.widget.ImageView", clickable=True)
    sign_btn2 = d(className="android.widget.ImageView", resourceId="com.taobao.idlefish:id/icon_entry")
    print(f"查找签到按钮，存在:{sign_btn1.exists}, {sign_btn2.exists}")
    if sign_btn1.exists:
        d.click(sign_btn1.center()[0], sign_btn1.center()[1])
        time.sleep(2)
    elif sign_btn2.exists:
        d.click(sign_btn2.center()[0], sign_btn2.center()[1])
        time.sleep(2)
    if d(className="android.webkit.WebView", text="闲鱼币首页").exists:
        print("已经进入闲鱼页面")
        break
    time.sleep(1)
time.sleep(10)
close_xy_dialog(d)
click_earn()
while True:
    try:
        print("正在查找按钮...")
        time.sleep(4)
        sign_btn = d(className="android.widget.TextView", text="签到")
        if sign_btn.exists:
            d.click(sign_btn.center()[0], sign_btn.center()[1])
            time.sleep(4)
        receive_btn = d(className="android.widget.TextView", text="领取奖励")
        if receive_btn.exists:
            receive_btn.click()
            print("点击领取奖励")
            finish_count += 1
            time.sleep(2)
            continue
        task_view = d.xpath(f"//android.view.View[@resource-id='taskWrap']/android.view.View[last()]/android.view.View/android.widget.TextView[{' or '.join([f"@text='{text}'" for text in xy_task_name])}]")
        if task_view.exists:
            task_name = task_view.get_text()
            print(f"查找任务:{task_name}")
            todo_btn = task_view.child("./following-sibling::android.widget.TextView[@text='去完成'][1]")
            if todo_btn.exists:
                todo_btn.click()
                if have_clicked.get(task_name) is None:
                    have_clicked[task_name] = 1
                else:
                    have_clicked[task_name] += 1
                time.sleep(5)
                operate_task(task_name)
        else:
            finish_view = d(className="android.widget.TextView", text="已完成")
            if finish_view.exists:
                break
            else:
                d.swipe_ext(u2.Direction.FORWARD)
    except Exception as e:
        print("报错", e)
        continue
print(f"共自动化完成{finish_count}个任务")
d.click(screen_width//2, 250)
click_count = 2
while click_count >= 0:
    receive_btn2 = d(className="android.view.View", resourceId="dailyRewardBox")
    if receive_btn2.exists:
        print("点击领取收益")
        receive_btn2.click()
        time.sleep(3)
    else:
        break
    click_count -= 1
throw_btn = d(className="android.view.View", resourceId="mapDiceBtn")
while True:
    print("开始摇骰子...")
    count_btn = throw_btn.child(className="android.widget.TextView", index=0)
    if count_btn.exists:
        print(f"摇骰子次数：{count_btn.get_text()}")
        numbers = re.findall(r'\d+', count_btn.get_text())
        if len(numbers) <= 0:
            break
        count = int(numbers[0])
        if count > 0:
            d.click(throw_btn.center()[0], throw_btn.center()[1])
            time.sleep(5)
            draw_btn = d(className="android.widget.TextView", text="开始抽奖")
            if draw_btn.exists:
                d.click(draw_btn.center()[0], draw_btn.center()[1])
                time.sleep(10)
                continue
            receive_btn3 = d(className="android.widget.TextView", text="领取奖励")
            if receive_btn3.exists:
                d.click(receive_btn3.center()[0], receive_btn3.center()[1])
                time.sleep(3)
                continue
            know_btn = d(className="android.widget.TextView", text="我知道了")
            if know_btn.exists:
                d.click(know_btn.center()[0], know_btn.center()[1])
                time.sleep(3)
                continue
            scratch_btn = d(className="android.widget.TextView", text="开始刮奖")
            if scratch_btn.exists:
                scratch_btn.click()
                time.sleep(15)
                continue
            in_btn = d(className="android.widget.TextView", text="收下礼物")
            if in_btn.exists:
                in_btn.click()
                time.sleep(3)
                continue
            continue_btn = d(className="android.widget.TextView", text="继续寻宝")
            if continue_btn.exists:
                continue_btn.click()
                time.sleep(3)
                continue
            screen_image = d.screenshot(format='opencv')
            pt1 = find_button(screen_image, "./img/fish_advance.png")
            if pt1:
                d.click(int(pt1[0]) + 50, int(pt1[1]) + 20)
                time.sleep(3)
                continue
            pt2 = find_button(screen_image, "./img/fish_continue.png")
            if pt2:
                d.click(int(pt2[0]) + 50, int(pt2[1]) + 20)
                time.sleep(3)
                continue
            pt3 = find_button(screen_image, "./img/fish_continue2.png")
            if pt3:
                d.click(int(pt3[0]) + 50, int(pt3[1]) + 20)
                time.sleep(3)
                continue
            pt4 = find_button(screen_image, "./img/fish_prize.png")
            if pt4:
                d.click(int(pt4[0]) + 100, int(pt4[1]) + 80)
                time.sleep(3)
                continue
            pt5 = find_button(screen_image, "./img/fish_swing.png")
            if pt5:
                d.click(int(pt5[0]) + 50, int(pt5[1]) + 50)
                time.sleep(10)
                continue
    else:
        break
    time.sleep(2)
print("任务完成。。。")
ctx.stop()
