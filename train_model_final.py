import os
import cv2
import numpy as np
from PIL import Image
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Activation, Dropout, Flatten, Dense
from tensorflow.keras.utils import to_categorical

# --- Configuration ---
# Set the input size for all images.
INPUT_SIZE = 64

def train_and_save_model(model_name, image_directory, class_labels, epochs=50):
    """
    Trains a new model for a specific diagnosis type and saves it.
    Args:
        model_name (str): The filename to save the trained model.
        image_directory (str): Path to the image dataset.
        class_labels (dict): Dictionary mapping folder names to class labels (e.g., {'yes': 1, 'no': 0}).
        epochs (int): Number of training epochs.
    """
    print(f"\n--- Loading and preprocessing data for {model_name} ---")

    dataset = []
    labels = []

    for folder_name, label in class_labels.items():
        folder_path = os.path.join(image_directory, folder_name)
        if not os.path.exists(folder_path):
            print(f"Warning: Directory '{folder_path}' not found. Skipping.")
            continue
        
        for image_name in os.listdir(folder_path):
            if image_name.endswith('.jpg') or image_name.endswith('.jpeg') or image_name.endswith('.png'):
                image_path = os.path.join(folder_path, image_name)
                try:
                    image = cv2.imread(image_path)
                    if image is not None:
                        image = Image.fromarray(image, 'RGB')
                        image = image.resize((INPUT_SIZE, INPUT_SIZE))
                        dataset.append(np.array(image))
                        labels.append(label)
                    else:
                        print(f"Could not read image: {image_path}")
                except Exception as e:
                    print(f"Error processing image {image_path}: {e}")

    dataset = np.array(dataset)
    labels = np.array(labels)

    if len(dataset) == 0:
        print(f"No data found for {model_name}. Skipping model training.")
        return

    print(f"Dataset size: {dataset.shape}")
    print(f"Labels size: {labels.shape}")

    # Data Splitting and Normalization
    x_train, x_test, y_train, y_test = train_test_split(dataset, labels, test_size=0.2, random_state=0)
    x_train = x_train / 255.0
    x_test = x_test / 255.0
    y_train = to_categorical(y_train, num_classes=len(class_labels))
    y_test = to_categorical(y_test, num_classes=len(class_labels))

    # Model Building
    model = Sequential()
    model.add(Conv2D(32, (3, 3), input_shape=(INPUT_SIZE, INPUT_SIZE, 3)))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Conv2D(32, (3, 3), kernel_initializer='he_uniform'))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Conv2D(64, (3, 3), kernel_initializer='he_uniform'))
    model.add(Activation('relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Flatten())
    model.add(Dense(64))
    model.add(Activation('relu'))
    model.add(Dropout(0.5))
    model.add(Dense(len(class_labels)))
    model.add(Activation('softmax'))

    # Model Compilation
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    # Model Training
    print(f"\nTraining the {model_name} model...")
    history = model.fit(
        x_train,
        y_train,
        batch_size=16,
        verbose=1,
        epochs=epochs,
        validation_data=(x_test, y_test),
        shuffle=True
    )

    # Model Saving
    print(f"\nTraining complete. Saving the model as '{model_name}'.")
    model.save(model_name)
    print(f"Model saved successfully.")

# --- Main Script ---

if __name__ == '__main__':
    # Train Brain Tumor Model
    train_and_save_model(
        model_name='BrainTumor10EpochsCategorical.h5',
        image_directory='datasets/brain_tumor',
        class_labels={'no': 0, 'yes': 1}
    )

    # Train Skin Cancer Model
    train_and_save_model(
        model_name='SkinCancerModel.h5',
        image_directory='datasets/skin_cancer',
        class_labels={'benign': 0, 'malignant': 1}
    )

    # Train Eye Disease Model
    train_and_save_model(
        model_name='EyeDiseaseModel.h5',
        image_directory='datasets/eye_disease',
        class_labels={'normal': 0, 'diabetic_retinopathy': 1}
    )
