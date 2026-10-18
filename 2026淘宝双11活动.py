import re
import time
import xml.etree.ElementTree as ET

import uiautomator2 as u2
from utils import check_chars_exist, other_app, get_current_app, select_device, task_loop, check_verify, start_app, TB_APP, check_popup

# 2026 版淘金币页面把「体力」改成了「能量」，把「跳一跳拿钱」改成了「升级赛车拿钱/加速升级」，
# 这里统一用正则同时兼容新旧两套文案，避免活动改版后脚本一直空转。
POWER_RE = r"(?:体力|能量)"
TASK_TITLE_RE = r"做任务赚" + POWER_RE            # 做任务赚体力 / 做任务赚能量
GAME_BTN_RE = re.compile(r"跳一跳拿钱|升级赛车拿钱|加速升级")
POWER_NUM_RE = re.compile(r"剩余\s*(\d+)\s*" + POWER_RE)
TASK_BTN_RE = re.compile(r"^(?:去完成|去逛逛|去浏览|逛一逛|立即领|去领取|去看看|搜一下|玩一把|捐一笔|逛一下)$")
ROW_RE = re.compile(r"\(\d+/\d+\)")

have_clicked = dict()
error_count = 0
time1 = time.time()
selected_device = select_device()
d = u2.connect(selected_device)
print(f"已成功连接设备：{selected_device}")

# 屏幕熄灭时所有控件查找都会“假成功/假失败”，先把屏幕点亮
# 这里不能让 d.info 抛错把整个脚本打断，所以包一层 try
try:
    if not d.info.get("screenOn", True):
        print("检测到屏幕已熄灭，正在点亮")
        d.screen_on()
        time.sleep(1)
except Exception as e:
    print(f"读取屏幕状态失败，跳过亮屏检查: {e}")

start_app(d, TB_APP, init=True)
screen_width, screen_height = d.window_size()
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
ctx.when(xpath="//android.widget.Image[@text='关闭']").click()
ctx.when(xpath="//android.widget.FrameLayout[@resource-id='com.taobao.taobao:id/poplayer_native_state_center_layout_frame_id']//android.widget.ImageView[@content-desc='关闭按钮']").click()
ctx.start()
time.sleep(3)


