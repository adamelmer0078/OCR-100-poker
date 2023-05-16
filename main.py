import numpy as np
import cv2 as cv
from utils import Card, Card_info

VIDEO_PATH = "videos/26.mp4"

class Main:
    def __init__(self, path):
        self.video_path = path
        self.cap = cv.VideoCapture(self.video_path)
        self.temp_pre_pos = 0
        self.pre_pos = 0
        self.temp_pre_img = np.zeros((131, 251)).astype("uint8")
        self.pre_img = np.zeros((131, 251)).astype("uint8")
        self.card_flag = False
        self.delay = 55
        self.temp_frame = np.zeros((1080,1920,3)).astype("uint8")
        self.come_out_flag = False
        self.come_in_flag = True
        self.temp_index = (self.delay + 1) *(-1)
        self.hand_flag = False
        self.pre_hand_index = -11
        self.hand_info = ''
        self.hand_time = 0
        self.flop_3_flag = False
        self.flop_4_flag = False
        self.flop_5_flag = False
        self.card_info = ''
    
    def write(self, result):
        file = open('result.txt', 'a+')
        file.write(result)
        file.close()
        
    def main(self):
        index = 0
        while True:
            ret, frame = self.cap.read()
            fps = self.cap.get(cv.CAP_PROP_FPS)
            if ret == False:
                break

            if Card().check_hand(frame) == True:
                if self.hand_flag == False:
                    self.pre_hand_index = index
                    self.hand_flag = True
            
                if self.hand_info != '':
                    y_pos, current_img = Card().get_current_img(frame)
                    if (current_img.mean() == 0):
                        crop_img = Card().get_card_imgs(self.temp_pre_img)[0][:7,:]
                        if (self.come_out_flag == True) and (crop_img.mean() > 190):
                            self.temp_index = index
                            self.pre_pos = self.temp_pre_pos
                            self.pre_img = self.temp_pre_img.copy()
                            self.come_out_flag = False
                            
                    if current_img.mean() != 0:
                        self.come_out_flag = True
                        self.temp_pre_img = current_img.copy()
                        self.temp_pre_pos = y_pos
                        self.temp_frame = frame
            
                    if (index - self.temp_index == self.delay):
                        card = Card().main(self.pre_pos, self.pre_img, frame)      
                        result_txt = Card_info().main(self.pre_img, card,index)    
                        self.write(result_txt+"\n")   
                        cv.imshow("ss", card)
                    
                    if self.flop_3_flag == False:  
                        if Card().check_flop_3(frame) == True:
                            self.card_info = Card().get_flop_info(frame, 3)
                            self.flop_3_flag = True
                            self.write("flop\n"+self.card_info+"\n")
                            # self.file.close()

                    elif self.flop_4_flag == False:  
                        if Card().check_flop_4(frame) == True:
                            self.card_info += Card().get_flop_info(frame, 4)[-2:]
                            # print(self.flop_4_flag, Card().get_flop_info(frame, 4))
                            self.flop_4_flag = True
                            self.write("turn\n"+self.card_info+"\n")
                            
                    elif self.flop_5_flag == False:  
                        if Card().check_flop_5(frame)[0] == True:
                            self.card_info += Card().get_flop_info(frame, 5)[-2:]
                            self.write("river\n"+self.card_info+"\n")
                            # if Card().check_flop_5(frame)[0] == '1':
                            # else:
                            #     cv.imshow("sef",frame)
                            #     cv.waitKey(0)
                            self.flop_5_flag = True
                            
                    

            else:
                self.hand_info = ''
                self.hand_flag = False
                
            if (self.hand_flag == True) and (index - self.pre_hand_index == 10):
                self.flop_3_flag == False
                self.flop_4_flag == False
                self.flop_5_flag == False
                self.hand_info = Card().get_hand_info(frame)
                self.hand_time = round((index/fps), 2)
                
                self.write(self.hand_info + "\n" + "start time: " + str(self.hand_time) +"\n" + "pre flop" + "\n")
                
   
                # cv.namedWindow("window", cv.WND_PROP_FULLSCREEN)
                # cv.setWindowProperty("window",cv.WND_PROP_FULLSCREEN,cv.WINDOW_FULLSCREEN)
            # print(frame[876:885, 1812:1822].mean())
            # frame[876:885, 1812:1822] = 0
            cv.imshow('window', frame[:,:500,])
            key = cv.waitKey(1)
            if key == ord('q'):
                break
            if key == ord('w'):
                cv.waitKey(-1)
        
            index += 1
                    
        self.cap.release()
        cv.destroyAllWindows()
        
if __name__ == '__main__':
    Main(VIDEO_PATH).main()

