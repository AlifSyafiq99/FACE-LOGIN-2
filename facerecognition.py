from cgitb import html
from re import L
from turtle import right
from cv2 import HOGDescriptor_DESCR_FORMAT_ROW_BY_ROW
import face_recognition
import cv2
import pickle
import os
import sys
import numpy as np

import tkinter as tk
from tkinter import *
from tkinter import ANCHOR, CENTER, Canvas, Label, PhotoImage, Tk, messagebox
from tkhtmlview import HTMLLabel
from PIL import ImageTk, Image

from pathlib import Path
import glob


#class: Dlib Face Unlock
#Purpose: This class will update the encoded known face if the directory has changed
#as well as encoding a face from a live feed to compare the face to allow the facial recognition
#to be integrated into the system
#Methods: ID
class Dlib_Face_Unlock:
	#When the Dlib Face Unlock Class is first initialised it will check if the employee photos directory has been updated
	#if an update has occurred either someone deleting their face from the system or someone adding their face to the system
	#the face will then be encoded and saved to the encoded pickle file
	def __init__(self):
		#this is to detect if the directory is found or not
		try:
			#this will open the existing pickle file to load in the encoded faces of the users who has sign up for the service
			with open (r'E:\Face Login 2\labels.pickle','rb') as self.f:
				self.og_labels = pickle.load(self.f)
			print(self.og_labels)
		#error checking
		except FileNotFoundError:
			#allowing me to known that their was no file found
			print("No label.pickle file detected, will create required pickle files")

		#this will be used to for selecting the photos
		self.current_id = 0
		#creating a blank ids dictionary
		self.labels_ids = {}
		#this is the directory where all the users are stored
		self.BASE_DIR = os.path.dirname(os.path.abspath(__file__))
		self.image_dir = os.path.join(self.BASE_DIR, 'images')
		for self.root, self.dirs, self.files in os.walk(self.image_dir):
			#checking each folder in the images directory
			for self.file in self.files:
				#looking for any png or jpg files of the users
				if self.file.endswith('png') or self.file.endswith('jpg'):
					#getting the folder name, as the name of the folder will be the user
					self.path = os.path.join(self.root, self.file)
					self.label = os.path.basename(os.path.dirname(self.path)).replace(' ','-').lower()
					if not self.label in self.labels_ids:
						#adding the user into the labels_id dictionary
						self.labels_ids[self.label] = self.current_id
						self.current_id += 1
						self.id = self.labels_ids[self.label]

		print(self.labels_ids)
		#this is compare the new label ids to the old label ids dictionary seeing if their has been any new users or old users
		#being added to the system, if there is no change then nothing will happen
		self.og_labels=0
		if self.labels_ids != self.og_labels:
			#if the dictionary change then the new dictionary will be dump into the pickle file
			with open('labels.pickle','wb') as self.file:
				pickle.dump(self.labels_ids, self.file)

			self.known_faces = []
			for self.i in self.labels_ids:
				#Get number of images of a person
				noOfImgs = len([filename for filename in os.listdir('images/' + self.i)
									if os.path.isfile(os.path.join('images/' + self.i, filename))])
				print(noOfImgs)
				for imgNo in range(1,(noOfImgs+1)):
					self.directory = os.path.join(self.image_dir, self.i, str(imgNo)+'.png')
					self.img = face_recognition.load_image_file(self.directory)
					self.img_encoding = face_recognition.face_encodings(self.img)[0]
					self.known_faces.append([self.i, self.img_encoding])
			print(self.known_faces)
			print("No Of Imgs"+str(len(self.known_faces)))
			with open('KnownFace.pickle','wb') as self.known_faces_file:
				pickle.dump(self.known_faces, self.known_faces_file)
		else:
			with open (r'E:\Face Login 2\KnownFace.pickle','rb') as self.faces_file:
				self.known_faces = pickle.load(self.faces_file)
			print(self.known_faces)
	  

	#Method: ID
	#Purpose:This is method will be used to create a live feed .i.e turning on the devices camera
	#then the live feed will be used to get an image of the user and then encode the users face
	#once the users face has been encoded then it will be compared to in the known faces
	#therefore identifying the user
	def ID(self):
		#turning on the camera to get a photo of the user frame by frame
		self.cap = cv2.VideoCapture(0)
		#seting the running variable to be true to allow me to known if the face recog is running
		self.running = True
		self.face_names = []
		while self.running == True:
			#taking a photo of the frame from the camera
			self.ret, self.frame = self.cap.read()
			#resizing the frame so that the face recog module can read it
			self.small_frame = cv2.resize(self.frame, (0,0), fx = 0.5, fy = 0.5)
			#converting the image into black and white
			self.rgb_small_frame = self.small_frame[:, :, ::-1]
			if self.running:
				#searching the black and white image for a face
				self.face_locations = face_recognition.face_locations(self.frame)

				# if self.face_locations == []:
				#     Dlib_Face_Unlock.ID(self)
				#it will then encode the face into a matrix
				self.face_encodings = face_recognition.face_encodings(self.frame, self.face_locations)
				#creating a names list to append the users identify into
				self.face_names = []
				#looping through the face_encoding that the system made
				for self.face_encoding in self.face_encodings:
					#looping though the known_faces dictionary
					for self.face in self.known_faces:
						#using the compare face method in the face recognition module
						self.matches = face_recognition.compare_faces([self.face[1]], self.face_encoding)
						print(self.matches)
						self.name = 'Unknown'
						#compare the distances of the encoded faces
						self.face_distances = face_recognition.face_distance([self.face[1]], self.face_encoding)
						#uses the numpy module to comare the distance to get the best match
						self.best_match = np.argmin(self.face_distances)
						print(self.best_match)
						print('This is the match in best match',self.matches[self.best_match])
						if self.matches[self.best_match] == True:
							self.running = False
							self.face_names.append(self.face[0])
							break
						next
			print("The best match(es) is"+str(self.face_names))
			self.cap.release()
			cv2.destroyAllWindows()
			break
		return self.face_names
