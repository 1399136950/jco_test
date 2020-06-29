import cv2

for i in range(1,35):

    img = cv2.imread('{}.png'.format(i),1)

    img1 = cv2.imread('{}.jpg'.format(i),1)

    res = cv2.matchTemplate(img1, img, cv2.TM_CCORR) # 进行匹配

    res1 = cv2.matchTemplate(img1, img, cv2.TM_CCOEFF) # 进行匹配

    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res) # 使用cv2.minMaxLoc()函数可以得到最大匹配值的坐标
    min_val1, max_val1, min_loc1, max_loc1 = cv2.minMaxLoc(res1)
    #print(min_val, max_val, min_loc, max_loc)

    print(max_loc,max_loc1)


    cv2.rectangle(img1,max_loc,(max_loc[0]+60,max_loc[1]+158),255,2)

    cv2.imshow('{}.jpg'.format(i),img1)

    cv2.waitKey(0)
    cv2.destroyAllWindows()
    #print(max_loc[0])

    
