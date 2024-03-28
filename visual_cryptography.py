import streamlit as st
import math
import numpy as np
import matplotlib.pyplot as plt
import cv2
from Crypto.Cipher import AES
from Crypto.Random import new as Random
from hashlib import sha256
from base64 import b64encode, b64decode
import pandas as pd
from sklearn.linear_model import LinearRegression
import time
import base64
import warnings
from io import BytesIO
import hashlib
from Crypto.Cipher import AES
from Crypto.Random import new as Random
from hashlib import sha256
from base64 import b64encode,b64decode
import tempfile
import os

warnings.filterwarnings("ignore")
st.title('VISUAL CRYPTOGRAPHY - APPLICATION')

class AESCipher:
    def __init__(self,data,key):
        self.block_size = 16
        self.data = data
        self.key = sha256(key.encode()).digest()[:32]
        self.pad = lambda s: s + (self.block_size - len(s) % self.block_size) * chr (self.block_size - len(s) % 
self.block_size)
        self.unpad = lambda s: s[:-ord(s[len(s) - 1:])]

    def encrypt(self):
        plain_text = self.pad(self.data)
        iv = Random().read(AES.block_size)
        cipher = AES.new(self.key,AES.MODE_OFB,iv)
        return b64encode(iv + cipher.encrypt(plain_text.encode())).decode()
    def decrypt(self):
        cipher_text = b64decode(self.data.encode())
        iv = cipher_text[:self.block_size]
        cipher = AES.new(self.key,AES.MODE_OFB,iv)
        return self.unpad(cipher.decrypt(cipher_text[self.block_size:])).decode("utf-8")


