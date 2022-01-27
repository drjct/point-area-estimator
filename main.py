import streamlit as st
import numpy as np
import cv2
import matplotlib.pyplot as plt
import pandas as pd


st.title('Point Counting Area Estimator')

uploaded_files = st.file_uploader('Upload your image file(s)', type=['tif'], accept_multiple_files=True)

q = st.number_input('Expand bounding box (pixels)', min_value=0,
                    max_value=None, value=23, step=1, format='%d') 


# Center Button

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    pass
with col2:
    pass
with col4:
    pass
with col5:
    pass
with col3 :
    run_start = st.button('Run files', key='run')

file_lst = []
black_lst = []
white_lst = []

if run_start:
    print('Running files...')
    
    for file in uploaded_files:
        st.write("Running: ", file.name)
        
        file_lst.append(file.name)
        
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
        contours,_ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # count for whole file
        black_count = 0 
        white_count = 0

        with st.expander("{} details".format(file.name)):
            
            st.write('Running... 🏃🏻‍♂️')
            
            try:           
                
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
                        st.warning('Black Pixels = White Pixels, try a different bounding box size')
                        st.image(crop_img)
                
                if st.checkbox("Click to see {}".format(file.name), value=True, key='widget_{}'.format(file.name)):
                    st.image(rect, caption=file.name)
                    
                st.write('Example of one bounding box of size: {} x {}'.format(crop_img.shape[0], crop_img.shape[1]))
                st.image(crop_img)
                    
                st.success(' {}'.format(file.name))
                           
                col1x, col2x, col3x = st.columns(3)
                col1x.metric("✅", "{}".format(file.name))
                col2x.metric("Alveoli Count", "{}".format(white_count))
                col3x.metric("Septum Count", "{}".format(black_count))
                
                black_lst.append(black_count)        
                white_lst.append(white_count)

            except Exception as e:
                st.error('Error. Maybe bounding box is too large?')
                st.write('Debug Tool:')
                st.exception('e')
                
    df = pd.DataFrame({'File' : file_lst, 'Alveoli Counts' : white_lst, 'Septum Counts' : black_lst})

    st.table(df)