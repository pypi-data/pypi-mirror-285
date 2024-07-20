from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from yta_general_utils.experimental.chrome_scrapper import start_chrome, go_to_and_wait_loaded

import time

def real_time_speach_to_text(activate_command = 'hola caracola', deactivate_command = 'chao pescao'):
    """
    This will activate the microphone and will be listening to your voice
    until you say the ending word, that will deactivate the software.

    This method listens to your voice and transcribes it in real time to
    be able to handle your voice commands and act as a consecuence of the
    things you ask.

    This method is using a web to continuously record your voice through
    the microphone and checks what is being transcripted (in Spanish).
    """
    if not activate_command:
        # TODO: Throw custom exception
        return None
    
    if not deactivate_command:
        # TODO: Throw custom exception
        return None
    
    # TODO: Check if invalid commands (commas, question marks, etc.)
    activate_command = activate_command.lower()
    deactivate_command = deactivate_command.lower()

    try:
        driver = start_chrome(gui = False)
        go_to_and_wait_loaded(driver, 'https://speechnotes.co/dictate/')
        # This webpage above handles the microphone voice by creating a temporary
        # transcription that is holded in 'mirror_container'. After a few seconds
        # of no voice detected it moves the temporary transcription to the 
        # definitive note text in 'results_box'
        transcription_textarea = driver.find_element(By.ID, 'results_box')
        while_speaking_transcription = driver.find_element(By.ID, 'mirror_container')

        # We force it to listen in Spanish (from Spain)
        select_language = driver.find_element(By.ID, 'select_language')
        select_language.click()
        select_language.send_keys('español, españa')
        select_language.send_keys(Keys.ENTER)

        time.sleep(1)

        # We force it to start listening (access is grant throw scrapper
        # default options)
        start_recording = driver.find_element(By.ID, 'start_button')
        start_recording.click()

        time.sleep(1)

        print('--->   En escucha, puedes comenzar a hablar :)   <---')

        last_command = ''
        last_note_text = ''
        do_end = False
        while not do_end:
            # Transcriptions are all stored in the transcription_area
            # element when the voice is over and the temporary
            # transcription (that is while_speaking_transcription 
            # element) becomes definitive (and is cleaned).
            input_message = while_speaking_transcription.text.lower()
            note_text = transcription_textarea.get_attribute('value')
            if not input_message and note_text != last_note_text:
                # Stopped talking and previous command was send to note
                # TODO: Analyze command, that is in 'last_command'
                if activate_command in last_command:
                    print('COMANDO DE ACTIVACIÓN')
                elif deactivate_command in last_command:
                    print('COMANDO DE DESACTIVACIÓN')
                    # By now I'm exiting when this is received
                    do_end = True
                else:
                    print('Otro mensaje no interpretado')
                print('Last command is: ' + last_command)

                last_note_text = note_text

            last_command = input_message
            time.sleep(0.1)
    finally:
        driver.close()
    
