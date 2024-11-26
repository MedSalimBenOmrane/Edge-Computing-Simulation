from utils.client import ClientFactory
import time
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from datetime import datetime

CLOUD_TOPIC = "cloud"
SENSORS_TOPIC = "sensors"
BROKER = "localhost"
PORT = 1883

cloud_data = []
sensor_data = []
cloud_times = []  # Timestamps for cloud data
sensor_times = []  # Timestamps for sensor data

client = ClientFactory(CLOUD_TOPIC)

# Callback function to handle incoming messages
def on_message(client, userdata, message):
    topic = message.topic
    data = float(message.payload.decode())
    timestamp = datetime.now()  # Get the current time

    if topic == CLOUD_TOPIC:
        cloud_data.append(data)
        cloud_times.append(timestamp)
        print(f"Received data from CLOUD at {timestamp}: {data}")
    elif topic == SENSORS_TOPIC:
        sensor_data.append(data)
        sensor_times.append(timestamp)
        print(f"Received data from SENSORS at {timestamp}: {data}")

# Assign the callback to the client
client.on_message = on_message

# Connect to the broker and subscribe to both topics
client.connect(BROKER, PORT)
client.subscribe([(CLOUD_TOPIC, 0), (SENSORS_TOPIC, 0)])
client.loop_start()

# Initialize the plot
fig, ax = plt.subplots()
ax.set_title("Graph of Data Published to Cloud and Sensors")
ax.set_xlabel("Time")
ax.set_ylabel("Data Value")

def update(frame):
    ax.clear()  # Clear the axis to prevent overlapping
    
    # Plot cloud data with time
    if cloud_times:
        ax.plot(cloud_times, cloud_data, label="Cloud Data", color="b")

    # Plot sensor data with time
    if sensor_times:
        ax.plot(sensor_times, sensor_data, label="Sensor Data", color="r")
    
    # Format the x-axis for better readability (rotating the time labels)
    ax.xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%H:%M:%S'))
    plt.xticks(rotation=45)
    
    ax.set_title("Graph of Data Published to Cloud and Sensors")
    ax.set_xlabel("Time")
    ax.set_ylabel("Data Value")
    ax.legend()

# Use FuncAnimation to update the plot in real-time
ani = FuncAnimation(fig, update, interval=1000)
plt.show()

# Keep the program running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Stopping the program")
finally:
    client.loop_stop()
    client.disconnect()