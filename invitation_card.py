import time
from PIL import Image, ImageFont, ImageDraw
import requests

def generate(invite_name) -> bool:
    try:
        print("================ Generate Invitation Card ================")
        
        # 1. Image & Font Paths
        base_img_path = 'invitation-card.png'
        output_path = 'invite-ticket.png'
        font_path = 'Battambang-Bold.ttf'
        
        # 2. Precise Coordinates for 3508x2480
        # The white box is roughly centered at x=890, y=2000
        center_x = 920  
        center_y = 2000 
        max_width = 1100 # Width of the white box area
        
        # Start with a much larger font size for high-res image
        current_font_size = 200 
        
        img = Image.open(base_img_path)
        draw = ImageDraw.Draw(img)
        
        # 3. Auto-scaling Loop
        font = ImageFont.truetype(font_path, current_font_size)
        
        # Use (0,0) for measurement to get raw text dimensions
        bbox = draw.textbbox((0, 0), invite_name, font=font)
        text_width = bbox[2] - bbox[0]
        
        while text_width > max_width and current_font_size > 20:
            current_font_size -= 5
            font = ImageFont.truetype(font_path, current_font_size)
            bbox = draw.textbbox((0, 0), invite_name, font=font)
            text_width = bbox[2] - bbox[0]

        # 4. Draw with 'mm' anchor for perfect centering
        draw.text(
            (center_x, center_y), 
            text=invite_name, 
            font=font, 
            fill=(92, 1, 1), # Dark Red/Burgundy
            anchor="mm"
        )
        
        img.save(output_path)
        print(f"Success! Final size: {current_font_size}px at ({center_x}, {center_y})")
        return True, output_path
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return False, output_path
    
def sentImage(chat_id, saved_path, bot_token):
    url = f'https://api.telegram.org/bot{bot_token}/sendPhoto'
    payload = {"chat_id": chat_id,}
    try:
        with open(saved_path, 'rb') as photo:
            files = {'photo': photo}
            response = requests.post(url, data=payload, files=files)
            return response.json()
    except Exception as e:
        print(f"Failed to send HTML message: {e}")
        return None
    
def sentMessage(chat_id, text_message, bot_token):
    action_url = f'https://api.telegram.org/bot{bot_token}/sendChatAction'
    action_payload = {
        "chat_id": chat_id, 
        "action": "typing"
    }
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    payload = {"chat_id": chat_id, "text": text_message}
    try:
        requests.post(action_url, json=action_payload)
        time.sleep(0.3)
        response = requests.get(url, data=payload)
        return response.json()
    except Exception as e:
        print(f"Failed to send HTML message: {e}")
        return None
    
def deleteMessage(chat_id, message_id, bot_token):
    url = f'https://api.telegram.org/bot{bot_token}/deleteMessage'
    payload = {"chat_id": chat_id, "message_id": message_id}
    try:
        response = requests.post(url, json=payload)
        if not response.json().get("ok"):
            print(f"Telegram Error: {response.json().get('description')}")
        return response.json()
    except Exception as e:
        print(f"Failed to delete message: {e}")
        return None