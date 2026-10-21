import time
import random
import re
import uiautomator2 as u2

from utils import (
    check_chars_exist,
    other_app,
    get_current_app,
    select_device,
    task_loop,
    check_verify,
    start_app,
    TB_APP,
    check_popup,
    print_error,
    start_watcher,
)

unclick_btn = []
have_clicked = dict()
error_count = 0
time1 = time.time()
selected_device = select_device()
d = u2.connect(selected_device)
print(f"已成功连接设备：{selected_device}")

start_app(d, TB_APP, init=True)
screen_width, screen_height = d.window_size()
ctx = start_watcher(d)
time.sleep(3)


def browse_shopping_list(d, max_rounds=3):
    """新版淘金币：在「淘宝购物清单」每浏览15秒得30金币页面自动下滑浏览"""
    w, h = d.window_size()
    round_idx = 0
    print("检测到已进入「淘宝购物清单」滑动赚金币页面")
    while round_idx < max_rounds:
        # 检查是否已达到本轮或今日上限
        is_limit = d.xpath("//*[contains(@text, '当前页下单另得') or contains(@text, '今日已领完') or contains(@text, '明日再来')]").exists
        has_timer = d.xpath("//*[contains(@text, '每浏览') and contains(@text, '秒得')]").exists
        if is_limit and not has_timer:
            print("购物清单浏览任务已达到上限，准备退出")
            break

        print(f"开始购物清单第 {round_idx + 1} 轮浏览（约16秒）...")
        start_t = time.time()
        while time.time() - start_t < 16:
            sy = random.randint(h // 2 + 100, h - 400)
            ey = sy - random.randint(350, 650)
            d.swipe(w // 2, sy, w // 2, ey, random.uniform(0.3, 0.6))
            time.sleep(random.uniform(2, 3))

        round_idx += 1
        time.sleep(2)

    print("完成购物清单浏览，按返回键回任务面板")
    d.press("back")
    time.sleep(3)


def handle_quiz(d):
    """处理淘金币趣味答题/课堂"""
    print("检测到答题页面，正在自动作答...")
    time.sleep(2)
    # 点击任意选项（例如 A 或第一项）
    opts = d.xpath("//*[contains(@text, '能') or @text='A' or @text='B']")
    if opts.exists:
        opts[0].click()
        time.sleep(1)
    # 确认提交
    ok = d.xpath("//*[contains(@text, '我选好了') or contains(@text, '确定') or contains(@text, '提交')]")
    if ok.exists:
        ok.click()
        time.sleep(2)
    print("答题完成，返回任务面板")
    d.press("back")
    time.sleep(3)


def check_in_task():
    """判断当前是否已在任务面板或金币主界面"""
    package_name, activity_name = get_current_app(d)
    if package_name != TB_APP:
        return False

    if "com.taobao.tao.welcome.Welcome" in (activity_name or ""):
        find_coin_btn()
        find_earn_btn()
        return True

    if "com.taobao.themis.container.app.TMSActivity" in (activity_name or ""):
        # 检查是否在新版任务面板
        if d.xpath("//*[contains(@text, '完成下方任务得额外金币') or contains(@text, '更多金币等你赚') or contains(@text, '任务已完成')]").exists:
            return True
        # 检查是否在购物清单浏览页
        if d.xpath("//*[contains(@text, '淘宝购物清单') or contains(@text, '每浏览')]").exists:
            return True
        # 检查是否在淘金币首页
        if d.xpath("//*[contains(@text, '淘金币首页') or contains(@text, '淘金币标题')]").exists:
            earn_btn = d.xpath("//*[contains(@text, '赚更多金币')]")
            if earn_btn.exists:
                earn_btn.click()
                time.sleep(3)
            return True

    return False


def back_to_task():
    """做完单项任务后返回金币任务页面"""
    print("开始返回任务页面")
    max_try = 8
    while max_try > 0:
        max_try -= 1
        try:
            temp_package, temp_activity = get_current_app(d)
            if not temp_package:
                continue

            if TB_APP not in temp_package:
                print(f"回到淘宝主应用: {TB_APP}")
                start_app(d, TB_APP)
                time.sleep(2)
            else:
                check_popup(d)
                if check_in_task():
                    print("已成功返回任务页面")
                    break

                close_btn = d.xpath("//android.widget.ImageView[@content-desc='关闭按钮' or @content-desc='关闭']")
                if close_btn.exists:
                    close_btn.click()
                    time.sleep(2)
                    continue

                print("执行返回上一页")
                d.press("back")
                time.sleep(1.5)
        except Exception:
            print_error()


def find_coin_btn():
    """从淘宝首页进入淘金币"""
    coin_btn = d(classNameMatches=r"android.widget.FrameLayout|android.view.View", description="领淘金币")
    if coin_btn.exists:
        print("点击领淘金币按钮")
        d.double_click(coin_btn[0].center()[0], coin_btn[0].center()[1])
        time.sleep(5)
    else:
        search_bar = d(className="android.view.View", description="搜索栏")
        if search_bar.exists:
            search_bar.click()
            time.sleep(1)
            search_edit = d(resourceId="com.taobao.taobao:id/searchEdit")
            if search_edit.exists:
                search_edit.send_keys("淘金币")
                time.sleep(2)
                d(className="android.view.View", descriptionContains="淘金币").click()
                time.sleep(5)


def find_earn_btn():
    """在淘金币首页打开任务面板"""
    time.sleep(3)
    # 检查是否有回日常版按钮
    back_btn = d(className="android.widget.Button", textContains="回日常版")
    if back_btn.exists(timeout=3):
        back_btn.click()
        time.sleep(2)

    # 首页签到
    sign_btn = d.xpath("//*[contains(@text, '签到领金币') or contains(@text, '点击签到') or contains(@text, '已帮你自动签到')]")
    if sign_btn.exists and not d.xpath("//*[contains(@text, '已完成')]").exists:
        sign_btn.click()
        time.sleep(2)

    # 检查气泡可领金币
    claim_bubble = d.xpath("//*[contains(@text, '可领') and not(contains(@text, '明天'))]")
    if claim_bubble.exists:
        print("领取首页可领金币:", claim_bubble.attrib.get("text", ""))
        claim_bubble.click()
        time.sleep(2)

    # 点击赚更多金币
    more_btn = d.xpath("//*[contains(@text, '赚更多金币')]")
    if more_btn.exists:
        print("点击「赚更多金币」打开任务面板")
        more_btn.click()
        time.sleep(3)
    else:
        print("未直接找到赚更多金币按钮，尝试继续检测当前页面")


def claim_pending_rewards():
    """收割任务面板上已经完成待领取的金币奖励"""
    claimed = 0
    # 查找如 +60, +30, 领取奖励, 立即领取 等待领按钮
    reward_nodes = d.xpath("//*[(@text='领取奖励' or @text='立即领取' or @text='点击得') or (contains(@text, '+') and not(contains(@text, '额外得')))]").all()
    for node in reward_nodes:
        b = node.attrib.get("bounds", "")
        t = node.attrib.get("text", "")
        m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", b)
        if m:
            x1, y1, x2, y2 = map(int, m.groups())
            # 按钮在屏幕右侧任务栏区域
            if x1 >= 1000 and 500 <= y1 <= 2700:
                print(f"收割待领取金币奖励: {t} @ ({ (x1+x2)//2 }, { (y1+y2)//2 })")
                d.click((x1 + x2) // 2, (y1 + y2) // 2)
                time.sleep(2)
                claimed += 1
    return claimed


# ---------------------------
# 主流程开始
# ---------------------------
ctx.wait_stable()
close_btn = d(className="android.widget.ImageView", description="关闭按钮")
if close_btn and close_btn.exists:
    close_btn.click()
    time.sleep(2)

find_coin_btn()
find_earn_btn()

finish_count = 0
empty_task_count = 0

print("进入淘金币任务循环...")

while True:
    try:
        time.sleep(3)
        check_verify(d)
        check_popup(d)

        # 1. 如果当前停留在「淘宝购物清单」浏览页面，优先处理下滑浏览
        if d.xpath("//*[contains(@text, '淘宝购物清单') or contains(@text, '每浏览')]").exists:
            browse_shopping_list(d)
            finish_count += 1
            continue

        # 2. 如果停留在答题页面，处理答题
        if d.xpath("//*[contains(@text, '淘金币趣味答题') or contains(@text, '淘金币答题')]").exists:
            handle_quiz(d)
            finish_count += 1
            continue

        # 3. 如果在淘金币主页但任务面板未呼出，点击「赚更多金币」呼出
        if not d.xpath("//*[contains(@text, '完成下方任务得额外金币') or contains(@text, '任务已完成') or contains(@text, '逛清单')]").exists:
            more_btn = d.xpath("//*[contains(@text, '赚更多金币')]")
            if more_btn.exists:
                print("重新唤起任务面板")
                more_btn.click()
                time.sleep(3)

        # 4. 优先收取已完成任务的浮动金币奖励（如 +60、领取）
        claimed_num = claim_pending_rewards()
        if claimed_num > 0:
            finish_count += claimed_num
            time.sleep(2)

        # 5. 扫描新版任务列表里的任务
        task_candidates = []
        for node in d.xpath("//*[@bounds and @text]").all():
            text = node.attrib.get("text", "").strip()
            bounds = node.attrib.get("bounds", "")
            m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bounds)
            if not m:
                continue
            x1, y1, x2, y2 = map(int, m.groups())
            # 标题特征：在屏幕左半部分、高度在任务面板区、长度大于3且非纯数字或符号
            if x1 < 800 and 700 <= y1 <= 2600 and len(text) >= 4:
                # 排除说明文字与广告
                if any(w in text for w in ["为你找到", "注：以上", "完成下方任务", "更多金币等你赚", "任务已完成"]):
                    continue
                task_candidates.append((text, (x1, y1, x2, y2)))

        found_task = False
        for task_title, (tx1, ty1, tx2, ty2) in task_candidates:
            # 黑名单过滤（如“下单”、“买商品”、“充值”、“拉好友助力”等）
            if check_chars_exist(task_title):
                continue

            # 重复点击控制（同一个任务最多点2次，避免卡死）
            if have_clicked.get(task_title, 0) >= 2:
                continue

            cy = (ty1 + ty2) // 2

            # 在该任务行右侧寻找操作按钮 (x >= 1000)
            btn_coord = None
            for b_node in d.xpath("//*[@bounds]").all():
                b_str = b_node.attrib.get("bounds", "")
                b_m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", b_str)
                if not b_m:
                    continue
                bx1, by1, bx2, by2 = map(int, b_m.groups())
                # 判断水平对齐在同一行
                if bx1 >= 950 and (by1 - 50 <= cy <= by2 + 50):
                    b_text = b_node.attrib.get("text", "").strip()
                    if "已完成" in b_text:
                        btn_coord = None
                        break
                    btn_coord = ((bx1 + bx2) // 2, (by1 + by2) // 2)

            # 如果没抓到具体子节点，采用该行右侧默认安全按钮点击坐标
            if not btn_coord:
                btn_coord = (int(screen_width * 0.88), cy)

            print(f"执行任务: [{task_title}] -> 点击位置: {btn_coord}")
            have_clicked[task_title] = have_clicked.get(task_title, 0) + 1
            d.click(btn_coord[0], btn_coord[1])
            time.sleep(4)

            # 点击后判断跳转页面类型
            if d.xpath("//*[contains(@text, '淘宝购物清单') or contains(@text, '每浏览')]").exists:
                browse_shopping_list(d)
            elif d.xpath("//*[contains(@text, '淘金币趣味答题') or contains(@text, '答题')]").exists:
                handle_quiz(d)
            else:
                # 普通浏览任务，浏览 16 秒后返回
                task_loop(d, back_to_task, duration=16)

            finish_count += 1
            found_task = True
            empty_task_count = 0
            break

        # 6. 如果新版未匹配到任务，兼容尝试老版原生按钮
        if not found_task:
            old_btns = d(className="android.widget.Button", textMatches=r"去完成|去逛逛|去浏览|逛一逛|去看看|去领取")
            if old_btns.exists:
                for view in old_btns:
                    if view not in unclick_btn:
                        view.click()
                        time.sleep(3.5)
                        task_loop(d, back_to_task, duration=16)
                        finish_count += 1
                        found_task = True
                        empty_task_count = 0
                        break

        # 7. 如果当前屏幕未找到可执行任务，稍微上滑面板查看更多
        if not found_task:
            empty_task_count += 1
            print(f"当前视窗未发现新任务 ({empty_task_count}/3)，尝试微幅上滑...")
            d.swipe(screen_width // 2, int(screen_height * 0.75), screen_width // 2, int(screen_height * 0.55), 0.5)
            time.sleep(2)
            if empty_task_count >= 3:
                print("所有可用日常任务已扫描完毕或无可继续执行任务，正常退出")
                break

    except Exception as e:
        print_error()
        time.sleep(3)
        continue

ctx.close()
print(f"=== 淘金币任务执行完成，共完成 {finish_count} 个任务 ===")
d.shell("settings put system accelerometer_rotation 0")
time2 = time.time()
minutes, seconds = divmod(int(time2 - time1), 60)
print(f"总耗时: {minutes} 分钟 {seconds} 秒")
