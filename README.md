# 🎓 Exam Score Prediction System — Full Stack ML Project

This project is a complete end‑to‑end machine learning system that predicts student exam scores based on study‑related features. It includes a Python machine learning pipeline, a Node.js backend API, a browser‑based frontend interface, and Netlify deployment configuration. The system demonstrates data processing, model training, prediction serving, and full‑stack integration.

---

## 🚀 Features

- Full machine learning workflow (data → model → prediction)
- Python regression model trained on real student performance data
- Node.js backend API for serving predictions
- Web‑based frontend for user interaction
- Netlify Functions + Netlify deployment support
- Saved model structure and metadata for reproducibility
- Clean project separation: ML, API, frontend, deployment

---

## 📂 Project Structure

Exam-Score-Prediction-System-Project-1  
│── .vscode/                     # Editor configuration  
│── dist/                        # Built frontend (production)  
│── netlify/functions/           # Netlify serverless functions  
│── outputs_project_1/           # Model outputs, logs, graphs  
│── public/                      # Frontend static assets  
│── .gitignore                   # Git ignore rules  
│── README.md                    # Project documentation  
│── build.js                     # Netlify build script  
│── desktop.ini                  # Windows metadata  
│── model_structure.json         # Saved model metadata  
│── netlify.toml                 # Netlify deployment config  
│── package-lock.json            # Node dependency lockfile  
│── package.json                 # Node project configuration  
│── predict.py                   # Python prediction script  
│── project_1_exam_score_regression.py   # Python model training script  
│── server.js                    # Node.js backend API  
│── student_performance_dataset.csv      # Dataset used for training  

---

## 🧠 How It Works

### 1. **Dataset**
The project uses `student_performance_dataset.csv`, containing features such as:
- Study hours  
- Attendance  
- Past scores  
- Additional academic indicators  

### 2. **Model Training (Python)**
`project_1_exam_score_regression.py`:
- Loads and cleans the dataset  
- Performs feature selection  
- Trains a regression model  
- Saves model metadata to `model_structure.json`  
- Outputs graphs and logs to `outputs_project_1/`

### 3. **Prediction Script (Python)**
`predict.py`:
- Loads the saved model  
- Accepts input values  
- Returns predicted exam score  

### 4. **Backend API (Node.js)**
`server.js`:
- Provides an HTTP API endpoint  
- Receives user input from the frontend  
- Calls the Python prediction script  
- Returns prediction results to the browser  

### 5. **Frontend**
`public/` and `dist/`:
- User interface for entering study data  
- Sends requests to the backend  
- Displays predicted exam score  

### 6. **Deployment**
Netlify configuration:
- `netlify.toml`  
- `netlify/functions/`  
- `build.js`  

Allows hosting the frontend + serverless backend.

---

## ▶️ How to Run Locally

### **Install Node.js dependencies**
npm install

### **Install Python dependencies**
pip install -r requirements.txt  
*(If no requirements file exists, install pandas, numpy, scikit-learn.)*

### **Train the model**
python project_1_exam_score_regression.py

### **Start the backend**
node server.js

### **Open the frontend**
Open `public/index.html` or run a local static server.

---

## 🛠️ Technologies Used

### **Machine Learning**
- Python  
- Pandas  
- NumPy  
- Scikit‑learn  

### **Backend**
- Node.js  
- Express  
- Child process integration with Python  

### **Frontend**
- HTML / CSS / JavaScript  

### **Deployment**
- Netlify  
- Netlify Functions  

---

## 📌 Current Limitations
- Model uses basic regression; could be improved with more features  
- No database storage  
- Frontend is static (no React/Vue)  
- Python and Node integration uses child processes (simple but not optimized)

---

## 🔧 Planned Improvements
- Add more ML models (Random Forest, Gradient Boosting)  
- Add charts showing prediction confidence  
- Add user authentication  
- Add database for storing past predictions  
- Convert frontend to React  
- Add API rate limiting and validation  

---
