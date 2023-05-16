import cv2
import numpy as np
from sewar.full_ref import mse
import pytesseract
from pytesseract import Output
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\AI\AppData\Local\Tesseract-OCR\tesseract.exe'

class Card:
    def __init__(self):
        self.x_pos = [29, 86]
        self.y_pos = [175, 326, 477, 628, 779, 930]
        self.first_height = 48
        self.second_height = 89
        self.card_height = 131
        self.card_width = 251
        self.card_x =[0,58, 61,119]
    
        
    def get_card_imgs(self, img):
        imgs = []
        crop_img = img[1:self.first_height, :]
        imgs.append(crop_img[:,:self.card_x[1]])
        imgs.append(crop_img[:,self.card_x[2]:self.card_x[3]])
        return imgs
        
    def get_current_img(self, src):   
        img  = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        result = np.zeros((self.card_height, self.card_width)).astype("uint8")
        result_y_pos = 0
        for y_pos in self.y_pos:
            temp_result = img[y_pos:y_pos+self.card_height,self.x_pos[1]:self.x_pos[1]+self.card_width].copy()
            temp_img = temp_result[self.second_height:self.card_height,self.card_width-10:self.card_width-1]
            if temp_img.mean() < 10:
                result = temp_result
                result_y_pos = y_pos
                break
        return result_y_pos, result
    
    def get_hand_info(self, img):
        hand_img = img[953:979, 1762:1876, :]
        return pytesseract.image_to_string(hand_img).strip()
    
    def check_hand(self, img):
        hand_roi = img[990:1010, 1880:1892,:]
        # hand_roi = img[913:920, 1873:1880,:]
        return True if hand_roi.mean() < 5 else False
    
    def check_flop_3(self, img):
        crop = img[933:940, 1724:1731,:].mean()
        return True if abs(crop.mean()-237)<3 else False
        
    def check_flop_4(self, img):
        crop = img[933:940, 1799:1806,:]
        return True if abs(crop.mean()-237)<3  else False
        
    def check_flop_5(self, img):
        crop = img[933:940, 1875:1882,:]
        if (abs(crop.mean()-96)<1):
            return True, '2'
        if abs(crop.mean()-237)<3 :
            return True, '1'
        else:
            return False, ''
        
    def get_flop_info(self, img, num):
        result = ''
        for i in range(num):
            frame = img[875:875 + 64, 1510 + 76 * i: 1510 + 76 * i + 69, :]
            crop_card = cv2.cvtColor(cv2.resize(frame, (58, 48)), cv2.COLOR_BGR2GRAY)[1:,:]
            num = Card_info().get_card_number(crop_card[8:-2,4:29])
            flower = Card_info().get_card_flower(crop_card[8:-10,30:-3])
            result += (num+flower)
        return result
        
    def main(self, pos, pre_card, src):
        gray = cv2.cvtColor(src, cv2.COLOR_BGR2GRAY)
        result_img = np.zeros((self.card_height, self.card_width)).astype("uint8")
        index = self.y_pos.index(pos)
        top_img = gray[self.y_pos[index-1]:self.y_pos[index-1]+self.card_height, self.x_pos[0]:self.x_pos[0]+self.card_width]
        bottom_img = gray[self.y_pos[index]:self.y_pos[index]+self.card_height, self.x_pos[0]:self.x_pos[0]+self.card_width]
        card_top = self.get_card_imgs(top_img)[0]
        card_bottom = self.get_card_imgs(bottom_img)[0]
        card_pre = self.get_card_imgs(pre_card)[0]
        top_diff = mse(card_top , card_pre)
        bottom_diff = mse(card_bottom , card_pre)
        result_img = top_img if top_diff < bottom_diff else bottom_img
        # cv2.imshow("top", top_img)
        # cv2.imshow("bottom", bottom_img)
        # cv2.imshow("card", pre_card)
        # cv2.imshow("pre_card", result_img)
        return result_img