"""
dfu = Dlib_Face_Unlock()
dfu.ID()
"""
def register():
	#Create images folder
	if not os.path.exists("images"):
		os.makedirs("images")
	#Create folder of person (IF NOT EXISTS) in the images folder
	Path("images/"+name.get()).mkdir(parents=True, exist_ok=True)
	#Obtain the number of photos already in the folder
	numberOfFile = len([filename for filename in os.listdir('images/' + name.get())
						if os.path.isfile(os.path.join('images/' + name.get(), filename))])
	#Add 1 because we start at 1
	numberOfFile+=1
	#Take a photo code
	cam = cv2.VideoCapture(0)
	
	cv2.namedWindow("test")
	
	
	while True:
		ret, frame = cam.read()
		cv2.imshow("test", frame)
		if not ret:
			break
		k = cv2.waitKey(1)
		
		if k % 256 == 27:
			# ESC pressed
			print("Escape hit, closing...")
			cam.release()
			cv2.destroyAllWindows()
			break
		elif k % 256 == 32:
			# SPACE pressed
			img_name = str(numberOfFile)+".png"
			cv2.imwrite(img_name, frame)
			print("{} written!".format(img_name))
			os.replace(str(numberOfFile)+".png", "images/"+name.get().lower()+"/"+str(numberOfFile)+".png")
			cam.release()
			cv2.destroyAllWindows()
			break
	raiseFrame(loginFrame)
	
#Passing in the model
def login():
	# After someone has registered, the face scanner needs to load again with the new face
	dfu = Dlib_Face_Unlock()
	#Will return the user's name as a list, will return an empty list if no matches
	user = dfu.ID()
	if user ==[]:
		messagebox.showerror("Sorry","Face Not Recognised")
		return
	loggedInUser.set(user[0])
	raiseFrame(userMenuFrame)
	
def logout():
	# After someone has registered, the face scanner needs to load again with the new face
	dfu = Dlib_Face_Unlock()
	#Will return the user's name as a list, will return an empty list if no matches
	user = dfu.ID()
	if user ==[]:
		messagebox.showerror("Sorry","Face Not Detected")
		return
	loggedOutUser.set(user[0])
	raiseFrame(loginFrame)	
	
	

#Tkinter
root = tk.Tk()
root.title("MUST STUDY")
root.configure(background='#0F2027')
root['background']='#0F2027'
#Frames
loginFrame=tk.Frame(root)
regFrame=tk.Frame(root)
userMenuFrame = tk.Frame(root)
MeetingApps = tk.Frame(root)

frame = tk.Frame(root)
frame.place(relx=0.5, rely=0.5, anchor="c")

#Define Frame List
frameList=[loginFrame,regFrame,userMenuFrame,MeetingApps]
#Configure all Frames
for frame in frameList:
	frame.grid(row=0,column=0, sticky='news')
	frame.configure(bg='#856ff8')
	
def raiseFrame(frame):
	frame.tkraise()

def regFrameRaiseFrame():
	raiseFrame(regFrame)
