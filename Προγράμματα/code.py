# Εισαγωγή βιβλιοθηκών
import board
import digitalio
import busio
import pwmio
from adafruit_motor import servo
from circuitPyHuskyLib import HuskyLensLibrary
from lcd.lcd import LCD
from lcd.i2c_pcf8574_interface import I2CPCF8574Interface
from time import sleep
import random

# Δημιουργία του αντικειμένου hl και αρχικοποίηση της HuskyLens
hl = HuskyLensLibrary('UART', TX=board.GP0, RX=board.GP1)
hl.algorithm("ALGORITHM_OBJECT_TRACKING")

# Δημιουργία του αντικειμένου i2c και αρχικοποίηση του πρωτόκολλου I2C 
i2c = busio.I2C(scl=board.GP5, sda=board.GP4)

# Αναζήτηση διευθύνσεων i2c
i2c.try_lock()
address = i2c.scan()[0]
i2c.unlock()

# Δημιουργία του αντικειμένου lcd και αρχικοποίηση της LCD
lcd = LCD(I2CPCF8574Interface(i2c, address), num_rows=2, num_cols=16)

# Δημιουργία του αντικειμένου pwmServo και αρχικοποίηση του PWM
pwmServo = pwmio.PWMOut(board.GP10, duty_cycle=2 ** 15, frequency=50)

# Δημιουργία του αντικειμένου servo1 και αρχικοποίηση του servo
servo1 = servo.Servo(pwmServo, min_pulse=500, max_pulse=2200)

# Δημιουργία τριών αντικειμένων για τα κουμπιά και δήλωση των ακροδεκτών τους
button1 = digitalio.DigitalInOut(board.GP11)
button2 = digitalio.DigitalInOut(board.GP14)
button3 = digitalio.DigitalInOut(board.GP15)

# Αν δεν πατηθεί κάποιο κουμπί καταγράφεται τιμή 0
button1.switch_to_input(pull=digitalio.Pull.DOWN)
button2.switch_to_input(pull=digitalio.Pull.DOWN)
button3.switch_to_input(pull=digitalio.Pull.DOWN)

# Συνάρτηση διαβάσματος πληροφορίας από τη Huskylens
def read_HuskyLens():
    global fish_detected
    results = hl.learnedBlocks() # Only get learned results
    
    if results: # if results not empty
        fish_detected = True  # Βοηθητική μεταβλητή
        r = results[0]
        return r.y
    else:
        fish_detected = False
        return 0

# Συνάρτηση για την εμφάνιση μηνυμάτων στην LCD
def lcd_message(message):
    if message == 1:
        lcd.clear()
        lcd.print("Button 1 pressed")
        lcd.set_cursor_pos(1,0)
        lcd.print("Pulling hook")
    elif message == 2:
        lcd.clear()
        lcd.print("Button 2 pressed")
        lcd.set_cursor_pos(1,0)
        lcd.print("Releasing hook")
    elif message == 3:
        lcd.clear()
        lcd.print("Button 3 pressed")
        lcd.set_cursor_pos(1,0)
        lcd.print("Hook on surface")
    elif message == 4:
        lcd.clear()
        lcd.print("Fish detected!")
        lcd.set_cursor_pos(1,0)
        lcd.print("Depth: ")
        lcd.print(str(fish_depth))
        lcd.print("m")
    elif message == 5:
        lcd.clear()
        lcd.print("Stop moving boat")
        lcd.set_cursor_pos(1,0)
        lcd.print("Wait for catch")
    elif message == 6:
        lcd.clear()
        lcd.print("Success! We have")
        lcd.set_cursor_pos(1,0)
        fish = random.choice(fishes)
        lcd.print(fish)
    elif message == 7:
        lcd.clear()
        lcd.print("No fish caught")
        lcd.set_cursor_pos(1,0)
        lcd.print("Try again :(")

# Συνάρτηση που σταματά την περιστροφή του servo
def stop_hook():
    servo1.angle = stop

