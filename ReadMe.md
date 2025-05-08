# 📅 Calendar Automation Project

This project automates calendar-related tasks using the **Google Calendar API**. Follow the detailed instructions below to properly set up your environment and authenticate using your Google credentials.

---

## ✅ Prerequisites

Before beginning, ensure you have:

* Python 3.8 or newer installed
* The provided `requirements.txt` file
* A Google Cloud project with the Google Calendar API enabled
* Your `credentials.json` file downloaded from the Google Developer Console

---

## 💻 Environment Setup

### 🪟 Windows

1. **Open PowerShell or CMD** in your project folder.

2. **Create a virtual environment**:

```powershell
python -m venv sandboxenvwin
```

3. **Activate the virtual environment**:

* PowerShell:

  ```powershell
  .\sandboxenvwin\Scripts\Activate.ps1
  ```
* CMD:

  ```cmd
  sandboxenvwin\Scripts\activate
  ```

4. **Install Dependencies**:

```powershell
pip install -r requirements.txt
```

### 🍎 macOS / Linux

1. **Open Terminal** in your project folder.

2. **Create a virtual environment**:

```bash
python3 -m venv sandboxenvwin
```

3. **Activate the virtual environment**:

```bash
source sandboxenvwin/bin/activate
```

4. **Install dependencies**:

```bash
pip install -r requirements.txt
```

---

## 🔐 Google Calendar API Authentication

### Step 1: Obtain Credentials

1. Navigate to the [Google Cloud Console](https://console.cloud.google.com/).
2. Enable the **Google Calendar API**.
3. Download the OAuth 2.0 Client ID credentials and save it to:

```
./UserCredentials/credentials.json
```

### Step 2: Generate Token File

After activating your virtual environment, execute the following Python commands to generate your token file:

```python
from auth import create_token_file

create_token_file(
    credentials_path='./UserCredentials/credentials.json',
    token_path='./UserCredentials/token.json'
)
```

> This will open a browser window prompting Google authentication.

---

## 🚨 Important Note

Always run your scripts using the Python executable from your activated virtual environment to ensure you're using the correct libraries:

* **Windows**:

```powershell
.\sandboxenvwin\Scripts\python.exe main.py
```

* **macOS/Linux**:

```bash
sandboxenvwin/bin/python main.py
```

---

## 🧪 Verify Setup

Confirm your Python environment and dependencies by running:

```bash
python --version
pip list
```

Then test your script with:

```bash
python main.py
```

---

## 📁 Project Structure

Your project directory should look like this:

```
GITHUB/
├── Calendar Automation Project/
│   ├── calendar_functions.ipynb
│   ├── main.py
│   ├── methods.py
│   └── README.md
├── sandboxenvmac/          # Virtual environment (ignored by Git)
├── sandboxenvwin/          # Virtual environment (ignored by Git)
├── UserCredentials/
│   ├── credentials.json
│   └── token.json
├── .gitignore
├── ReadMe.md
└── requirements.txt
```

---

## 🛟 Troubleshooting

* If PowerShell restricts scripts, execute:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

* If browser authentication doesn't auto-open, use:

```python
flow.run_local_server(open_browser=False)
```

---
