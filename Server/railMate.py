
from flask import request, Response
import json
import os
import csv
import smtplib
from pathlib import Path
from PIL import Image
import io
import google.generativeai as genai


def check_gmail_validity(dbParams):
    email=dbParams['userName']
    # Get the current directory
    current_directory = os.getcwd()

    # Specify the settings filename
    main_config_name = "settings.json"
    Build_key = "BuildPath"
    Extracted_key = "ExtractedPath"

    # Specify the CSV filename
    csv_filename = "AuthenticatedUsers.csv"

    settings = os.path.join(current_directory, main_config_name)

    # Combine the current directory and filename to create the full path
    csv_file = os.path.join(current_directory, csv_filename)

    with open(settings, 'r') as file:
            data = json.load(file)
            build_path_value = data.get(Build_key)
            extracted_path_value = data.get(Extracted_key)
    
    with open(csv_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            if row['EmailID'] == email:
                print( f"Success: Email ID found. Name: {row['Name']}")
                # print(type(ast.literal_eval(row['Permission'])))
                return {"status": "Success", "Name": row['Name'], "Email": email, "Role": row['Role'], "PermissionList": row['Permission'], "BuildPath" : build_path_value, "ExtractedPath" : extracted_path_value}                             
            
    print("Error: Email ID not found in the CSV.")
    return {"status": "Error", "Email": email}
def register_user(dbParams):
    formValues=dbParams["formValues"]


def sendAlert(dbParams):
    recipient=dbParams["emergencyEmail"]
    user=dbParams["travellerName"]
    mail=smtplib.SMTP('smtp.gmail.com', 587)
    mail.ehlo()
    mail.starttls()
    sender='paladinschamp29@gmail.com'
    
    sender_email="paladinschamp29@gmail.com"
    sender_password="hgppbdtqtnrwfvar"
    mail.login(sender_email,sender_password)
    
    message = "Emergency message."
    subject = "Emergency Alert from RailMate"
    body = f"An emergency alert has been triggered from RailMate for your friend {user}. \n Message: {message} \n Email: {sender}"
    email_message = f"Subject: {subject}\n\n{body}"
    mail.sendmail(sender, recipient, email_message)
    mail.close()
    return {"response":"success"}
    
def gemini(dbParams):
    responseOut=""
    def compress_image_if_needed(image_path):
        # Check if the image size is greater than 4MB
        if os.path.getsize(image_path) > 4 * 1024 * 1024:
            image = Image.open(image_path)
            # Adjust these parameters as needed to balance quality and file size
            base_width = 640
            quality = 85
            
            # Resize the image to reduce size
            w_percent = (base_width / float(image.size[0]))
            h_size = int((float(image.size[1]) * float(w_percent)))
            image = image.resize((base_width, h_size), Image.ANTIALIAS)
            
            # Compress the image by reducing quality and checking the size
            img_byte_arr = io.BytesIO()
            while True:
                img_byte_arr.seek(0)
                image.save(img_byte_arr, format='JPEG', quality=quality, optimize=True)
                size = len(img_byte_arr.getvalue())
                if size <= 4 * 1024 * 1024 or quality <= 10:  # Stop if under 4MB or quality too low
                    break
                quality -= 5  # Decrease quality to further reduce file size
            
            # Return the compressed image bytes
            img_byte_arr.seek(0)
            return img_byte_arr.getvalue()
        else:
            # If the image is under 4MB, return the original bytes
            return Path(image_path).read_bytes()

    api=os.getenv('GEMINI_API')
    genai.configure(api_key=api)
    # Set up the model
    generation_config = {
    "temperature": 0.4,
    "top_p": 0.5,
    "top_k": 32,
    "max_output_tokens": 4096,
    }

    safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_MEDIUM_AND_ABOVE"
    },
    ]

    model = genai.GenerativeModel(model_name="gemini-1.0-pro-vision-latest",
                                generation_config=generation_config,
                                safety_settings=safety_settings)


    # Validate that an image is present
    folder_path = r"C:\Users\shiva\Desktop\Hack30\Data\GenAI test"

    # Loop through all the files in the folder
    for filename in os.listdir(folder_path):
        image_path = os.path.join(folder_path, filename)

        if not (img := Path(image_path)).exists():
            raise FileNotFoundError(f"Could not find image: {img}")

        # Use the utility function to get either the original or compressed image bytes
        image_bytes = compress_image_if_needed(image_path)

        image_parts = [
            {
                "mime_type": "image/jpeg",
                "data": image_bytes
            },
        ]

        prompt_parts = [
            image_parts[0],
            """who is this ?
            what is age group?
            any sign of fear?""",
        ]

        response = model.generate_content(prompt_parts)
        print(response.text)
        responseOut+=response.text
    return {"response":responseOut}

def generate(dbparams):
    api=os.getenv('GEMINI_API')
    location=dbparams["location"]
    genai.configure(api_key=api)

    model = genai.GenerativeModel('gemini-pro')

    response1 = model.generate_content("top 3 hospitals in "+location+"with map links")
    response1 = response1.text.split('\n')

    response2 = model.generate_content("top 3 restaurants in "+location)
    response2 = response2.text.split('\n')

    response3 = model.generate_content("top 3 schools in "+location)
    response3 = response3.text.split('\n')

    return response1+response2+response3
