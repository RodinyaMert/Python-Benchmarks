import sys
import time
import json
import os
from datetime import datetime
import numpy as np
import psutil
import GPUtil
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QLabel, QProgressBar, QTextEdit, QTabWidget, QComboBox,
    QCheckBox, QTimeEdit, QMessageBox, QHBoxLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QTime
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Dil dosyaları
TRANSLATIONS = {
    'tr': {
        'cpu_tab': 'CPU',
        'ram_tab': 'RAM',
        'disk_tab': 'Disk',
        'gpu_tab': 'GPU',
        'settings_tab': 'Ayarlar',
        'start_test': 'Testi Başlat',
        'stop_test': 'Testi Durdur',
        'cpu_temp': 'CPU Sıcaklığı',
        'gpu_temp': 'GPU Sıcaklığı',
        'score': 'Puan',
        'theme': 'Tema',
        'language': 'Dil',
        'auto_test': 'Otomatik Test',
        'dark_theme': 'Koyu Tema',
        'light_theme': 'Açık Tema',
        'neon_theme': 'Neon Tema',
        'turkish': 'Türkçe',
        'english': 'İngilizce',
        'enable_auto_test': 'Otomatik Testi Etkinleştir',
        'test_time': 'Test Saati',
        'system_info': 'Sistem Bilgileri',
        'cpu_usage': 'CPU Kullanımı (%)',
        'ram_usage': 'RAM Kullanımı (%)',
        'disk_usage': 'Disk Kullanımı (%)',
        'gpu_usage': 'GPU Kullanımı (%)',
        'performance': 'Performans',
        'temperature': 'Sıcaklık (°C)',
        'cpu_model': 'CPU Model',
        'cpu_cores': 'CPU Çekirdek',
        'cpu_freq': 'CPU Frekansı',
        'ram_total': 'Toplam RAM',
        'ram_available': 'Kullanılabilir RAM',
        'disk_total': 'Toplam Disk',
        'disk_free': 'Boş Disk',
        'gpu_name': 'GPU Adı',
        'test_running': 'Test Çalışıyor...',
        'test_completed': 'Test Tamamlandı!',
        'benchmark_title': 'Sistem Performans Benchmark',
        'current_temp': 'Mevcut Sıcaklık',
        'max_temp': 'Maksimum Sıcaklık',
        'avg_usage': 'Ortalama Kullanım'
    },
    'en': {
        'cpu_tab': 'CPU',
        'ram_tab': 'RAM',
        'disk_tab': 'Disk',
        'gpu_tab': 'GPU',
        'settings_tab': 'Settings',
        'start_test': 'Start Test',
        'stop_test': 'Stop Test',
        'cpu_temp': 'CPU Temperature',
        'gpu_temp': 'GPU Temperature',
        'score': 'Score',
        'theme': 'Theme',
        'language': 'Language',
        'auto_test': 'Auto Test',
        'dark_theme': 'Dark Theme',
        'light_theme': 'Light Theme',
        'neon_theme': 'Neon Theme',
        'turkish': 'Turkish',
        'english': 'English',
        'enable_auto_test': 'Enable Auto Test',
        'test_time': 'Test Time',
        'system_info': 'System Information',
        'cpu_usage': 'CPU Usage (%)',
        'ram_usage': 'RAM Usage (%)',
        'disk_usage': 'Disk Usage (%)',
        'gpu_usage': 'GPU Usage (%)',
        'performance': 'Performance',
        'temperature': 'Temperature (°C)',
        'cpu_model': 'CPU Model',
        'cpu_cores': 'CPU Cores',
        'cpu_freq': 'CPU Frequency',
        'ram_total': 'Total RAM',
        'ram_available': 'Available RAM',
        'disk_total': 'Total Disk',
        'disk_free': 'Free Disk',
        'gpu_name': 'GPU Name',
        'test_running': 'Test Running...',
        'test_completed': 'Test Completed!',
        'benchmark_title': 'System Performance Benchmark',
        'current_temp': 'Current Temperature',
        'max_temp': 'Maximum Temperature',
        'avg_usage': 'Average Usage'
    }
}

