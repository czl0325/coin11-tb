import time

import uiautomator2 as u2
from utils import select_device, start_app, TMALL_APP

selected_device = select_device()
d = u2.connect(selected_device)
print(f"已成功连接设备：{selected_device}")
start_app(d, TMALL_APP, init=True)
ctx = d.watch_context()
ctx.when(xpath='//android.widget.FrameLayout[@resource-id="com.tmall.wireless:id/poplayer_native_state_center_layout_frame_id"]/android.widget.ImageView').click()
ctx.close()
d.shell("settings put system accelerometer_rotation 0")
print("关闭手机自动旋转")