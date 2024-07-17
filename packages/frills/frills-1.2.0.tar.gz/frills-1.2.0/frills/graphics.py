import cv2
import sys


def showw(message, image):
	cv2.imshow(message, image)
	cv2.waitKey(0)
	cv2.destroyAllWindows()


def showx(message, image):
	cv2.imshow(message, image)
	cv2.waitKey(0)
	cv2.destroyAllWindows()
	sys.exit()