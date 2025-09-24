I'll help you design a comprehensive Student Management System using microservices architecture. Here's a complete implementation plan:

## System Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Gateway   │    │   Service       │    │   Database      │
│   (Gateway)     │    │   Discovery     │    │   Per Service   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────────────────────────────────────────────────────┐
│                      MICROSERVICES                              │
└─────────────────────────────────────────────────────────────────┘
```

## Core Microservices

### 1. API Gateway Service
```javascript
// gateway-service/index.js
const express = require('express');
const { createProxyMiddleware } = require('http-proxy-middleware');
const rateLimit = require('express-rate-limit');

const app = express();

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100 // limit each IP to 100 requests per windowMs
});

app.use(limiter);

// Service routing
app.use('/api/students', createProxyMiddleware({
  target: 'http://student-service:3001',
  changeOrigin: true,
  pathRewrite: { '^/api/students': '' }
}));

app.use('/api/courses', createProxyMiddleware({
  target: 'http://course-service:3002',
  changeOrigin: true,
  pathRewrite: { '^/api/courses': '' }
}));

app.use('/api/enrollments', createProxyMiddleware({
  target: 'http://enrollment-service:3003',
  changeOrigin: true,
  pathRewrite: { '^/api/enrollments': '' }
}));

app.use('/api/auth', createProxyMiddleware({
  target: 'http://auth-service:3004',
  changeOrigin: true,
  pathRewrite: { '^/api/auth': '' }
}));

app.listen(3000, () => {
  console.log('API Gateway running on port 3000');
});
```

### 2. Student Service
```javascript
// student-service/models/Student.js
const mongoose = require('mongoose');

const studentSchema = new mongoose.Schema({
  studentId: { type: String, unique: true, required: true },
  firstName: { type: String, required: true },
  lastName: { type: String, required: true },
  email: { type: String, unique: true, required: true },
  phone: String,
  address: {
    street: String,
    city: String,
    state: String,
    zipCode: String
  },
  dateOfBirth: Date,
  enrollmentDate: { type: Date, default: Date.now },
  status: { type: String, enum: ['active', 'inactive', 'graduated'], default: 'active' }
}, { timestamps: true });

module.exports = mongoose.model('Student', studentSchema);
```

```javascript
// student-service/controllers/studentController.js
const Student = require('../models/Student');

