**Step 1**: Install Python

To install:
python3 --version

If it’s 3.10 or newer, you’re good! If not:

sudo apt update
sudo apt install python3 python3-venv python3-pip


**Step 2**: Create Project Folder
This is your project workspace.

mkdir workdirekt_project
cd workdirekt_project


**Step 3**: Set up Virtual Environment

python3 -m venv venv
source venv/bin/activate

**Step 4**: Install Required Packages
Inside the **venv** (you should see `(venv)` in your terminal):

pip install fastapi "uvicorn[standard]" motor flet requests matplotlib requests

**Step 5**: Create Folder Structure

mkdir Work Direkt

**Step 6**: Add Your Files

Assuming the backend is named backend.py
The frontend is named app.py
Do not forget to add pie_chart.py
All these three in the same folder

**Step 7**: Run the Backend
I
uvicorn backend:app --reload
The --reload makes sure that changes made in the frontend reflect the backend,
this prevents data not being sent properly

Backend running at:
[http://localhost:8000](http://localhost:8000)  
Check API docs at: [http://localhost:8000/docs](http://localhost:8000/docs)

**Step 8**: Run the Frontend
Open a new terminal tab (keep backend running in first tab).

Activate venv again in the new tab:

cd workdirekt_project
source venv/bin/activate

Run the frontend:
python app.py
Using 'flet run' needs to have app.py inside a folder named 'src'
Use this only when running multiple different apps with flet,
not reccommened for this project since pie_chart.py is needed

A desktop app window should pop up — that’s your frontend (Flet).
"# CookQuest" 
