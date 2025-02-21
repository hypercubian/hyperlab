Here's a **Poetry Cheat Sheet** for managing dependencies and virtual environments in Python:

---

# **📌 Poetry Cheat Sheet**
Poetry is a dependency management and packaging tool for Python.

---

## **🔹 Installation**
```sh
curl -sSL https://install.python-poetry.org | python3 -
```
Verify installation:
```sh
poetry --version
```

---

## **🔹 Create a New Project**
```sh
poetry new my_project
cd my_project
```

---

## **🔹 Initialize Poetry in an Existing Project**
```sh
poetry init
```
Follow the prompts to configure the project.

---

## **🔹 Virtual Environment**
Poetry automatically manages a virtual environment.

Activate the environment:
```sh
poetry shell
```

Check where the environment is located:
```sh
poetry env info
```

If needed, create a new virtual environment:
```sh
poetry env use python3
```

---

## **🔹 Managing Dependencies**
### **📥 Add Dependencies**
```sh
poetry add requests
```
For a specific version:
```sh
poetry add pandas@1.3.3
```
For development dependencies:
```sh
poetry add pytest --dev
```

### **📤 Remove Dependencies**
```sh
poetry remove requests
```

### **📋 List Dependencies**
```sh
poetry show
```

---

## **🔹 Dependency Resolution**
### **🔄 Update Dependencies**
```sh
poetry update
```

### **📌 Lock Dependencies**
```sh
poetry lock
```

### **🔄 Install Dependencies from `pyproject.toml`**
```sh
poetry install
```

---

## **🔹 Running Scripts**
Run a Python script within the environment:
```sh
poetry run python script.py
```
Run any command within the environment:
```sh
poetry run <command>
```

---

## **🔹 Publishing a Package**
1. **Build the package**:
   ```sh
   poetry build
   ```
2. **Publish to PyPI**:
   ```sh
   poetry publish --username <your-username> --password <your-password>
   ```

---

## **🔹 Miscellaneous**
### **📌 Show Project Info**
```sh
poetry show --tree
```

### **📌 Check for Security Vulnerabilities**
```sh
poetry audit
```

### **📌 Remove Virtual Environment**
```sh
poetry env remove python
```

---