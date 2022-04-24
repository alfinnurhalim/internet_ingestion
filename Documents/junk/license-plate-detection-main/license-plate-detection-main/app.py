import os
import sys
import time
import asyncio
import cv2

import threading
import uvicorn

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from script.ALPR import ALPR

from lib.utils.folder_manager import is_path_exist

# init max thread
max_thread = 5

# Init API
app = FastAPI()
origins = ["*"]
app.add_middleware(CORSMiddleware, allow_origins=origins)

# # Init ALPR Model
alpr = ALPR()
alpr.init_model()

def run(video_path,max_frame=None,visualize=True):
	print('vis',visualize)
	try:
		alpr.run(video_path,max_frame=max_frame,visualize=visualize)
	except Exception as e:
		print(e)

@app.get('/')
def index():
	return "API License Plate Detection"

@app.post('/lpdetect')
async def get_causality(request: Request):
	input_raw = await request.json()
	
	# parse input
	video_path = input_raw.get("filepath", "")
	max_frame = int(input_raw.get("max_frame", ""))
	visualize_video = bool(int(input_raw.get("visualize", "")))

	if not is_path_exist(video_path):
		return {"status": 0, "error": "path does not exist","path":video_path}
	if len(threading.enumerate()) > max_thread:
		return {"status": 0, "error": "server busy maximum porcess exceeded"}

	try:
		print(len(threading.enumerate()),'out of',max_thread,'thread running')
		thread = threading.Thread(target=run,args=(video_path,max_frame,visualize_video,))
		thread.start()
		return {"status": 1, "success": "processing video"}
	except:
		return {"status": 0, "error": "an error occured"}

@app.get('/info')
def print_info():
	info = dict()

	thread_info = threading.enumerate()

	info['is_available'] = False if len(thread_info)>=max_thread else True
	info['max_thread'] = max_thread
	info['running_thread'] = len(thread_info)
	info['active_thread'] = [x.name for x in thread_info]

	return info

if __name__ == '__main__':
	uvicorn.run('app:app', host='127.0.0.1', port=8128)