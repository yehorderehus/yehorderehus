import tkinter as tk
from tkinter import filedialog, ttk
from PIL import Image, ImageTk
import cv2
import numpy as np
import os
import datetime
import glob

# Load Aruco detector
parameters = cv2.aruco.DetectorParameters()
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250)
original_image = None
replacement_images = []

def swap_frames():
    if swap_button["text"] == "Přepnutí na video":
        swap_button["text"] = "Přepnutí na obrázek"
        root.geometry('1200x450')
        image_frame.pack_forget()
        separator2.pack_forget()
        polygons_frame.pack_forget()
        video_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        process_button.config(font=('Barlow', 18, 'overstrike'), state=tk.DISABLED)
    else:
        swap_button["text"] = "Přepnutí na video"
        root.geometry('1600x450')
        video_frame.pack_forget()
        image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        separator2.pack(side=tk.LEFT, fill='y', padx=10)
        polygons_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        process_button.config(font=('Barlow', 18), state=tk.NORMAL)


def choose_folder():
    global original_image, replacement_images, replacement_image

    original_image = None
    replacement_images = []

    folder_path = filedialog.askdirectory()
    if folder_path:

        choose_folder_label.config(text="Vybraná složka: " + os.path.basename(folder_path))
        if len(folder_path) > 16:
            shortened_path_desired = os.path.basename(folder_path)[:10] + "..."
            choose_folder_label.config(text="Vybraná složka: " + shortened_path_desired)
        else:
            choose_folder_label.config(text="Vybraná složka: " + os.path.basename(folder_path))

        original_image_files = glob.glob(os.path.join(folder_path, 'original_image.*'))
        if len(original_image_files) > 0:
            original_image = original_image_files[0]

        replacement_image_files = glob.glob(os.path.join(folder_path, 'desired_image.*'))
        if len(replacement_image_files) > 0:
            replacement_images = []
            for file in replacement_image_files:
                replacement_images.append(cv2.imread(file))
                replacement_image = replacement_images[0]

        if original_image is None or not os.path.exists(original_image):
            frame_label.config(text="Nepodařilo se nalézt původní snímek")
            polygons_label.config(text="Nepodařilo se nalézt požadovaný snímek")
            
        if original_image is None or replacement_images is []:
            error_label.config(text='Vyberte správnou složku!')
        else:
            error_label.config(text='')

        video_processing()
        

def process_images():
    global video_frame, video_label
    
    if original_image is None or replacement_images is []:
        error_label.config(text='Vyberte správnou složku!')
        return

    else:
        error_label.config(text='')

        # Split original image
        polygons = cv2.imread(original_image)
        frame = cv2.imread(original_image)

        # Aruco marker properties
        markerCorners_poly, markerIds_poly, markerRejected_poly = cv2.aruco.detectMarkers(polygons, aruco_dict, parameters=parameters)
        markerCorners, markerIds, markerRejected = cv2.aruco.detectMarkers(frame, aruco_dict, parameters=parameters)

        # Check if markers are detected
        if markerIds_poly is None or len(markerIds_poly) == 0:
            error_label.config(text="Nepodařilo se načíst aruco marker")
            return

        # Draw polygons around the markers
        for i in range(len(markerCorners_poly)):
            corners = np.int32(markerCorners_poly[i]).reshape(-1, 2)
            cv2.polylines(polygons, [corners], isClosed=True, color=(0, 255, 0), thickness=50)

            # Draw marker ID
            marker_id = markerIds_poly[i][0]
            center = np.mean(corners, axis=0, dtype=np.int32)
            cv2.putText(polygons, str(marker_id), (center[0], center[1]), cv2.FONT_HERSHEY_SIMPLEX, 15, (0, 255, 255), 50)
            

        # Replace markers with new images
        for i in range(len(replacement_images)):
            replacement_image = replacement_images[i]

            def augmentation(bbox, original_image, augment):
                top_left = bbox[0][0][0], bbox[0][0][1]
                top_right = bbox[0][1][0], bbox[0][1][1]
                bottom_right = bbox[0][2][0], bbox[0][2][1]
                bottom_left = bbox[0][3][0], bbox[0][3][1]

                height, width, _, = augment.shape

                points_1 = np.array([top_left, top_right, bottom_right, bottom_left])
                points_2 = np.float32([[0, 0], [width, 0], [width, height], [0, height]])

                matrix, _ = cv2.findHomography(points_2, points_1)
                image_out = cv2.warpPerspective(augment, matrix, (original_image.shape[1], original_image.shape[0]))
                cv2.fillConvexPoly(original_image, points_1.astype(int), (0, 0, 0))
                image_out = original_image + image_out

                return image_out

            for j in range(len(markerCorners)):
                frame = augmentation(markerCorners[j], frame, replacement_image)

        # Frames folder
        frames_dir = os.path.join(os.getcwd(), 'saved_frames')
        if not os.path.exists(frames_dir):
            os.makedirs(frames_dir)

        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')

        # Save the refreshed frame with timestamp
        frame_file = os.path.join(frames_dir, f'rframe_{timestamp}.jpg')
        cv2.imwrite(frame_file, frame)

        # Show and rewrite last in the polygons_frame
        cv2.imwrite('last_showed_polygons.jpg', polygons)

        polygons_img = cv2.cvtColor(polygons, cv2.COLOR_BGR2RGB)
        polygons_img = Image.fromarray(polygons_img)
        polygons_img.thumbnail((image_frame.winfo_width() - 20, image_frame.winfo_height() - 20))
        polygons_img = ImageTk.PhotoImage(polygons_img)
        polygons_label.config(image=polygons_img)
        polygons_label.image = polygons_img 

        # Show and rewrite last in the image_frame
        cv2.imwrite('last_refreshed_frame.jpg', frame)

        frame_img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_img = Image.fromarray(frame_img)
        frame_img.thumbnail((image_frame.winfo_width() - 20, image_frame.winfo_height() - 20))
        frame_img = ImageTk.PhotoImage(frame_img)
        frame_label.config(image=frame_img)
        frame_label.image = frame_img 


