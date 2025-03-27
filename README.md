# ResFlow 🖥️

## CSE316 Project: Resource Allocation Monitor

ResFlow is a real-time system resource monitoring application developed as part of the CSE316 course project, helping you track memory usage, identify top memory-consuming processes, and get alerts when system memory reaches critical levels.

### 👥 Project Team

#### CSE316 Project Team
1. **Sravan Krishna C M**
   - Registration Number: 12314058
   - Role: Lead Developer,Performance Optimization

2. **Abhishek Krishna M**
   - Registration Number: 12318459
   - Role: Backend Development, System Monitoring

3. **Kavya**
   - Registration Number: 12313998
   - Role:  UI/UX Designer, Alerting System

### 🎓 Course Details
- **Course Code:** CSE316
- **Course Name:** Operating System
- **Semester:** 4rth 
- **Academic Year:** 2nd

### 🌟 Features

- **Real-time Memory Monitoring**
  - Graphical representation of memory usage over time
  - Live tracking of system memory consumption
  - Detailed visualization of memory usage percentage

- **Process Tracking**
  - List top memory-consuming processes
  - Display process details including:
    - Process name
    - Process ID (PID)
    - Memory usage
    - CPU usage
  - Ability to kill resource-intensive processes directly from the app

- **Intelligent Alerts**
  - Customizable memory usage threshold (default: 80%)
  - Desktop notifications when memory usage becomes critical
  - Logging of high memory usage events

- **Adaptive UI**
  - Dark and Light mode
  - Responsive and clean interface
  - Real-time graph updates
  - Intuitive process management

### 🛠️ Requirements

- Python 3.8+
- PyQt5
- psutil
- pyqtgraph
- qt-material

### 📦 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/resflow.git
   cd resflow
   ```

2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 🚀 Running the Application

```bash
python main.py
```

### 🔧 Customization

- Modify `tracker/alert.py` to change the memory usage alert threshold
- Adjust logging configurations in `tracker/logger.py`

### 📊 Logging

ResFlow generates two types of logs:
- `logs/memory_log.txt`: Detailed memory usage logs
- `logs/alert_log.txt`: High memory usage alerts and top consuming processes

### 🌓 Theme Switching

Use the theme button in the top-right corner to switch between Dark and Light modes.

### 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### 📄 License

This project is licensed under the MIT License.

### 🐞 Known Issues

- Some system processes might require elevated permissions to track or kill
- Performance may vary based on system specifications

### 🔮 Future Roadmap

- [ ] CPU Usage Tracking
- [ ] Disk Space Monitoring
- [ ] Network Resource Monitoring
- [ ] Customizable Alert Configurations
