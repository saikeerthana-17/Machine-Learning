CNN MODEL FILE
Put your trained TensorFlow/Keras model in the project root and name it:
model.keras

The model must accept 224x224 RGB images normalised to [0,1], and return seven
class probabilities in this exact order:
Plastic, Paper, Cardboard, Glass, Metal, Organic Waste, Trash.

If your model has a different preprocessing pipeline or class order, update
backend/app.py before using real predictions. No trained model was supplied
with the project presentation.