def logFrameRaiseFrame():
	raiseFrame(loginFrame)
def MeetingAppsRaiseFrame():
	raiseFrame(MeetingApps)
#Tkinter Vars
#Stores user's name when registering
name = tk.StringVar()
#Stores user's name when they have logged in
loggedInUser = tk.StringVar()
loggedOutUser = tk.StringVar()


tk.Label(loginFrame,text="MUST STUDY LOGIN",font=("Times New Roman",70),foreground="white",bg="#856ff8").grid(row=2,column=3,padx=100, pady=100)
loginButton = tk.Button(loginFrame,text="Login",bg="white",font=("Arial", 30),command=login)
loginButton.grid(row=5,column=3,padx=50, pady=50)
regButton = tk.Button(loginFrame,text="Register",command=regFrameRaiseFrame,bg="white",font=("Arial", 30))
regButton.grid(row=3,column=3,padx=50, pady=50)


tk.Label(regFrame,text="REGISTER",font=("Times New Roman",70),foreground="white",bg="#856ff8").grid(row=1,column=2,padx=100, pady=100)
tk.Label(regFrame,text="NAME: ",font=("Times New Roman",30),foreground="white",bg="#856ff8").grid(row=2,column=1,padx=50, pady=50)
nameEntry=tk.Entry(regFrame,textvariable=name,font=("Arial",30)).grid(row=2,column=2,padx=50, pady=50)

registerButton = tk.Button(regFrame,text="Register",command=register,bg="white",font=("Arial", 30))
registerButton.grid(row=4,column=2,padx=30,pady=30)
BackButton = tk.Button(regFrame,text="Back",command=logFrameRaiseFrame,bg="red",font=("Arial", 30))
BackButton.grid(row=6,column=2,padx=30,pady=30)

tk.Label(userMenuFrame,text="PROFILE",font=("Times New Roman",70),foreground="white",bg="#856ff8").grid(row=1,column=3,padx=100, pady=100)
tk.Label(userMenuFrame,text="Hello, ",font=("Arial",60),foreground="white",bg="#856ff8").grid(row=2,column=3,padx=50, pady=50)
tk.Label(userMenuFrame,textvariable=loggedInUser,font=("Arial",60),foreground="red",bg="#856ff8").grid(row=2,column=4,padx=50, pady=50)
tk.Button(userMenuFrame,text="Back",font=("Arial", 30),bg="red",command=logFrameRaiseFrame).grid(row=5,column=3,padx=50, pady=50)
NextButton=tk.Button(userMenuFrame,text="Next",command=MeetingAppsRaiseFrame,bg="white",font=("Arial", 30))
NextButton.grid(row=5,column=6,padx=50, pady=50)


#tk.Label(MeetingApps,text="Meeting Apps, ",font=("Permanent Marker",60),foreground="white",bg="#856ff8").grid(row=1,column=3,padx=50, pady=50)
#tk.Label(MeetingApps,text="Meeting Apps, ",font=("Permanent Marker",60),foreground="white",bg="#856ff8")
#tk.Label.pack(pady=10,padx=10,anchor=CENTER)
#BackButton = tk.Button(MeetingApps,text="Back",command=logFrameRaiseFrame,bg="red",font=("Arial", 30))
#BackButton.grid(row=2,column=1)
#HTMLLabel(MeetingApps,html='<a href="index.html">Meeting Apps</a>',font=("Arial",200),bg="#856ff8").grid(row=5,column=3,)
my_Label=Label(MeetingApps,text="MEETING APPS",font=("Times New Roman",70),foreground="white",bg="#856ff8")
my_Label.pack(pady=30,padx=30,anchor=CENTER)
my_Label=HTMLLabel(MeetingApps, html="<pre><h1><a href='index.html'>Meeting Apps</a><h1><pre>",foreground="white",bg="#856ff8")
my_Label.pack(pady=10,padx=10,anchor=CENTER)
BackButton = tk.Button(MeetingApps,text="Log Out",command=logout,bg="red",font=("Arial", 30))
BackButton.pack(pady=30,padx=30,anchor=CENTER, side=LEFT)
def run():
    #os.system('tryb.py')
	os.system("taskkill /im chrome.exe /f")
	os.system("taskkill /im firefox.exe /f")
CloseButton = tk.Button(MeetingApps, text="Close",command=run, bg="blue", font=("Arial",30))
CloseButton.pack(pady=30, padx=30,anchor=CENTER, side=RIGHT)



#Load Faces
dfu = Dlib_Face_Unlock()
raiseFrame(loginFrame)

root.mainloop()