class Card_info:
    def __init__(self):
        self.card_flower = ["d", "c", "h", "s"]
        self.card_number = ["A", '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K']
        self.seat_string = ['+1', '+2', 'HJ', 'CO', 'D', 'SB', 'BB' ,'UG|S']
        self.seat_imgs = []
        self.card_imgs = []
        for j in range(17):
            self.card_imgs.append(cv2.imread(f'source_imgs/card_imgs/{j+1}.jpg', 0))
        for k in range(8):
            self.seat_imgs.append(cv2.imread(f'source_imgs/seat_num_imgs/{k+1}.jpg', 0))
    
    def get_card_number(self, img):
        img = cv2.threshold(img, 0,255,cv2.THRESH_OTSU)[1]
        result_info = []
        for k in range(13):
            # result_info.append (compare_ssim(img, self.card_imgs[k], full=True)[0])
            result_info.append(mse(img, self.card_imgs[k]))
        return self.card_number[np.argmin(result_info)]
    
    def get_card_flower(self, img):
        img = cv2.threshold(img, 0,255,cv2.THRESH_OTSU)[1]
        result_info = []
        for k in range(4):
            result_info.append(mse(img, self.card_imgs[k+13]))
        return self.card_flower[np.argmin(result_info)]
    
    def get_play_card_info(self, img):
        crop_imgs = Card().get_card_imgs(img)
        num_1 = crop_imgs[0][8:-2,4:29]
        flower_1 = crop_imgs[0][8:-10,30:-3]
        num_2 = crop_imgs[1][8:-2,4:29]
        flower_2 = crop_imgs[1][8:-10,30:-3]
        return self.get_card_number(num_1) + self.get_card_flower(flower_1) + self.get_card_number(num_2) + self.get_card_flower(flower_2)
    
    def get_second_row_info(self, img):
        temp = img[Card().first_height+2:Card().second_height, :]
        temp_str = pytesseract.image_to_string(temp).strip()
        return temp_str
    
    def get_action_info(self, img):
        temp = img[Card().first_height+1:Card().card_height-1, :]
        # res = pytesseract.image_to_string(temp).strip()
        temp_list = pytesseract.image_to_data(temp, output_type=Output.DICT)['text']
        length = len(temp_list)
        result = ''
        if length > 3:
            for i in range(3):
                if temp_list[length-(3-i)] != '':
                    result += ' ' + temp_list[length-(3-i)]

        return result.strip()
    
    def get_name_info(self, temp_info):
        name = ''
        if (temp_info != '') and (temp_info[0].isnumeric()):
            name =  temp_info[1:temp_info.index('$')].strip() if '$' in temp_info else temp_info[1:].strip()   
        result_name = ''
        for k in range(len(name)):
            ch = name[k]
            if (ch.isupper() == True) or (ch.isnumeric() == True) or (ch == ' '):
                result_name += ch
        return result_name
    
    def get_seat_num_info(self, temp_info):
        return temp_info[0] if (temp_info != '') and (temp_info[0].isnumeric()) else ''
    
    def get_money_info(self, temp_info):
        money_str = ''
        if (temp_info != '') and (temp_info[0].isnumeric()):
            money_str = temp_info[temp_info.index('$'):] if '$' in temp_info else ''  
        return money_str
    
    def get_seat_info(self, img, index):
        seat_img = img[19:Card().first_height-2, 120:165]
        result = pytesseract.image_to_string(seat_img).strip()
        result = 'CO' if result == 'co' else result
        result = 'UG|S' if result[:2] == 'UG' else result
        if result == '':
            result_info = []
            for t in range(7):
                result_info.append(mse(seat_img, self.seat_imgs[t]))
            result = self.seat_string[np.argmin(result_info)]
        return result
    
    def main(self, pre, img, index):
        seat_info = self.get_seat_info(img, index)
        play_card_info = self.get_play_card_info(img)
        second_row = self.get_second_row_info(pre)
        name = self.get_name_info(second_row)
        action_info = self.get_action_info(img)
        seat_num = self.get_seat_num_info(second_row)
        money = self.get_money_info(second_row)
        result_text = "Seat " + seat_num + ": " + name +": " +seat_info + ": " + money + ": " + play_card_info +": " + action_info
        return result_text