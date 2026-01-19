from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel
from bson import ObjectId

# MongoDB Atlas connection
MONGO_URI = "mongodb+srv://jckngo:Jan2021130120@cluster0.1vhlw.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = AsyncIOMotorClient(MONGO_URI)
db = client.work_direkt

app = FastAPI()

'''-------------------- Models --------------------'''

class Job(BaseModel):
    name: str
    description: str

class Review(BaseModel):
    username: str
    rating: int
    text: str

class LoginRequest(BaseModel):
    username: str
    password: str

'''-------------------- Authentication --------------------'''

users_db = users_collection = db.users

@app.post("/auth/login")
async def login(user: LoginRequest):
    existing_user = await db.users.find_one({"username": user.username})

    if existing_user and existing_user["password"] == user.password:
        return {"username": user.username, "role": existing_user.get("role", "customer")}
    
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/auth/signup")
async def signup(user: LoginRequest):
    existing_user = await users_collection.find_one({"username": user.username})
    
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    new_user = {"username": user.username, "password": user.password, "role": "customer"}
    await users_collection.insert_one(new_user)

    return {"message": "Signup successful"}


'''-------------------- Database Helper Functions --------------------'''

def job_serializer(job):
    return {
        "_id": str(job["_id"]),
        "name": job["name"],
        "description": job["description"],
    }

def review_serializer(review):
    return {
        "_id": str(review["_id"]),
        "job_id": str(review["job_id"]),  # Ensure job_id is a string
        "username": review["username"],
        "rating": review["rating"],
        "text": review["text"],
    }

'''-------------------- Job Management --------------------'''

@app.get("/jobs/")
async def get_jobs():
    jobs = await db.jobs.find().to_list(None)
    return [job_serializer(job) for job in jobs]

@app.post("/jobs/")
async def add_job(job: Job):
    new_job = await db.jobs.insert_one(job.dict())
    return {"id": str(new_job.inserted_id)}

@app.put("/jobs/{job_id}")
async def edit_job(job_id: str, job: Job):
    result = await db.jobs.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": job.dict()}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Job updated"}

@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    result = await db.jobs.delete_one({"_id": ObjectId(job_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Job deleted"}

@app.get("/jobs/{job_id}/rating")
async def get_average_rating(job_id: str):
    reviews = await db.reviews.find({"job_id": ObjectId(job_id)}).to_list(None)
    if not reviews:
        return {"average_rating": None}  # No reviews yet
    avg_rating = sum(review["rating"] for review in reviews) / len(reviews)
    return {"average_rating": round(avg_rating, 1)}

'''-------------------- Review Management --------------------'''

@app.get("/reviews/{job_id}")
async def get_reviews(job_id: str):
    reviews = await db.reviews.find({"job_id": ObjectId(job_id)}).to_list(None)
    return [review_serializer(review) for review in reviews]

@app.post("/reviews/{job_id}")
async def add_review(job_id: str, review: Review):
    review_data = review.dict()
    review_data["job_id"] = ObjectId(job_id)  # Store job_id as ObjectId
    new_review = await db.reviews.insert_one(review_data)
    return {"id": str(new_review.inserted_id)}

@app.get("/reviews/")
async def get_all_reviews():
    reviews = await db.reviews.find().to_list(None)
    return [review_serializer(review) for review in reviews]

