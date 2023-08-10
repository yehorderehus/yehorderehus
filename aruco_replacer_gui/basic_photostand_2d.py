import customtkinter
import cv2
import os
import datetime
import random
import numpy as np
from tkinter import filedialog
from PIL import Image, ImageTk

# Load Aruco detector
parameters = cv2.aruco.DetectorParameters()
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)

# Set variables
shot_image = None
output_image = None
replacement = [] # list because augmentation function used in this code needs list for replacement image
marker_corners = None
video_shot = None


def main_gui():
    global app, swap_frames_button, swap_flag, choose_replacement_button, choose_shot_button, save_output_image_button, save_output_label, save_screenshot_button, aruco_generator_button, replaced_frame, replaced_label, detected_frame, detected_label, video_frame, video_label, empty_label, loaded_replacement_label, loaded_shot_image_label

    customtkinter.set_appearance_mode("system")  # Modes: system (default), light, dark
    customtkinter.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

    app = customtkinter.CTk()
    app.title('Nahrazení ArUco markeru obrázkem')
    app.geometry('880x480')

    # Buttons frame
    buttons_frame = customtkinter.CTkFrame(master=app)
    buttons_frame.pack(expand=False, side=customtkinter.LEFT, fill=customtkinter.Y, padx=5, pady=5)
    buttons_frame.pack_propagate(False)

    swap_frames_button = customtkinter.CTkButton(master=buttons_frame, text="Přepnutí na obrázek", command=button_swap_frames, height=30, width=240)
    swap_frames_button.pack(expand=False, padx=5, pady=5)
    swap_flag = 'To image'

    choose_replacement_button = customtkinter.CTkButton(master=buttons_frame, text="Vybrat nahrazení", command=button_choose_replacement, height=30, width=240)
    choose_replacement_button.pack(expand=False, padx=5, pady=5)

    choose_shot_button = customtkinter.CTkButton(master=buttons_frame, text="Vybrat snímek", command=button_choose_shot, height=30, width=240)
    choose_shot_button.pack_forget()

    loaded_shot_image_label = customtkinter.CTkLabel(master=buttons_frame, text="", font=('Hight tower text', 14), text_color='yellow')
    loaded_shot_image_label.pack(expand=False, pady=10)

    loaded_replacement_label = customtkinter.CTkLabel(master=buttons_frame, text="", font=('Hight tower text', 14), text_color='yellow')
    loaded_replacement_label.pack(expand=False)

    empty_label = customtkinter.CTkLabel(master=buttons_frame, text='')
    empty_label.pack(expand=False, pady=78)

    save_output_label = customtkinter.CTkLabel(master=buttons_frame, text="", font=('Hight tower text', 16))
    save_output_label.pack(expand=False, pady=10)

    save_output_image_button = customtkinter.CTkButton(master=buttons_frame, text="Uložit obrázek", command=button_save_output_image, height=30, width=240)
    save_output_image_button.pack_forget()

    save_screenshot_button = customtkinter.CTkButton(master=buttons_frame, text="Uložit screenshot", command=button_save_screeenshot, height=30, width=240)
    save_screenshot_button.pack(expand=False, padx=5, pady=5)

    aruco_generator_button = customtkinter.CTkButton(master=buttons_frame, text="Generátor markerů", command=button_aruco_marker, height=30, width=240)
    aruco_generator_button.pack(expand=False, padx=5, pady=5)

    # Replaced frame
    replaced_frame = customtkinter.CTkFrame(master=app)
    replaced_frame.pack_forget()
    replaced_frame.pack_propagate(False)

    replaced_label = customtkinter.CTkLabel(master=replaced_frame, text="Nahrazení", text_color='cyan', font=('Hight tower text', 18))
    replaced_label.pack(expand=True, pady=10)
    replaced_label.pack_propagate(False)

    # Detected frame
    detected_frame = customtkinter.CTkFrame(master=app)
    detected_frame.pack_forget()
    detected_frame.pack_propagate(False)

    detected_label = customtkinter.CTkLabel(master=detected_frame, text="Detekce", text_color='lime', font=('Hight tower text', 18))
    detected_label.pack(expand=True, pady=10)
    detected_label.pack_propagate(False)

    # Video frame
    video_frame = customtkinter.CTkFrame(master=app)
    video_frame.pack(expand=True, side=customtkinter.LEFT, fill=customtkinter.BOTH, padx=10)

    video_label = customtkinter.CTkLabel(master=video_frame, text="Vyberte požadovaný obrázek", text_color='yellow', font=('Hight tower text', 18))
    video_label.pack(expand=True, pady=10)

    app.mainloop()


