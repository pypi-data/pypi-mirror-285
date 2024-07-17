
import cv2
import numpy
import numpy as np
from PIL import Image, ImageDraw, ImageFont


def get_word_img(img, text, left=0, top=0, textColor=(0, 0, 0), textSize=50):
    if (isinstance(img, numpy.ndarray)):
        img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img)
    fontStyle = ImageFont.truetype("font/simsun.ttc", textSize, encoding="utf-8")
    draw.text((left, top), text, textColor, font=fontStyle)
    return cv2.cvtColor(numpy.asarray(img), cv2.COLOR_RGB2BGR)

def save_word_img(word):
    img = get_word_img(np.ones((50, 50, 3), dtype=np.uint8) * 255, word, 0, 0, (0, 0, 0), 50)
    img = Image.fromarray(img)
    img.save(r"C:\Users\14271\Desktop\del\word\{0}.jpg".format(word))

def show_word():
    # 将读取的字符串打印出来
    pass

if __name__ == '__main__':


    # img = get_word_img(np.ones((50, 50, 3), dtype=np.uint8) * 255, "好的", 0, 0, (0, 0, 0), 50)
    # img = Image.fromarray(img)
    # img.save(r"C:\Users\14271\Desktop\del\word\")

    for ch in range(0x4e00, 0x9fa6):
        save_word_img(chr(ch))
        print(chr(ch))
    # img[img < 253] = 1
    # img[img >= 253] = 8
    #
    # for i in range(img.shape[0]):
    #     a = list(img[i][:,0])
    #     new_line = []
    #     for each in a:
    #         if each == 8:
    #             new_line.append("  ")
    #         else:
    #             new_line.append("██")
    #     print("".join(new_line))

