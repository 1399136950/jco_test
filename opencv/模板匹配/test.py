import cv2

def match_tmp(src_img_path, tmp_img_path):
    srcImage = cv2.imread(src_img_path, 1)
    templateImage = cv2.imread(tmp_img_path, 1)
    h, w = templateImage.shape[:2]  # rows->h, cols->w
    res = cv2.matchTemplate(srcImage, templateImage, cv2.TM_CCOEFF_NORMED)
    
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
    print (max_val)
    left_top = max_loc  # 左上角
    return left_top # 返回匹配的左上角坐标
    right_bottom = (left_top[0] + w, left_top[1] + h)  # 右下角
    cv2.rectangle(srcImage, left_top, right_bottom, (0,255,17), 1)  # 画出矩形位置
    cv2.imshow('',srcImage)
    cv2.waitKey(0)

res = match_tmp('src.jpg','111.png')
print(res)


# 参考文章
# https://www.jianshu.com/p/c20adfa72733
# https://www.jianshu.com/p/31034e8e195f
