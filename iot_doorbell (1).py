#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IoT security camera project
"""

import numpy as np
import cv2
import imutils
import time
import os
#alert msg
import twilio
import twilio.rest
from twilio.rest import Client
#aws upload
import boto3
from botocore.exceptions import NoCredentialsError

#AWS
# I comment out some of the access key that attach to my aws/twillo account keys/numbers, feel free to replace them with your keys
ACCESS_KEY = 'xxx'
SECRET_KEY = 'xxx'

def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)

    try:
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False
#aws
    
def mask_image(img):
    #bbox=cv2.selectROI(img,False)
    #print(bbox)
    mask=np.zeros((img.shape[0],img.shape[1]),dtype="uint8")
    pts=np.array([[1100,500],[1100,700],[100,700],[100,500]],dtype=np.int32)
    cv2.fillConvexPoly(mask,pts,255)
    masked=cv2.bitwise_and(img,img,mask=mask)
    gray=imutils.resize(masked,width=200)
    gray=cv2.cvtColor(gray,cv2.COLOR_BGR2GRAY)
    gray=cv2.GaussianBlur(gray,(11,11),0)
    
    return masked,gray

#counter variable for analysis
counter= 0

while True:

	counter=counter+1
	print(" ")
	print("----Times through loop since starting----",counter,"-$")
	print(" ")

	#take a 1st and 2nd image to compare
	#command='raspistill -w 1280 -h 720 -vf -hf -t 1000 -tl 1000 -o test%0d.jpg'
	command='raspistill -w 1280 -h 720 -t 1000 -tl 1000 -o test%0d.jpg'

	os.system(command)

	print("Captured 1st & 2nd image for analysis...")

	#mask images
	test1=cv2.imread("test0.jpg")
	test2=cv2.imread("test1.jpg")
	masked1,gray1=mask_image(test1)
	masked2,gray2=mask_image(test2)


	#compare the two images
	pixel_threshold=50

	detector_total=np.uint64(0)
	detector=np.zeros((gray2.shape[0],gray2.shape[1]),dtype="uint8")

	#pixel by pixel comparison
	for i in range(0,gray2.shape[0]):
		for j in range(0,gray2.shape[1]):
			if abs(int(gray2[i,j])-int(gray1[i,j]))>pixel_threshold:
				detector[i,j]=255

	#sum the detector array
	detector_total = np.uint64(np.sum(detector))
	print("detector_total= ", detector_total)
	print(" ")
 
	if detector_total>10000:
		print("Smart Doorbell has detected someone/something at the door!")
		#define a unique name for the new video file
		timestr=time.strftime("doorbell-%Y%m%d-%H%M%S")
        
		#command2='raspivid -t 2000 -w 1280 -h 720 -vf -hf -fps 30 -o ' + timestr + '.h264'
		command2='raspivid -t 2000 -w 1280 -h 720 -fps 30 -o ' + timestr + '.h264'
		os.system(command2)

		print("Finished recording...converting to mp4...")

		command3='MP4Box -fps 30 -add ' + timestr + '.h264 ' + timestr +'.mp4'
		os.system(command3)

		print("Finished converting file...available for viewing")
		
		#write masked images to file
		cv2.imwrite("gray1.jpg",gray1)
		cv2.imwrite("gray2.jpg",gray2)
		cv2.imwrite("masked1.jpg",masked1)
		cv2.imwrite("masked2.jpg",masked2)
		
		#upload video file to the cloud
		#fullDirectory='/home/pi/SmartDoorbell' + timestr + '.mp4'
		#command4='/home/pi/Dropbox-Uploader/dropbox_uploader.sh upload ' + fullDirectory + ' /'
		#os.system(command4)
		
		#send text message
		account_sid="xxx"
		auth_token="xxx"
		
		client=Client(account_sid,auth_token)
		message=client.api.account.messages.create(
		#	to="+16502239057",
            
			from_="+xxx",
			body="Smart Doorbell detection")
		
		uploaded = upload_to_aws('masked2.jpg', 'myiotcamera', 'iot-'+ timestr + '.jpg')
		print("AWS uploaded")
       
       
	else:
		print("Nothing detected..yet!")