def dump_nodes(retry=2):
    """一次性拉取界面层级，返回 [{cls, text, desc, res, clickable, bounds}]。
    避免逐个元素调用 uiautomator 导致的慢速与 StaleObjectException。"""
    for _ in range(retry + 1):
        try:
            xml = d.dump_hierarchy()
            root = ET.fromstring(xml)
        except Exception as e:
            print(f"获取界面层级失败: {e}")
            time.sleep(1)
            continue
        nodes = []
        for el in root.iter("node"):
            attr = el.attrib
            m = re.search(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", attr.get("bounds", ""))
            if not m:
                continue
            nodes.append({
                "cls": attr.get("class", ""),
                "text": attr.get("text", ""),
                "desc": attr.get("content-desc", ""),
                "res": attr.get("resource-id", ""),
                "clickable": attr.get("clickable") == "true",
                "bounds": tuple(int(v) for v in m.groups()),
            })
        if nodes:
            return nodes
        time.sleep(1)
    return []


def tap_bounds(bounds):
    x = (bounds[0] + bounds[2]) // 2
    y = (bounds[1] + bounds[3]) // 2
    d.click(x, y)
    return x, y


def in_coin_page():
    """是否已经在淘金币页面（新旧版本文案都算）。
    注意：这里只能用 textContains，游戏按钮的文案很长
    （「升级中 长按可加速升级 … 升级赛车拿钱 剩余 1200 能量」），textMatches 是整串匹配会失效。"""
    if d(className="android.webkit.WebView", text="淘金币首页").exists:
        return True
    if d(resourceId="energy_task_button").exists:
        return True
    for keyword in ("赚能量", "赚体力", "升级赛车拿钱", "跳一跳拿钱"):
        if d(className="android.widget.Button", textContains=keyword).exists:
            return True
    return False


def in_task_page():
    return bool(d(className="android.widget.TextView", textMatches=TASK_TITLE_RE).exists)


def find_coin_btn(rounds=10):
    """从淘宝首页点「领淘金币」进入淘金币页面。
    注意：原来这里等的是「跳一跳拿钱」，2026 版已经改成「升级赛车拿钱」，所以会无限空转。"""
    for i in range(1, rounds + 1):
        if in_coin_page():
            print("已进入淘金币页面")
            return
        coin_btn = d(classNameMatches=r"android.widget.FrameLayout|android.view.View", description="领淘金币")
        if coin_btn.exists:
            print(f"点击首页「领淘金币」入口 ({i}/{rounds})")
            try:
                tap_bounds(coin_btn[0].bounds())
            except Exception as e:
                print(f"点击入口失败: {e}")
        else:
            print(f"未找到「领淘金币」入口 ({i}/{rounds})，等待页面加载")
        # 秒级轮询，页面一出来就继续，避免停留太久被活动弹窗盖住
        for _ in range(12):
            time.sleep(0.5)
            if in_coin_page():
                print("已进入淘金币页面")
                return
    raise RuntimeError("进不去淘金币页面：请确认淘宝停留在首页、屏幕已解锁且未被弹窗遮挡")


def to_task(rounds=6):
    """在淘金币页面点「赚体力/赚能量」打开任务面板。
    活动版页面加载后几秒会弹出「看加购优惠得能量」之类的广告，抢在弹窗出现前点才点得动。"""
    for i in range(1, rounds + 1):
        if in_task_page():
            print("进入任务页面。。。")
            return
        earn_btn = d(resourceId="energy_task_button")
        if not earn_btn.exists:
            earn_btn = d(className="android.widget.Button", text="赚能量")
        if not earn_btn.exists:
            earn_btn = d(className="android.widget.Button", text="赚体力")
        if earn_btn.exists:
            print(f"点击「赚能量/赚体力」({i}/{rounds})")
            try:
                tap_bounds(earn_btn[0].bounds())
            except Exception as e:
                print(f"点击任务按钮失败: {e}")
        else:
            print(f"未找到「赚能量」按钮 ({i}/{rounds})")
        # 点击后 5 秒内轮询面板，一旦出现立即返回
        for _ in range(10):
            time.sleep(0.5)
            if in_task_page():
                print("进入任务页面。。。")
                return
        # 面板没出来，通常是活动弹窗挡住了，先关弹窗再重试
        close_btn = d(className="android.widget.Button", text="关闭")
        if close_btn.exists:
            print("关闭遮挡弹窗")
            try:
                tap_bounds(close_btn[0].bounds())
            except Exception:
                pass
            time.sleep(1)
    raise RuntimeError("打不开「做任务赚能量」任务面板：多半被活动弹窗遮挡，请手动关掉弹窗后重试")


def check_in_task():
    return in_task_page()


def back_to_task():
    print("开始返回任务页面")
    for i in range(1, 31):
        try:
            temp_package, temp_activity = get_current_app(d)
            if not temp_package or not temp_activity:
                time.sleep(0.5)
                continue
            if "Ext2ContainerActivity" in temp_activity:
                time.sleep(0.5)
                continue
            print(f"{temp_package}--{temp_activity}")
            if TB_APP not in temp_package:
                print(f"回到原始APP,{TB_APP}")
                start_app(d, TB_APP)
                jump_btn = d(resourceId="com.taobao.taobao:id/tv_close", text="跳过")
                if jump_btn.exists:
                    jump_btn.click()
                    time.sleep(2)
                continue
            check_popup(d)
            if check_in_task():
                print("当前是任务列表画面，不能继续返回")
                return
            if in_coin_page():
                # 还在淘金币页面，只是任务面板被关掉了，重新打开面板即可
                print("任务面板已关闭，重新打开")
                try:
                    to_task()
                    return
                except Exception as e:
                    print(f"重新打开任务面板失败: {e}")
                    continue
            close_btn1 = d.xpath("//android.widget.FrameLayout[@resource-id='com.alipay.multiplatform.phone.xriver_integration:id/frameLayout_rightButton1']/android.widget.LinearLayout/android.widget.RelativeLayout/android.widget.RelativeLayout/android.widget.FrameLayout[2]")
            if close_btn1.exists:
                print("点击关闭小程序按钮")
                close_btn1.click()
                time.sleep(1)
                continue
            task_view = d.xpath('//android.widget.TextView[contains(@text, "限时下单任务")]')
            if task_view.exists:
                close_btn2 = d.xpath('//android.widget.TextView[contains(@text, "限时下单任务")]/preceding-sibling::android.view.View[1]')
                if close_btn2.exists:
                    print("点击关闭限时下单任务按钮")
                    close_btn2.click()
                    time.sleep(1)
                    continue
            print("点击后退")
            d.press("back")
            time.sleep(0.5)
        except Exception as e:
            print(f"返回任务页面出现异常: {e}")
            time.sleep(1)
    print("多次返回仍未回到任务页，重新进入淘金币任务")
    find_coin_btn()
    to_task()


def collect_task_buttons(nodes):
    """把「去完成」类按钮和它左边同一行的任务名配对。
    2026 版任务行的文案被合并成一个 TextView（如「逛一逛蚂蚁庄园(0/1)逛一逛蚂蚁庄园+600」），
    原来的 sibling 定位方式在这里取不到任务名，所以改成按坐标配对。"""
    rows = [n for n in nodes if n["cls"] == "android.widget.TextView" and ROW_RE.search(n["text"])]
    result = []
    for btn in nodes:
        if btn["cls"] != "android.widget.Button":
            continue
        if not TASK_BTN_RE.match(btn["text"].strip()):
            continue
        bx1, by1, bx2, by2 = btn["bounds"]
        bcy = (by1 + by2) // 2
        name, best = None, 9999
        for row in rows:
            rx1, ry1, rx2, ry2 = row["bounds"]
            if rx2 > bx1 + 10:  # 任务名必须整行都在按钮左侧
                continue
            dy = abs((ry1 + ry2) // 2 - bcy)
            if dy < 60 and dy < best:
                name, best = row["text"], dy
        if not name:
            name = f"未知任务_y{bcy}"
        name = re.split(r"[(（]", name)[0].strip() or name
        result.append((name, btn))
    return result


def first_button(nodes, pattern):
    for n in nodes:
        if n["cls"] == "android.widget.Button" and re.fullmatch(pattern, n["text"].strip()):
            return n
    return None


find_coin_btn()
to_task()
finish_count = 0
loop_round = 0
MAX_LOOP = 400  # 主循环兜底上限，防止某个「立即领取」按钮一直点不动导致死循环
while loop_round < MAX_LOOP:
    loop_round += 1
    try:
        time.sleep(4)
        check_verify(d)
        nodes = dump_nodes()
        if not nodes:
            error_count += 1
            print(f"读取界面失败 {error_count}")
            if error_count >= 3:
                break
            continue

        draw_down_btn = first_button(nodes, r"立即领取")
        if draw_down_btn:
            tap_bounds(draw_down_btn["bounds"])
            print("点击立即领取")
            time.sleep(2)
            continue

        print("开始查找按钮。。。")
        get_btn = first_button(nodes, r"领取奖励")
        if get_btn:
            tap_bounds(get_btn["bounds"])
            print("点击领取奖励")
            time.sleep(2)
            continue

        de_btn = first_button(nodes, r"点击得")
        if de_btn:
            tap_bounds(de_btn["bounds"])
            print("点击点击得")
            time.sleep(4)
            continue

        tasks = collect_task_buttons(nodes)
        chosen = None
        for name, btn in tasks:
            if check_chars_exist(name):
                continue
            if have_clicked.get(name, 0) >= 2:
                continue
            chosen = (name, btn)
            break
        if chosen:
            task_name, btn = chosen
            print("点击按钮", task_name)
            have_clicked[task_name] = have_clicked.get(task_name, 0) + 1
            tap_bounds(btn["bounds"])
            time.sleep(3.5)
            task_loop(d, back_to_task, duration=18)
            finish_count = finish_count + 1
            error_count = 0
        else:
            error_count += 1
            print(f"未找到可点击按钮 {error_count}（当前任务数 {len(tasks)}）")
            if error_count >= 2:
                break
    except Exception as e:
        print(e)
        continue
else:
    print(f"主循环达到上限 {MAX_LOOP} 轮，强制结束任务阶段")

print(f"共自动化完成{finish_count}个任务")

# 收起任务面板，回到淘金币首页
close_btn = d(className="android.widget.Button", text="关闭")
if close_btn.exists:
    try:
        tap_bounds(close_btn[0].bounds())
        time.sleep(2)
    except Exception:
        pass
d.click(screen_width // 2, 200)
time.sleep(2)

print("开始跳一跳/升级赛车")
game_round = 0
while game_round < 60:
    game_round += 1
    nodes = dump_nodes()
    if not nodes:
        time.sleep(3)
        continue
    close_btn = first_button(nodes, r"关闭")
    if close_btn:
        tap_bounds(close_btn["bounds"])
        time.sleep(2)
        continue
    game_btn = next((n for n in nodes if n["cls"] == "android.widget.Button" and GAME_BTN_RE.search(n["text"])), None)
    if not game_btn:
        print("未找到「跳一跳拿钱/升级赛车」按钮，结束")
        break
    match = POWER_NUM_RE.search(game_btn["text"])
    if not match:
        print(f"按钮文案解析不出剩余能量: {game_btn['text'][:40]}")
        break
    phy_num = int(match.group(1))
    if phy_num < 10:
        print(f"剩余能量不足({phy_num})，结束")
        break
    print(f"当前剩余{('能量' if '能量' in game_btn['text'] else '体力')}：{phy_num}")
    bx1, by1, bx2, by2 = game_btn["bounds"]
    center_x, center_y = (bx1 + bx2) // 2, (by1 + by2) // 2
    if phy_num < 50:
        d.click(center_x, center_y)
    else:
        d.long_click(center_x, center_y, 3)
    time.sleep(7)
else:
    print("升级赛车循环达到上限，结束")

ctx.close()
d.shell("settings put system accelerometer_rotation 0")
print("关闭手机自动旋转")
time2 = time.time()
minutes, seconds = divmod(int(time2 - time1), 60)
print(f"共耗时: {minutes} 分钟 {seconds} 秒")
