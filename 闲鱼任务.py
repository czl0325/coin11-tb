import time
import re

import uiautomator2 as u2

from utils import get_current_app, fish_not_click, find_button, majority_chinese
import ddddocr

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


def click_earn():
    while True:
        if d(className="android.view.View", resourceId="taskWrap").exists:
            break
        throw_btn1 = d(className="android.view.View", resourceId="mapDiceBtn")
        if throw_btn1.exists:
            d.click(throw_btn1.bounds()[2] + 50, throw_btn1.center()[1] + 30)
            time.sleep(5)
        time.sleep(2)


def back_to_ad():
    while True:
        _, activity = get_current_app(d)
        if activity == "com.taobao.idlefish.ads.ylh.YlhPortraitADActivity":
            break
        d.press("back")
        time.sleep(0.2)


def back_to_task(to_treasure=False):
    print("开始返回到闲鱼币首页。")
    try_count = 0
    while True:
        if d(className="android.webkit.WebView", text="闲鱼币首页").exists:
            print("当前是闲鱼币首页，不能继续返回")
            break
        elif to_treasure and d(className="android.widget.TextView", text="我的夺宝").exists:
            print("当前是我的夺宝页面，不能继续返回")
            break
        else:
            pt = find_button(d.screenshot(format='opencv'), "./img/fish_back.png", (0, 0, 300, 500))
            if pt and try_count <= 2:
                print("点击后退按钮, ", int(pt[0]) + 15, int(pt[1]) + 25)
                d.click(int(pt[0]) + 15, int(pt[1]) + 25)
                try_count += 1
            else:
                d.press("back")
            time.sleep(0.1)


def check_popup():
    continue_btn = d(className="android.widget.TextView", text="继续寻宝")
    if continue_btn.exists:
        continue_btn.click()
        return
    screen_image1 = d.screenshot(format='opencv')
    pt11 = find_button(screen_image1, "./img/fish_close.png")
    if pt11:
        d.click(int(pt11[0]) + 15, int(pt11[1]) + 15)
        return
    pt22 = find_button(screen_image1, "./img/fish_close2.png")
    if pt22:
        d.click(int(pt11[0]) + 15, int(pt11[1]) + 15)
        return