exports.createStudent = async (req, res) => {
  try {
    const student = new Student(req.body);
    await student.save();
    res.status(201).json(student);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};

exports.getStudents = async (req, res) => {
  try {
    const { page = 1, limit = 10, search } = req.query;
    const query = search ? {
      $or: [
        { firstName: { $regex: search, $options: 'i' } },
        { lastName: { $regex: search, $options: 'i' } },
        { email: { $regex: search, $options: 'i' } }
      ]
    } : {};

    const students = await Student.find(query)
      .limit(limit * 1)
      .skip((page - 1) * limit)
      .sort({ createdAt: -1 });

    const count = await Student.countDocuments(query);

    res.json({
      students,
      totalPages: Math.ceil(count / limit),
      currentPage: page,
      total: count
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

exports.getStudentById = async (req, res) => {
  try {
    const student = await Student.findById(req.params.id);
    if (!student) return res.status(404).json({ error: 'Student not found' });
    res.json(student);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

exports.updateStudent = async (req, res) => {
  try {
    const student = await Student.findByIdAndUpdate(
      req.params.id,
      req.body,
      { new: true, runValidators: true }
    );
    if (!student) return res.status(404).json({ error: 'Student not found' });
    res.json(student);
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
};

exports.deleteStudent = async (req, res) => {
  try {
    const student = await Student.findByIdAndDelete(req.params.id);
    if (!student) return res.status(404).json({ error: 'Student not found' });
    res.json({ message: 'Student deleted successfully' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};
```

### 3. Course Service
```javascript
// course-service/models/Course.js
const mongoose = require('mongoose');

const courseSchema = new mongoose.Schema({
  courseCode: { type: String, unique: true, required: true },
  title: { type: String, required: true },
  description: String,
  credits: { type: Number, required: true, min: 1, max: 6 },
  department: String,
  instructor: String,
  schedule: {
    days: [String],
    startTime: String,
    endTime: String,
    room: String
  },
  maxCapacity: { type: Number, required: true },
  currentEnrollment: { type: Number, default: 0 },
  status: { type: String, enum: ['open', 'closed', 'cancelled'], default: 'open' }
}, { timestamps: true });

module.exports = mongoose.model('Course', courseSchema);
```

### 4. Enrollment Service
```javascript
// enrollment-service/models/Enrollment.js
const mongoose = require('mongoose');

const enrollmentSchema = new mongoose.Schema({
  studentId: { type: mongoose.Schema.Types.ObjectId, ref: 'Student', required: true },
  courseId: { type: mongoose.Schema.Types.ObjectId, ref: 'Course', required: true },
  enrollmentDate: { type: Date, default: Date.now },
  status: { type: String, enum: ['enrolled', 'dropped', 'completed'], default: 'enrolled' },
  grade: { type: String, enum: ['A', 'B', 'C', 'D', 'F', 'I'], default: 'I' },
  semester: String
}, { timestamps: true });

// Compound index to prevent duplicate enrollments
enrollmentSchema.index({ studentId: 1, courseId: 1 }, { unique: true });

module.exports = mongoose.model('Enrollment', enrollmentSchema);
```

### 5. Authentication Service
```javascript
// auth-service/models/User.js
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');

const userSchema = new mongoose.Schema({
  username: { type: String, unique: true, required: true },
  email: { type: String, unique: true, required: true },
  password: { type: String, required: true },
  role: { type: String, enum: ['admin', 'faculty', 'student'], required: true },
  profileId: { type: mongoose.Schema.Types.ObjectId, required: true } // Links to student/faculty profile
}, { timestamps: true });

userSchema.pre('save', async function(next) {
  if (!this.isModified('password')) return next();
  this.password = await bcrypt.hash(this.password, 12);
  next();
});

userSchema.methods.correctPassword = async function(candidatePassword, userPassword) {
  return await bcrypt.compare(candidatePassword, userPassword);
};

module.exports = mongoose.model('User', userSchema);
```

## Docker Configuration

```dockerfile
# Dockerfile for each service (example for student service)
FROM node:16-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3001

CMD ["npm", "start"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  api-gateway:
    build: ./gateway-service
    ports:
      - "3000:3000"
    depends_on:
      - student-service
      - course-service
      - enrollment-service
      - auth-service

  student-service:
    build: ./student-service
    ports:
      - "3001:3001"
    environment:
      - DB_CONNECTION=mongodb://mongo:27017/student_db
    depends_on:
      - mongo

  course-service:
    build: ./course-service
    ports:
      - "3002:3002"
    environment:
      - DB_CONNECTION=mongodb://mongo:27017/course_db

  enrollment-service:
    build: ./enrollment-service
    ports:
      - "3003:3003"
    environment:
      - DB_CONNECTION=mongodb://mongo:27017/enrollment_db

  auth-service:
    build: ./auth-service
    ports:
      - "3004:3004"
    environment:
      - DB_CONNECTION=mongodb://mongo:27017/auth_db
      - JWT_SECRET=your-secret-key

  mongo:
    image: mongo:latest
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db

volumes:
  mongo_data:
```

## Service Communication

```javascript
// enrollment-service/services/studentService.js
const axios = require('axios');

class StudentService {
  constructor() {
    this.baseURL = process.env.STUDENT_SERVICE_URL || 'http://student-service:3001';
  }

  async getStudent(studentId) {
    try {
      const response = await axios.get(`${this.baseURL}/students/${studentId}`);
      return response.data;
    } catch (error) {
      throw new Error(`Student service error: ${error.message}`);
    }
  }

  async validateStudent(studentId) {
    const student = await this.getStudent(studentId);
    return student && student.status === 'active';
  }
}

module.exports = new StudentService();
```

## Database Configuration

```javascript
// shared/database.js
const mongoose = require('mongoose');

const connectDB = async (connectionString) => {
  try {
    await mongoose.connect(connectionString, {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
    console.log('MongoDB connected successfully');
  } catch (error) {
    console.error('Database connection error:', error);
    process.exit(1);
  }
};

module.exports = connectDB;
```

## Testing Setup

```javascript
// student-service/tests/student.test.js
const request = require('supertest');
const app = require('../app');
const Student = require('../models/Student');

describe('Student Service', () => {
  beforeEach(async () => {
    await Student.deleteMany({});
  });

  it('should create a new student', async () => {
    const studentData = {
      studentId: 'S001',
      firstName: 'John',
      lastName: 'Doe',
      email: 'john.doe@university.edu'
    };

    const response = await request(app)
      .post('/students')
      .send(studentData)
      .expect(201);

    expect(response.body.email).toBe(studentData.email);
  });

  it('should get all students with pagination', async () => {
    const response = await request(app)
      .get('/students?page=1&limit=10')
      .expect(200);

    expect(response.body).toHaveProperty('students');
    expect(response.body).toHaveProperty('totalPages');
  });
});
```

## Environment Configuration

```env
# .env.example
NODE_ENV=development
PORT=3001
DB_CONNECTION=mongodb://localhost:27017/student_db
JWT_SECRET=your-secret-key
STUDENT_SERVICE_URL=http://localhost:3001
COURSE_SERVICE_URL=http://localhost:3002
```

## API Documentation (Swagger/OpenAPI)

```yaml
# swagger.yaml for Student Service
openapi: 3.0.0
info:
  title: Student Management API
  version: 1.0.0
paths:
  /students:
    post:
      summary: Create a new student
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/Student'
      responses:
        '201':
          description: Student created successfully
```

## Deployment Scripts

```json
{
  "scripts": {
    "start": "node index.js",
    "dev": "nodemon index.js",
    "test": "jest --coverage",
    "docker:build": "docker build -t student-service .",
    "docker:run": "docker run -p 3001:3001 student-service",
    "compose:up": "docker-compose up -d",
    "compose:down": "docker-compose down"
  }
}
```

This microservices architecture provides:
- **Scalability**: Each service can be scaled independently
- **Maintainability**: Services are focused and manageable
- **Technology Diversity**: Different services can use different technologies
- **Fault Isolation**: Failure in one service doesn't affect others
- **Continuous Deployment**: Independent deployment of services

Would you like me to elaborate on any specific service or add additional features like logging, monitoring, or message queues?
