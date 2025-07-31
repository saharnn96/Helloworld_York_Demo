# RoboSAPIENS Adaptive Platform

A distributed robotics platform implementing the MAPLE-K (Monitor-Analysis-Plan-Execute-Knowledge) architecture for autonomous TurtleBot simulation and control.

## 🏗️ Architecture Overview

The platform consists of several key components:

- **Monitor**: Processes sensor data (LiDAR scans) and publishes events
- **Analysis**: Analyzes sensor data for anomaly detection
- **Plan**: Generates navigation plans based on analysis results
- **Execute**: Executes movement commands for the TurtleBot
- **Dashboard**: Web-based monitoring and control interface
- **Simulator**: TurtleBot simulation environment
- **Orchestrator**: Manages dynamic deployment of components
- **Redis**: Message broker and data storage backend

## 🚀 Quick Start

### Prerequisites

- Docker Desktop installed and running
- Docker Compose v3.8 or higher
- Git (to clone the repository)

### Running the Complete System

1. **Clone the repository**:

   ```bash
   git clone https://github.com/saharnn96/Helloworld_York_Demo.git
   cd Helloworld_York_Demo
   ```

2. **Navigate to the Realization directory**:

   ```bash
   cd Realization
   ```

3. **Start all services using Docker Compose**:

   ```bash
   docker-compose up --build
   ```

   This command will:

   - Build all Docker images for the services
   - Start Redis as the message broker
   - Launch all MAPLE-K components (Monitor, Analysis, Plan, Execute)
   - Start the TurtleBot Simulator
   - Launch the Dashboard for monitoring
   - Initialize the Orchestrator for dynamic component management

4. **Access the interfaces**:
   - **Dashboard**: http://localhost:8050 - Main monitoring and control interface
   - **TurtleBot Simulator**: http://localhost:8051 - Interactive robot simulation
   - **Redis**: localhost:6379 - Message broker (internal use)

## 🖥️ User Interfaces

### Dashboard (Port 8050)

The main control interface provides:

- **Components Timeline**: Real-time Gantt chart showing execution history of all components
- **Device Status**: Cards showing the status of each component (Running/Stopped/Offline)
- **System Logs**: Aggregated logs from all components with filtering options
- **Component Control**: Start/stop individual components dynamically

### TurtleBot Simulator (Port 8051)

Interactive simulation environment featuring:

- **2D Robot Visualization**: Real-time position and orientation display
- **LiDAR Visualization**: Live sensor data with configurable range
- **Manual Control**: Arrow keys for direct robot control
- **Autonomous Mode**: AI-driven navigation with obstacle avoidance
- **Environmental Controls**: Adjustable simulation parameters

## 🔧 Configuration

### Environment Variables

The system uses several environment variables that can be configured:

- `REDIS_HOST`: Redis server hostname (default: `redis`)
- `REDIS_PORT`: Redis server port (default: `6379`)
- `DASH_HOST`: Dashboard bind address (default: `0.0.0.0`)
- `DASH_PORT`: Dashboard port (default: `8050`)

### Configuration Files

- `config_redis.yaml`: Redis-based configuration for all MAPLE-K components
- `config_mqtt.yaml`: Alternative MQTT configuration (if needed)

## 🔍 Component Details

### Core MAPLE-K Components

1. **Monitor** (`./Nodes/Monitor/`)

   - Processes incoming sensor data (/Scan topic)
   - Stores LiDAR data in Redis knowledge base
   - Publishes new_data events to trigger analysis

2. **Analysis** (`./Nodes/Analysis/`)

   - Analyzes sensor data for anomaly detection
   - Publishes anomaly events when issues are detected
   - Implements probabilistic masking for LiDAR data

3. **Plan** (`./Nodes/Plan/`)

   - Generates navigation plans based on anomaly events
   - Publishes new_plan and direction data
   - Implements path planning algorithms

4. **Execute** (`./Nodes/Execute/`)
   - Executes movement commands for the robot
   - Processes plans from the Planning component
   - Publishes spin_config for robot movement

### Support Components

- **Dashboard**: Web-based Dash application for system monitoring
- **Simulator**: Interactive TurtleBot simulation using Dash
- **Orchestrator**: Dynamic component deployment and management
- **Redis**: Message broker and knowledge storage

## 🐳 Docker Services

The `docker-compose.yml` defines the following services:

```yaml
services:
  redis: # Message broker and data storage
  dashboard: # Web monitoring interface (port 8050)
  simulator: # TurtleBot simulation (port 8051)
  orchestrator: # Dynamic component management
  monitor: # Sensor data processing
  analysis: # Anomaly detection
  plan: # Path planning
  execute: # Motion execution
```

## 📊 Monitoring and Debugging

### Viewing Logs

1. **Real-time logs from all services**:

   ```bash
   docker-compose logs -f
   ```

2. **Logs from a specific service**:
   ```bash
   docker-compose logs -f monitor
   docker-compose logs -f dashboard
   ```

### Dashboard Features

- **Component Timeline**: Shows execution history and timing
- **Device Cards**: Real-time status of each component
- **System Logs**: Centralized logging with source filtering
- **Component Controls**: Start/stop components dynamically

### Redis Monitoring

You can connect to Redis directly to inspect data:

```bash
docker-compose exec redis redis-cli
```

Common Redis keys:

- `devices:list`: List of active devices
- `devices:{device}:nodes`: Components for each device
- `{component}:execution_time`: Execution timing data
- `log`: General system logs

## 🛠️ Development

### Building Individual Components

To rebuild a specific component:

```bash
docker-compose build monitor
docker-compose up monitor
```

### Adding New Components

1. Create a new directory under `./Nodes/YourComponent/`
2. Add the component implementation
3. Create a `Dockerfile` for the component
4. Add the service to `docker-compose.yml`
5. Update the orchestrator configuration

### Custom Configuration

Modify `config_redis.yaml` to customize:

- Logging levels and formats
- Redis connection parameters
- Component-specific settings
- Event and knowledge topic mappings

## 🔄 System Workflow

1. **Initialization**: Redis starts and becomes healthy
2. **Component Startup**: All MAPLE-K components connect to Redis
3. **Simulation**: TurtleBot simulator generates sensor data
4. **Data Flow**:
   - Monitor receives sensor data → Analysis processes it → Plan generates paths → Execute moves robot
5. **Monitoring**: Dashboard shows real-time status and logs
6. **Dynamic Management**: Orchestrator can start/stop components as needed

## 🚨 Troubleshooting

### Common Issues

1. **Port conflicts**: Ensure ports 8050, 8051, and 6379 are available
2. **Docker daemon**: Make sure Docker Desktop is running
3. **Memory issues**: Components may need more memory allocation
4. **Network issues**: Check that the `rap_network` bridge is created properly

### Checking Service Health

```bash
# Check all services status
docker-compose ps

# Check Redis health
docker-compose exec redis redis-cli ping

# Restart a problematic service
docker-compose restart monitor
```

### Reset Everything

To completely reset the system:

```bash
docker-compose down -v --remove-orphans
docker-compose up --build
```

## 📝 License

This project is part of the roboarch R&D project.
Copyright (C) 2024-present Bert Van Acker (B.MKR) <bert.vanacker@uantwerpen.be>

RAP R&D concepts can not be copied and/or distributed without the express permission of Bert Van Acker.

## 🤝 Contributing

This is a research project. For questions or collaboration opportunities, please contact the project maintainer.

---

**Happy Robotics! 🤖**