# CSS Stilleri
DARK_THEME = """
    QMainWindow {
        background-color: #1e1e1e;
        color: #ffffff;
    }
    QTabWidget::pane {
        border: 2px solid #3a3a3a;
        background-color: #2b2b2b;
        border-radius: 8px;
    }
    QTabBar::tab {
        background-color: #3a3a3a;
        color: #ffffff;
        padding: 10px 20px;
        margin-right: 2px;
        border-top-left-radius: 6px;
        border-top-right-radius: 6px;
        min-width: 80px;
        font-weight: normal;
    }
    QTabBar::tab:selected {
        background-color: #555555;
        border-bottom: 2px solid #ffffff;
    }
    QTabBar::tab:hover {
        background-color: #4a4a4a;
    }
    QPushButton {
        background-color: #0078d4;
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 6px;
        font-weight: normal;
        font-size: 12px;
    }
    QPushButton:hover {
        background-color: #106ebe;
    }
    QPushButton:pressed {
        background-color: #005a9e;
    }
    QLabel {
        color: #ffffff;
        font-size: 12px;
    }
    QProgressBar {
        border: 2px solid #3a3a3a;
        border-radius: 6px;
        text-align: center;
        background-color: #2b2b2b;
    }
    QProgressBar::chunk {
        background-color: #0078d4;
        border-radius: 4px;
    }
    QTextEdit {
        background-color: #2b2b2b;
        color: #ffffff;
        border: 1px solid #3a3a3a;
        border-radius: 6px;
        padding: 8px;
    }
    QComboBox {
        background-color: #3a3a3a;
        color: #ffffff;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 6px;
        min-width: 120px;
    }
    QComboBox::drop-down {
        border: none;
    }
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid #ffffff;
    }
    QCheckBox {
        color: #ffffff;
        spacing: 8px;
    }
    QCheckBox::indicator {
        width: 16px;
        height: 16px;
        border: 1px solid #555555;
        border-radius: 3px;
        background-color: #2b2b2b;
    }
    QCheckBox::indicator:checked {
        background-color: #0078d4;
        border: 1px solid #0078d4;
    }
    QTimeEdit {
        background-color: #3a3a3a;
        color: #ffffff;
        border: 1px solid #555555;
        border-radius: 4px;
        padding: 6px;
    }
"""

LIGHT_THEME = """
    QMainWindow {
        background-color: #f5f5f5;
        color: #333333;
    }
    QTabWidget::pane {
        border: 2px solid #cccccc;
        background-color: #ffffff;
        border-radius: 10px;
    }
    QTabBar::tab {
        background-color: #e0e0e0;
        color: #333333;
        padding: 12px 24px;
        margin-right: 2px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
        min-width: 80px;
        font-weight: bold;
    }
    QTabBar::tab:selected {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                   stop:0 #4CAF50, stop:1 #45a049);
        color: white;
    }
    QTabBar::tab:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                   stop:0 #f0f0f0, stop:1 #e0e0e0);
    }
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                   stop:0 #4CAF50, stop:1 #45a049);
        color: white;
        border: none;
        padding: 12px 24px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 12px;
    }
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                   stop:0 #5CBF60, stop:1 #4CAF50);
    }
    QPushButton:pressed {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                   stop:0 #45a049, stop:1 #3d8b40);
    }
    QLabel {
        color: #333333;
        font-size: 12px;
    }
    QProgressBar {
        border: 2px solid #cccccc;
        border-radius: 8px;
        text-align: center;
        background-color: #f0f0f0;
    }
    QProgressBar::chunk {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                   stop:0 #4CAF50, stop:0.5 #FFC107, stop:1 #FF5722);
        border-radius: 6px;
    }
    QTextEdit {
        background-color: #ffffff;
        color: #333333;
        border: 2px solid #cccccc;
        border-radius: 8px;
        padding: 8px;
    }
    QComboBox {
        background-color: #ffffff;
        color: #333333;
        border: 2px solid #cccccc;
        border-radius: 6px;
        padding: 6px;
        min-width: 120px;
    }
    QComboBox::drop-down {
        border: none;
    }
    QComboBox::down-arrow {
        image: none;
        border-left: 5px solid transparent;
        border-right: 5px solid transparent;
        border-top: 5px solid #333333;
    }
    QCheckBox {
        color: #333333;
        spacing: 8px;
    }
    QCheckBox::indicator {
        width: 18px;
        height: 18px;
        border: 2px solid #cccccc;
        border-radius: 4px;
        background-color: #ffffff;
    }
    QCheckBox::indicator:checked {
        background-color: #4CAF50;
        border: 2px solid #4CAF50;
    }
    QTimeEdit {
        background-color: #ffffff;
        color: #333333;
        border: 2px solid #cccccc;
        border-radius: 6px;
        padding: 6px;
    }
"""

