# Audio Recorder
import sounddevice as sd
import numpy as np
import wave
import tempfile
import os
import threading
import queue
import time
import logging

logger = logging.getLogger(__name__)


class AudioRecorder:
    """Handles audio recording with silence detection"""
    
    def __init__(self, sample_rate=44100, channels=1, block_size=1024):
        self.sample_rate = sample_rate
        self.channels = channels
        self.block_size = block_size
        
        self.audio_queue = queue.Queue()
        self.stop_event = threading.Event()
        self.is_recording = False
        self.last_speech_time = 0
        self.current_volume = 0
        
        # Volume tracking for quality indicator
        self.recent_volumes = []
        self.max_volume_history = 10
        
        # Callbacks
        self.on_volume_change = None  # Callback for volume updates
        self.on_recording_complete = None  # Callback with WAV file path
        self.on_low_volume_warning = None  # Callback for low volume warning
    
    def start(self, silence_threshold=0.015, silence_duration=1.2):
        """Start recording audio"""
        if self.is_recording:
            logger.warning("Already recording")
            return
        
        self.is_recording = True
        self.stop_event.clear()
        self.audio_queue = queue.Queue()
        self.last_speech_time = time.time()
        
        logger.info("Recording started")
        
        # Start recording thread
        threading.Thread(
            target=self._record_loop,
            args=(silence_threshold, silence_duration),
            daemon=True
        ).start()
    
    def stop(self):
        """Stop recording"""
        if not self.is_recording:
            return
        
        logger.info("Stopping recording")
        self.is_recording = False
        self.stop_event.set()
    
    def _record_loop(self, silence_threshold, silence_duration):
        """Recording loop with silence detection"""
        try:
            with sd.InputStream(
                samplerate=self.sample_rate,
                channels=self.channels,
                blocksize=self.block_size,
                callback=self._audio_callback
            ):
                while not self.stop_event.is_set():
                    if time.time() - self.last_speech_time > silence_duration:
                        logger.info("Silence detected, stopping")
                        self.stop_event.set()
                        break
                    time.sleep(0.05)
            
            # Process recorded audio
            self._process_audio(silence_threshold)
            
        except Exception as e:
            logger.error(f"Recording error: {e}")
            if self.on_recording_complete:
                self.on_recording_complete(None, error=str(e))
    
    def _audio_callback(self, indata, frames, time_info, status):
        """Callback for each audio block"""
        self.audio_queue.put(indata.copy())
        
        # Calculate volume
        vol = np.linalg.norm(indata) * 10
        self.current_volume = vol
        
        # Track volume history for quality indicator
        self.recent_volumes.append(vol)
        if len(self.recent_volumes) > self.max_volume_history:
            self.recent_volumes.pop(0)
        
        # Update last speech time if volume above threshold
        if vol > 0.015:  # Use a default threshold here
            self.last_speech_time = time.time()
        
        # Check for low volume warning
        if len(self.recent_volumes) >= 5:  # Need some history
            avg_volume = sum(self.recent_volumes) / len(self.recent_volumes)
            if self.on_low_volume_warning:
                # Emit warning if average is below 0.01 (configurable threshold)
                self.on_low_volume_warning(avg_volume < 0.01)
        
        # Notify volume change
        if self.on_volume_change:
            self.on_volume_change(vol)
    
    def _process_audio(self, silence_threshold):
        """Process recorded audio into WAV file"""
        if self.audio_queue.empty():
            logger.warning("No audio data recorded")
            if self.on_recording_complete:
                self.on_recording_complete(None)
            return
        
        # Collect all frames
        frames = []
        while not self.audio_queue.empty():
            frames.append(self.audio_queue.get())
        
        audio = np.concatenate(frames, axis=0)
        
        # Check minimum duration
        if len(audio) < self.sample_rate * 0.5:
            logger.warning("Audio too short, skipping")
            if self.on_recording_complete:
                self.on_recording_complete(None)
            return
        
        # Save to temporary WAV file
        try:
            temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
            temp_path = temp_file.name
            temp_file.close()
            
            with wave.open(temp_path, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)
                wf.setframerate(self.sample_rate)
                wf.writeframes((audio * 32767).astype(np.int16).tobytes())
            
            logger.info(f"Audio saved to: {temp_path}")
            
            if self.on_recording_complete:
                self.on_recording_complete(temp_path)
                
        except Exception as e:
            logger.error(f"Audio processing error: {e}")
            if self.on_recording_complete:
                self.on_recording_complete(None, error=str(e))
