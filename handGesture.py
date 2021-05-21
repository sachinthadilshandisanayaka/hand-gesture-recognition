#import numpy as np
import cv2
#import imutils
import math

top, right, bottom, left = 10, 350, 225, 590

cap = cv2.VideoCapture(0)

while (True):

    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)

    roi = frame[top:bottom, right:left]
    roi_copy = roi.copy()

    roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
    roi = cv2.GaussianBlur(roi,(17,17),0)

    #roi = cv2.absdiff(bg.astype('uint8'), roi)
    #roi = cv2.bitwise_not(roi)
    
    et,thresh1 = cv2.threshold(roi,127,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    contours, hierarchy = cv2.findContours(thresh1, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    max_cnt = max(contours, key=cv2.contourArea)
    
    epsilon = 0.0005*cv2.arcLength(max_cnt,True)
    approx= cv2.approxPolyDP(max_cnt,epsilon,True)
    cv2.polylines(roi_copy, [approx], True, (0, 0, 255), 2)
        
    #make convex hull around hand
    hull = cv2.convexHull(max_cnt)
        
     #define area of hull and area of hand
    areahull = cv2.contourArea(hull)
    areacnt = cv2.contourArea(max_cnt)  
    #find the percentage of area not covered by hand in convex hull
    arearatio=((areahull-areacnt)/areacnt)*100

    
    hull = cv2.convexHull(max_cnt, returnPoints = True)
    hull=hull.reshape(hull.shape[0],hull.shape[2])
    cv2.polylines(roi_copy, [hull],True,(255,255,0),3)
    

    
    M = cv2.moments(max_cnt)
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])
    cv2.drawContours(roi_copy, contours, -1, (0, 0, 255), 2)
    cv2.circle(roi_copy, (cx, cy), 7, (0, 0, 0), -1)
    

   # (x,y),radius = cv2.minEnclosingCircle(max_cnt)
   # center = (int(x),int(y))
    #print("----"+ str(x) + " , " + str(y) +" , "+ str(radius));
    #cv2.circle(roi_copy, center, 7, (255, 0, 0), -1)

    hull = cv2.convexHull(approx, returnPoints=False)
    defects = cv2.convexityDefects(approx, hull)
    
   # l = no. of defects
    l=0
    value=0;
    vehicleDirection = "default";
    for i in range(defects.shape[0]):
        s,e,f,d = defects[i,0]
        start = tuple(approx[s][0])
        end = tuple(approx[e][0])
        far = tuple(approx[f][0])
        pt= (100,180)
        
        
        a = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2) # d3
        b = math.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2) # d1
        c = math.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)     # d2
        s = (a+b+c)/2
        ar = math.sqrt(s*(s-a)*(s-b)*(s-c))
        
        d=(2*ar)/a
            
            # apply cosine rule here
        angle = math.acos((b**2 + c**2 - a**2)/(2*b*c)) * 57
            
        
            # ignore angles > 90 and ignore points very close to convex hull(they generally come due to noise)
        if angle <= 90 and d>30:
            l += 1
           
            cv2.circle(roi_copy, far, 3, [255,0,0], -1)
            if(value == 0):
                cv2.circle(roi_copy, (start[0], start[1]), 7, [0,0,0], -1)
                beta = math.atan((cy-start[1])/(cx-start[0]));
                #print(str(beta));
                #if(cy<start[0]):
                 #   print("right");
                #print(str(value));
               
                #print(str(i));
                print("-------------");
                xpossition = cx - start[0];
                ypossition = cy - start[1];
                if(ypossition <= 100 and xpossition < 0):
                    vehicleDirection = "right";
                elif(ypossition <= 90 and xpossition > 0):
                    vehicleDirection = "left";
                else:
                    vehicleDirection = "gohead";
                print(str(cy) + " " + str(start[1])+ " "+ vehicleDirection);
                value += 1;
        
        #cv2.line(roi_copy,start,end,[0,255,0],2)
       
    l+=1
    font = cv2.FONT_HERSHEY_SIMPLEX
    if l==1:
        if areacnt<2000:
            cv2.putText(frame,'Put hand in the box',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
        else:
            if arearatio<12:
                cv2.putText(frame,"Stop",(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
            elif arearatio<17.5:
                cv2.putText(frame,"Stop",(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
                   
            else:
                cv2.putText(frame,'1',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
                    
    elif l==2 or l==3:
            cv2.putText(frame,vehicleDirection + " " + str(l),(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
            
    elif l==4 or l==5:
        cv2.putText(frame,"Reverse" + " " + str(l),(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
    #elif l==3:
        
         
     #   if arearatio<27:
      #      cv2.putText(frame,'3',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
       # else:
        #    cv2.putText(frame,'ok',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
                    
#    elif l==4:
 #       cv2.putText(frame,'4',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
            
  #  elif l==5:
   #     cv2.putText(frame,'5',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
            
    elif l==6:
        cv2.putText(frame,'reposition',(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
            
    else :
        cv2.putText(frame,'reposition',(10,50), font, 2, (0,0,255), 3, cv2.LINE_AA)    
    

    cv2.rectangle(frame, (left, top), (right, bottom), (0,255,0), 2)

    cv2.imshow('frame', frame)
    cv2.imshow('threshold', thresh1)
    cv2.imshow('contours', roi_copy)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        #print(range(defects.shape[0]))
        break

cap.release()
cv2.destroyAllWindows()