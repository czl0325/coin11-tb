import ddddocr
import os
from PIL import Image
from paddleocr import PaddleOCR

os.environ['PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK'] = 'True'
ocr = ddddocr.DdddOcr(det=True, show_ad=False)

def practical_example():
    """
    实际应用示例：识别图片中的特定信息
    """
    # 初始化OCR
    det_ocr = ddddocr.DdddOcr(det=True, show_ad=False)
    rec_ocr = ddddocr.DdddOcr(show_ad=False)

    image_path = "text_ocr.jpg"

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


def get_sorted_text_from_region():
    # 2. 识别文字并获取坐标
    # 返回格式：[(box, text, score), ...]
    # box: 四个点的坐标，左上角是 box[0]
    image_path = "text_ocr.jpg"

    with open(image_path, 'rb') as f:
        image_bytes = f.read()
    result = ocr.detection(image_bytes)

    # 3. 按“从上到下，同行从左到右”排序
    # 先按 y 坐标（行）分组，再按 x 坐标（列）排序
    # 假设同一行文字的高度差在 20 像素以内
    line_height = 20
    lines = {}

    for box, text, score in result:
        # 取左上角坐标
        x, y = box[0]
        # 计算行号（向下取整，将相近高度的文字归为同一行）
        line_key = y // line_height

        # 将文字添加到对应的行
        if line_key not in lines:
            lines[line_key] = []
        lines[line_key].append((x, text))

    # 4. 按行号排序（从上到下），每行内按 x 坐标排序（从左到右）
    sorted_lines = sorted(lines.items(), key=lambda item: item[0])
    sentence_parts = []
    for line_key, words in sorted_lines:
        # 对当前行的文字按 x 坐标排序
        sorted_words = sorted(words, key=lambda w: w[0])
        # 提取文字内容
        line_text = ' '.join([word[1] for word in sorted_words])
        sentence_parts.append(line_text)
    # 5. 组合成完整句子（行与行之间用换行符或空格连接）
    # 使用换行符连接，保持原布局
    full_sentence = '\n'.join(sentence_parts)
    # 如果希望所有文字连成一行，可以用空格连接：
    # full_sentence = ' '.join(sentence_parts)
    return full_sentence


def paddle_ocr_test():
    ocr = PaddleOCR(use_angle_cls=True, lang='ch')
    image_path = 'text_ocr.jpg'
    result = ocr.ocr(image_path)
    texts = []
    for line in result[0]:  # result 是列表，result[0] 是当前图片的行信息
        text = line[1][0]  # line[1][0] 是识别的文字，line[1][1] 是置信度
        texts.append(text)
    # 拼接方式：可以直接连在一起，或者加空格/换行，根据你的图片实际情况调整
    full_sentence = ''.join(texts)  # 无空格直接拼接（适合连续文字）
    print("提取的完整文字：")
    print(full_sentence)
    # 可选：打印每行的置信度，便于检查准确性
    print("\n详细结果：")
    for line in result[0]:
        print(f"{line[1][0]}  (置信度: {line[1][1]:.3f})")


# 运行示例
paddle_ocr_test()
