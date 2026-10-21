import time
import re
import random
import uiautomator2 as u2

from utils import (
    get_current_app,
    find_button,
    close_xy_dialog,
    FISH_APP,
    start_app,
    check_app,
    select_device,
)

selected_device = select_device()
d = u2.connect(selected_device)
print(f"已成功连接设备：{selected_device}")

start_app(d, FISH_APP, init=False)
screen_width, screen_height = d.window_size()

ctx = d.watch_context()
ctx.when("暂不升级").click()
ctx.when("放弃").click()
ctx.when("确定").click()
ctx.when("我知道了").click()
ctx.when("收下礼物").click()
ctx.when("开心收下").click()
ctx.when("全部收下").click()
ctx.when("残忍离开").click()
ctx.when('//android.widget.ImageView[@resource-id="com.taobao.idlefish:id/fish_layer_js_native_window_background_view"]/following-sibling::android.widget.RelativeLayout/android.widget.FrameLayout/android.widget.ImageView[2]').click()
ctx.start()

finish_count = 0

GAME_KEYWORDS = [
    "玩游戏", "消了还想消", "玩1关", "向往的生活", "点点消不停", "织梦森林", "赵云与阿斗", "游戏", "合成", "主线"
]

_ocr_reader = None

def get_ocr():
    global _ocr_reader
    if _ocr_reader is None:
        import easyocr
        _ocr_reader = easyocr.Reader(['ch_sim', 'en'], gpu=True)
    return _ocr_reader


def is_game_task(task_title):
    """严格过滤游戏类任务（按用户要求跳过）"""
    return any(k in task_title for k in GAME_KEYWORDS)


def check_in_xy():
    """检测当前是否已在闲鱼币/大富翁寻宝主页面"""
    if d.xpath("//*[@resource-id='mapStepBtn' or @resource-id='mapDiceBtn']").exists:
        return True
    if d.xpath("//*[contains(@text, '完成1圈') or contains(@text, '圈数挑战') or contains(@text, '当前已完成')]").exists:
        return True
    return False


def to_task():
    """自动导航进入闲鱼币寻宝首页"""
    for try_i in range(12):
        if check_in_xy():
            print("已成功在闲鱼币寻宝页面")
            break

        check_popup()

        # 1. 尝试旧版首页浮动入口
        sign_btn1 = d(resourceId="com.taobao.idlefish:id/icon_entry_lottie")
        sign_btn2 = d(className="android.widget.ImageView", resourceId="com.taobao.idlefish:id/icon_entry")
        if sign_btn1.exists:
            print("点击首页浮动签到图标 (lottie)")
            sign_btn1.click()
            time.sleep(3)
        elif sign_btn2.exists:
            print("点击首页浮动签到图标")
            sign_btn2.click()
            time.sleep(3)
        else:
            # 2. 新版：点击底栏「我的」 -> 点击「闲鱼币」
            me_btn = d.xpath("//*[@text='我的']")
            if me_btn.exists:
                print("点击底栏「我的」")
                me_btn.click()
                time.sleep(2)
            coin_btn = d.xpath("//*[contains(@text, '闲鱼币')]")
            if coin_btn.exists:
                print("点击「闲鱼币」入口")
                coin_btn.click()
                time.sleep(4)

        if check_in_xy():
            print("已经进入闲鱼币寻宝页面")
            break
        time.sleep(1)

    time.sleep(3)
    close_xy_dialog(d)