def b():
    st.subheader("IMAGE ENCRYPTION")
    #file = st.file_uploader("UPLOAD ORIGINAL IMAGE ", type = ["jpg","jpeg","png"])
    file = st.file_uploader("UPLOAD ORIGINAL IMAGE ")
    

    if file is not None:
        image_bytes = file.read()

        temp_dir = "D:\\Users\\pobba\\Documents\\Project"
        temp_file_path = os.path.join(temp_dir, file.name)
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(image_bytes)

        
        nparr = np.frombuffer(image_bytes, dtype = np.uint8)
        x0 = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if x0 is not None:
            x0 = cv2.cvtColor(x0, cv2.COLOR_BGR2RGB)
            # Display the image
            st.image(x0, caption='ORIGINAL Image', use_column_width=True)

            img_io = BytesIO(image_bytes)
            BI = base64.b64encode(img_io.read())
            BI = BI.decode("utf-8")

        else:
            st.warning("Failed to read the image. Please check the file format.")
            return

        K = st.text_input('Enter Key:')
        if K != "":
            SK = hashlib.sha256(K.encode())
            st.write("The hexadecimal equivalent of SHA256 is : ")
            st.write(SK.hexdigest())
            c = AESCipher(BI, SK.hexdigest()).encrypt()
            w = 255
            h = len(K)
            C = np.ones((h, w, 1), dtype='uint8')
            for i in range(h):
                j = ord(K[i])
                for k in range(w):
                    if k < j:
                        C[i][k][0] = 0
                    else:
                        break
            R = np.ones((h, w, 3), dtype='uint8')
            P = np.ones((h, w, 3), dtype='uint8')
            for i in range(h):
                for j in range(w):
                    r = np.random.normal(0, 1, 1)
                    R[i][j][0] = r
            for i in range(h):
                for j in range(w):
                    p = R[i][j][0] ^ C[i][j][0]
                    P[i][j][0] = p
            st.subheader("ENCRYPTION")
            filename = os.path.join(temp_dir, 'R.png')
            cv2.imwrite(filename, R)
            x_ = cv2.imread(filename)
            if x_ is not None:
                st.image(x_, caption='Share 1', use_column_width=True)
            else:
                st.warning("Failed to read the image. Please check the file format.")
                return
            
            filename = os.path.join(temp_dir, 'P.png')
            cv2.imwrite(filename, P)

            xo = cv2.imread(filename)
            st.image(xo, caption='Share 2', use_column_width=True)
            xdf = pd.DataFrame(columns=['1', '2'])
            a = []
            b = []
            cnt = 0
            for i in P:
                cnt += 1
                k = 0
                n1 = []
                n2 = []
                for j in i:
                    if k % 2 == 0:
                        n1.append(np.sum(j))
                    else:
                        n2.append(np.sum(j))
                    k += 1
                a.append(sum(n1))
                b.append(sum(n2))
            xdf['1'] = a
            xdf['2'] = b
            ydf = pd.DataFrame(columns=['1', '2'])
            a = []
            b = []
            for i in R:
                k = 0
                n1 = []
                n2 = []
                for j in i:
                    if k % 2 == 0:
                        n1.append(np.sum(j))
                    else:#
                        n2.append(np.sum(j))
                    k += 1
                a.append(sum(n1))
                b.append(sum(n2))
            ydf['1'] = a
            ydf['2'] = b
            LRmodel = LinearRegression()
            LRmodel.fit(xdf, ydf)
            zdf = pd.DataFrame(columns=['1', '2'])
            a = []
            b = []
            for i in C:
                k = 0
                n1 = []
                n2 = []
                for j in i:
                    if k % 2 == 0:
                        n1.append(np.sum(j))
                    else:
                        n2.append(np.sum(j))
                    k += 1
                a.append(sum(n1))
                b.append(sum(n2))
            zdf['1'] = a
            zdf['2'] = b
            predict = LRmodel.predict([[sum(zdf['1']), sum(zdf['2'])]])
            x = round(predict[0][0]) % 26
            y = round(predict[0][1]) % 26
            txt = []
            for each in c:
                ch = ord(each) + x - y
                txt.append(int(ch))
            text = ""
            for t in txt:
                text += chr(t) + " "
            f = open(temp_dir+"\\cipher.txt", 'a', encoding='utf-8')
            f.write(text)
            f.close()
            cipher = text
            P = cv2.imread(temp_dir+'\\P.png')
            R = cv2.imread(temp_dir+'\\R.png')
            h = np.shape(P)[0]
            w = np.shape(P)[1]
            CK = np.ones((h, w, 1), dtype='uint8')
            for i in range(h):
                for j in range(w):
                    ck = P[i][j][0] ^ R[i][j][0]
                    CK[i][j][0] = ck
            K1 = []
            for i in range(len(CK)):
                K1.append(0)
            for i in range(len(CK)):
                count = 0
                for j in range(len(CK[i])):
                    if CK[i][j][0] == 0:
                        count += 1
                K1[i] = chr(count)
            K1 = "".join(K1)
            SK1 = hashlib.sha256(K1.encode())
            xdf = pd.DataFrame(columns=['1', '2'])
            a = []
            b = []
            for i in P:
                k = 0
                n1 = []
                n2 = []
                for j in i:
                    if k % 2 == 0:
                        n1.append(np.sum(j))
                    else:
                        n2.append(np.sum(j))
                    k += 1
                a.append(sum(n1))
                b.append(sum(n2))
            xdf['1'] = a
            xdf['2'] = b
            ydf = pd.DataFrame(columns=['1', '2'])
            a = []
            b = []
            for i in R:
                k = 0
                n1 = []
                n2 = []
                for j in i:
                    if k % 2 == 0:
                        n1.append(np.sum(j))
                    else:
                        n2.append(np.sum(j))
                    k += 1
                a.append(sum(n1))
                b.append(sum(n2))
            ydf['1'] = a
            ydf['2'] = b
            LRmodel = LinearRegression()
            LRmodel.fit(xdf, ydf)
            zdf = pd.DataFrame(columns=['1', '2'])
            a = []
            b = []
            for i in CK:
                k = 0
                n1 = []
                n2 = []
                for j in i:
                    if k % 2 == 0:
                        n1.append(np.sum(j))
                    else:
                        n2.append(np.sum(j))
                    k += 1
                a.append(sum(n1))
                b.append(sum(n2))
            zdf['1'] = a
            zdf['2'] = b
            predict = LRmodel.predict([[sum(zdf['1']), sum(zdf['2'])]])
            x = round(predict[0][0]) % 26
            y = round(predict[0][1]) % 26
            cipher = cipher.split(' ')
            txt = []
            for each in cipher:
                try:
                    ch = ord(each) - x + y
                    txt.append(int(ch))
                except:
                    print(each)
            text = ""
            for t in txt:
                text += chr(t)
            
            if st.button("Decrypt",type="primary"):
                de = AESCipher(text, SK1.hexdigest()).decrypt()
                de = de.encode("utf-8")
                with open(temp_dir+"\\DecryptedImg.png", "wb") as fh:
                    fh.write(base64.decodebytes(de))
                x_ = cv2.imread(temp_dir+"\\DecryptedImg.png")
                st.subheader("DECRYPTION")
                x_=cv2.cvtColor(x_, cv2.COLOR_BGR2RGB)
                st.image(x_, caption='Decrypted Image', use_column_width=True)
                st.success("Image is Decrypted ...")

rad = st.sidebar.radio('APPLICATION', ['IMAGE ENCRYPTION'])
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/0/0e/Visual_crypto_animation_demo.gif")

if rad == 'IMAGE ENCRYPTION':
    b()