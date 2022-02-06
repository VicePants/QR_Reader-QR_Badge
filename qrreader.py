

import time
import datetime
import sqlite3

# needs to be instaled before importing (pip install...)
# pytesseract its an opensource module used to recognise text, go easy on it, its nos so acurate
import pytesseract
import numpy as np
from pyzbar.pyzbar import decode
import smtplib
import cv2

# pytesseract path
pytesseract.pytesseract.tesseract_cmd = r'path\tesseract.exe'


# the whole thing is off at the beginning, to activate it, just show it an wrong access code
ACTIVE = 0

# used to
count = 0


#L = c.execute("""SELECT name FROM access""")
#LIST = [L]
#print(LIST)

#A = c.execute("""SELECT code FROM access""")
#ACCESS = [A]
#print(ACCESS)


mail_sender = "the mail adress wich will send you a message"
mail_reciver = "the reciver mail box"
password = "sender mail password"
message = 'the message you want to recive (Movement Detected)'


def mail():

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(mail_sender, password)
    server.sendmail(mail_sender, mail_reciver, message)
    # a console message, just to be sure its done
    print('Mail Sent')
    server.quit()

# VideoCapture(0) means that its set to use the default camera of your PC
vid = cv2.VideoCapture(0)

# needed only if you use an image as repere. It means that its searches for changes on the actual immage by comparing it to the default img
rval, frame = vid.read()
cv2.imwrite('first_frame.png', frame)

background = cv2.imread("first_frame.png")

status, frame1 = vid.read()
frame2 = background

while vid.isOpened():

    now = datetime.datetime.now()
    snow = now.strftime('%H:%M:%S')
    #inow = int(now.strftime('%S'))

    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
    dilate = cv2.dilate(thresh, None, iterations=3)

    contour, _ = cv2.findContours(dilate, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    for cntrs in contour:
        (x, y, w, h) = cv2.boundingRect(cntrs)


        if cv2.contourArea(cntrs) < 20000 or ACTIVE == 0:
            continue
        cv2.rectangle(frame1, (x, y), (x+w, y+h), (0, 255, 0), 2)
        count = count + 1
        if count % 10 == 0:
            mail()
        else:
            print(count)
            continue






    success, img = vid.read()
    for qr in decode(img):
        myData = qr.data.decode('utf-8')
        sdata = str(myData)

        #for name in (myData):
         #   c.execute("SELECT * FROM access WHERE code = ?", (myData))
          #  data = c.fetchall()
           # if len(data) == 0:
            #    print('There is no component named %s' % name)
            #else:
             #   print('s %s')

        conn = sqlite3.connect("access.db")

        c = conn.cursor()



        access = c.execute("SELECT code FROM access WHERE code = ?", [sdata])
        ACCESS = access.fetchone()
        #ctn_ACCESS = len(ACCESS)

        if ACCESS is not None:

           sLIST = c.execute("SELECT name FROM access WHERE code = ?", [sdata])
           LIST = str(sLIST.fetchone())

           print(myData)
           print(snow)
           print("Welcome " + LIST.strip('(,)') + " !")

           ACTIVE = 0
            #verif = c.execute(f"""SELECT * FROM name WHERE code = '{myData}'""")
            #verif2 = verif.rowcount
            #if verif2 > 0:
             #   print(myData)

        else:
            print(myData)
            print(snow)
            print("Access Denied !")

            if ACTIVE == 0:
                time.sleep(5)
                ACTIVE = 1

        pts = np.array([qr.polygon], np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(frame1, [pts], True, (0, 0, 255), 5)
        pts2 = qr.rect
        cv2.putText(frame1, "SCANING", (pts2[0], pts2[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255, 10))



    #cv2.drawContours(frame1, contour, -1, (0, 255, 0), 2)

    cv2.imshow("video", frame1)
    frame1 = frame2

    status, frame2 = vid.read()



    #now2 = datetime.datetime.now()
    #inow2 = int(now2.strftime('%S'))

    #if inow % 3 == 0 and inow != inow2:
    #    print(inow)
    #    rval, frame = vid.read()
    #    cv2.imwrite('first_frame.png', frame)


    key = cv2.waitKey(1)
    if key == ord('q'):
        break


vid.release()
cv2.destroyAllWindows()