def video_processing():
    global video_frame, video_label

    # Create a video capture object
    cap = cv2.VideoCapture(0)

    def augmentation(bbox, original_image, augment):
        top_left = bbox[0][0][0], bbox[0][0][1]
        top_right = bbox[0][1][0], bbox[0][1][1]
        bottom_right = bbox[0][2][0], bbox[0][2][1]
        bottom_left = bbox[0][3][0], bbox[0][3][1]

        height, width, _, = augment.shape

        points_1 = np.array([top_left, top_right, bottom_right, bottom_left])
        points_2 = np.float32([[0, 0], [width, 0], [width, height], [0, height]])

        matrix, _ = cv2.findHomography(points_2, points_1)
        image_out = cv2.warpPerspective(augment, matrix, (original_image.shape[1], original_image.shape[0]))
        cv2.fillConvexPoly(original_image, points_1.astype(int), (0, 0, 0))
        image_out = original_image + image_out

        return image_out


    def process_video():
        nonlocal cap

        # Read a frame from the video capture
        ret, frame = cap.read()

        # Check if the frame is valid
        if not ret:
            # Release the video capture object and destroy any OpenCV windows
            cap.release()
            cv2.destroyAllWindows()
            return

        # Detect Aruco markers
        markerCorners_video, markerIds_video, rejectedMarkers_video = cv2.aruco.detectMarkers(frame, aruco_dict, parameters=parameters)

        if markerIds_video is not None and len(markerIds_video) > 0:
            # Replace markers with new images
            for i in range(len(markerCorners_video)):
                frame = augmentation(markerCorners_video[i], frame, replacement_image)

        # Convert the frame to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

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
            cap.release()
            cv2.destroyAllWindows()
            return

        frame_tk = ImageTk.PhotoImage(frame_pil)

        # Update the video label with the new frame
        video_label.config(image=frame_tk)
        video_label.image = frame_tk

        # Schedule the next frame processing
        root.after(10, process_video)
        

    # Start processing the video frames
    process_video()


def gui():
    global root, separator2, frame_label, polygons_label, image_frame, polygons_frame, video_frame, swap_button, process_button, buttons_frame, choose_folder_label, error_label, video_label

    root = tk.Tk()
    root.title("Změna obrázku")
    root.geometry('1800x450')
    root.wm_attributes("-topmost", 1)

    # Buttons frame
    buttons_frame = tk.Frame(root)
    buttons_frame.pack(expand=False, side=tk.LEFT, fill=tk.Y, padx=10)

    swap_button = tk.Button(buttons_frame, text="Přepnutí na video", command=swap_frames, font=('Barlow', 18), height=2, width=3)
    swap_button.grid(row=0, column=0, sticky='nsew')

    choose_folder_button = tk.Button(buttons_frame, text="Vybrat složku", command=choose_folder, font=('Barlow', 18), height=2, width=24)
    choose_folder_button.grid(row=1, column=0, sticky='nsew')

    choose_folder_label = tk.Label(buttons_frame, text="Vybraná složka: ", font=('Neutra', 14), height=2)
    choose_folder_label.grid(row=2, column=0, sticky='nsew')

    process_button = tk.Button(buttons_frame, text="Uložení obrázků", command=process_images, font=('Barlow', 18), height=2, width=24)
    process_button.grid(row=3, column=0, sticky='nsew')

    error_label = tk.Label(buttons_frame, text="", fg="red", font=('Hight tower text', 16), height=2)
    error_label.grid(row=4, column=0, sticky='nsew')

    separator1 = ttk.Separator(root, orient='vertical')
    separator1.pack(side=tk.LEFT, fill='y', padx=10)

    # Image frame 
    image_frame = tk.Frame(root)
    image_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

    frame_label = tk.Label(image_frame)
    frame_label.pack(expand=True, pady=10)
    frame_label.config(text="Nahrazený obraz", fg="red", font=('Hight tower text', 18))

    separator2 = ttk.Separator(root, orient='vertical')
    separator2.pack(side=tk.LEFT, fill='y', padx=10)

    # Polygons frame 
    polygons_frame = tk.Frame(root)
    polygons_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

    polygons_label = tk.Label(polygons_frame)
    polygons_label.pack(expand=True, pady=10)
    polygons_label.config(text="Identifikované markery", fg="red", font=('Hight tower text', 18))

    # Swapped video frame 
    video_frame = tk.Frame(root)

    # Hide the video_frame initially
    video_frame.pack_forget()

    video_label = tk.Label(video_frame)
    video_label.pack(expand=True, pady=10)
    video_label.config(text="Příchozí video", fg="red", font=('Hight tower text', 18))

    root.mainloop()

gui()