def operate_task(to_treasure=False):
    _, activity = get_current_app(d)
    if activity == "com.taobao.idlefish.ads.ylh.YlhPortraitADActivity":
        print("第一种情况：去微信看短剧或点击广告看详情")
        while True:
            click_btn = d(className="android.widget.TextView", textContains="点击广告")
            if click_btn.exists:
                detail_btn = d(className="android.widget.TextView", text="查看详情")
                if detail_btn.exists:
                    d.click(detail_btn[0].center()[0], detail_btn[0].center()[1])
                    time.sleep(5)
                    back_to_ad()
                    image = d.screenshot(format='opencv')
                    pt = find_button(image, "./img/fish_close.png")
                    if pt:
                        d.click(int(pt[0]) + 5, int(pt[1]) + 5)
                        time.sleep(2)
                    break
            wechat_btn = d(className="android.widget.TextView", text="去微信看短剧")
            if wechat_btn.exists:
                d.click(wechat_btn[0].center()[0], wechat_btn[0].center()[1])
                time.sleep(20)
                back_to_ad()
                continue
            wechat_btn = d(className="android.widget.TextView", text="去微信继续看")
            if wechat_btn.exists:
                d.click(wechat_btn[0].center()[0], wechat_btn[0].center()[1])
                time.sleep(8)
                back_to_ad()
                continue
            wechat_btn = d(className="android.widget.TextView", text="去微信看全集")
            if wechat_btn.exists:
                image = d.screenshot(format='opencv')
                pt = find_button(image, "./img/fish_close.png")
                if pt:
                    d.click(int(pt[0]) + 5, int(pt[1]) + 5)
                    time.sleep(2)
                break
    elif activity == "com.taobao.idlefish.ads.csj.TTAdStandardPortraitActivity":
        print("第二种情况：我要直接拿奖励")
        while True:
            direct_btn = d(className="android.widget.TextView", text="我要直接拿奖励")
            if direct_btn.exists:
                d.click(direct_btn[0].center()[0], direct_btn[0].center()[1])
                time.sleep(20)
                break
            detail_btn = d(className="android.widget.TextView", text="查看详情")
            if detail_btn.exists:
                print("点击查看详情，跳转app。")
                d.click(detail_btn[0].center()[0], detail_btn[0].center()[1])
                time.sleep(5)
                break
            time_div = d(className="android.widget.TextView", textMatches=r"\d+s")
            if time_div.exists:
                time.sleep(int(time_div[0].get_text().replace("s", "")) + 3)
                break
            time.sleep(3)
        back_to_task()
    else:
        if d(className="android.widget.TextView", textMatches=r"继续浏览\d+s获1个骰子").exists:
            print("首页滑动，开始模拟滑动")
            start_time = time.time()
            while True:
                if time.time() - start_time > 24:
                    break
                d.swipe_ext("up", scale=0.4)
                time.sleep(0.5)
            d(scrollable=True).fling.vert.toBeginning(max_swipes=1000)
            time.sleep(2)
            click_earn()
        elif d(className="android.webkit.WebView", text="闲鱼币首页").exists:
            return
        elif d(className="android.widget.TextView", text="我的夺宝").exists:
            print("现金夺宝页面...")
            treasures_btn = d(className="android.widget.TextView", text="我的夺宝")
            if treasures_btn.exists:
                d.click(screen_width / 2, treasures_btn[0].bounds()[3] + 50)
                time.sleep(5)
                red_btn = d(className="android.widget.TextView", textMatches=r"获得\d+个红包.*")
                if red_btn.exists:
                    d.click(red_btn[0].bounds()[2] - 50, red_btn[0].center()[1])
                    time.sleep(5)
                    pt = find_button(d.screenshot(format='opencv'), "./img/fish_open.png")
                    if pt:
                        d.click(int(pt[0]) + 40, int(pt[1]) + 15)
                        print("点击一键开启")
                        time.sleep(5)
                    while True:
                        if d(className="android.widget.TextView", text="我的夺宝").exists:
                            break
                        d.press("back")
                        time.sleep(0.2)
            take_part_btn = d(className="android.widget.TextView", textContains="500币")
            if take_part_btn.exists:
                d.click(take_part_btn[0].center()[0], take_part_btn[0].center()[1])
                time.sleep(2)
                pt = find_button(d.screenshot(format='opencv'), "./img/fish_confirm_attend.png")
                if pt:
                    d.click(screen_width / 2, int(pt[1]) + 20)
                    time.sleep(2)
            back_to_task()
        elif d(className="android.webkit.WebView", text="好物夺宝").exists:
            print("好物夺宝页面...")
            # re_btn = d(className="android.widget.Image", text="TB1NMQKL7voK1RjSZPfXXXPKFXa-112-78")
            treasures_btn = d(className="android.widget.TextView", textContains="闲鱼币夺宝")
            if treasures_btn.exists:
                d.click(treasures_btn[0].center()[0], treasures_btn[0].center()[1])
                time.sleep(4)
                treasures_btn = d(className="android.widget.TextView", textContains="闲鱼币夺宝")
                d.click(treasures_btn[0].center()[0], treasures_btn[0].center()[1])
                time.sleep(2)
                reduce_btn = d(className="android.widget.Image", text="O1CN01FnFgEu1pxA2fVZtOh_!!6000000005426-0-tps-330-330")
                if reduce_btn.exists:
                    d.click(reduce_btn[0].center()[0], reduce_btn[0].center()[1])
                    time.sleep(1)
                    d.click(reduce_btn[0].center()[0], reduce_btn[0].center()[1])
                    time.sleep(1)
                bet_btn = d(className="android.widget.TextView", text="确定投注")
                if bet_btn.exists:
                    bet_btn.click()
                    time.sleep(2)
                    tou_btn = d(className="android.widget.TextView", text="直接投1注")
                    if tou_btn.exists:
                        d.click(tou_btn[0].center()[0], tou_btn[0].center()[1])
                        time.sleep(2)
            back_to_task()
        elif d(className="android.webkit.WebView", text="红包签到").exists:
            print("红包签到页面...")
            ball_btn = d(className="android.widget.View", resourceId="wingBallId")
            if ball_btn.exists:
                d.click(ball_btn[0].center()[0], ball_btn[0].center()[1])
                time.sleep(2)
            back_to_task()
        else:
            advert_text = d(className="android.widget.TextView", textContains="广告")
            if advert_text.exists:
                print("看广告领取奖励页面")
                while True:
                    touch_btn = d(className="android.widget.TextView", text="点击广告可领取奖励")
                    if touch_btn.exists:
                        download_btn = d(className="android.widget.TextView", text="立即下载")
                        if download_btn.exists:
                            d.click(50, download_btn[0].center()[1])
                            time.sleep(5)
                            back_to_task()
                            break
                    time.sleep(3)
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
                while True:
                    d.swipe_ext(u2.Direction.FORWARD)
                    time.sleep(1)
                    d.swipe_ext(u2.Direction.BACKWARD)
                    time.sleep(1)
                    if time.time() - start_time > 30:
                        break
                print("滑动完毕，开始退出")
                back_to_task(to_treasure)


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
check_popup()
click_earn()
swipe_count = 0
find_count = 0
no_button = 0
while True:
    try:
        print("正在查找按钮...")
        time.sleep(4)
        check_popup()
        sign_btn = d(className="android.widget.TextView", text="签到")
        if sign_btn.exists:
            d.click(sign_btn.center()[0], sign_btn.center()[1])
            time.sleep(4)
        receive_btn = d(className="android.widget.TextView", text="领取奖励")
        if receive_btn.exists:
            d.click(receive_btn.center()[0], receive_btn.center()[1])
            print("点击领取奖励")
            finish_count += 1
            find_count = 5
            time.sleep(2)
            continue
        to_btn = d(className="android.widget.TextView", text="去完成", )
        if to_btn.exists:
            no_button = 0
            need_click_view = None
            task_name = None
            if finish_count > 5:
                to_btn = reversed(to_btn)
            for btn in to_btn:
                # if btn.bounds()[1] < 1300:
                #     continue
                print("开始识别...")
                screen_shot = d.screenshot()
                cropped_rect = (200, btn.bounds()[1] - 50, btn.bounds()[0] - 50, btn.bounds()[1] + 30)
                cropped_image = screen_shot.crop(cropped_rect)
                task_name = ocr.classification(cropped_image)
                print(f"识别成功:{task_name}")
                if not majority_chinese(task_name):
                    continue
                if fish_not_click(task_name):
                    continue
                if task_name in have_clicked and have_clicked[task_name] >= 2:
                    continue
                need_click_view = btn
                break
            if need_click_view and task_name:
                d.click(need_click_view.center()[0], need_click_view.center()[1])
                print(f"点击按钮{task_name}")
                if have_clicked.get(task_name) is None:
                    have_clicked[task_name] = 1
                else:
                    have_clicked[task_name] += 1
                time.sleep(8 if "视频" in task_name else 3)
                operate_task()
            else:
                print(f"未找到可点击按钮。error_count={error_count},swipe_count={swipe_count},find_count={find_count}")
                if swipe_count > 10:
                    break
                if (swipe_count > 0 and find_count > 5) or swipe_count == 0:
                    swipe_count += 1
                    find_count = 0
                    d.shell("input swipe 540 2000 540 1400 200")
                    print("执行滑动")
                    time.sleep(5)
                find_count += 1
        else:
            no_button += 1
            if no_button > 2:
                print("未找到去完成按钮，退出循环")
                break
    except Exception as e:
        print("报错", e)
        continue
print(f"共自动化完成{finish_count}个任务")
task_close_btn = d(resourceId="taskWrap", className="android.view.View").child(className="android.widget.TextView", index=0)
if task_close_btn.exists:
    print("点击关闭任务列表")
    d.click(task_close_btn.center()[0], task_close_btn.center()[1])
    time.sleep(1)
receive_btn2 = d(className="android.widget.TextView", resourceId="dailyRewardBox")
if receive_btn2.exists:
    print("点击领取收益")
    click_count = 2
    while click_count >= 0:
        d.click(receive_btn2.center()[0], receive_btn2.bounds()[3] - 10)
        click_count -= 1
        time.sleep(2)
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
                d.click(scratch_btn.center()[0], scratch_btn.center()[1])
                time.sleep(15)
                continue
            in_btn = d(className="android.widget.TextView", text="收下礼物")
            if in_btn.exists:
                d.click(in_btn.center()[0], in_btn.center()[1])
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
# d.shell(f"settings put system screen_off_timeout {origin_timeout}")
ctx.stop()
