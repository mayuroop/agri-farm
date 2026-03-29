# 🌾 Agri-Marketplace - Smart Agriculture Platform

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0.3-green.svg)](https://flask.palletsprojects.com/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4.3.3-orange.svg)](https://www.mongodb.com/)
[![Vercel](https://img.shields.io/badge/Deploy%20on-Vercel-black.svg)](https://vercel.com)
[![Six Sigma](https://img.shields.io/badge/Six%20Sigma-DMAIC-yellow.svg)](https://en.wikipedia.org/wiki/Six_Sigma)

> **A comprehensive agriculture marketplace platform built with Flask, featuring Six Sigma methodology implementation for continuous improvement and quality assurance.**

## 🚀 Live Demo

**Deploy your own instance:** [![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fyourusername%2Fagri-main)

## 📋 Table of Contents

- [Overview](#-overview)
- [✨ Key Features](#-key-features)
- [🔧 Six Sigma Implementation](#-six-sigma-implementation)
- [🏗️ Architecture](#️-architecture)
- [📱 Screenshots](#-screenshots)
- [🚀 Getting Started](#-getting-started)
- [📊 API Endpoints](#-api-endpoints)
- [🔒 Security Features](#-security-features)
- [📈 Analytics & Monitoring](#-analytics--monitoring)
- [🛠️ Technologies Used](#️-technologies-used)
- [📁 Project Structure](#-project-structure)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)

## 🌟 Overview

Agri-Marketplace is a modern, full-stack web application designed to revolutionize agricultural commerce. Built with Flask and MongoDB, it provides a comprehensive platform for farmers, buyers, and administrators to manage agricultural products, orders, and market dynamics.

The platform incorporates **Six Sigma methodology** to ensure high quality, reliability, and continuous improvement across all system processes.

## ✨ Key Features

### 🛒 **Marketplace Management**
- **Product Catalog**: Browse and search agricultural items
- **Smart Pricing**: Real-time crop price integration via government APIs
- **Inventory Management**: Admin-controlled product addition and removal
- **Order Processing**: Streamlined purchase workflow

### 👥 **User Management**
- **Role-Based Access**: Separate interfaces for users and administrators
- **Secure Authentication**: Session-based login with security measures
- **User Profiles**: Personalized experience with order history
- **Registration System**: Email validation and password strength requirements

### 🌤️ **External Integrations**
- **Weather API**: Real-time weather data for agricultural planning
- **Crop Prices**: Government data integration for market insights
- **Responsive Design**: Mobile-first approach for field accessibility

### 📊 **Analytics & Insights**
- **Admin Dashboard**: Comprehensive metrics and performance indicators
- **Order Analytics**: Success rates, user behavior, and market trends
- **System Monitoring**: Real-time logging and error tracking
- **Performance Metrics**: Six Sigma quality indicators

## 🔧 Six Sigma Implementation

This project implements the **DMAIC framework** (Define, Measure, Analyze, Improve, Control) to ensure quality and continuous improvement:

### 📋 **Define Phase**
- **Problem Identification**: Registration failures, login issues, order processing inefficiencies
- **Scope Definition**: User experience, system reliability, data quality
- **Stakeholder Analysis**: Farmers, buyers, administrators, end-users

### 📊 **Measure Phase**
- **Key Metrics**: Success rates, error frequencies, response times
- **Data Collection**: Comprehensive logging system implementation
- **Baseline Establishment**: Current system performance benchmarks

### 🔍 **Analyze Phase**
- **Root Cause Analysis**: Input validation gaps, security vulnerabilities
- **Process Mapping**: User journey analysis and pain point identification
- **Data Analysis**: Pattern recognition in failures and user behavior

### ⚡ **Improve Phase**
- **Input Validation**: Email format and password strength requirements
- **Security Enhancements**: Login attempt limiting and lockout mechanisms
- **User Experience**: Streamlined workflows and feedback systems
- **Monitoring Tools**: Real-time analytics and logging capabilities

### 🎯 **Control Phase**
- **Continuous Monitoring**: Admin dashboard for real-time oversight
- **Performance Tracking**: Success rate monitoring and trend analysis
- **Feedback Loops**: User feedback collection and system improvement
- **Quality Assurance**: Automated validation and error prevention

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   (HTML/CSS/JS) │◄──►│   (Flask)       │◄──►│   (MongoDB)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Templates     │    │   API Routes    │    │   Collections   │
│   - User Pages  │    │   - Auth        │    │   - Users       │
│   - Admin Pages │    │   - Marketplace │    │   - Items       │
│   - Forms       │    │   - Orders      │    │   - Orders      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📱 Screenshots

<img width="1551" height="951" alt="image" src="https://github.com/user-attachments/assets/6901e77f-29e1-4ec8-a7d7-55321d23e72a" />
<img width="1568" height="949" alt="image" src="https://github.com/user-attachments/assets/4b48a06b-566d-4fcb-a4c0-7a294718451d" />
<img width="1550" height="938" alt="image" src="https://github.com/user-attachments/assets/86069fea-826d-4c85-be06-a430c9b3f830" />
<img width="1566" height="951" alt="image" src="https://github.com/user-attachments/assets/dda9ab74-fe06-41e7-afa4-3f36b8d0ab51" />
<img width="1568" height="950" alt="image" src="https://github.com/user-attachments/assets/26fb4256-c88f-483b-bdd9-b6d05ce076c1" />






## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- MongoDB instance
- Weather API key (from [weatherapi.com](https://weatherapi.com/))
- Government API access (for crop prices)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/agri-main.git
   cd agri-main
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Create .env file
   MONGODB_URI=your_mongodb_connection_string
   WEATHER_API_KEY=your_weather_api_key
   SECRET_KEY=your_secret_key
   ```

4. **Run the application**
   ```bash
   python api/index.py
   ```

5. **Access the application**
   - **Local**: http://localhost:5000
   - **Production**: Deploy to Vercel for serverless hosting

## 📊 API Endpoints

### 🔐 Authentication
- `POST /register` - User registration with validation
- `POST /login` - User authentication with security measures
- `GET /logout` - Session termination

### 🛒 Marketplace
- `GET /marketplace` - Browse available items
- `GET /buy/<item_id>` - Purchase item page
- `POST /buy/<item_id>` - Place order with logging

### 📋 Orders
- `GET /orders` - View user orders
- `GET /admin/orders` - Admin order management
- `POST /admin/mark_done/<order_id>` - Mark order as completed

### 🎯 Admin Functions
- `GET /admin/dashboard` - Analytics and system monitoring
- `POST /add-item` - Add new marketplace items
- `DELETE /delete_item/<item_id>` - Remove items

### 🌤️ External Data
- `GET /weather` - Weather information
- `GET /crop-prices` - Government crop price data

### 💬 Feedback
- `GET /feedback` - Feedback form
- `POST /feedback` - Submit user feedback

## 🔒 Security Features

- **Input Validation**: Comprehensive email and password validation
- **Session Management**: Secure Flask session handling
- **Login Protection**: Attempt limiting and account lockout
- **CSRF Protection**: Form security measures
- **Error Handling**: Secure error messages without information leakage

## 📈 Analytics & Monitoring

### **Admin Dashboard Features**
- **User Statistics**: Total users, registration success rates
- **Order Analytics**: Order volumes, success rates, trends
- **System Health**: Error rates, performance metrics
- **Recent Activity**: Latest user actions and admin operations
- **Feedback Overview**: User satisfaction and improvement suggestions

### **Logging System**
- **User Actions**: Registration, login, order placement
- **Admin Operations**: Item management, order processing
- **System Events**: Errors, warnings, performance metrics
- **Security Events**: Failed login attempts, validation failures

## 🛠️ Technologies Used

### **Backend**
- **Flask 3.0.3** - Modern Python web framework
- **MongoDB** - NoSQL database for scalability
- **PyMongo** - MongoDB Python driver

### **Frontend**
- **HTML5** - Semantic markup
- **CSS3** - Modern styling with CSS variables
- **JavaScript** - Interactive functionality
- **Responsive Design** - Mobile-first approach

### **External APIs**
- **Weather API** - Real-time weather data
- **Government Data** - Crop price information
- **Vercel** - Serverless deployment platform

### **Development Tools**
- **Git** - Version control
- **Vercel CLI** - Deployment automation
- **Six Sigma** - Quality improvement methodology

## 📁 Project Structure

```
agri-main/
├── api/
│   ├── index.py              # Main Flask application
│   ├── static/
│   │   ├── script.js         # Frontend JavaScript
│   │   └── style.css         # Styling
│   └── templates/
│       ├── index.html        # Home page
│       ├── login.html        # Authentication
│       ├── register.html     # User registration
│       ├── marketplace.html  # Product catalog
│       ├── orders.html       # Order management
│       ├── admin_orders.html # Admin order view
│       ├── admin_dashboard.html # Analytics dashboard
│       ├── feedback.html     # User feedback
│       ├── error.html        # Error handling
│       └── ...               # Other templates
├── requirements.txt           # Python dependencies
├── vercel.json              # Vercel configuration
└── README.md                # Project documentation
```

## 🤝 Contributing

We welcome contributions to improve the Agri-Marketplace platform! Here's how you can help:

### **Development Process**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### **Contribution Areas**
- **UI/UX Improvements**: Better user experience and accessibility
- **Feature Development**: New marketplace capabilities
- **Performance Optimization**: Faster loading and better efficiency
- **Security Enhancements**: Additional protection measures
- **Documentation**: Better guides and examples

### **Code Standards**
- Follow PEP 8 Python style guidelines
- Include comprehensive error handling
- Add logging for important operations
- Ensure mobile responsiveness
- Maintain Six Sigma quality standards

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Six Sigma Methodology** - For quality improvement framework
- **Flask Community** - For the excellent web framework
- **MongoDB** - For the robust database solution
- **Vercel** - For seamless deployment platform
- **Open Source Community** - For inspiration and tools

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/agri-main/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/agri-main/discussions)
- **Email**: mayurxsu@gmail.com

---

<div align="center">

**Made with ❤️ for the Agriculture Community**

[![GitHub stars](https://img.shields.io/github/stars/yourusername/agri-main?style=social)](https://github.com/yourusername/agri-main)
[![GitHub forks](https://img.shields.io/github/forks/yourusername/agri-main?style=social)](https://github.com/yourusername/agri-main)
[![GitHub issues](https://img.shields.io/github/issues/yourusername/agri-main)](https://github.com/yourusername/agri-main/issues)

**Star this repository if it helped you! ⭐**

</div>
