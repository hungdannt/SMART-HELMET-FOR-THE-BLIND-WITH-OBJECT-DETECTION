import cv2

# IMG_PATH = 'D:\\Documents\\Picture\\Data\\data_3000\\IMG (555).jpg'
IMG_PATH = 'D:\\Documents\\Picture\\Data\\data_5000\\'

# read image
for _ in range (0,5462):
    try:
        path = str(IMG_PATH + "IMG (" + str(_) + ").jpg")
        img = cv2.imread(path)
        # print(IMG_PATH, img.shape)
        new_width = 416
        new_height = 416
        img_resized = cv2.resize(src=img, dsize=(new_width, new_height))
        reisze_img_name = "IMG (" + str(_) + ").jpg"
        cv2.imwrite(reisze_img_name, img_resized)
        print(reisze_img_name, img_resized.shape)

        print('Done')
    except:
        print("Can not get image")
        continue