NEON_THEME = """
    QMainWindow {
        background-color: #0a0a0a;
        color: #00ffff;
    }
    QTabWidget::pane {
        border: 2px solid #00ffff;
        background-color: #1a1a1a;
        border-radius: 12px;
    }
    QTabBar::tab {
        background-color: #1a1a1a;
        color: #00ffff;
        padding: 12px 24px;
        margin-right: 2px;
        border-top-left-radius: 10px;
        border-top-right-radius: 10px;
        min-width: 80px;
        font-weight: bold;
        border: 1px solid #00ffff;
    }
    QTabBar::tab:selected {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                   stop:0 #00ffff, stop:1 #0099cc);
        color: #000000;
    }
    QTabBar::tab:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                   stop:0 #003333, stop:1 #001a1a);
    }
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                   stop:0 #00ffff, stop:1 #0099cc);
        color: #000000;
        border: 2px solid #00ffff;
        padding: 12px 24px;
        border-radius: 10px;
        font-weight: bold;
        font-size: 12px;
    }
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                   stop:0 #33ffff, stop:1 #00ccff);
    }
    QPushButton:pressed {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                   stop:0 #0099cc, stop:1 #006699);
    }
    QLabel {
        color: #00ffff;
        font-size: 12px;
    }
    QProgressBar {
        border: 2px solid #00ffff;
        border-radius: 10px;
        text-align: center;
        background-color: #1a1a1a;
        color: #00ffff;
    }
    QProgressBar::chunk {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                                   stop:0 #ff00ff, stop:0.5 #00ffff, stop:1 #ffff00);
        border-radius: 8px;
    }
    QTextEdit {
        background-color: #1a1a1a;
        color: #00ffff;
        border: 2px solid #00ffff;
        border-radius: 10px;
        padding: 10px;
    }
    QComboBox {
        background-color: #1a1a1a;
        color: #00ffff;
        border: 2px solid #00ffff;
        border-radius: 8px;
        padding: 8px;
        min-width: 120px;
    }
    QComboBox::drop-down {
        border: none;
    }
    QComboBox::down-arrow {
        image: none;
        border-left: 6px solid transparent;
        border-right: 6px solid transparent;
        border-top: 6px solid #00ffff;
    }
    QCheckBox {
        color: #00ffff;
        spacing: 10px;
    }
    QCheckBox::indicator {
        width: 20px;
        height: 20px;
        border: 2px solid #00ffff;
        border-radius: 5px;
        background-color: #1a1a1a;
    }
    QCheckBox::indicator:checked {
        background-color: #00ffff;
        border: 2px solid #00ffff;
    }
    QTimeEdit {
        background-color: #1a1a1a;
        color: #00ffff;
        border: 2px solid #00ffff;
        border-radius: 8px;
        padding: 8px;
    }
"""

