from fastapi import FastAPI

app = FastAPI()

cycle = 0

@app.get('/policy/cycle')
def getCycle():
    global cycle
    cycle += 1
    return cycle

