import cv2
import pytesseract
import numpy as np
import re
import tkinter as tk
from tkinter import messagebox
from matplotlib import pyplot as plt
from matplotlib.widgets import Button
import threading

total_students = 71

# Student data
students_list = ['22331A05D3', '22331A05D4', '22331A05D5', '22331A05D6', '22331A05D7',
                 '22331A05D8', '22331A05D9', '22331A05E0', '22331A05E1', '22331A05E2',
                 '22331A05E3', '22331A05E4', '22331A05E5', '22331A05E6', '22331A05E7',
                 '22331A05E8', '22331A05E9', '22331A05F0', '22331A05F1', '22331A05F2',
                 '22331A05F3', '22331A05F4', '22331A05F5', '22331A05F6', '22331A05F7',
                 '22331A05F8', '22331A05F9', '22331A05G0', '22331A05G1', '22331A05G2',
                 '22331A05G3', '22331A05G4', '22331A05G5', '22331A05G6', '22331A05G7',
                 '22331A05G8', '22331A05G9', '22331A05H0', '22331A05H1', '22331A05H2',
                 '22331A05H3', '22331A05H4', '22331A05H5', '22331A05H6', '22331A05H7',
                 '22331A05H8', '22331A05H9', '22331A05I0', '22331A05I1', '22331A05I2',
                 '22331A05I3', '22331A05I5', '22331A05I6', '22331A05I7', '22331A05I8',
                 '22331A05I9', '22331A05J0', '22331A05J1', '22331A05J2', '22331A05J3',
                 '22331A05J4', '22331A05J6', '22331A05J7', '22331A05J8', '23335A0513',
                 '23335A0514', '23335A0515', '23335A0516', '23335A0517', '23335A0518',
                 '23335A0519']

# Ensure Tesseract is properly linked in your code
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Initialize webcam capture
cap = cv2.VideoCapture(0)

# Create a figure for Matplotlib
fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.2)
ax.set_title("Place your ID card inside the green box")

# Variables to hold the current frame
frame = None

# Define the coordinates and size of the green rectangle (Region of Interest)
rect_x, rect_y, rect_w, rect_h = 100, 100, 600, 200  # Wider box

# List to store the extracted registration numbers
extracted_regnos = []

# Function to show a popup message (using threading to prevent blocking)
def show_popup_message(message):
    def thread_popup():
        root = tk.Tk()
        root.withdraw()  # Hide the main window
        messagebox.showinfo("Info", message)
        root.destroy()  # Destroy the window after the message is shown

    # Run the popup in a separate thread to avoid blocking the loop
    threading.Thread(target=thread_popup).start()

# Custom pop-up window for manual registration number entry
def custom_manual_input_popup(callback):
    def thread_input():
        root = tk.Tk()
        root.title("Manual Registration Number Input")

        # Set the geometry of the pop-up window (size)
        root.geometry("400x200")  # Set width and height to 400x200

        label = tk.Label(root, text="Enter Registration Number:", font=("Arial", 14))
        label.pack(pady=20)  # Padding for spacing

        entry = tk.Entry(root, font=("Arial", 14), width=20)
        entry.pack(pady=10)

        # Function to handle submission of input
        def submit():
            reg_no = entry.get()
            root.destroy()  # Close the window after submission
            callback(reg_no)  # Call the callback function with the entered value

        submit_button = tk.Button(root, text="Submit", font=("Arial", 12), command=submit)
        submit_button.pack(pady=20)

        root.mainloop()

    # Run the popup in a separate thread to avoid blocking the loop
    threading.Thread(target=thread_input).start()

# Function to update frame from the webcam
def update_frame():
    global frame
    ret, frame = cap.read()
    if ret:
        # Draw a green rectangle on the frame where the ID card should be placed
        cv2.rectangle(frame, (rect_x, rect_y), (rect_x + rect_w, rect_y + rect_h), (0, 255, 0), 2)

        # Display the current frame
        ax.clear()
        ax.imshow(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        plt.draw()

# Callback function to handle manual input processing
def handle_manual_input(manual_input):
    # After manual entry, check if it is valid
    if manual_input in students_list and manual_input not in extracted_regnos:
        extracted_regnos.append(manual_input)
        show_popup_message(f"Registration Number {manual_input} extracted successfully!")
    else:
        show_popup_message("Manual entry rejected. Invalid or already registered.")

# Function to capture the image and extract the registration number
def capture(event):
    global frame
    if frame is not None:
        # Extract the region of interest (ROI) where the ID card is placed
        roi = frame[rect_y:rect_y + rect_h, rect_x:rect_x + rect_w]

        # Convert the ROI to grayscale (better for OCR)
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        # Use pytesseract to extract text from the ROI
        text = pytesseract.image_to_string(gray_roi, config='--psm 6')

        # Use regex to find the first 10-character alphanumeric pattern (case-insensitive)
        match = re.search(r'\b[A-Za-z0-9]{10}\b', text)

        if match:
            reg_no = match.group(0)  # Get the first 10-character alphanumeric pattern
            print("Roll Number Extracted: ", reg_no)

            # Check if the extracted registration number is valid
            if reg_no in students_list and reg_no not in extracted_regnos:
                extracted_regnos.append(reg_no)
                show_popup_message(f"Registration Number {reg_no} extracted successfully!")
            else:
                show_popup_message("Invalid ID or already registered.")
                custom_manual_input_popup(handle_manual_input)  # Get manual input from custom pop-up
        else:
            show_popup_message("No valid 10-character alphanumeric registration number detected.")

    # Ensure the program continues to capture after handling the ID
    update_frame()

# Function to exit the program
def exit_program(event):
    cap.release()
    plt.close()

# Create buttons for "Capture" and "Exit"
ax_capture = plt.axes([0.25, 0.05, 0.2, 0.075])
ax_exit = plt.axes([0.55, 0.05, 0.2, 0.075])

button_capture = Button(ax_capture, 'Capture')
button_exit = Button(ax_exit, 'Exit')

# Connect buttons to their respective functions
button_capture.on_clicked(capture)
button_exit.on_clicked(exit_program)

# Start the frame update loop
while cap.isOpened():
    update_frame()

    # Check if the Matplotlib window is still open
    if not plt.fignum_exists(fig.number):
        break

    # Call this to keep the event loop running smoothly
    plt.pause(0.01)

# Calculate presentees and absentees
presentees = extracted_regnos
absentees = [student for student in students_list if student not in presentees]  # Ordered absentees list

# Display the extracted registration numbers
print("Extracted Registration Numbers (Presentees):")
print(presentees)

# Print the total number of presentees
total_captures = len(presentees)
print(f"Total number of presentees: {total_captures}")

# Print the total number of absentees and their registration numbers in the same order as the students_list
print(f"Number of absentees: {len(absentees)}")
print("Absentees' Registration Numbers (in order):")
print(absentees)