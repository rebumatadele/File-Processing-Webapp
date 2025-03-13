# 📂 File Processing Webapp  

🚀 **File Processing Webapp** is a powerful and efficient web-based tool that allows users to **upload, process, and manage text files** with AI-driven capabilities. Built with **Next.js**, **FastAPI**, and **ShadCN**, this app provides a seamless experience for handling large text files, processing them in chunks, and optimizing AI-powered interactions.  

🔗 **Live Web App:** [File Processing Webapp](https://fileprocessor.netlify.app/)  
📂 **GitHub Repository:** [File Processing Webapp](https://github.com/rebumatadele/File-Processing-Webapp)  

---

## 📝 About  

File Processing Webapp is designed for users who work with **large text files** and require efficient **AI-powered processing**. It enables **file uploads**, **chunked processing**, and **real-time updates** while maintaining robust **error handling** and **progress tracking**.  

With support for **multiple AI providers** (OpenAI, Anthropic Claude, and Gemini), users can leverage advanced AI models to analyze, summarize, or transform text files dynamically.  

---

## 🚀 Features  

✅ **File Upload & Management** – Easily upload and manage text files via an intuitive interface.  
✅ **AI-Powered Processing** – Supports OpenAI, Claude, and Gemini models for intelligent text processing.  
✅ **Chunked File Processing** – Handles large text files efficiently by processing them in chunks.  
✅ **Real-Time Updates** – Displays status updates without interrupting workflow.  
✅ **Error Handling & Logging** – Provides detailed error messages and allows users to clear logs.  
✅ **Custom Prompt Management** – Save, edit, and manage AI processing prompts dynamically.  
✅ **File Editing & Previewing** – View and edit file contents before processing.  
✅ **Download Processed Files** – Retrieve processed files for further use.  
✅ **Graceful Retry Mechanism** – Automatically retries failed processing tasks with a backoff strategy.  
✅ **API Utility Functions** – Integrates backend API calls seamlessly for smooth user interactions.  

---

## 🔧 Tech Stack  

### **Frontend (Next.js & ShadCN)**  
- **📜 Next.js** – React-based framework for fast and efficient web applications.  
- **🎨 ShadCN** – Modern UI components for a sleek, aesthetic user experience.  
- **⚡ Tailwind CSS** – Responsive and customizable styling.  
- **📌 React Hook Form & Zod** – Form validation for better user input handling.  

### **Backend (FastAPI)**  
- **🚀 FastAPI** – High-performance API for handling text processing requests.  
- **📂 File Storage** – Manages file uploads and retrieval efficiently.  
- **📡 AI Model Integrations** – Supports OpenAI, Anthropic Claude, and Gemini.  
- **🔄 Background Processing** – Processes files asynchronously with retry mechanisms.  
- **📊 Logging & Error Tracking** – Provides visibility into system operations.  

---

## 📜 How It Works  

### **1️⃣ Upload Files**  
- Users can **drag and drop** or select files to upload.  

### **2️⃣ Configure AI Processing**  
- Choose an AI provider (OpenAI, Claude, Gemini).  
- Set processing options and prompts.  

### **3️⃣ Process Files in Chunks**  
- Large files are split into chunks for efficient processing.  
- Processing status updates appear in real-time.  

### **4️⃣ View & Edit Results**  
- Users can preview, edit, and manage processed files.  

### **5️⃣ Download or Retry Processing**  
- Download final processed files.  
- Retry failed tasks with built-in error handling.  

---

## 🛠 Installation & Setup  

### **Running Locally**  

1. **Clone the repository:**  
   ```bash
   git clone https://github.com/rebumatadele/File-Processing-Webapp.git
   cd File-Processing-Webapp
   ```

2. **Backend Setup (FastAPI):**  
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   pip install -r requirements.txt
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

3. **Frontend Setup (Next.js):**  
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

4. Open your browser and navigate to `http://localhost:3000/`  

---

## 🖥 API Endpoints  

### **1️⃣ Upload a File**  
- **Endpoint:** `POST /upload`  
- **Description:** Uploads a text file for processing.  

### **2️⃣ Start File Processing**  
- **Endpoint:** `POST /process/{file_id}`  
- **Description:** Begins AI-powered processing of a file in chunks.  

### **3️⃣ Check Processing Status**  
- **Endpoint:** `GET /status/{file_id}`  
- **Description:** Retrieves real-time file processing progress.  

### **4️⃣ Download Processed File**  
- **Endpoint:** `GET /download/{file_id}`  
- **Description:** Fetches the final processed text file.  

### **5️⃣ Manage AI Prompts**  
- **Endpoint:** `GET /prompts`, `POST /prompts`, `PUT /prompts/{id}`, `DELETE /prompts/{id}`  
- **Description:** CRUD operations for AI processing prompts.  

---

## 🔥 Deployment  

### **Docker Setup**  
1. **Build and run the FastAPI backend:**  
   ```bash
   docker-compose up -d --build
   ```

2. **Deploy the frontend on Netlify:**  
   - Connect the **frontend** directory to **Netlify**.  
   - Set up environment variables for API URL and authentication keys.  

---

## 📜 License  

This project is open-source and licensed under the **MIT License**.  

---

## 🙌 Contributing  

We welcome contributions! If you’d like to improve the project, feel free to:  
- **Fork the repository**  
- **Submit issues and feature requests**  
- **Open pull requests with improvements**  

---

## 📩 Contact  

For any inquiries or collaborations:  
🔗 **GitHub:** [Rebuma Tadele](https://github.com/rebumatadele)  

Let’s make AI-powered file processing efficient and accessible! 🚀📂