def check_popup():
    """处理寻宝过程中弹出的各类奖励、事件与提示"""
    w, h = d.window_size()

    # 1. 真实小游戏页面误入处理（通过页面文本精准识别，避免后台 Activity 误判）
    if d.xpath("//*[contains(@text, '游戏任务入口') or contains(@text, '再玩1关游戏')]").exists:
        print("检测到误入小程序页面，正在点击胶囊退出...")
        d.click(1331, 259)
        time.sleep(1.5)
        leave = d.xpath("//*[contains(@text, '残忍离开')]")
        if leave.exists:
            leave.click()
            time.sleep(1.5)
        return

    # 2. 道具/宝箱获得弹窗（"道具可至「背包」查看使用"）
    item_p = d.xpath("//*[contains(@text, '道具可至「背包」查看使用')]")
    if item_p.exists:
        print("检测到道具弹窗，正在关闭...")
        d.click(w // 2, int(h * 0.795))
        time.sleep(2)
        return

    # 3. 圈数通关通报弹窗与立即领取
    lap_claim = d.xpath("//*[@text='立即领取' or @text='开心收下' or @text='全部收下']")
    if lap_claim.exists:
        print("点击通关奖励:", lap_claim.attrib.get("text", ""))
        lap_claim.click()
        time.sleep(2)
        close_btn = d.xpath("//*[@text='关闭']")
        if close_btn.exists:
            close_btn.click()
            time.sleep(1.5)
        return

    # 4. 浏览20秒领100闲鱼币事件
    browse_task = d.xpath("//*[contains(@text, '浏览') and contains(@text, '秒获得') and contains(@text, '闲鱼币')]")
    if browse_task.exists:
        print(f"触发地图事件：{browse_task.attrib.get('text', '')}，开始模拟浏览21秒...")
        start_t = time.time()
        while time.time() - start_t < 21:
            d.swipe(w // 2, int(h * 0.7), w // 2, int(h * 0.4), 0.4)
            time.sleep(2.5)
        back_btn = d.xpath("//*[@text='返回']")
        if back_btn.exists:
            back_btn.click()
        else:
            d.press("back")
        time.sleep(3)
        return

    # 5. 立刻前进
    forward_btn = d.xpath("//*[@text='立刻前进']")
    if forward_btn.exists:
        print("点击「立刻前进」")
        forward_btn.click()
        time.sleep(4)
        return

    # 6. 定时收益「领」
    gain_btn = d.xpath("//*[@text='领']")
    if gain_btn.exists:
        print("点击收取闲鱼币定时收益「领」")
        gain_btn.click()
        time.sleep(2)
        return

    # 7. 常见奖励与确认弹窗
    claim_btn = d.xpath("//*[contains(@text, '收下') or @text='全部收下' or @text='开心收下' or @text='我知道了' or @text='确认' or @text='继续前进' or @text='继续寻宝' or @text='开始抽奖' or @text='开始刮奖']")
    if claim_btn.exists:
        print("点击弹窗按钮:", claim_btn.attrib.get("text", ""))
        claim_btn.click()
        time.sleep(2)
        return

    # 8. 图像模板匹配备用
    try:
        screen_image = d.screenshot(format='opencv')
        for template_name in ["fish_advance.png", "fish_continue.png", "fish_continue2.png", "fish_advance2.png", "fish_prize.png", "fish_throw.png"]:
            pt = find_button(screen_image, f"./img/{template_name}")
            if pt:
                print(f"模板匹配命中 {template_name}，点击对应区域")
                d.click(int(pt[0]) + 50, int(pt[1]) + 20)
                time.sleep(3)
                return
    except Exception:
        pass


def scroll_map_to_top():
    """滑动重置闲鱼币大富翁地图到顶部，使步数按钮可见且有效"""
    w, h = d.window_size()
    d.swipe(w // 2, 500, w // 2, int(h * 0.8), 0.3)
    time.sleep(1.5)
    d.swipe(w // 2, 500, w // 2, int(h * 0.8), 0.3)
    time.sleep(2)


def open_task_panel():
    """打开日常任务面板浮层（若已在面板则直接返回）"""
    if d.xpath("//*[@text='去完成' or contains(@text, '领取奖励') or contains(@text, '提醒签到')]").exists:
        return True
    print("点击右侧浮动「做任务/赚步数」图标打开面板...")
    d.click(1293, 1871)
    time.sleep(2.5)
    return d.xpath("//*[@text='去完成' or contains(@text, '领取奖励') or contains(@text, '提醒签到')]").exists


def close_task_panel():
    """通过向下滑动抽屉抽拉栏，稳定关闭任务面板浮层"""
    w, h = d.window_size()
    d.swipe(w // 2, 600, w // 2, 1900, 0.25)
    time.sleep(2)


def throw_dice_loop():
    """循环掷骰子/走步数直至耗尽"""
    print("准备开始自动掷骰子/走步数...")
    close_task_panel()
    scroll_map_to_top()
    max_rounds = 40
    while max_rounds > 0:
        max_rounds -= 1
        check_popup()

        step_btn = d.xpath("//*[@resource-id='mapStepBtn']")
        if step_btn.exists:
            btn_text = step_btn.attrib.get("text", "").strip()
            m = re.findall(r"(\d+)步$", btn_text)
            if not m or int(m[-1]) <= 0:
                print(f"当前无剩余可用步数: {btn_text}")
                break

            steps = int(m[-1])
            print(f"当前剩余 {steps} 步，点击前进！")
            step_btn.click()
            time.sleep(5)
            check_popup()
            time.sleep(1.5)
            continue
        break


def claim_task_rewards():
    """收取任务面板上所有已完成的待领奖励（包括阶段奖励 +100, +300, +500 等）"""
    claimed = 0
    # 1. 查找“领取奖励”按钮
    for btn in d.xpath("//*[contains(@text, '领取奖励')]").all():
        print("点击领取奖励:", btn.attrib.get("text", ""))
        btn.click()
        time.sleep(2)
        claimed += 1

    # 2. 查找顶部阶段奖励 (+100已领取, +300已领取, +500可领)
    for stage in d.xpath("//*[contains(@text, '+100') or contains(@text, '+300') or contains(@text, '+500')]").all():
        text = stage.attrib.get("text", "")
        if "领取" in text or "可领" in text or "完成" in text:
            stage.click()
            time.sleep(1.5)
            claimed += 1

    # 3. 定时收益「领」
    gain_btn = d.xpath("//*[@text='领']")
    if gain_btn.exists:
        print("点击收取闲鱼币定时收益「领」")
        gain_btn.click()
        time.sleep(1.5)
        claimed += 1

    return claimed


def handle_video_task(title, btn_to_click):
    """执行视频任务：观看18秒，OCR智能识别跳过与确认退出"""
    print(f"🎬 开始执行视频任务: [{title}]")
    btn_to_click.click()
    time.sleep(3)

    print("正在观看视频广告 (18秒)...")
    time.sleep(18)

    w, h = d.window_size()
    # 智能跳过广告
    try:
        reader = get_ocr()
        img = d.screenshot(format='opencv')
        results = reader.readtext(img)
        skip_clicked = False
        for bbox, text, prob in results:
            if '跳过' in text and prob > 0.3:
                cx = int((bbox[0][0] + bbox[2][0]) / 2)
                cy = int((bbox[0][1] + bbox[2][1]) / 2)
                print(f"OCR识别到「跳过」按钮，点击坐标 ({cx}, {cy})")
                d.click(cx, cy)
                skip_clicked = True
                break

        if not skip_clicked:
            # 常见位置兜底：右上角
            d.click(int(w * 0.916), int(h * 0.084))

        time.sleep(2)
        # 检查是否有二次确认弹窗（坚持退出 / 残忍离开 / 离开）
        img2 = d.screenshot(format='opencv')
        results2 = reader.readtext(img2)
        for bbox, text, prob in results2:
            if any(k in text for k in ['坚持退出', '残忍离开', '离开']) and prob > 0.3:
                cx = int((bbox[0][0] + bbox[2][0]) / 2)
                cy = int((bbox[0][1] + bbox[2][1]) / 2)
                print(f"OCR识别到确认弹窗「{text}」，点击坐标 ({cx}, {cy})")
                d.click(cx, cy)
                break
    except Exception as e:
        print(f"OCR跳过异常，使用兜底逻辑: {e}")
        d.click(int(w * 0.916), int(h * 0.084))
        time.sleep(1.5)
        d.click(int(w * 0.5), int(h * 0.69))

    time.sleep(2.5)

    # 确保返回闲鱼主界面
    for _ in range(3):
        # 检查是否误入小程序页面
        if d.xpath("//*[contains(@text, '游戏任务入口') or contains(@text, '再玩1关游戏')]").exists:
            d.click(1331, 259)
            time.sleep(1.5)
            leave = d.xpath("//*[contains(@text, '残忍离开')]")
            if leave.exists:
                leave.click()
                time.sleep(1.5)

        if not check_in_xy():
            d.press("back")
            time.sleep(2)
        else:
            break

    open_task_panel()
    time.sleep(1.5)
    claim_task_rewards()


def handle_channel_goods(title, btn_to_click):
    """执行点击指定频道好物任务：点击商品浏览3秒后返回"""
    print(f"🛍️ 开始执行频道好物任务: [{title}]")
    btn_to_click.click()
    time.sleep(3.5)

    w, h = d.window_size()
    item = d.xpath("//*[contains(@text, '抵') or contains(@text, '¥') or contains(@text, '￥')]")
    if item.exists:
        print("点击好物商品卡片:", item.attrib.get("text", "")[:15])
        item.click()
    else:
        d.click(w // 2, int(h * 0.4))

    time.sleep(3.5)
    print("浏览好物详情完成，返回任务面板...")
    d.press("back")
    time.sleep(2.5)

    # 如果返回到了「我的」个人主页，重新进入闲鱼币
    if d.xpath("//*[contains(@text, '在闲鱼赚了') or contains(@text, '我的交易')]").exists:
        coin_btn = d.xpath("//*[contains(@text, '闲鱼币')]")
        if coin_btn.exists:
            coin_btn.click()
            time.sleep(3.5)

    open_task_panel()
    time.sleep(1.5)
    claim_task_rewards()


def handle_feed_items():
    """执行主界面「点击10个宝贝，可获得步数+3」任务"""
    close_task_panel()
    time.sleep(1.5)
    w, h = d.window_size()

    # 向下滑动到瀑布流宝贝区域
    print("滑动到主界面底部宝贝瀑布流...")
    d.swipe(w // 2, int(h * 0.8), w // 2, int(h * 0.2), 0.3)
    time.sleep(2)

    # 检查是否还有剩余未点击的宝贝
    xml = d.dump_hierarchy()
    m = re.findall(r"点击(\d+)个宝贝", xml)
    remaining = int(m[0]) if m else 0
    if remaining <= 0:
        print("「点击宝贝」任务已全部完成！")
        scroll_map_to_top()
        return

    print(f"检测到剩余需点击 {remaining} 个宝贝，开始自动浏览...")
    for round_i in range(remaining):
        print(f"正在浏览第 {round_i + 1}/{remaining} 个宝贝...")
        item = d.xpath("//*[contains(@text, '¥') or contains(@text, '￥') or contains(@text, '抵')]")
        if item.exists:
            item.click()
        else:
            d.click(int(w * 0.3), int(h * 0.6))

        time.sleep(3)
        d.press("back")
        time.sleep(2)

        # 稍微向下滑动查看新宝贝
        d.swipe(w // 2, int(h * 0.65), w // 2, int(h * 0.45), 0.3)
        time.sleep(1)

    print("宝贝点击任务完成，重置地图至顶部...")
    scroll_map_to_top()
    time.sleep(2)
    check_popup()


def handle_regular_browse(title, btn_to_click):
    """执行普通浏览类任务（浏览16秒后返回）"""
    print(f"👀 开始执行浏览任务: [{title}]")
    btn_to_click.click()
    time.sleep(4)

    w, h = d.window_size()
    start_b = time.time()
    while time.time() - start_b < 16:
        d.swipe(w // 2, int(h * 0.7), w // 2, int(h * 0.4), 0.4)
        time.sleep(2.5)

    # 返回闲鱼
    d.press("back")
    time.sleep(2.5)

    open_task_panel()
    time.sleep(1.5)
    claim_task_rewards()


# =========================================================
# 主运行逻辑
# =========================================================
print("=== 启动闲鱼币大富翁与全量任务引擎 ===")
to_task()
time.sleep(2)
check_popup()

# 1. 优先走完已有步数
throw_dice_loop()

# 2. 打开日常任务面板并循环处理所有可做及可重复任务
if open_task_panel():
    print("已成功打开任务面板！")

    # 签到
    sign_btn = d.xpath("//*[@text='签到']")
    if sign_btn.exists:
        print("点击每日签到")
        sign_btn.click()
        time.sleep(2)

    claim_task_rewards()

    # 循环多轮，直至没有非游戏类的去完成任务
    max_panel_loops = 15
    while max_panel_loops > 0:
        max_panel_loops -= 1
        claim_task_rewards()

        # 扫描当前面板上的所有任务
        task_rows = []
        for node in d.xpath("//*[@bounds and @text]").all():
            title = node.attrib.get("text", "").strip()
            b = node.attrib.get("bounds", "")
            m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", b)
            if not m:
                continue
            x1, y1, x2, y2 = map(int, m.groups())
            # 任务标题位于左侧，且长度适中
            if x1 < 800 and 600 <= y1 <= 3150 and len(title) >= 4:
                # 严格跳过游戏类和发宝贝任务
                if is_game_task(title) or "发布" in title:
                    continue

                cy = (y1 + y2) // 2
                # 寻找该行右侧去完成按钮
                btn_to_click = None
                for btn in d.xpath("//*[@text='去完成']").all():
                    bb = btn.attrib.get("bounds", "")
                    bm = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bb)
                    if bm and int(bm.group(1)) > 950 and abs((int(bm.group(2)) + int(bm.group(4))) // 2 - cy) < 90:
                        btn_to_click = btn
                        break

                if btn_to_click:
                    task_rows.append((title, btn_to_click))

        if not task_rows:
            print("当前可视区域无待完成非游戏任务，尝试向下滑动扫描...")
            d.swipe(screen_width // 2, int(screen_height * 0.7), screen_width // 2, int(screen_height * 0.4), 0.3)
            time.sleep(2)
            # 再查一次
            for node in d.xpath("//*[@bounds and @text]").all():
                title = node.attrib.get("text", "").strip()
                b = node.attrib.get("bounds", "")
                m = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", b)
                if m:
                    x1, y1, x2, y2 = map(int, m.groups())
                    if x1 < 800 and 600 <= y1 <= 3150 and len(title) >= 4:
                        if not is_game_task(title) and "发布" not in title:
                            cy = (y1 + y2) // 2
                            for btn in d.xpath("//*[@text='去完成']").all():
                                bb = btn.attrib.get("bounds", "")
                                bm = re.match(r"\[(\d+),(\d+)\]\[(\d+),(\d+)\]", bb)
                                if bm and int(bm.group(1)) > 950 and abs((int(bm.group(2)) + int(bm.group(4))) // 2 - cy) < 90:
                                    task_rows.append((title, btn))
                                    break
            if not task_rows:
                print("所有非游戏任务已全部扫描并完成！")
                break

        print(f"本轮检测到 {len(task_rows)} 个待处理非游戏任务")
        for title, btn in task_rows:
            if "视频" in title:
                handle_video_task(title, btn)
            elif "好物" in title or "指定频道" in title:
                handle_channel_goods(title, btn)
            else:
                handle_regular_browse(title, btn)

            finish_count += 1
            claim_task_rewards()
            time.sleep(1)

    # 3. 执行主界面点击10个宝贝任务
    handle_feed_items()

# 4. 把所有新获得的步数全部走完
throw_dice_loop()

# 5. 最后收割一轮阶段奖励
open_task_panel()
time.sleep(1)
claim_task_rewards()
close_task_panel()

# 6. 充能领奖（如果有）
power_btn = d.xpath("//*[contains(@text, '充能领奖') or contains(@text, '点击充能')]")
if power_btn.exists:
    print("点击充能领奖")
    power_btn.click()
    time.sleep(2)

ctx.stop()
print(f"==================================================")
print(f"🎉 闲鱼币任务全量完成！共计执行 {finish_count} 轮任务")
print(f"==================================================")
