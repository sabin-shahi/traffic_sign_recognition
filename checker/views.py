from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from keras.models import load_model
import os
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from PIL import Image
import numpy as np
from django.contrib.auth.decorators import login_required
from .forms import UserForm
from .models import CustomUser


@login_required
def user_profile(request):
    user = request.user
    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_profile')
    else:
        form = UserForm(instance=user)
    return render(request, 'user_profile.html', {'form': form})


def user_list(request):
    users = CustomUser.objects.all()
    return render(request, 'user_list.html', {'users': users})



# Define the path to the model file
MODEL_PATH = os.path.join('models', 'tmodel.keras')

# Define the upload folder
UPLOAD_FOLDER = settings.UPLOAD_FOLDER

def load_model_from_file(model_path: str) -> any:
    """Load the model from the file."""
    try:
        return load_model(model_path)
    except Exception as e:
        print(f"Error loading model: {e}")
        return None

# Define the classes
classes = {
    1: 'Speed limit (20km/h)',
    2: 'Speed limit (30km/h)',
    3: 'Speed limit (50km/h)',
    4: 'Speed limit (60km/h)',
    5: 'Speed limit (70km/h)',
    6: 'Speed limit (80km/h)',
    7: 'End of speed limit (80km/h)',
    8: 'Speed limit (100km/h)',
    9: 'Speed limit (120km/h)',
    10: 'No passing',
    11: 'No passing veh over 3.5 tons',
    12: 'Right-of-way at intersection',
    13: 'Priority road',
    14: 'Yield',
    15: 'Stop',
    16: 'No vehicles',
    17: 'Veh > 3.5 tons prohibited',
    18: 'No entry',
    19: 'General caution',
    20: 'Dangerous curve left',
    21: 'Dangerous curve right',
    22: 'Double curve',
    23: 'Bumpy road',
    24: 'Slippery road',
    25: 'Road narrows on the right',
    26: 'Road work',
    27: 'Traffic signals',
    28: 'Pedestrians',
    29: 'Children crossing',
    30: 'Bicycles crossing',
    31: 'Beware of ice/snow',
    32: 'Wild animals crossing',
    33: 'End speed + passing limits',
    34: 'Turn right ahead',
    35: 'Turn left ahead',
    36: 'Ahead only',
    37: 'Go straight or right',
    38: 'Go straight or left',
    39: 'Keep right',
    40: 'Keep left',
    41: 'Roundabout mandatory',
    42: 'End of no passing',
    43: 'End no passing vehicle with a weight greater than 3.5 tons',
}



def process_image(image_file: any) -> np.ndarray:
    """Process the image."""
    image = Image.open(image_file)
    image = image.resize((30, 30))  # Resize the image
    image = np.array(image) / 255.0  # Normalize the image
    image = np.expand_dims(image, axis=0)  # Add batch dimension
    return image

def make_prediction(model: any, image: np.ndarray) -> str:
    """Make a prediction using the model."""
    try:
        pred = np.argmax(model.predict(image), axis=1)[0]  # Get index of the highest probability
        return classes.get(pred + 1, "Unknown sign")  # Use .get() to avoid KeyError
    except Exception as e:
        print(f"Error making prediction: {e}")
        return "Unknown sign"

def store_prediction_history(sign: str, image_name: str) -> None:
    """Store the prediction history."""
    history_file_path = os.path.join(settings.BASE_DIR, 'history.txt')
    history_list = read_prediction_history()
    history_list.append({'prediction': sign, 'image_name': image_name})
    with open(history_file_path, 'w') as f:
        for item in history_list:
            f.write(f"{item['prediction']} - {item['image_name']}\n")

def read_prediction_history() -> list:
    """Read the prediction history."""
    history_file_path = os.path.join(settings.BASE_DIR, 'history.txt')
    if os.path.exists(history_file_path):
        with open(history_file_path, 'r') as f:
            history_list = []
            for line in f.readlines():
                sign, image_name = line.strip().split(' - ')
                history_list.append({'prediction': sign, 'image_name': image_name})
            return history_list[-6:] 
    else:
        print('no_such file')
        return []

def samples_read() -> list:
    """Read the prediction history."""
    history_file_path = os.path.join(settings.BASE_DIR, 'samples.txt')
    if os.path.exists(history_file_path):
        with open(history_file_path, 'r') as f:
            sample_list = []
            for line in f.readlines():
                sign, image_name = line.strip().split(' - ')
                sample_list.append({'prediction': sign, 'image_name': image_name})
            return sample_list

def checker(request):
    if request.method == 'POST' and request.FILES['image']:
        image_file = request.FILES['image']
        image_name = image_file.name  # Get the original filename

        # Save the image
        fs = FileSystemStorage(location=UPLOAD_FOLDER)
        filename = fs.save(image_file.name, image_file)
        image_path = fs.url(filename)  # URL to be used in the template

        # Load the model
        model = load_model(MODEL_PATH)

        # Process the image
        image = process_image(image_file)

        # Make a prediction
        sign = make_prediction(model, image)

        # Store the prediction history
        store_prediction_history(sign, image_name)

        # Read the prediction history
        history_list = read_prediction_history()
        


    return render(request, 'checker.html', {'sign': sign, 'new_image': image_path, 'history_list': history_list})

    # return render(request, 'checker.html')

# def index(request):
#     return render(request, 'index.html')

def index(request):
    sample_list = samples_read()
    return render(request, 'index.html', {'sample_list': sample_list})