from utils.client import ClientFactory
from utils.movingaverage import moving_average
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime

CLOUD_TOPIC = "sensors"
BROKER = "localhost"
PORT = 1883

data = []
original_data = []
reduced_data = []
original_times = []  # To store timestamps for original data
reduced_times = []   # To store timestamps for reduced data
WINDOW_SIZE = 15

client = ClientFactory(CLOUD_TOPIC)

# Callback function to handle incoming messages
def on_message(client, userdata, message):
    global original_data, reduced_data
    payload = float(message.payload.decode())
    current_time = datetime.now()  # Get the current time

    # Store original data and timestamp
    original_data.append(payload)
    original_times.append(current_time)
    
    # Add data to the window for moving average calculation
    data.append(payload)

    # Calculate moving average once we have enough data
    if len(data) >= WINDOW_SIZE:
        avg = moving_average(data, WINDOW_SIZE)
        reduced_data.append(avg)
        reduced_times.append(current_time)  # Store the same timestamp as original data
        
        # Remove the oldest data point from the window
        data.pop(0)
    
    print(f"Received original data: {payload}, moving average: {reduced_data}")

# Assign the callback to the client
client.on_message = on_message

# Connect to the broker and subscribe to the cloud topic
client.connect(BROKER, PORT)
client.subscribe(CLOUD_TOPIC)
client.loop_start()

# Set up the plot
#plt.style.use("seaborn")
fig, ax = plt.subplots()
ax.set_title("Graphique des données moyennes publiées vers le cloud")
ax.set_xlabel("Temps")
ax.set_ylabel("Valeur moyenne")

def update(frame):
    ax.clear()  # Clear the axis to prevent overlapping

    # Plot original data with timestamps
    if original_times:
        ax.plot(original_times, original_data, label="Données originales", color="r")

    # Plot reduced (moving average) data with timestamps
    if reduced_times:
        ax.plot(reduced_times, reduced_data, label="Moyenne mobile", color="b")

    # Format the x-axis to show time in HH:MM:SS format
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M:%S'))
    plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
    
    ax.set_title("Graphique des données moyennes publiées vers le cloud")
    ax.set_xlabel("Temps")
    ax.set_ylabel("Valeur moyenne")
    ax.legend()

# Use FuncAnimation to update the plot in real-time
ani = FuncAnimation(fig, update, interval=1000)
plt.show()

# Keep the program running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Arrêt du programme")
finally:
    client.loop_stop()
    client.disconnect()