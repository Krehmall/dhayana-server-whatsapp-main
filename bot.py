import time
from openai import OpenAI
from whatsapp_chatbot_python import (
    BaseStates,
    GreenAPIBot,
    Notification,
    filters,
)

# Configuration for the bot
ID_INSTANCE = 'ID_INSTANCE'
API_TOKEN_INSTANCE = 'API_TOKEN_INSTANCE'

# Initialize the bot
bot = GreenAPIBot(
    ID_INSTANCE,
    API_TOKEN_INSTANCE
)

# Set up OpenAI API client
client = OpenAI(api_key="api_key")


# Function to start a new session with OpenAI
class Student:

    def __init__(self, user_id):
        self.current_run_id = None
        self.current_thread_id = None
        self.user_id = user_id
        self.chats_history = []
        self.class_id = 0

    def start_new_session(self):
        self.current_thread_id = client.beta.threads.create().id
        run_instance = client.beta.threads.runs.create(
            thread_id=self.current_thread_id,
            instructions="",
            assistant_id="assistant_id", model="gpt-3.5-turbo-1106")
        self.current_run_id = run_instance.id
        return self.current_thread_id


students = {}
# Predefine the user_id for simplicity
user_id = 'user_id'
students[user_id] = (Student(user_id))
sid = students[user_id].start_new_session()
print(f"Started session with thread ID: {sid}")


# Define a handler for text messages
@bot.router.message(type_message=filters.TEXT_TYPES)
def handle_text_message(notification: Notification) -> None:
    global messages, response
    try:
        message_content = notification.event.get("messageData", {}).get("textMessageData", {}).get("textMessage", "")
        print(f"Received message from {notification.sender}: {message_content}")
        client.beta.threads.messages.create(
            thread_id=students[user_id].current_thread_id,
            role="user",
            content=message_content
        )
        run_instance = client.beta.threads.runs.create(
            thread_id=students[user_id].current_thread_id,
            assistant_id="assistant_id")
        students[user_id].current_run_id = run_instance.id
        if students[user_id]:
            t_id = students[user_id].current_thread_id
            r_id = students[user_id].current_run_id
            while True:
                run = client.beta.threads.runs.retrieve(thread_id=t_id, run_id=r_id)
                if run.status == "completed":
                    break
                time.sleep(0.2)
            messages = client.beta.threads.messages.list(thread_id=students[user_id].current_thread_id)
            response = messages.data[0].content[0].text.value
        for i in messages.data:
            print(i)
        notification.answer(response)
    except Exception as e:
        print(f"Error handling message: {e}")


# Start the bot
if __name__ == "__main__":
    try:
        bot.run_forever()
    except KeyboardInterrupt:
        print("Bot stopped by user.")
    except Exception as e:
        print(f"Error running the bot: {e}")
