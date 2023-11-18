   # Base Python image
   FROM python 3.11

   # Set the working directory in the container
   WORKDIR /game_id

   # Copy the local code to the container
   COPY . .

   # Install FastAPI and Uvicorn
   RUN pip install --no-cache-dir --upgrade -r requirements.txt
   
   # Expose the port the app runs on

   # Command to run the application
   CMD ["utils/uvicorn/game_id/uvicorn", "main:app", "--host 0.0.0.0", "--port 8000"]
