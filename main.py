import streamlit as st
import numpy as np
import cv2
import matplotlib.pyplot as plt
import pandas as pd


st.title('Point Counting Area Estimator')

uploaded_files = st.file_uploader('Upload your image file(s)', type=['tif'], accept_multiple_files=True)

run_start = st.button('Run files')

if run_start:
    print('Running files...')
    for file in uploaded_files:
        st.write("Running: ", file.name)
        
        image = cv2.imdecode(np.frombuffer(file.read(), np.uint8), 1)
        
        # convert to RGB
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # convert to hsv
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
         # upper boundary RED color range values; Hue (160 - 180)
         # Play with this color a lot to make sure that the contours drawn later will
         # wrap around the +
        lower =  np.array([120,63,63])
        upper = np.array([120,255,255])
        
        mask = cv2.inRange(hsv, lower, upper)
        
        draft = image.copy()
        contours,_ = cv2.findContours(mask.copy(), 1, 1)

        # count for whole file
        black_count = 0 
        white_count = 0

        q = 0 # useless, in case you want to expand the bounding box area later

        for contour in contours:
            
            (x, y, w, h) = cv2.boundingRect(contour)
                
            rect = cv2.rectangle(draft, (x,y), (x+w,y+h), (0, 120, 255), 1)
            # don't forget to add q later for bounding box expansion
            
            # im[y1:y2, x1:x2]
            
            # y1 has to go up
            # x1 has to go left 
            # y2 has to go down
            # x2 has to go right
            
            crop_img = image[y-q:y+q+w, x-q:x+q+w].copy() # x and y are flipped
            
            white = 0 
            black = 0
            
            row, col, _ = crop_img.shape

            for i in range(row):
                for j in range(col):
                    pix = crop_img[i][j]
                    if np.array_equal(pix, np.array([0, 0, 0])):
                        black += 1
                    if np.array_equal(pix, np.array([255, 255, 255])):
                        white += 1

            if white > black:
                white_count += 1
            
            if black > white:
                black_count += 1
            
            if black == white:
                st.write('black pixels = white pixels, weird...')
        
        with st.expander("Click to see {}".format(file.name)):
            st.image(rect, caption=file.name)
            
        st.write('✅ {} : Alveoli Counts: {}, Septa Counts: {}'.format(file.name, black_count, white_count))

