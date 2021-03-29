#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
COEN243 Project
IoT Security Camera
Team: Alex Law and Elita Liu
"""

import numpy as np
import cv2
import imutils
import time
import os
#twilio alert msg
import twilio
import twilio.rest
from twilio.rest import Client
#aws upload
import boto3
from botocore.exceptions import ClientError

#AWS
#access keys that attach to my AWS account are commented with 'xxx', feel free to replace 'xxx' with your AWS keys
access_key = 'xxx'
secret_access_key = 'xxx'
def upload_to_aws(local_file_location, aws_bucket, aws_s3file):
    s3 = boto3.client('s3', aws_access_key_id = access_key, aws_secret_access_key = secret_access_key)
    try:
        s3.upload_file(local_file_location, aws_bucket, aws_s3file)
        print("Success!")
        return True
    except FileNotFoundError:
        print("No File Found")
        return False

# Define the mask area that you want to bring to your photos for reducing the interferences of the environment
# Then, apply Gray Scale and Gaussian Blur to the masked photo for reducing the noise of your detected area
def create_initial_mask(img):
	#Mask photo
    initial_mask=np.zeros((img.shape[0],img.shape[1]),dtype="uint8")
    points=np.array([[1100,500],[1100,700],[100,700],[100,500]],dtype=np.int32)
    cv2.fillConvexPoly(initial_mask,points,255)
    initial_masked=cv2.bitwise_and(img,img,initial_mask=initial_mask)
	#Gray and blur photo
    grayscale=imutils.resize(initial_masked,width=200)
    grayscale=cv2.cvtColor(grayscale,cv2.COLOR_BGR2grayscale)
    grayscale=cv2.GaussianBlur(grayscale,(11,11),0)
    return initial_masked,grayscale

#count variable for analysis
count= 0

while True:

	count=count+1
	print(" --- Times through loop since starting --- ",count,"-$")
	print(" ")

	#take 2 photos to compare
	command='raspistill -w 1280 -h 720 -t 1000 -tl 1000 -o test%0d.jpg'
	os.system(command)
	print("Captured the 1st and 2nd photos for analysis...")

	#mask, gray and blur photos
	test1=cv2.imread("test0.jpg")
	test2=cv2.imread("test1.jpg")
	initial_masked1,grayscale1=create_initial_mask(test1)
	initial_masked2,grayscale2=create_initial_mask(test2)

	#compare two photos
	pixel_limit=50
	detector_sum=np.uint64(0)
	detector=np.zeros((grayscale2.shape[0],grayscale2.shape[1]),dtype="uint8")

	#pixel by pixel comparison
	for i in range(0,grayscale2.shape[0]):
		for j in range(0,grayscale2.shape[1]):
			if abs(int(grayscale2[i,j])-int(grayscale1[i,j]))>pixel_limit:
				detector[i,j]=255

	#sum the detector array
	detector_sum = np.uint64(np.sum(detector))
	print("detector_sum= ", detector_sum)
	print(" ")
 
	if detector_sum>10000:
		print("IoT Security Camera has detected someone near the door!")

		#define a unique name for video file and record a video
		timestamp=time.strftime("doorbell-%Y%m%d-%H%M%S")
		command2='raspivid -t 2000 -w 1280 -h 720 -fps 30 -o ' + timestamp + '.h264'
		os.system(command2)
		print("Finished recording...Converting to mp4...")
		command3='MP4Box -fps 30 -add ' + timestamp + '.h264 ' + timestamp +'.mp4'
		os.system(command3)
		print("Finished converting file...Available for viewing...")
		
		#write initial_masked photos to file
		cv2.imwrite("grayscale1.jpg",grayscale1)
		cv2.imwrite("grayscale2.jpg",grayscale2)
		cv2.imwrite("initial_masked1.jpg",initial_masked1)
		cv2.imwrite("initial_masked2.jpg",initial_masked2)
		
		#send a text message
		#Twilio account id and auth_token is commented out with 'xxx', feel free to apply your Twilio account id and auth_token here
		account_sid="xxx"
		auth_token="xxx"
		client=Client(account_sid,auth_token)
		message=client.api.account.messages.create(
			to="+xxx",
            # add your phone number here
			from_="+xxx",
			# add your Twilio virtual phone number here
			body="Your IoT Security Camera has detected someone near the door! Please verify this person in your AWS S3!")
		
		#upload photo to AWS cloud
		uploaded = upload_to_aws('initial_masked2.jpg', 'myiotcamera', 'iot-'+ timestamp + '.jpg')
		print("AWS uploaded")
       
	else:
		print("--- Nothing Detected Yet ---")