def button_swap_frames():
    global swap_flag

    if swap_flag == 'To video':
        swap_flag = 'To image'
        swap_frames_button.configure(text = "Přepnutí na obrázek")
        app.geometry('880x480')

        # Frames replacement
        replaced_frame.pack_forget()
        detected_frame.pack_forget()
        video_frame.pack(expand=True, side=customtkinter.LEFT, fill=customtkinter.BOTH, padx=10)

        # Forget all after replacement_button
        choose_shot_button.pack_forget()
        loaded_shot_image_label.pack_forget()
        loaded_replacement_label.pack_forget()
        empty_label.pack_forget()
        save_output_label.pack_forget()
        save_output_image_button.pack_forget()
        aruco_generator_button.pack_forget()

        # Build new structure after replacement_button
        loaded_shot_image_label.pack(expand=False, pady=10)
        loaded_replacement_label.pack(expand=False)
        empty_label.pack(expand=False, pady=78)
        save_output_label.pack(expand=False, pady=10)
        save_screenshot_button.pack(expand=False, padx=5, pady=5)
        aruco_generator_button.pack(expand=False, padx=5, pady=5)

    elif swap_flag == 'To image':
        swap_flag = 'To video'
        swap_frames_button.configure(text = "Přepnutí na video")
        app.geometry('1520x480')

        # Frames replacement
        video_frame.pack_forget()
        replaced_frame.pack(expand=True, side=customtkinter.LEFT, fill=customtkinter.BOTH, padx=10)
        detected_frame.pack(expand=True, side=customtkinter.LEFT, fill=customtkinter.BOTH, padx=10)

        # Forget all after replacement_button
        loaded_shot_image_label.pack_forget()
        loaded_replacement_label.pack_forget()
        empty_label.pack_forget()
        save_output_label.pack_forget()
        save_screenshot_button.pack_forget()
        aruco_generator_button.pack_forget()

        # Build new structure after replacement_button
        choose_shot_button.pack(expand=False, padx=5, pady=5)
        loaded_shot_image_label.pack(expand=False, pady=10)
        loaded_replacement_label.pack(expand=False)
        empty_label.pack(expand=False, pady=58)
        save_output_label.pack(expand=False, pady=10)
        save_output_image_button.pack(expand=False, padx=5, pady=5)
        aruco_generator_button.pack(expand=False, padx=5, pady=5)


def blink_label(label, color1, color2, delay_ms, count, previous_color=None):
    if count > 0:
        current_color = label.cget("text_color")
        new_color = color1 if current_color == color2 else color2
        label.configure(text_color=new_color)

        if previous_color is None:
            previous_color = current_color

        app.after(delay_ms, blink_label, label, color1, color2, delay_ms, count - 1, previous_color)
    else:
        label.configure(text_color=previous_color)


def button_choose_shot():
    global shot_image

    shot_image_file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")])
    if shot_image_file_path:
        try:
            shot_image = cv2.imread(shot_image_file_path)
            if shot_image is None:
                raise FileNotFoundError("Image file could not be opened")
            shot_image = shot_image_file_path
            loaded_shot_image_label.configure(text = "Vybraný obrázek")
            blink_label(loaded_shot_image_label, "yellow", "cyan", 400, 10)
            process_images()
            
        except FileNotFoundError:
            loaded_shot_image_label.configure(text="")
            detected_label.configure(image='')
            detected_label.configure(text="Invalidní název souboru")
            blink_label(detected_label, "lime", "red", 200, 5)
    

