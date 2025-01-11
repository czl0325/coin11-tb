

def check_chars_exist(text, chars=None):
    if chars is None:
        chars = ["拉好友", "快手", "抢红包", "搜索兴趣商品下单", "买精选商品", "全场3元3件", "固定入口", "农场小游戏", "砸蛋", "福气提现金", "大众点评", "蚂蚁新村", "消消乐", "玩一玩", "斗地主", "3元抢3件包邮到家", "拍一拍", "1元抢爆款好货", "拉1人助力", "玩消消乐", "淘宝秒杀", "下单即得", "添加签到神器", "下单得肥料", "开88VIP", "邀请好友"]
    for char in chars:
        if char in text:
            return True
    return False


other_app = ["蚂蚁森林", "农场", "百度", "支付宝", "芝麻信用", "蚂蚁庄园", "闲鱼", "神奇海洋", "淘宝特价版", "点淘", "饿了么", "微博", "直播间", "领肥料礼包"]
