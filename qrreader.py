
import time
import datetime
import sqlite3

# needs to be instaled before importing (pip install...)
# go easy on pytesseract, its nos so acurate
import pytesseract
import numpy as np
from pyzbar.pyzbar import decode
import smtplib
import cv2

# pytesseract path
pytesseract.pytesseract.tesseract_cmd = r'path\tesseract.exe'



ACTIVE = 0

count = 0

mail_sender = "sender@mail.com"
mail_reciver = "reciver@mail.com"
password = "sender_pass"
message = "Message"


def mail():

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(mail_sender, password)
    server.sendmail(mail_sender, mail_reciver, message)
    # a console message
    print('Mail Sent')
    server.quit()

# VideoCapture(0) - the default camera
vid = cv2.VideoCapture(0)

# repere img
rval, frame = vid.read()
cv2.imwrite('first_frame.png', frame)

background = cv2.imread("first_frame.png")

status, frame1 = vid.read()
frame2 = background

while vid.isOpened():

    now = datetime.datetime.now()
    str_now = now.strftime('%H:%M:%S')

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
        str_data = str(myData)

        conn = sqlite3.connect("access.db")

        c = conn.cursor()

        access = c.execute("SELECT code FROM access WHERE code = ?", [str_data])
        ACCESS = access.fetchone()

        if ACCESS:

           sLIST = c.execute("SELECT name FROM access WHERE code = ?", [str_data])
           LIST = str(sLIST.fetchone())

           print(myData)
           print(str_now)
           print("Welcome " + LIST.strip('(,)') + " !")

           ACTIVE = 0
            #check = c.execute(f"""SELECT * FROM name WHERE code = '{myData}'""")
            #check_cnt = check.rowcount
            #if Ccheck_cnt > 0:
            #print(myData)

        else:
            print(myData)
            print(str_now)
            print("Access Denied !")

            if ACTIVE == 0:
                time.sleep(5)
                ACTIVE = 1

        pts = np.array([qr.polygon], np.int32)
        pts = pts.reshape((-1, 1, 2))
        cv2.polylines(frame1, [pts], True, (0, 0, 255), 5)
        pts_r = qr.rect
        cv2.putText(frame1, "SCANING", (pts_r[0], pts_r[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255, 10))


    cv2.imshow("video", frame1)
    frame1 = frame2

    status, frame2 = vid.read()


    key = cv2.waitKey(1)
    if key == ord('q'):
        break


vid.release()
cv2.destroyAllWindows()