def button_choose_replacement():
    global replacement, replacement_image

    replacement_file_path = filedialog.askopenfilenames(filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")])
    if replacement_file_path:
        try:
            replacement = []
            for replacement_for_file_path in replacement_file_path:
                replacement_image = cv2.imread(replacement_for_file_path)
                if replacement_image is None:
                    raise FileNotFoundError("Replacement image file could not be opened")
            
            if replaced_label.cget("text") == "Invalidní název souboru":
                replaced_label.configure(text = "Nahrazení")
            replacement.append(replacement_image)
            loaded_replacement_label.configure(text="Vybraná náhrada")
            blink_label(loaded_replacement_label, "yellow", "cyan", 400, 10)
            process_images(), initialise_video()
            
        except FileNotFoundError:
            loaded_replacement_label.configure(text="")
            replaced_label.configure(image='')
            replaced_label.configure(text="Invalidní název souboru")
            blink_label(replaced_label, "cyan", "red", 200, 5)
            video_label.configure(text="Invalidní název souboru")
            blink_label(video_label, "yellow", "red", 200, 5)
    

def button_save_output_image():
    if marker_corners is None:
        save_output_label.configure(text = f"Nepodařilo se uložit obrázek", text_color='red')
        blink_label(save_output_label, "white", "red", 200, 5)
    else:
        # Frames folder
        saved_output_dir = os.path.join(os.getcwd(), 'saved_output')
        if not os.path.exists(saved_output_dir):
            os.makedirs(saved_output_dir)

        # Save the replaced image with timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
        replaced_image_file = os.path.join(saved_output_dir, f'replaced_{timestamp}.jpg')
        cv2.imwrite(replaced_image_file, output_image)

        # Show that output image was saved
        save_output_label.configure(text = 'Obrázek byl uložen', text_color='white')
        blink_label(save_output_label, "white", "cyan", 400, 10)


def button_save_screeenshot():
    if video_shot is None:
        save_output_label.configure(text = f"Nepodařilo se uložit obrázek", text_color='red')
        blink_label(save_output_label, "white", "red", 200, 5)
    else:
        # Frames folder
        saved_screenshots_dir = os.path.join(os.getcwd(), 'saved_screenshots')
        if not os.path.exists(saved_screenshots_dir):
            os.makedirs(saved_screenshots_dir)

        # Save screenshot with timestamp
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
        screenshot_file = os.path.join(saved_screenshots_dir, f'screenshot_{timestamp}.jpg')
        screenshot_img_np = np.array(video_shot)
        screenshot_img_rgb = cv2.cvtColor(screenshot_img_np, cv2.COLOR_BGR2RGB)
        screenshot_img_pil = Image.fromarray(screenshot_img_rgb)
        screenshot_img_pil.save(screenshot_file)

        # Show that screenshot was saved
        save_output_label.configure(text='Screenshot byl uložen', text_color='white')
        blink_label(save_output_label, "white", "cyan", 400, 10)


def augmentation(bbox, shot, augment, margin=50): # margin - increase the size of the bounding box if needed
    top_left = bbox[0][0][0], bbox[0][0][1]
    top_right = bbox[0][1][0], bbox[0][1][1]
    bottom_right = bbox[0][2][0], bbox[0][2][1]
    bottom_left = bbox[0][3][0], bbox[0][3][1]

    top_left = (top_left[0] - margin, top_left[1] - margin)
    top_right = (top_right[0] + margin, top_right[1] - margin)
    bottom_right = (bottom_right[0] + margin, bottom_right[1] + margin)
    bottom_left = (bottom_left[0] - margin, bottom_left[1] + margin)

    height, width, _, = augment.shape

    points_1 = np.array([top_left, top_right, bottom_right, bottom_left])
    points_2 = np.float32([[0, 0], [width, 0], [width, height], [0, height]])

    matrix, _ = cv2.findHomography(points_2, points_1)
    image_out = cv2.warpPerspective(augment, matrix, (shot.shape[1], shot.shape[0]), flags=cv2.INTER_CUBIC) # flag - antialiasing, maybe works
    image_out = cv2.resize(image_out, (shot.shape[1], shot.shape[0]), interpolation=cv2.INTER_LANCZOS4) # antialiasing, maybe works
    cv2.fillConvexPoly(shot, points_1.astype(int), (0, 0, 0))
    image_out = shot + image_out

    return image_out


def process_images():
    global output_image, marker_corners

    if shot_image is not None:
        
        # Split shot image
        detected_marker = cv2.imread(shot_image)
        output_image = cv2.imread(shot_image)

        # Create marker properties
        markerCorners_poly, markerIds_poly, markerRejected_poly = cv2.aruco.detectMarkers(detected_marker, aruco_dict, parameters=parameters)
        markerCorners, markerIds, markerRejected = cv2.aruco.detectMarkers(output_image, aruco_dict, parameters=parameters)

        # Check if markers are detected
        if markerIds_poly is None or len(markerIds_poly) == 0:
            detected_label.configure(image='')
            loaded_shot_image_label.configure(text="")
            detected_label.configure(text="Nepodařilo se načíst aruco marker")
            blink_label(detected_label, "lime", "red", 200, 5)
            raise ValueError('ArUco marker was not detected')     

        # Draw detected markers and their IDs
        for i in range(len(markerCorners_poly)):
            marker_corners = np.int32(markerCorners_poly[i]).reshape(-1, 2)
            cv2.polylines(detected_marker, [marker_corners], isClosed=True, color=(0, 255, 0), thickness=50)

            marker_id = markerIds_poly[i][0]
            center = np.mean(marker_corners, axis=0, dtype=np.int32)
            cv2.putText(detected_marker, str(marker_id), (center[0], center[1]), cv2.FONT_HERSHEY_SIMPLEX, 15, (0, 255, 255), 50)
                
        # Replace markers with replacement
        if replacement is not []:
            for i in range(len(replacement)):
                replacement_image = replacement[i]
                for j in range(len(markerCorners)):
                    output_image = augmentation(markerCorners[j], output_image, replacement_image)

                # Show and rewrite last in the replaced_frame
                cv2.imwrite('last_replaced.jpg', output_image)
                replaced_img = cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB)
                replaced_img = Image.fromarray(replaced_img)
                replaced_img.thumbnail((replaced_frame.winfo_width() - 20, replaced_frame.winfo_height() - 20))
                replaced_img = ImageTk.PhotoImage(replaced_img)
                replaced_label.configure(text = '')
                replaced_label.configure(image=replaced_img)
                replaced_label.image = replaced_img

        # Show and rewrite last in the detected_frame
        cv2.imwrite('last_detected.jpg', detected_marker)
        detected_img = cv2.cvtColor(detected_marker, cv2.COLOR_BGR2RGB)
        detected_img = Image.fromarray(detected_img)
        detected_img.thumbnail((detected_frame.winfo_width() - 20, detected_frame.winfo_height() - 20))
        detected_img = ImageTk.PhotoImage(detected_img)
        detected_label.configure(text = '')
        detected_label.configure(image=detected_img)
        detected_label.image = detected_img 

    
