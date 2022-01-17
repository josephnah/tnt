from psychopy import visual, gui, event
import sys
import os, datetime as dt
import time
import csv
import numpy as np
import random

class experiment:
    def __init__(self):
        self.exp_name = "tnt"
        self.exp_ver = "exp01"
        self.exp_ver_data = 1  # for data file
        self.exp_iter = 1  # Experiment iteration
        self.practice = 0  # ( 1: start w/ Practice, 0: start w/o practice)
        self.oshimai = 0  # (1: marks end of exp, 0: default)
        # Screen stuff
        self.monitor_name = "asus_vg278q_rm184"
        self.screen_width = 800
        self.screen_height = 600
        self.img_ext = ".png"
        self.filler = "_"
        self.full_screen_var = False
        self.screen_select = 0

        # --- Set Duration (ms) ---
        self.fix_time = .5
        if self.exp_iter == 1:
            self.object_time = .75
        elif self.exp_iter == 2:
            self.object_time = .5
        elif self.exp_iter == 3:
            self.object_time = .25
        self.gabor_time = .2
        self.response_time = 2
        self.break_time = 10
        self.jyunbi_time = 1
        self.oshimai_time = 2

        # --- Set Visual Angle ---
        self.obj_size = 6

        # --- target variables ---
        self.targ_size = 3
        self.targ_cont = 0.5
        self.targ_freq = 2

        # Define Units
        self.fovea = [0, 0]
        self.obj_unit = 4

        # Define positions
        self.left_object_pos = [-self.obj_unit, 0]
        self.rght_object_pos = [self.obj_unit, 0]

        # Define trial and blocks
        self.npractice_trials = 1
        self.nexperiment_trials = 120
        self.nBlocks = 1
        self.block_num = 1
        self.data_rows = ["exp_ver", "exp_iter", "par_num", "par_age", "par_gen", "par_hand", "block_num", "trial_num",
                          "condition", "object_pair", "object_loc", "match", "targ1_ori", "targ2_ori", "key_press",
                          "accuracy", "RT"]

        # Default Messages
        self.pre_jyunbi_text = " Experiment will begin in " + str(self.jyunbi_time) + " seconds"
        self.jyunbi_text = "Please press SPACE to begin the experiment"
        self.feedback_text = "please respond during the trial"
        self.cont_text = "Please press SPACE when you're ready to continue"
        self.end_text = "Thank you for participating. You have received credit and are good to go."
        self.practice_text = "Let's practice before the experiment."

    # Participant information
    def participant_info(self):
        myDlg = gui.Dlg(title="Geng Lab Experiment 8001")
        myDlg.addText("Participant Info")
        myDlg.addField("Participant Number:")
        myDlg.addField("Age:")
        myDlg.addField("Gender:")
        myDlg.addField("Handedness:")
        myDlg.addField("RA?: 1 for yes")
        myDlg.show()
        if myDlg.OK:
            self.exp_start_time = time.time()
            self.expInfo = myDlg.data
            self.pNo = self.expInfo[0]
            self.pAge = self.expInfo[1]
            if self.expInfo[2] == "M" or "m":
                self.pGender = 1
            elif self.expInfo[2] == "F" or "f":
                self.pGender = 2
            elif self.expInfo[2] == "O" or "o":
                self.pGender = 3
            else:
                self.pGender = 3
            if self.expInfo[3] == "R" or "r":
                self.pHand = 1
            elif self.expInfo[3] == "L" or "l":
                self.pHand = 2
            else:
                self.pHand = 3
            if self.expInfo[4] == "Y" or "y":
                self.RA = 1
            else:
                self.RA = 0
        else:
            print("You messed up")
            sys.exit()

        if int(self.pNo) < 10:
            self.parNo = "00" + str(self.pNo)
        elif 100 > int(self.pNo) >= 10:
            self.parNo = "0" + str(self.pNo)
        elif int(self.pNo) >= 100:
            self.parNo = str(self.pNo)

    # Load and shuffle all possible trials (equiv of 1 block)
    def balance_factors(self):
        self.pre_kernel = []
        self.kernel = []
        self.kernel_file = "./balanceFactors-tnt.csv"
        self.kernel_plan = open(self.kernel_file)
        file_reader = csv.reader(self.kernel_plan, delimiter=',')
        next(file_reader)

        for row in file_reader:
            self.pre_kernel.append(row)

        self.kernel = np.array(list(self.pre_kernel))
        np.random.shuffle(self.kernel)

    # Get key responses, restrict response to 3 keys
    def get_key_response(self):
        self.key_pressed = event.waitKeys(maxWait=1.8, keyList=["c", "m", "w"])

    # Key press to exit out of experiment
    def evacuation(self):
        if self.key_pressed == ['w']:
            sys.exit()
        elif self.oshimai == 1:
            sys.exit()

    # Create CSV for data saving
    def create_datafile(self):
        try:
            os.makedirs("./data")
        except OSError:
            print("directory " + "./data" + " already exists")

        self.date = dt.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self.data_name = str(self.exp_name) + self.filler + (self.parNo) + self.filler + self.date + ".csv"
        self.data_file = "./data/" + str(self.exp_name) + self.filler + (self.parNo) + self.filler + self.date + ".csv"
        with open(self.data_file, "w") as my_empty_csv:
            data_writer = csv.writer(my_empty_csv, delimiter=",")
            data_writer.writerow(self.data_rows)

        # Array of Zeros for data
        self.data_matrix = np.array(np.zeros([self.nTrials, len(self.data_rows)]), dtype=object)
        print("data file:", self.data_file, "created")

    def break_time(self):
        start_break = time.time()
        t = time.time() - start_break
        while t < self.break_time:
            t = time.time() - start_break

            self.break_text = "Please take a " + str(self.break_time) + " second break." + \
                              "\n\nYou have " + str(self.nBlocks - self.block_num) + " blocks remaining."
            break_message = visual.TextStim(self.win, text=self.break_text, pos=[9, 2], color=(0.7, 0.7, 0.7),
                                            alignHoriz='center', alignVert='center', units="deg", height=.7)
            self.fixation.draw()
            break_message.draw()
            self.win.flip()
        break_message.text = self.cont_text

        self.fixation.draw()
        break_message.draw()
        self.win.flip()
        self.key_pressed = event.waitKeys(keyList=["space"])
        self.block_num += 1
        experiment.evacuation(self)
        end_break = time.time()
        print("Break was " + str((end_break - start_break) / 1000) + " s")

    def jyunbi(self):
        self.nTrials = self.nexperiment_trials
        if self.practice == 0:
            self.win = visual.Window(size=(self.screen_width, self.screen_height), fullscr=self.full_screen_var,
                                     screen=self.screen_select,
                                     winType="pyglet", monitor="testMonitor", units="deg", colorSpace="rgb",
                                     color="gray")

        start_jyunbi = time.time()
        t = time.time() - start_jyunbi
        while t < self.jyunbi_time:
            t = time.time() - start_jyunbi
            self.fixation = visual.Circle(self.win, radius=.1, edges=32, color=[0, 1, 0], pos=self.fovea)
            self.win.setMouseVisible(False)
            self.jyunbi_message = visual.TextStim(self.win, text=self.pre_jyunbi_text, pos=[9, 2], color=(0.7),
                                                  alignHoriz='center',
                                                  alignVert='center', units="deg", height=.7)

            self.jyunbi_message.draw()
            self.fixation.draw()
            self.win.flip()
        self.jyunbi_message.text = self.jyunbi_text
        self.jyunbi_message.draw()
        self.fixation.draw()
        self.win.flip()
        self.key_pressed = event.waitKeys(keyList=["space"])
        self.practice = 0

    def oshimai(self):
        self.end_message = visual.TextStim(self.win, text=self.end_text, pos=[9, 2], color=(0.7), alignHoriz='center',
                                           alignVert='center', units="deg", height=.7)

        start_oshimai = time.time()

        end_date = dt.datetime.now().strftime("%H-%M-%S")
        t = time.time() - start_oshimai
        while t < self.oshimai_time:
            t = time.time() - start_oshimai
            self.end_message.draw()
            self.win.flip()
        self.oshimai = 1
        print("Smooth experiment, data saved, next!")

        import smtplib, email, ssl
        import config
        from email import encoders
        from email.mime.base import MIMEBase
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        body = "Participant %s started experiment %s %s on %s and finished on %s." % (self.parNo,  self.exp_name,
                                                                                             self.exp_ver, self.date,
                                                                                             end_date)
        # Create a multipart message and set holders
        message = MIMEMultipart()
        message['From'] = 'Your Data <nahdata890@gmail.com>'
        message['To'] = 'Researcher <nahdata890@gmail.com>'
        message['Subject'] = "Exp: %s %s, par: %s" %(self.exp_name, self.exp_ver, self.parNo)

        # Add body to email
        message.attach(MIMEText(body, "plain"))

        if self.RA == 1:
            message2 = MIMEMultipart()
            message2['From'] = 'Your Data <nahdata890@gmail.com>'
            message2['To'] = 'RA <fayhan@ucdavis.edu>'
            message2['Subject'] = "Exp: %s %s, par: %s" % (self.exp_name, self.exp_ver, self.parNo)
            message2.attach(MIMEText(body, "plain"))
            text2 = message2.as_string()

        # Open file in binary mode
        with open(self.data_file, "rb") as attachment:
            # Add file as application/octet-stream
            # Email client can usually download this automatically as attachment
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment.read())

        # Encode file in ASCII characters to send by email
        encoders.encode_base64(part)

        # Add header as key/value pair to attachment part
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {self.data_name}",
        )

        # Add attachment to message and convert message to string
        message.attach(part)
        text = message.as_string()

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login('nahdata890@gmail.com', config.password())
            server.sendmail('nahdata890@gmail.com', 'nahdata890@gmail.com', text)
            if self.RA == 1:
                server.sendmail('nahdata890@gmail.com', 'RA <fayhan@ucdavis.edu>', text2)
            server.quit()
        experiment.evacuation(self)

    def practice_trials(self):
        self.prac_start_time = time.time()
        self.nTrials = self.npractice_trials
        self.win = visual.Window(size=(self.screen_width, self.screen_height), fullscr=self.full_screen_var,
                                 screen=self.screen_select,
                                 winType="pyglet", monitor="testMonitor", units="deg", colorSpace="rgb",
                                 color="gray")
        self.data_matrix = np.array(np.zeros([self.nTrials, len(self.data_rows)]), dtype=object)

        print("practice your heart out, participant")
        self.practice_message = visual.TextStim(self.win, text=self.practice_text, pos=[9, 2], color=(0.7),
                                                alignHoriz='center',
                                                alignVert='center', units="deg", height=.7)
        self.practice_message.draw()
        self.win.flip()
        self.key_pressed = event.waitKeys(keyList=["space"])
        experiment.experiment_trials(self)
        self.prac_end_time = time.time()
        print("Practice took:", (self.prac_end_time - self.prac_start_time) / 60, "m")

    def experiment_trials(self):
        self.exp_start_time = time.time()
        self.fixation = visual.Circle(self.win, radius=.1, edges=32, color=[0, 1, 0], pos=self.fovea)
        self.win.setMouseVisible(False)
        self.fixation.draw()
        self.win.flip()
        # print(self.data_matrix)
        # Start Loop (for 1 block, or 1 full trial rotation)
        for i in range(self.nTrials):

            # Save Data
            self.data_matrix[i, 0] = self.exp_ver_data
            self.data_matrix[i, 1] = self.exp_iter
            self.data_matrix[i, 2] = int(self.parNo)
            self.data_matrix[i, 3] = self.pAge
            self.data_matrix[i, 4] = self.pGender
            self.data_matrix[i, 5] = self.pHand
            self.data_matrix[i, 6] = self.block_num  # block
            self.data_matrix[i, 7] = i + 1

            start_time = time.time()

            # Set condition
            if self.kernel[i, 0] == "1":
                image_condition = "neu"
                image_condition_data = 1
            elif self.kernel[i, 0] == "2":
                image_condition = "tax"
                image_condition_data = 2
            elif self.kernel[i, 0] == "3":
                image_condition = "thm"
                image_condition_data = 3

            else:
                print("conditions are scrambled", self.kernel[i, 0])
                sys.exit()

            # Set image location
            if self.kernel[i, 2] == "1":
                left_image = "_a"
                rght_image = "_b"
                image_loc = 1
            elif self.kernel[i, 2] == "2":
                left_image = "_b"
                rght_image = "_a"
                image_loc = 2

            else:
                print("where do the objects go?")
                sys.exit()

            # Set image
            img_left_name = image_condition + "_" + str(self.kernel[i, 1]) + left_image + self.img_ext
            img_rght_name = image_condition + "_" + str(self.kernel[i, 1]) + rght_image + self.img_ext

            img_left = "./stim/" + image_condition + "/" + img_left_name
            img_rght = "./stim/" + image_condition + "/" + img_rght_name

            left_object = visual.ImageStim(self.win, image=img_left, size=self.obj_size,
                                           pos=self.left_object_pos, units="deg")
            rght_object = visual.ImageStim(self.win, image=img_rght, size=self.obj_size,
                                           pos=self.rght_object_pos, units="deg")

            # Set Gabors (targets)
            target1 = visual.GratingStim(self.win, tex='sin', mask='gauss', sf=self.targ_freq, ori=0,
                                         size=self.targ_size,
                                         pos=self.left_object_pos,
                                         contrast=0.5,
                                         units='deg')
            target2 = visual.GratingStim(self.win, tex='sin', mask='gauss', sf=self.targ_freq, ori=0,
                                         size=self.targ_size,
                                         pos=self.rght_object_pos,
                                         contrast=0.5,
                                         units='deg')

            targetDetermine = random.random()
            if targetDetermine <= .5:
                target1.ori = -45
            else:
                target1.ori = 45

            matchDetermine = random.random()
            if matchDetermine <= .5:
                target2.ori = target1.ori
                self.match = 1
            else:
                target2.ori = -target1.ori
                self.match = 2

            # Save image information
            self.data_matrix[i, 8] = image_condition_data
            self.data_matrix[i, 9] = int(self.kernel[i, 1])  # image pair number
            self.data_matrix[i, 10] = image_loc
            self.data_matrix[i, 11] = self.match
            self.data_matrix[i, 12] = target1.ori
            self.data_matrix[i, 13] = target2.ori

            # Experiment presentation start
            t = time.time() - start_time
            while t < self.fix_time:
                t = time.time() - start_time
                self.fixation.draw()
                self.win.flip()

            # Object presentation
            t = time.time() - (start_time + self.fix_time)
            while t < self.object_time:
                t = time.time() - (start_time + self.fix_time)

                self.fixation.draw()
                left_object.draw()
                rght_object.draw()
                self.win.flip()

            # Gabor presentation + start recording RT
            RT_start = time.time()
            t = time.time() - (start_time + self.fix_time + self.object_time)
            while t < self.gabor_time:
                t = time.time() - (start_time + self.fix_time + self.object_time)
                self.fixation.draw()
                left_object.draw()
                rght_object.draw()
                target1.draw()
                target2.draw()
                self.win.flip()

            # Back to only objects
            t = time.time() - (start_time + self.fix_time + self.object_time + self.gabor_time)
            while t < self.response_time:
                t = time.time() - (start_time + self.fix_time + self.object_time + self.gabor_time)
                self.fixation.draw()
                left_object.draw()
                rght_object.draw()
                print(3)
                self.win.flip()
                experiment.get_key_response(self)
                experiment.evacuation(self)

                if self.key_pressed:
                    key_press = 1
                    self.data_matrix[i, 14] = key_press
                    RT_end = time.time()
                    RT = (RT_end - RT_start) * 1000
                    # print("key has been pressed")

                    # Save Data
                    self.data_matrix[i, -1] = RT

                    if (self.match == 1 and self.key_pressed == ["c"]) or (
                            self.match == 2 and self.key_pressed == ["m"]):
                        self.data_matrix[i, -2] = 1
                        feedback_time = 0
                        # print(RT, "correct")
                        t = time.time()
                    else:
                        self.data_matrix[i, -2] = 0
                        feedback_time = 1
                        # print(RT, "incorrect")
                        t = time.time()
                else:
                    key_press = 2
                    RT_end = time.time()
                    RT = (RT_end - RT_start) * 1000
                    # print("key has NOT been pressed")
                    feedback_time = 2
                    # Save Data
                    self.data_matrix[i, 14] = key_press
                    self.data_matrix[i, -1] = RT
                    self.data_matrix[i, -2] = 0
                    # print(RT, RT_end, RT_start, "please respond")
                    t = time.time()
                self.curr_trial_data = self.data_matrix[i, :]
                # print(self.curr_trial_data, len(self.curr_trial_data), type(self.curr_trial_data))

                # saves data
                if self.practice == 0:
                    with open(self.data_file, "a") as data_read:
                        data_saver = csv.writer(data_read, delimiter=",")
                        data_saver.writerow(self.curr_trial_data)

            trial_end_time = time.time()

            # feedback time
            t = time.time() - trial_end_time
            while t < feedback_time:
                t = time.time() - trial_end_time

                if self.data_matrix[i, -2] == 0:
                    self.fixation.color = [1, 0, 0]
                if key_press == 2:
                    feedback_message = visual.TextStim(self.win, text=self.feedback_text, pos=[9, 2],
                                                       color=(0.7, 0.7, 0.7), alignHoriz='center', alignVert='center',
                                                       units="deg", height=.7)
                    feedback_message.draw()
                self.fixation.draw()
                self.win.flip()
                self.fixation.color = [0, 1, 0]

        self.exp_end_time = time.time()
        if self.practice == 0:
            print(
                "Block #" + str(self.block_num) + " took " + str((self.exp_end_time - self.exp_start_time) / 60) + " m")

    def go_experiment(self):
        experiment.participant_info(self)
        if self.practice == 1:
            experiment.balance_factors(self)
            experiment.practice_trials(self)
        experiment.jyunbi(self)
        experiment.create_datafile(self)
        for i in range(self.nBlocks):
            experiment.balance_factors(self)
            experiment.experiment_trials(self)
            if self.block_num < self.nBlocks:
                experiment.break_time(self)
            else:
                experiment.oshimai(self)


if __name__ == '__main__':
    experiment.go_experiment((experiment()))