class PerformanceChart(FigureCanvas):
    def __init__(self, parent=None, title="Performance", ylabel="Usage (%)", theme_type="dark"):
        self.figure = Figure(figsize=(8, 4), dpi=100)
        super().__init__(self.figure)
        self.ax = self.figure.add_subplot(111)
        self.title = title
        self.ylabel = ylabel
        self.theme_type = theme_type
        self.data = []
        self.timestamps = []
        self.max_points = 30
        
        self.setup_chart()
        
    def setup_chart(self):
        self.ax.clear()
        
        # Tema renklerini ayarla
        if self.theme_type == "dark":
            bg_color = '#2b2b2b'
            text_color = 'white'
            grid_color = 'gray'
            line_color = '#0078d4'
        elif self.theme_type == "neon":
            bg_color = '#1a1a1a'
            text_color = '#00ffff'
            grid_color = '#00ffff'
            line_color = '#ff00ff'
        else:  # light
            bg_color = '#ffffff'
            text_color = 'black'
            grid_color = '#cccccc'
            line_color = '#4CAF50'
        
        self.ax.set_facecolor(bg_color)
        self.figure.patch.set_facecolor(bg_color)
        
        self.ax.set_title(self.title, color=text_color, fontsize=12, pad=15)
        self.ax.set_ylabel(self.ylabel, color=text_color, fontsize=10)
        self.ax.set_xlabel('Time', color=text_color, fontsize=10)
        self.ax.grid(True, alpha=0.3, color=grid_color)
        
        # Eksen renklerini ayarla
        self.ax.tick_params(colors=text_color, labelsize=8)
        for spine in self.ax.spines.values():
            spine.set_color(text_color)
        
        self.draw()
        
    def update_data(self, value):
        current_time = datetime.now().strftime("%H:%M:%S")
        self.data.append(value)
        self.timestamps.append(current_time)
        
        if len(self.data) > self.max_points:
            self.data.pop(0)
            self.timestamps.pop(0)
        
        self.ax.clear()
        
        # Tema renklerini ayarla
        if self.theme_type == "dark":
            bg_color = '#2b2b2b'
            text_color = 'white'
            grid_color = 'gray'
            line_color = '#0078d4'
        elif self.theme_type == "neon":
            bg_color = '#1a1a1a'
            text_color = '#00ffff'
            grid_color = '#00ffff'
            line_color = '#ff00ff'
        else:  # light
            bg_color = '#ffffff'
            text_color = 'black'
            grid_color = '#cccccc'
            line_color = '#4CAF50'
        
        self.ax.set_facecolor(bg_color)
        self.figure.patch.set_facecolor(bg_color)
        
        if len(self.data) > 1:
            self.ax.plot(range(len(self.data)), self.data, 
                        color=line_color, linewidth=2, marker='o', markersize=3)
            self.ax.fill_between(range(len(self.data)), self.data, 
                               alpha=0.3, color=line_color)
        
        self.ax.set_title(self.title, color=text_color, fontsize=12, pad=15)
        self.ax.set_ylabel(self.ylabel, color=text_color, fontsize=10)
        self.ax.set_xlabel('Time', color=text_color, fontsize=10)
        self.ax.grid(True, alpha=0.3, color=grid_color)
        self.ax.set_ylim(0, 100)
        
        # X ekseninde zaman etiketleri
        if len(self.timestamps) > 1:
            step = max(1, len(self.timestamps) // 5)
            ticks = range(0, len(self.timestamps), step)
            labels = [self.timestamps[i] for i in ticks]
            self.ax.set_xticks(ticks)
            self.ax.set_xticklabels(labels, rotation=45)
        
        # Eksen renklerini ayarla
        self.ax.tick_params(colors=text_color, labelsize=8)
        for spine in self.ax.spines.values():
            spine.set_color(text_color)
        
        self.draw()

class BenchmarkThread(QThread):
    progress_updated = pyqtSignal(str, float, dict)  # component, score, info
    
    def __init__(self, component):
        super().__init__()
        self.component = component
        self.running = False
        
    def run(self):
        self.running = True
        
        if self.component == "CPU":
            self.cpu_benchmark()
        elif self.component == "RAM":
            self.ram_benchmark()
        elif self.component == "Disk":
            self.disk_benchmark()
        elif self.component == "GPU":
            self.gpu_benchmark()
            
    def cpu_benchmark(self):
        for i in range(101):
            if not self.running:
                break
                
            # CPU bilgileri
            cpu_percent = psutil.cpu_percent(interval=0.1)
            cpu_freq = psutil.cpu_freq()
            cpu_count = psutil.cpu_count()
            
            # Sıcaklık bilgisi (Windows'ta mevcut değilse simüle et)
            try:
                temps = psutil.sensors_temperatures()
                cpu_temp = temps.get('coretemp', [{'current': 45}])[0]['current']
            except:
                cpu_temp = 45 + (cpu_percent * 0.5)  # Simülasyon
            
            info = {
                'model': f"CPU Model (Generic)",
                'cores': cpu_count,
                'frequency': f"{cpu_freq.current:.2f} MHz" if cpu_freq else "N/A",
                'usage': cpu_percent,
                'temperature': cpu_temp
            }
            
            score = min((cpu_percent / 10) + (cpu_temp / 20), 10.0)
            self.progress_updated.emit("CPU", score, info)
            
            self.msleep(100)
    
    def ram_benchmark(self):
        for i in range(101):
            if not self.running:
                break
                
            # RAM bilgileri
            memory = psutil.virtual_memory()
            
            info = {
                'total': f"{memory.total / (1024**3):.2f} GB",
                'available': f"{memory.available / (1024**3):.2f} GB",
                'used': f"{memory.used / (1024**3):.2f} GB",
                'usage': memory.percent
            }
            
            score = min((memory.percent / 10), 10.0)
            self.progress_updated.emit("RAM", score, info)
            
            self.msleep(100)
    
    def disk_benchmark(self):
        for i in range(101):
            if not self.running:
                break
                
            # Disk bilgileri
            disk = psutil.disk_usage('/')
            
            info = {
                'total': f"{disk.total / (1024**3):.2f} GB",
                'free': f"{disk.free / (1024**3):.2f} GB",
                'used': f"{disk.used / (1024**3):.2f} GB",
                'usage': (disk.used / disk.total) * 100
            }
            
            score = min(((disk.used / disk.total) * 100) / 10, 10.0)
            self.progress_updated.emit("Disk", score, info)
            
            self.msleep(100)
    
    def gpu_benchmark(self):
        for i in range(101):
            if not self.running:
                break
                
            try:
                gpus = GPUtil.getGPUs()
                if gpus:
                    gpu = gpus[0]
                    info = {
                        'name': gpu.name,
                        'memory_total': f"{gpu.memoryTotal} MB",
                        'memory_used': f"{gpu.memoryUsed} MB",
                        'usage': gpu.load * 100,
                        'temperature': gpu.temperature
                    }
                    score = min((gpu.load * 10) + (gpu.temperature / 20), 10.0)
                else:
                    # GPU bulunamadıysa simülasyon
                    usage = np.random.uniform(20, 80)
                    temp = np.random.uniform(60, 85)
                    info = {
                        'name': 'Generic GPU',
                        'memory_total': '8192 MB',
                        'memory_used': f"{int(usage * 40)} MB",
                        'usage': usage,
                        'temperature': temp
                    }
                    score = min((usage / 10) + (temp / 20), 10.0)
            except:
                # Hata durumunda simülasyon
                usage = np.random.uniform(20, 80)
                temp = np.random.uniform(60, 85)
                info = {
                    'name': 'Generic GPU',
                    'memory_total': '8192 MB',
                    'memory_used': f"{int(usage * 40)} MB",
                    'usage': usage,
                    'temperature': temp
                }
                score = min((usage / 10) + (temp / 20), 10.0)
            
            self.progress_updated.emit("GPU", score, info)
            self.msleep(100)
    
    def stop(self):
        self.running = False

class ComponentTab(QWidget):
    def __init__(self, component_name, translations, current_lang, theme_type):
        super().__init__()
        self.component_name = component_name
        self.translations = translations
        self.current_lang = current_lang
        self.theme_type = theme_type
        self.benchmark_thread = None
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Kontrol butonları
        control_layout = QHBoxLayout()
        
        self.start_btn = QPushButton(self.translations[self.current_lang]['start_test'])
        self.start_btn.clicked.connect(self.start_test)
        
        self.stop_btn = QPushButton(self.translations[self.current_lang]['stop_test'])
        self.stop_btn.clicked.connect(self.stop_test)
        self.stop_btn.setEnabled(False)
        
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        control_layout.addStretch()
        
        layout.addLayout(control_layout)
        
        # Performans grafiği
        chart_title = f"{self.component_name} {self.translations[self.current_lang]['performance']}"
        self.chart = PerformanceChart(title=chart_title, theme_type=self.theme_type)
        layout.addWidget(self.chart)
        
        # Puan göstergesi
        score_layout = QHBoxLayout()
        score_layout.addWidget(QLabel(f"{self.translations[self.current_lang]['score']}:"))
        
        self.score_progress = QProgressBar()
        self.score_progress.setRange(0, 100)
        self.score_progress.setValue(0)
        self.score_progress.setFormat("0.0/10.0")
        
        score_layout.addWidget(self.score_progress)
        layout.addLayout(score_layout)
        
        # Sistem bilgileri
        info_label = QLabel(self.translations[self.current_lang]['system_info'])
        info_label.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(info_label)
        
        self.info_text = QTextEdit()
        self.info_text.setMaximumHeight(150)
        self.info_text.setReadOnly(True)
        layout.addWidget(self.info_text)
        
        self.setLayout(layout)
        
    def start_test(self):
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        
        self.benchmark_thread = BenchmarkThread(self.component_name)
        self.benchmark_thread.progress_updated.connect(self.update_progress)
        self.benchmark_thread.start()
        
    def stop_test(self):
        if self.benchmark_thread:
            self.benchmark_thread.stop()
            self.benchmark_thread = None
            
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
    def update_progress(self, component, score, info):
        if component == self.component_name:
            # Puanı güncelle
            self.score_progress.setValue(int(score * 10))
            self.score_progress.setFormat(f"{score:.1f}/10.0")
            
            # Grafiği güncelle
            usage_value = info.get('usage', 0)
            self.chart.update_data(usage_value)
            
            # Sistem bilgilerini güncelle
            info_text = f"{self.component_name} Bilgileri:\n"
            for key, value in info.items():
                if key != 'usage':
                    info_text += f"{key.title()}: {value}\n"
            
            self.info_text.setPlainText(info_text)

class SettingsTab(QWidget):
    theme_changed = pyqtSignal(str)  # 'dark', 'light', 'neon'
    language_changed = pyqtSignal(str)  # 'tr' or 'en'
    
    def __init__(self, translations, current_lang, theme_type):
        super().__init__()
        self.translations = translations
        self.current_lang = current_lang
        self.theme_type = theme_type
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # Tema ayarları
        theme_group = QVBoxLayout()
        theme_label = QLabel(self.translations[self.current_lang]['theme'])
        theme_label.setFont(QFont("Arial", 12, QFont.Bold))
        theme_group.addWidget(theme_label)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems([
            self.translations[self.current_lang]['dark_theme'],
            self.translations[self.current_lang]['light_theme'],
            self.translations[self.current_lang]['neon_theme']
        ])
        
        # Mevcut temayı seç
        if self.theme_type == "dark":
            self.theme_combo.setCurrentIndex(0)
        elif self.theme_type == "light":
            self.theme_combo.setCurrentIndex(1)
        else:  # neon
            self.theme_combo.setCurrentIndex(2)
            
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        theme_group.addWidget(self.theme_combo)
        
        layout.addLayout(theme_group)
        
        # Dil ayarları
        lang_group = QVBoxLayout()
        lang_label = QLabel(self.translations[self.current_lang]['language'])
        lang_label.setFont(QFont("Arial", 12, QFont.Bold))
        lang_group.addWidget(lang_label)
        
        self.lang_combo = QComboBox()
        self.lang_combo.addItems([
            self.translations['tr']['turkish'],
            self.translations['en']['english']
        ])
        self.lang_combo.setCurrentIndex(0 if self.current_lang == 'tr' else 1)
        self.lang_combo.currentIndexChanged.connect(self.on_language_changed)
        lang_group.addWidget(self.lang_combo)
        
        layout.addLayout(lang_group)
        
        # Otomatik test ayarları
        auto_test_group = QVBoxLayout()
        auto_test_label = QLabel(self.translations[self.current_lang]['auto_test'])
        auto_test_label.setFont(QFont("Arial", 12, QFont.Bold))
        auto_test_group.addWidget(auto_test_label)
        
        self.auto_test_check = QCheckBox(self.translations[self.current_lang]['enable_auto_test'])
        auto_test_group.addWidget(self.auto_test_check)
        
        time_layout = QHBoxLayout()
        time_layout.addWidget(QLabel(self.translations[self.current_lang]['test_time']))
        
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime(12, 0))
        self.time_edit.setDisplayFormat("HH:mm")
        time_layout.addWidget(self.time_edit)
        
        auto_test_group.addLayout(time_layout)
        layout.addLayout(auto_test_group)
        
        layout.addStretch()
        self.setLayout(layout)
        
    def on_theme_changed(self, index):
        themes = ['dark', 'light', 'neon']
        self.theme_changed.emit(themes[index])
        
    def on_language_changed(self, index):
        lang = 'tr' if index == 0 else 'en'
        self.language_changed.emit(lang)