def initialise_video(): 
    global video_frame, video_label

    video_cap = cv2.VideoCapture(0)
    video_label.configure(text = '')


    def process_video(): 
        global video_shot
        nonlocal video_cap

        # Read a frame from the video capture
        video_ret, video_shot = video_cap.read()

        # Check if the frame is valid
        if not video_ret:
            # Release the video capture object and destroy any OpenCV windows
            video_cap.release()
            cv2.destroyAllWindows()
            raise ValueError("Unable to read frame from video capture device")

        # Detect Aruco markers
        markerCorners_video, markerIds_video, rejectedMarkers_video = cv2.aruco.detectMarkers(video_shot, aruco_dict, parameters=parameters)

        if markerIds_video is not None and len(markerIds_video) > 0:
            # Replace markers with replacement
            if replacement is not []:
                for i in range(len(replacement)):
                    replacement_image = replacement[i]
                    for j in range(len(markerCorners_video)):
                        video_shot = augmentation(markerCorners_video[j], video_shot, replacement_image)

        # Convert the frame to RGB
        frame_rgb = cv2.cvtColor(video_shot, cv2.COLOR_BGR2RGB)

        # Resize the frame to fit the video_frame
        frame_pil = Image.fromarray(frame_rgb)

        # Get the current width and height of the video_frame
        video_frame_width = video_frame.winfo_width() - 20
        video_frame_height = video_frame.winfo_height() - 20

        # Check if the width and height are valid (> 0)
        if video_frame_width > 0 and video_frame_height > 0:
            frame_pil.thumbnail((video_frame_width, video_frame_height))
        else:
            # Release the video capture object and destroy any OpenCV windows
            video_cap.release()
            cv2.destroyAllWindows()
            raise ValueError("Video frame width and height must be greater than 0")

        video_frame_tk = ImageTk.PhotoImage(frame_pil)

        # Update the video label with the new frame
        video_label.configure(image=video_frame_tk)
        video_label.image = video_frame_tk

        # Schedule the next frame processing
        app.after(10, process_video)
        

    # Start processing the video frames
    process_video()


