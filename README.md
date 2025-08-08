# 🛡️ AI-Powered Web Activity Firewall: Real-Time Bot Detection for a Secure Digital Frontier

## ✨ Project Overview
**Bot Detector** is a real-time, scalable AI-powered firewall designed to detect and mitigate automated threats across web and network environments. It combines behavioral analytics with deep network-flow profiling to identify bot-driven attacks and anomalous user behavior—without compromising user experience.

## 🚨 Problem Statement
Modern web platforms face a surge in automated attacks such as credential stuffing, scraping, and reconnaissance. Traditional rule-based firewalls often:
- Frustrate legitimate users
- Fail to detect novel or low-volume threats
- Require constant manual updates
- Raise privacy and accessibility concerns

## 🎯 Solution Highlights
Bot Detector addresses these limitations through:
- Real-time detection using streaming data pipelines
- Ensemble modeling combining login behavior and network flow
- Privacy-conscious design with full control over data
- Cloud-native deployment for scalability and resilience

## 🛠️ Core Features
- **Streaming Architecture**: Kafka-based ingestion and real-time feature extraction
- **Machine Learning Models**: LightGBM classifiers trained on synthetic and real-world datasets
- **Ensemble Intelligence**: Combines login behavior and network-flow metrics for robust scoring
- **FastAPI Service**: Issues JWTs for verified users, blocks bots, and logs activity
- **Admin Dashboard**: Visualizes attack patterns and supports real-time monitoring
- **Feedback Loop**: Continuous model retraining using Optuna for hyperparameter tuning

## 📊 Datasets Used
1. **Login Behavior Dataset** (Synthetic, 400K rows)
   - Balanced: 200K benign vs. 200K attack samples
   - Features: `time_to_submit`, `failed_login_count_last_10min`, `user_agent`, `login_hour`, `client_ip`, `password_length`, `is_username_email`
2. **Network Flow Dataset** (CIC-IDS2018, ~1.1M flows)
   - 78 flow metrics per TCP session
   - Attack classes: DoS, brute-force, web attacks, etc.
3. **Ensemble Test Set** (10K rows)
   - Combines login and flow features to evaluate joint model performance

## 🏗️ Architecture Overview

- Microservices: Containerized components for ingestion, scoring, API, and UI
- Deployment: Docker + docker-compose (or Kubernetes), AWS-ready (EC2, ECS, RDS, MSK)
- Fallback Logic: Simple rule-based detection if ML model is unavailable

## 📈 Experimental Results
| Model       | AUC  | FPR @ 95% TPR |
|-------------|------|---------------|
| Login-only  | 0.93 | 8%            |
| Ensemble    | 0.98 | 2%            |

- **+5 points** in AUC
- **75% reduction** in false alarms

## 🔧 Technologies Used
- Python
- FastAPI
- LightGBM
- Kafka
- Docker
- PostgreSQL
- React
- Optuna
- CIC-IDS2018 dataset

## 👤 My Role
- Led feature engineering and exploratory data analysis
- Developed and optimized LightGBM models
- Integrated ML components into the backend API
- Validated and tuned ensemble models
- Collaborated on deployment and system architecture

## 🚀 Future Improvements
- Early integration testing and CI/CD setup
- Enhanced user feedback and usability testing
- Visual project tracking (e.g., Trello, Gantt charts)
- Risk assessment planning at project kickoff

## 🛠️ Setup Instructions
1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd bot-detector
   
2. Install Dependencies:

```bash
pip install -r requirements.txt
```

3. Set Up Environment:

Configure Kafka, PostgreSQL, and environment variables in .env
Example .env:
```bash
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
POSTGRES_URL=postgresql://user:password@localhost:5432/bot_detector
```


4. Run Services:
```bash
docker-compose up -d
```
Access the Dashboard:

```bash
Navigate to http://localhost:3000 for the React-based admin dashboard
```
