import psutil
import numpy as np
import cv2
import time

try:
    import sounddevice as sd
except Exception:
    pass

class SensorReader:
    def __init__(self):
        self.available_sensors = self.detect_sensors()

    def detect_sensors(self):
        sensors = {}
        if self.is_cpu_temp_available():
            sensors['cpu_temp'] = self.read_cpu_temp
        if self.is_webcam_available():
            sensors['webcam_noise'] = self.read_webcam_noise
        if self.is_microphone_available():
            sensors['mic_noise'] = self.read_microphone_noise
        sensors['timer_fallback'] = self.timer_fallback
        print('used sensors:'," ".join(sensors.keys()))
        return sensors

    def is_cpu_temp_available(self):
        try:
            psutil.sensors_temperatures()
            return True
        except Exception:
            return False

    def is_microphone_available(self):
        try:
            sd.query_devices()
            return True
        except Exception:
            return False

    def is_webcam_available(self):
        try:
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()
            if not ret:
                return False
            return True
        except Exception:
            return False
        
    def timer_fallback(self):
        read = time.time() * 1e7
        time.sleep(0.001)
        return read

    def read_cpu_temp(self):
        if not self.is_cpu_temp_available():
            return None
        temps = psutil.sensors_temperatures()
        for name, entries in temps.items():
            for entry in entries:
                #print('cpu used')
                return entry.current
        return None

    def read_microphone_noise(self, duration=0.001):
        if not self.is_microphone_available():
            return None
        try:
            sample_rate = 44100
            recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
            sd.wait()
            #print('mic used')
            return recording
        except Exception:
            return None

    def read_webcam_noise(self):
        if not self.is_webcam_available():
            return None
        try:
            cap = cv2.VideoCapture(0)
            ret, frame = cap.read()
            cap.release()
            if not ret:
                return None
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            #print('img used')
            return gray_frame
        except Exception:
            return None

    def read_sensors(self):
        sensor_data = []
        for sensor_name, sensor_func in self.available_sensors.items():
            data = sensor_func()
            if data is not None:
                sensor_data.append(data)
        return sensor_data

