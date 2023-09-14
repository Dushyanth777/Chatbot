# chatbot_server.py
import openai
import speech_recognition as sr
import pyttsx3
import time
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# OpenAI API key
openai.api_key = "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"

# Define a variable to keep track of the last API request time
last_api_request_time = 0

# Define the rate limit interval (in seconds) - adjust as needed
rate_limit_interval = 2  # 1 request per 2 seconds

# Initialize the input method as None (to be set by the user)
input_method = None

def generate_response(prompt):
    global last_api_request_time  # Use the global variable

    # Calculate the time elapsed since the last API request
    time_elapsed = time.time() - last_api_request_time

    # Check if the time elapsed is less than the rate limit interval
    if time_elapsed < rate_limit_interval:
        # If the rate limit is exceeded, wait for the remaining time
        sleep_time = rate_limit_interval - time_elapsed
        print(f"Rate limit exceeded. Waiting for {sleep_time:.2f} seconds...")
        time.sleep(sleep_time)

    # Record the current time as the new last API request time
    last_api_request_time = time.time()

    # Rest of your code to generate the OpenAI response
    model_engine = "text-davinci-003"
    prompt = (f"{prompt}")

    completions = openai.Completion.create(
        engine=model_engine,
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )

    message = completions.choices[0].text
    return message.strip()

def get_user_input():
    global input_method  # Use the global variable

    if input_method is None:
        print("Choose your input method:")
        print("1. Text")
        print("2. Voice")

        while True:
            choice = input("Enter 1 or 2: ")

            if choice == "1":
                input_method = "text"
                break
            elif choice == "2":
                input_method = "voice"
                break
            else:
                print("Invalid choice. Enter 1 for text or 2 for voice.")

    if input_method == "text":
        text_input = input("Enter your question: ")
        return text_input
    elif input_method == "voice":
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            audio = recognizer.listen(source)

        try:
            text_input = recognizer.recognize_google(audio)
            return text_input
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that.")
        except sr.RequestError as e:
            print("Could not request results; {0}".format(e))

def speak_response(response_text):
    engine = pyttsx3.init()
    engine.say(response_text)
    engine.runAndWait()

@app.route("/", methods=["GET", "POST"])
def chat():
    if request.method == "POST":
        user_input = request.form.get("user_input")
        if user_input.lower() == "exit":
            return jsonify({"bot_response": "Goodbye!"})
        response = generate_response(user_input)
        speak_response(response)
        return jsonify({"bot_response": response})
    return render_template("Fronend.html")  # Render the "Fronend.html" template

if __name__ == "__main__":
    app.run(debug=True)
