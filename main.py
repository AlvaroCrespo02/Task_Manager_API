from fastapi import FastAPI
import db_test

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/health")
def health_check():
    db_test.dbHealthCheck()
    return {"status": "healthy"}

@app.get("/cars")
def listCars():
    garage = db_test.checkGarage()
    print("List of cars: ", garage)
    # return {"task status": "finished"}
    return garage