class BenchmarkApp(QWidget):
    def __init__(self):
        super().__init__()
        self.current_lang = 'tr'
        self.theme_type = 'dark'
        self.translations = TRANSLATIONS
        self.settings_file = 'benchmark_settings.json'
        
        # Ayarları yükle
        self.load_settings()
        
        # Otomatik test timer'ı
        self.auto_test_timer = QTimer()
        self.auto_test_timer.timeout.connect(self.run_auto_test)
        
        self.init_ui()
        self.apply_theme()
        
        # Otomatik test kontrolü
        self.check_auto_test_schedule()
        
    def init_ui(self):
        self.setWindowTitle(self.translations[self.current_lang]['benchmark_title'])
        self.setGeometry(100, 100, 1200, 800)
        
        layout = QVBoxLayout()
        
        # Ana tab widget
        self.tab_widget = QTabWidget()
        
        # Component tabs
        self.cpu_tab = ComponentTab("CPU", self.translations, self.current_lang, self.theme_type)
        self.ram_tab = ComponentTab("RAM", self.translations, self.current_lang, self.theme_type)
        self.disk_tab = ComponentTab("Disk", self.translations, self.current_lang, self.theme_type)
        self.gpu_tab = ComponentTab("GPU", self.translations, self.current_lang, self.theme_type)
        
        # Settings tab
        self.settings_tab = SettingsTab(self.translations, self.current_lang, self.theme_type)
        self.settings_tab.theme_changed.connect(self.change_theme)
        self.settings_tab.language_changed.connect(self.change_language)
        
        # Sekmeleri ekle
        self.tab_widget.addTab(self.cpu_tab, self.translations[self.current_lang]['cpu_tab'])
        self.tab_widget.addTab(self.ram_tab, self.translations[self.current_lang]['ram_tab'])
        self.tab_widget.addTab(self.disk_tab, self.translations[self.current_lang]['disk_tab'])
        self.tab_widget.addTab(self.gpu_tab, self.translations[self.current_lang]['gpu_tab'])
        self.tab_widget.addTab(self.settings_tab, self.translations[self.current_lang]['settings_tab'])
        
        layout.addWidget(self.tab_widget)
        self.setLayout(layout)
        
    def apply_theme(self):
        if self.theme_type == "dark":
            self.setStyleSheet(DARK_THEME)
        elif self.theme_type == "neon":
            self.setStyleSheet(NEON_THEME)
        else:  # light
            self.setStyleSheet(LIGHT_THEME)
            
        # Grafiklerin tema güncellemesi
        for tab in [self.cpu_tab, self.ram_tab, self.disk_tab, self.gpu_tab]:
            if hasattr(tab, 'chart'):
                tab.chart.theme_type = self.theme_type
                tab.chart.setup_chart()
                
    def change_theme(self, theme_type):
        self.theme_type = theme_type
        self.apply_theme()
        self.save_settings()
        
    def change_language(self, lang):
        self.current_lang = lang
        self.save_settings()
        
        # UI'ı yeniden oluştur
        self.close()
        self.__init__()
        self.show()
        
    def load_settings(self):
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    self.current_lang = settings.get('language', 'tr')
                    self.theme_type = settings.get('theme_type', 'dark')
                    self.auto_test_enabled = settings.get('auto_test_enabled', False)
                    self.auto_test_time = settings.get('auto_test_time', '12:00')
        except Exception as e:
            print(f"Ayarlar yüklenirken hata: {e}")
            
    def save_settings(self):
        try:
            settings = {
                'language': self.current_lang,
                'theme_type': self.theme_type,
                'auto_test_enabled': getattr(self, 'auto_test_enabled', False),
                'auto_test_time': getattr(self, 'auto_test_time', '12:00')
            }
            
            # Settings tab'dan güncel bilgileri al
            if hasattr(self, 'settings_tab'):
                settings['auto_test_enabled'] = self.settings_tab.auto_test_check.isChecked()
                settings['auto_test_time'] = self.settings_tab.time_edit.time().toString("HH:mm")
            
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Ayarlar kaydedilirken hata: {e}")
            
    def check_auto_test_schedule(self):
        # Her dakika kontrol et
        self.schedule_timer = QTimer()
        self.schedule_timer.timeout.connect(self.check_auto_test_time)
        self.schedule_timer.start(60000)  # 60 saniye
        
    def check_auto_test_time(self):
        if not hasattr(self, 'settings_tab'):
            return
            
        if self.settings_tab.auto_test_check.isChecked():
            current_time = QTime.currentTime()
            target_time = self.settings_tab.time_edit.time()
            
            # Zaman eşleşmesi kontrolü (dakika hassasiyetinde)
            if (current_time.hour() == target_time.hour() and 
                current_time.minute() == target_time.minute()):
                self.run_auto_test()
                
    def run_auto_test(self):
        # Tüm component'lar için testi başlat
        for tab in [self.cpu_tab, self.ram_tab, self.disk_tab, self.gpu_tab]:
            if not tab.benchmark_thread or not tab.benchmark_thread.isRunning():
                tab.start_test()
                
        # Bildirim göster
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Otomatik Test")
        msg.setText(self.translations[self.current_lang]['test_running'])
        msg.exec_()
        
    def closeEvent(self, event):
        # Ayarları kaydet
        self.save_settings()
        
        # Çalışan thread'leri durdur
        for tab in [self.cpu_tab, self.ram_tab, self.disk_tab, self.gpu_tab]:
            if tab.benchmark_thread and tab.benchmark_thread.isRunning():
                tab.stop_test()
                tab.benchmark_thread.wait()
                
        event.accept()

def main():
    app = QApplication(sys.argv)
    
    # Uygulama ayarları
    app.setApplicationName("System Benchmark")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("BenchmarkApp")
    
    # Font ayarları
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Ana pencereyi oluştur ve göster
    window = BenchmarkApp()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()