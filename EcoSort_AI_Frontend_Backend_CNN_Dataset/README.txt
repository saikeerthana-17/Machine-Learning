ECOSORT AI — WASTE CLASSIFICATION PROJECT
=========================================

FOLDER STRUCTURE
----------------
frontend/
  index.html     -> Frontend structure and all pages
  style.css      -> Frontend design and responsive styling
  app.js         -> Frontend interactions and API calls

backend/
  app.py         -> Flask backend, API routes, SQLite history, CNN inference hook

dataset/
  README_DATASET.txt -> Dataset labels and instructions

model/
  README_MODEL.txt -> Where to put your trained CNN model

requirements.txt -> Python dependencies
README.txt       -> Run instructions

RUN ON WINDOWS / VS CODE
------------------------
1. Extract the ZIP using "Extract All".
2. Open the extracted EcoSort_AI_Project_Files folder in VS Code.
3. Open Terminal > New Terminal.
4. Run:
   py -m venv .venv
   .venv\\Scripts\\activate
   pip install -r requirements.txt
5. Start the Flask backend:
   python backend/app.py
6. Open Chrome:
   http://127.0.0.1:5000

IMPORTANT
---------
This package includes a working website workflow, Flask REST API, SQLite
prediction history, dataset category display, and CNN model loading integration.
A real trained model.keras file and actual dataset images are not included because
they were not present in the uploaded presentation. Without a trained model,
the website uses a clearly labeled demo simulation; it is not real CNN inference.
For real inference, put a trained model.keras in the project root (next to this
README) and make sure its 7 output classes follow the exact order in backend/app.py.
