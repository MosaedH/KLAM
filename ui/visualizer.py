# Framer-Style Audio Visualizer Component
import tkinter as tk
import time
import math
import random
from utils.constants import DPI_SCALE, WAVE_ACTIVE_COLOR, WAVE_IDLE_COLOR


class AudioVisualizer(tk.Canvas):
    """Framer-style symmetric vertical bar audio visualizer"""
    
    def __init__(self, master, width, height, bg_color):
        super().__init__(master, width=width, height=height, bg=bg_color, 
                         highlightthickness=0, bd=0)
        
        self.width = width
        self.height = height
        
        # Bar configuration - Framer style
        self.bar_count = 17  # Odd number for center symmetry
        self.bar_width = int(2 * DPI_SCALE)  # Thin bars
        self.bar_spacing = int(4 * DPI_SCALE)  # Space between bars
        self.min_height = int(3 * DPI_SCALE)  # Minimum dot size
        self.max_height = height * 0.7  # Maximum bar height
        
        # Animation state
        self.target_volume = 0.0
        self.current_volume = 0.0
        
        # Bar state (height and velocity for spring physics)
        self.bar_heights = [self.min_height] * self.bar_count
        self.bar_velocities = [0.0] * self.bar_count
        self.bar_targets = [self.min_height] * self.bar_count
        
        # Random phases for idle animation
        self.bar_phases = [random.random() * math.pi * 2 for _ in range(self.bar_count)]
        
        # Create bars
        self.bars = []
        total_width = (self.bar_width * self.bar_count) + (self.bar_spacing * (self.bar_count - 1))
        start_x = (width - total_width) / 2
        
        for i in range(self.bar_count):
            x = start_x + i * (self.bar_width + self.bar_spacing)
            bar = self.create_line(
                x, height/2,
                x, height/2,
                width=self.bar_width,
                capstyle="round",
                fill=WAVE_IDLE_COLOR
            )
            self.bars.append(bar)
        
        self._animate()
    
    def set_volume(self, vol):
        """Set target volume for animation"""
        self.target_volume = min(vol * 60, 1.0)
    
    def _get_symmetric_factor(self, index):
        """Get position factor for symmetric design (0=edge, 1=center)"""
        center = self.bar_count // 2
        distance_from_center = abs(index - center)
        max_distance = center
        return 1.0 - (distance_from_center / max_distance) if max_distance > 0 else 1.0
    
    def _animate(self):
        """Animate the bars with symmetric mirroring"""
        # Smooth volume transition
        diff = self.target_volume - self.current_volume
        self.current_volume += diff * 0.25
        
        t = time.time()
        center = self.bar_count // 2
        
        # Determine if we're in active mode
        is_active = self.current_volume > 0.05
        
        # Update bar targets
        for i in range(self.bar_count):
            # Get symmetric factor (1.0 at center, 0.0 at edges)
            sym_factor = self._get_symmetric_factor(i)
            
            if is_active:
                # Active mode: audio-reactive with symmetry
                # Center bars are tallest, edge bars are smallest
                base_amplitude = self.min_height + (self.max_height - self.min_height) * self.current_volume
                
                # Add some randomness for natural feel (but keep it symmetric)
                if i <= center:
                    # Left half or center - generate random
                    noise = math.sin(t * 3 + self.bar_phases[i]) * 0.2 + 1.0
                    target = self.min_height + (base_amplitude - self.min_height) * sym_factor * noise
                else:
                    # Right half - mirror the left
                    mirror_index = self.bar_count - 1 - i
                    target = self.bar_targets[mirror_index]
                
                self.bar_targets[i] = target
            else:
                # Idle mode: gentle symmetric pulsing
                idle_wave = math.sin(t * 2 + self.bar_phases[i]) * 0.5 + 0.5
                idle_amplitude = self.min_height + int(4 * DPI_SCALE) * idle_wave
                
                # Make it symmetric
                if i <= center:
                    self.bar_targets[i] = idle_amplitude * (0.3 + 0.7 * sym_factor)
                else:
                    mirror_index = self.bar_count - 1 - i
                    self.bar_targets[i] = self.bar_targets[mirror_index]
        
        # Apply spring physics to reach targets smoothly
        spring_strength = 0.18
        damping = 0.72
        
        for i, bar in enumerate(self.bars):
            # Spring physics
            force = (self.bar_targets[i] - self.bar_heights[i]) * spring_strength
            self.bar_velocities[i] = self.bar_velocities[i] * damping + force
            self.bar_heights[i] += self.bar_velocities[i]
            
            # Clamp height
            h = max(self.min_height, min(self.bar_heights[i], self.max_height))
            
            # Update bar position (centered vertically)
            x = self.coords(bar)[0]
            y_center = self.height / 2
            self.coords(bar, x, y_center - h/2, x, y_center + h/2)
            
            # Update color based on state
            color = WAVE_ACTIVE_COLOR if is_active else WAVE_IDLE_COLOR
            self.itemconfig(bar, fill=color)
        
        # Schedule next frame (60 FPS)
        self.after(16, self._animate)
