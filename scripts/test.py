import cv2

# # read input image
# img = cv2.imread('../images/Dashboard.mp4')

# # flip the image by vertically
# img_v = cv2.flip(img, 0)

# # display the rotated image
# cv2.imshow("Vertical Flip", img_v)
# cv2.waitKey(0)
# cv2.destroyAllWindows()


cap = cv2.VideoCapture('../images/Dashboard.mp4')

while(cap.isOpened()):
    ret,frame = cap.read()
    
    frame = cv2.resize(frame, (1200,700))
    frame = cv2.flip(frame, -1)
    cv2.imshow("video", frame)
    
    if(cv2.waitKey(10) & 0xFF == ord('q')):
        break
cap.release()
cap.destroyAllWindows()