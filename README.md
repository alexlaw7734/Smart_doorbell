# Smart_doorbell
A front-door security camera costs us a lot of money, both in installation and maintenance cost. A Raspberry Pi operating system was installed and configured to allow remote access and allow for the camera to be used. The camera is set up so it is able to see outside the front door. The program takes two photos in a loop and constantly checks the difference in pixels between a configured version of the two images. If the difference in pixel colors passes a certain threshold, the camera is deemed to have seen a change in the door. A video file will be generated in addition to the images. A text message will be sent to the cell phone user to notify them someone has been at the door, and a face image of this person will be uploaded to AWS for the user to manually verify the suspected entry. 

The report of the project is uploaded.
The python code used in the project is also uploaded.
