import ddddocr
import cv2
from PIL import Image


def practical_example():
    """
    实际应用示例：识别图片中的特定信息
    """
    # 初始化OCR
    det_ocr = ddddocr.DdddOcr(det=True, show_ad=False)
    rec_ocr = ddddocr.DdddOcr(show_ad=False)

    image_path = "screenshot.png"

    with open(image_path, 'rb') as f:
        image_bytes = f.read()

    # 检测所有文字区域
    bboxes = det_ocr.detection(image_bytes)

    # 按位置排序（从上到下，从左到右）
    bboxes.sort(key=lambda bbox: (bbox[1], bbox[0]))  # 先按y坐标，再按x坐标排序

    # 识别每个区域的文字
    img_pil = Image.open(image_path)
    recognized_text = []

    for i, bbox in enumerate(bboxes):
        x1, y1, x2, y2 = bbox
        cropped = img_pil.crop((x1, y1, x2, y2))

        # 使用BytesIO进行识别
        from io import BytesIO
        img_byte_arr = BytesIO()
        cropped.save(img_byte_arr, format='PNG')

        text = rec_ocr.classification(img_byte_arr.getvalue())
        recognized_text.append({
            'text': text,
            'position': bbox,
            'area': (x2 - x1) * (y2 - y1)
        })

    # 输出整理后的结果
    print("=== 图片文字识别结果 ===")
    for i, item in enumerate(recognized_text):
        print(f"{i + 1:2d}. 位置: {item['position']} | 文字: '{item['text']}'")

    return recognized_text


# 运行示例
results = practical_example()
print(results)