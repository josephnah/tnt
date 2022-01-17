import psychopy
from psychopy import visual, gui, event, core, data
import os, datetime as dt
import numpy as np
import random, getpass, glob, csv, time, sys, webbrowser
from colorthief import ColorThief

class experiment:
    def __init__(self):
        self.exp_name = "tnt_v2"
        self.exp_ver = "exp02"
        self.exp_ver_data = 2  # for data file
        self.exp_iter = 1  # Experiment iteration

        # Debug Section
        self.debug = 0 # (1 for debug mode, 0 for experiment)
        self.practice = 1  # ( 1: start w/ Practice, 0: start w/o practice)
        self.staircase_go = 1 # (1: default, 0: testing mode)
        self.oshimai = 0  # (1: marks end of exp, 0: default)


        # Screen stuff
        if getpass.getuser() == "cnah":
            self.monitor_name = "testMonitor"
            self.screen_width = 1000
            self.screen_height = 500
            self.full_screen_var = False
        else:
            self.monitor_name = "asus_vg278q_rm184"
            self.screen_width = 1920
            self.screen_height = 1080
            self.full_screen_var = True

        self.img_ext = ".png"
        self.filler = "_"
        self.screen_select = 0
        self.email_send = 1

        # --- Noise Parameters ---
        self.noise_start_val = .75
        self.visual_noise_size = 5

        # --- Set Durations (ms) ---
        self.staircase_time = .2
        self.mask_time = .2
        self.staircase_response_time = 3
        self.fix_time = .500
        self.prime_time = .050
        self.ITI = .200
        self.targ_time = .200
        self.response_time = 5
        self.break_time = 10
        self.jyunbi_time = 10
        self.oshimai_time = 5

        # --- Set Visual Angle ---
        self.obj_size = 6

        # Define Units
        self.fovea = [0, 0]
        self.obj_unit = 4

        # Define positions
        self.object_pos = self.fovea

        # Define trial and blocks
        self.npractice_trials = 20
        self.nexperiment_trials = 120
        self.nBlocks = 2
        self.block_num = 1
        self.data_rows = ["exp_ver", "exp_iter", "par_num", "par_age", "par_gen", "par_hand", "block_num", "trial_num",
                          "mask_size", "condition", "obj_pair", "mask_opacity", "objectness", "key_press ", "accuracy", "RT"]

        # Default Messages
        self.pre_jyunbi_text = " Experiment will begin in " + str(self.jyunbi_time) + " seconds"
        self.jyunbi_text = "Please press SPACE to begin the experiment"

        self.pre_calib_text = " Calibration stage will begin in " + str(self.jyunbi_time) + " seconds"
        self.calib_text = " Press SPACE to begin calibration"

        self.feedback_text = "please respond during the trial"
        self.cont_text = "Please press SPACE when you're ready to continue"
        self.end_text = "Please sit tight for the survey. The experimenter will be with you shortly."
        self.practice_text = "Let's practice before the experiment."

    # Participant information
    def participant_info(self):
        myDlg = gui.Dlg(title="Geng Lab Experiment 8002")
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
        self.kernel_file = "./balanceFactors-tnt_v2.csv"
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
                              "\n\nYou have " + str(self.nBlocks - self.block_num) + " block remaining."
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
        if self.debug == 1:
            self.win = visual.Window(size=(self.screen_width, self.screen_height), fullscr=self.full_screen_var,
                                     screen=self.screen_select,
                                     winType="pyglet", monitor=self.monitor_name, units="deg", colorSpace="rgb",
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

        url = 'https://ucdavis.co1.qualtrics.com/jfe/form/SV_4Zz8P9U9wbAcz9H'
        chrome_path = 'open -a /Applications/Google\ Chrome.app %s'

        end_date = dt.datetime.now().strftime("%H-%M-%S")
        t = time.time() - start_oshimai
        while t < self.oshimai_time:
            t = time.time() - start_oshimai
            self.end_message.draw()
            self.win.flip()
        self.oshimai = 1
        print("Smooth experiment, data saved, next!")
        if self.email_send == 1:
            import smtplib, email, ssl
            import config
            from email import encoders
            from email.mime.base import MIMEBase
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText

            body = "Participant %s started experiment %s %s on %s and finished on %s." % (self.parNo, self.exp_name,
                                                                                          self.exp_ver, self.date,
                                                                                          end_date)
            # Create a multipart message and set holders
            message = MIMEMultipart()
            message['From'] = 'Your Data <nahdata890@gmail.com>'
            message['To'] = 'Researcher <nahdata890@gmail.com>'
            message['Subject'] = "Exp: %s %s, par: %s" % (self.exp_name, self.exp_ver, self.parNo)

            # Add body to email
            message.attach(MIMEText(body, "plain"))

            if self.RA == 1:
                message2 = MIMEMultipart()
                message2['From'] = 'Your Data <nahdata890@gmail.com>'
                message2['To'] = 'RA <fayhan@ucdavis.edu>'
                message2['Subject'] = "Exp: %s %s, par: %s is done" % (self.exp_name, self.exp_ver, self.parNo)
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
        webbrowser.get(chrome_path).open(url)
        experiment.evacuation(self)

    def staircase(self):
        if self.practice == 0:
            self.win = visual.Window(size=(self.screen_width, self.screen_height), monitor=self.monitor_name,
                                     fullscr=False, color="gray", units='deg')

        start_calib = time.time()
        t = time.time() - start_calib
        while t < self.jyunbi_time:
            t = time.time() - start_calib
            self.fixation = visual.Circle(self.win, radius=.1, edges=32, color=[0, 1, 0], pos=self.fovea)
            self.win.setMouseVisible(False)
            self.jyunbi_message = visual.TextStim(self.win, text=self.pre_calib_text, pos=[9, 2], color=(0.7),
                                                  alignHoriz='center',
                                                  alignVert='center', units="deg", height=.7)

            self.jyunbi_message.draw()
            self.fixation.draw()
            self.win.flip()
        self.jyunbi_message.text = self.calib_text
        self.jyunbi_message.draw()
        self.fixation.draw()
        self.win.flip()
        self.key_pressed = event.waitKeys(keyList=["space"])

        staircase = data.StairHandler(self.noise_start_val,
                                      # nReversals=5,
                                      stepSizes=[.03, .02, .01],
                                      # applyInitialRule=False,
                                      nTrials=50,
                                      nUp=3,
                                      nDown=2,
                                      stepType='lin',
                                      minVal=0,
                                      maxVal=1)

        self.fixation = visual.Circle(self.win, radius=.1, edges=32, color=[0, 1, 0], pos=self.fovea)
        self.fixation.draw()
        self.win.flip()
        core.wait(1)

        # Data Directory
        stim_name = "./stim/v2/staircase/obj/*.png"
        stim_files = glob.glob(stim_name)
        stim_list = list(range(len(stim_files)))
        np.random.shuffle(stim_list)
        stim_list = stim_list + stim_list

        file_counter = 0
        for step in staircase:
            key_pressed = []
            stim_name = "./stim/v2/staircase/obj/*.png"
            staircase_object_type = "obj"

            # # Randomly select object or non-object
            object_select = random.random()

            if object_select <= .5:
                stim_name = "./stim/v2/staircase/non-obj/*.png"
                stim_files = glob.glob(stim_name)
                staircase_object_type = "non-obj"
                print("m")
            else:
                print("c")

            # present images
            stim_files = glob.glob(stim_name)
            np.random.shuffle(stim_files)
            img_test_obj = stim_files[stim_list[file_counter]]

            # present object
            test_object = visual.ImageStim(self.win, image=img_test_obj, size=self.obj_size, pos=self.object_pos,
                                           units="deg")

            # Get Color Palette
            color_thief = ColorThief(img_test_obj)
            palette = color_thief.get_palette(color_count=3)
            start_time = time.time()
            t = time.time() - start_time
            while t < self.staircase_time:
                t = time.time() - start_time
                test_object.draw()
                noise_texture = np.random.randn(self.visual_noise_size, self.visual_noise_size)
                np.random.shuffle(palette)
                noise_color = palette[0]
                visual_noise = [visual.GratingStim(win=self.win,
                                                   tex=noise_texture,
                                                   color=noise_color,
                                                   colorSpace='rgb255',
                                                   size=(7,7),
                                                   interpolate=False,
                                                   opacity=step)]

                visual_noise[-1].draw()
                self.win.flip()

            t = time.time() - (start_time + self.staircase_time)
            while t < self.mask_time:
                t = time.time() - (start_time + self.staircase_time)
                np.random.shuffle(palette)
                noise_color = palette[0]
                noise_texture = np.random.randn(self.visual_noise_size, self.visual_noise_size)

                visual_noise = [visual.GratingStim(win=self.win,
                                                   tex=noise_texture,
                                                   color=noise_color,
                                                   colorSpace='rgb255',
                                                   size=(7,7),
                                                   interpolate=False,
                                                   opacity=step)]

                visual_noise[-1].draw()
                self.win.flip()


            t = time.time() - (start_time + self.staircase_time + self.mask_time)
            while t < self.staircase_response_time:
                t = time.time() - (start_time + self.staircase_time + self.mask_time)
                # feedback = visual.TextStim(self.win, text="object or not?", pos=(11,5), color=(0.7, 0.7, 0.7))
                # feedback.draw()
                self.win.flip()
                experiment.get_key_response(self)
                experiment.evacuation(self)

                if self.key_pressed:
                    key_press = 1
                    if (self.key_pressed == ["c"] and staircase_object_type == "obj") or (
                            self.key_pressed == ["m"] and staircase_object_type == "non-obj"):
                        response = 0
                        accuracy = 1
                        feedback_text = "correct"
                        print(str(staircase_object_type) + " correct")
                    else:
                        response = 1
                        accuracy = 0
                        feedback_text="incorrect"
                        print(str(staircase_object_type) + " incorrect")
                    feedback = visual.TextStim(self.win, text = feedback_text, pos = (13,0))
                    feedback.draw()
                    self.win.flip()
                    core.wait(.5)
                    self.fixation.draw()
                    self.win.flip()
                    t = time.time()
                    core.wait(.5)


            staircase.addData(response)
            self.step = step
            print("step ", self.step)
            file_counter += 1
            print(file_counter)

    def practice_trials(self):
        self.prac_start_time = time.time()
        self.nTrials = self.npractice_trials
        self.win = visual.Window(size=(self.screen_width, self.screen_height), fullscr=self.full_screen_var,
                                 screen=self.screen_select,
                                 winType="pyglet", monitor=self.monitor_name, units="deg", colorSpace="rgb",
                                 color="gray")
        self.data_matrix = np.array(np.zeros([self.nTrials, len(self.data_rows)]), dtype=object)

        print("Welcome to the world of practice")
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
        if self.staircase_go == 0:
            self.step = .8
        self.exp_start_time = time.time()
        self.fixation = visual.Circle(self.win, radius=.1, edges=32, color=[0, 1, 0], pos=self.fovea)
        self.win.setMouseVisible(False)
        self.fixation.draw()
        self.win.flip()
        # print(self.data_matrix)
        # Start Loop (for 1 block, or 1 full trial rotation)
        for i in range(self.nTrials):
            print("trial: ", i, self.nTrials/2)

            if i == self.nTrials/2 and self.practice == 0:
                experiment.break_time(self)


            # Set condition (in order, neu, tax, thm
            if self.kernel[i, 0] == "1":
                image_condition_data = 1
                image_condition_file = "d"
            elif self.kernel[i, 0] == "2":
                image_condition_data = 2
                image_condition_file = "c"
            elif self.kernel[i, 0] == "3":
                image_condition_data = 3
                image_condition_file = "b"

            else:
                print("conditions are scrambled", self.kernel[i, 0])
                sys.exit()

            # Set image
            if self.kernel[i, 2] == "1":
                self.objectness = "obj"
            elif self.kernel[i, 2] == "2":
                self.objectness = "non-obj"

            prime_obj_name = str(self.kernel[i, 1]) + "a" + self.img_ext
            target_obj_name = str(self.kernel[i, 1]) + image_condition_file + self.img_ext

            if self.practice == 1:
                img_prime_obj = "./stim/v2/staircase/obj/" + prime_obj_name
                img_target_obj = "./stim/v2/staircase/" + self.objectness + "/" + target_obj_name
                self.step = .5
            elif self.practice == 0:
                img_prime_obj = "./stim/v2/obj/" + prime_obj_name
                img_target_obj = "./stim/v2/" + self.objectness + "/" + target_obj_name

            prime_object = visual.ImageStim(self.win, image=img_prime_obj, size=self.obj_size,
                                            pos=self.object_pos, units="deg")
            target_object = visual.ImageStim(self.win, image=img_target_obj, size=self.obj_size,
                                             pos=self.object_pos, units="deg")

            # Get Color Palette
            color_thief = ColorThief(img_target_obj)
            palette = color_thief.get_palette(color_count=3)

            # Save Data
            self.data_matrix[i, 0] = self.exp_ver_data
            self.data_matrix[i, 1] = self.exp_iter
            self.data_matrix[i, 2] = int(self.parNo)
            self.data_matrix[i, 3] = self.pAge
            self.data_matrix[i, 4] = self.pGender
            self.data_matrix[i, 5] = self.pHand
            self.data_matrix[i, 6] = self.block_num  # block #
            self.data_matrix[i, 7] = i + 1  # trial #
            self.data_matrix[i, 8] = self.visual_noise_size  # Mask pixel size
            self.data_matrix[i, 9] = image_condition_data
            self.data_matrix[i, 10] = int(self.kernel[i, 1]) # image pair number
            self.data_matrix[i, 11] = self.step # Mask Opacity (1 = opaque)
            self.data_matrix[i, 12] = self.kernel[i,2] #objectness

            # Experiment presentation start
            start_time = time.time()
            t = time.time() - start_time
            while t < self.fix_time:
                t = time.time() - start_time
                self.fixation.draw()
                self.win.flip()

            # Prime presentation (3 frames if 60 Hz)
            t = time.time() - (start_time + self.fix_time)
            while t < self.prime_time:
                t = time.time() - (start_time + self.fix_time)
                self.fixation.draw()
                prime_object.draw()
                self.win.flip()

            t = time.time() - (start_time + self.fix_time + self.prime_time)
            while t < self.ITI:
                t = time.time() - (start_time + self.fix_time + self.prime_time)
                # self.fixation.draw()
                # prime_object.draw()
                self.win.flip()

            t = time.time() - (start_time + self.fix_time + self.prime_time + self.ITI)
            while t < self.mask_time:
                t = time.time() - (start_time + self.fix_time + self.prime_time + self.ITI)
                target_object.draw()
                noise_texture = np.random.randn(self.visual_noise_size, self.visual_noise_size)
                np.random.shuffle(palette)
                noise_color = palette[0]
                visual_noise = [visual.GratingStim(win=self.win,
                                                   tex=noise_texture,
                                                   color=noise_color,
                                                   colorSpace='rgb255',
                                                   size=(7, 7),
                                                   interpolate=False,
                                                   opacity=self.step)]

                visual_noise[-1].draw()

                self.win.flip()

            # Object presentation + start recording RT
            RT_start = time.time()
            t = time.time() - (start_time + self.fix_time + self.prime_time + self.mask_time)
            while t < self.response_time:
                t = time.time() - (start_time + self.fix_time + self.prime_time + self.mask_time)
                # feedback = visual.TextStim(self.win, text="object or not?", pos=(11, 5), color=(0.7, 0.7, 0.7))
                # feedback.draw()
                self.win.flip()
                experiment.get_key_response(self)
                experiment.evacuation(self)

                if self.key_pressed:
                    key_press = 1
                    self.data_matrix[i, 13] = key_press
                    RT_end = time.time()
                    RT = (RT_end - RT_start) * 1000
                    # print("key has been pressed")

                    # Save Data
                    self.data_matrix[i, -1] = RT

                    if (self.objectness == "obj" and self.key_pressed == ["c"]) or (
                            self.objectness == "non-obj" and self.key_pressed == ["m"]):
                        self.data_matrix[i, -2] = 1 # accuracy
                        feedback_time = 1
                        print(RT, "correct")
                        t = time.time()
                    else:
                        self.data_matrix[i, -2] = 0 # accuracy
                        feedback_time = 1
                        print(RT, "incorrect")
                        t = time.time()
                else:
                    key_press = 2
                    RT_end = time.time()
                    RT = (RT_end - RT_start) * 1000
                    # print("key has NOT been pressed")
                    feedback_time = 2
                    # Save Data
                    self.data_matrix[i, 13] = key_press
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

                if self.data_matrix[i, -2] == 0 and self.practice == 1:
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
        if self.staircase_go == 1:
            experiment.staircase(self)
        experiment.jyunbi(self)
        experiment.create_datafile(self)
        experiment.balance_factors(self)
        experiment.experiment_trials(self)
        experiment.oshimai(self)


if __name__ == '__main__':
    experiment.go_experiment((experiment()))