def button_aruco_marker():
    global marker_id, marker_size, generator, id_entry, size_entry, generate_button, marker_label, error_label

    marker_id = 0
    marker_size = 800

    generator = customtkinter.CTk()
    generator.title("ArUco Marker Generator DICT_6X6_250")
    generator.geometry("240x320") ## change if pyimage1 error will be fixed

    id_label = customtkinter.CTkLabel(generator, text="Marker ID (0-249):")
    id_label.pack(expand=False)
    id_entry = customtkinter.CTkEntry(generator)
    id_entry.pack(expand=False, padx=5, pady=5)
    
    size_label = customtkinter.CTkLabel(generator, text="Velikost markeru: (>=50)\nDoporučené max.: 800")
    size_label.pack(expand=False, pady=10)

    size_entry = customtkinter.CTkEntry(generator)
    size_entry.insert(0, str(marker_size))
    size_entry.pack(expand=False, padx=5, pady=5)

    generate_button = customtkinter.CTkButton(generator, text="Vygenerovat Marker a uložit", command=generate_marker)
    generate_button.pack(expand=False, padx=5, pady=5)

    randomize_button = customtkinter.CTkButton(generator, text="S náhodným ID", command=generate_randomized)
    randomize_button.pack(expand=False, padx=5, pady=5)

    error_label = customtkinter.CTkLabel(generator, text="", text_color='red', font=('Hight tower text', 18))
    error_label.pack(expand=False, pady=10)

    marker_label = customtkinter.CTkLabel(generator, text="ArUco marker", text_color='pink', font=('Hight tower text', 18))
    marker_label.pack(expand=False, pady=10)

    generator.mainloop()


def generate_marker():
    try:
        marker_id = int(id_entry.get())
        marker_size = int(size_entry.get())

        if marker_size >= 50 and (0 <= marker_id < 250):

            # Generate marker
            marker_image = np.zeros((marker_size, marker_size), dtype=np.uint8)
            cv2.aruco.generateImageMarker(aruco_dict, marker_id, marker_size, marker_image, 1)

            # Save marker
            saved_marker_folder_path = os.path.join(os.getcwd(), "markers_DICT_6X6_250")
            if not os.path.exists(saved_marker_folder_path):
                os.makedirs(saved_marker_folder_path)

            saved_marker_name = "DICT_6X6_250_marker_id_{}_size_{}.png".format(marker_id, marker_size)
            saved_marker_path = os.path.join(saved_marker_folder_path, saved_marker_name)
            cv2.imwrite(saved_marker_path, marker_image)

            ## Temporarily ArUco label blinking
            blink_label(marker_label, 'white', 'pink', 200, 5)

            ''' ## TO FIX pyimage1 error
            # Display marker
            marker_image = cv2.cvtColor(marker_image, cv2.COLOR_GRAY2RGB)
            marker_image = Image.fromarray(marker_image)
            marker_image.thumbnail((marker_label.winfo_width() - 20, marker_label.winfo_height() - 20))
            marker_image = ImageTk.PhotoImage(marker_image)
            marker_label.configure(image=marker_image)
            marker_label.image = marker_image
            '''

        else:
            if not (0 <= marker_id < 250) and marker_size < 50:
                marker_label.configure(text = "ArUco marker")
                error_label.configure(text="Chyba ID a velikosti")
                blink_label(error_label, 'white', 'red', 200, 5)
            elif not (0 <= marker_id < 250):
                marker_label.configure(text = "ArUco marker")
                error_label.configure(text="Chyba ID")
                blink_label(error_label, 'white', 'red', 200, 5)
            else:
                marker_label.configure(text = "ArUco marker")
                error_label.configure(text="Chyba velikosti")
                blink_label(error_label, 'white', 'red', 200, 5)
                
    except ValueError:
        error_label.configure(text="Chyba hodnoty")
        blink_label(error_label, 'white', 'red', 200, 5)


def generate_randomized():
    if marker_size >= 50:
        error_label.configure(text="")
    id_entry.delete(0, customtkinter.END)
    id_entry.insert(0, str(random.randint(0, 249)))
    generate_marker()


main_gui()