# Συνάρτηση που περιστρέφει το servo αριστερόστροφα
def pull_hook():
    global hook_depth
    if hook_depth > min_depth:
        servo1.angle = counterclockwise
        hook_depth = hook_depth - 1
        show_on_plotter()
        sleep(delay_time)

# Συνάρτηση που περιστρέφει το servo δεξιόστροφα
def release_hook():
    global hook_depth
    if hook_depth < max_depth:
        servo1.angle = clockwise
        hook_depth = hook_depth + 1
        show_on_plotter()
        sleep(delay_time)

# Συνάρτηση που περιστρέφει το servo γρήγορα αριστερόστροφα
def surface_pull_hook():
    global hook_depth, fish_depth
    while hook_depth > min_depth:
        servo1.angle = max_counterclockwise
        hook_depth = hook_depth - 1
        show_on_plotter()
        sleep(delay_time)

def wait_for_catch():
    stop_hook()
    lcd_message(5)
    sleep(5)
    fish_catched = random.choice([True, False])
    if fish_catched == True:
        lcd_message(6)
        sleep(1)
        surface_pull_hook()
    else:
        lcd_message(7)
        sleep(3)
    fish_depth = 0

# Συνάρτηση για την οπτικοποίηση μέσω του plotter
def show_on_plotter():
    print("Επιφάνεια:", min_depth, "Αγκίστρι:", hook_depth, "Ψάρι:", fish_depth, "Βυθός:", max_depth) 

# Η λίστα με τα ψάρια
fishes = ["Lavraki!", "Gopa!", "Mourmoura!", "Tsipoura!", "Barbouni!", "Salahi", "Melanouri!", "Ksifias!", "Kolios!", "Fagri!", "Synagrida!", "Vlaxos!"]

stop = 104                        # Γωνία στην οποία το servo δεν περιστρέφεται
clockwise = stop + 10             # Γωνία αργής δεξιόστροφης περιστροφής servo
max_clockwise = stop + 30         # Γωνία γρήγορης δεξιόστροφης περιστροφής servo
counterclockwise = stop - 10      # Γωνία αργής αριστερόστροφης περιστροφής servo
max_counterclockwise = stop - 30  # Γωνία γρήγορης αριστερόστροφης περιστροφής servo
hook_depth = 0                    # Το βάθος στο οποίο βρίσκεται το αγκίστρι
fish_depth = 0                    # Το βάθος στο οποίο βρίσκεται το ψάρι
min_depth = 0                     # Επιφάνεια
max_depth = 300                   # Βυθός
delay_time = 0.1                  # Καθυστέρηση κατά την προσομοίωση της κίνησης που κάνει το αγκίστρι

while True:
    sleep(0.1)
    lcd.clear() # Διαγραφή ενδείξεων οθόνης LCD
    stop_hook() # Ακινητοποίηση του servo
    show_on_plotter() 

    # Μηνύματα που εμφανίζονται στην LCD αν πατηθούν τα κουμπιά
    if button1.value == 1:
        lcd_message(1)
    elif button2.value == 1:
        lcd_message(2)
    elif button3.value == 1:
        lcd_message(3)

    # Όσο πατάμε το κουμπί 1 τραβάμε το αγκίστρι
    while button1.value == 1:
        pull_hook()
    # Όσο πατάμε το κουμπί 2 αμολάμε το αγκίστρι
    while button2.value == 1:
        release_hook()
    # Αν πατηθεί το κουμπί 3 το αγκίστρι έρχεται γρήγορα μέχρι την επιφάνεια
    if button3.value == 1:
        surface_pull_hook()
    
    fish_depth = read_HuskyLens()         # Καταχώρηση της τιμής που πάιρνουμε από τη HuskyLens
    difference = fish_depth - hook_depth  # Υπολογισμός της απόστασης ψάρι-αγκίστρι
    
    if difference > 0 and fish_detected == True:
        lcd_message(4)
        while difference != 0:
            release_hook()
            difference = fish_depth - hook_depth
        wait_for_catch()
    elif difference < 0 and fish_detected == True:
        lcd_message(4)
        while difference != 0:
            pull_hook()
            difference = fish_depth - hook_depth
        wait_for_catch()

