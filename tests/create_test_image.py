from PIL import Image, ImageDraw
import os

def create_test_image():
    # Create a new image with a white background
    img = Image.new('RGB', (500, 500), 'white')
    draw = ImageDraw.Draw(img)
    
    # Draw a red rectangle
    draw.rectangle([100, 100, 400, 400], fill='red')
    
    # Draw a blue circle
    draw.ellipse([150, 150, 350, 350], fill='blue')
    
    # Save the image
    os.makedirs('tests/test_images', exist_ok=True)
    img.save('tests/test_images/test_image.jpg', 'JPEG')

if __name__ == "__main__":
    create_test_image() 