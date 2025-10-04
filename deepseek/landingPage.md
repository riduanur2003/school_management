Here's a complete React registration page that integrates with your FastAPI backend:

## 📁 Project Structure
```
react-auth-frontend/
├── src/
│   ├── components/
│   │   └── RegistrationForm.jsx
│   ├── services/
│   │   └── api.js
│   ├── styles/
│   │   └── RegistrationForm.css
│   ├── App.js
│   └── index.js
├── package.json
└── public/
    └── index.html
```

## 1. package.json
```json
{
  "name": "react-auth-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.0",
    "vite": "^5.0.0"
  }
}
```

## 2. src/services/api.js
```javascript
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const authAPI = {
  register: async (userData) => {
    const response = await api.post('/auth/register', userData);
    return response.data;
  },
  
  login: async (credentials) => {
    const response = await api.post('/auth/login', credentials);
    return response.data;
  },
};

export default api;
```

## 3. src/styles/RegistrationForm.css
```css
.registration-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 30px;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  background-color: white;
}

.registration-title {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
  font-size: 24px;
}

.registration-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-label {
  margin-bottom: 5px;
  font-weight: 600;
  color: #555;
}

.form-input {
  padding: 12px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 16px;
  transition: border-color 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.25);
}

.submit-button {
  padding: 12px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.submit-button:hover {
  background-color: #0056b3;
}

.submit-button:disabled {
  background-color: #6c757d;
  cursor: not-allowed;
}

.error-message {
  background-color: #f8d7da;
  color: #721c24;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 20px;
  border: 1px solid #f5c6cb;
}

.success-container {
  text-align: center;
  padding: 40px;
}

.success-icon {
  font-size: 48px;
  color: #28a745;
  margin-bottom: 20px;
}

.success-title {
  color: #28a745;
  margin-bottom: 15px;
  font-size: 24px;
}

.success-message {
  color: #666;
  margin-bottom: 25px;
  line-height: 1.5;
}

.user-details {
  background-color: #f8f9fa;
  padding: 20px;
  border-radius: 4px;
  margin-top: 20px;
  text-align: left;
}

.user-detail {
  margin-bottom: 8px;
}

.loading {
  opacity: 0.7;
  pointer-events: none;
}
```

## 4. src/components/RegistrationForm.jsx
```javascript
import React, { useState } from 'react';
import { authAPI } from '../services/api';
import '../styles/RegistrationForm.css';

const RegistrationForm = () => {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: '',
    full_name: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isRegistered, setIsRegistered] = useState(false);
  const [userData, setUserData] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    // Clear error when user starts typing
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError('');

    try {
      // Remove empty full_name if not provided
      const submitData = { ...formData };
      if (!submitData.full_name.trim()) {
        delete submitData.full_name;
      }

      const response = await authAPI.register(submitData);
      
      // Registration successful
      setUserData(response);
      setIsRegistered(true);
      
      // Reset form
      setFormData({
        email: '',
        username: '',
        password: '',
        full_name: ''
      });
      
    } catch (err) {
      if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else if (err.response?.data) {
        // Handle validation errors
        const errors = err.response.data;
        if (typeof errors === 'object') {
          const errorMessages = Object.values(errors).flat().join(', ');
          setError(errorMessages);
        } else {
          setError('Registration failed. Please try again.');
        }
      } else {
        setError('Network error. Please check your connection.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const resetForm = () => {
    setIsRegistered(false);
    setUserData(null);
    setError('');
  };

  if (isRegistered) {
    return (
      <div className="registration-container">
        <div className="success-container">
          <div className="success-icon">✓</div>
          <h2 className="success-title">Registration Successful!</h2>
          <p className="success-message">
            Your account has been created successfully. You can now log in to your account.
          </p>
          
          <div className="user-details">
            <h3>Your Account Details:</h3>
            <div className="user-detail"><strong>Username:</strong> {userData.username}</div>
            <div className="user-detail"><strong>Email:</strong> {userData.email}</div>
            <div className="user-detail"><strong>Full Name:</strong> {userData.full_name || 'Not provided'}</div>
            <div className="user-detail"><strong>User ID:</strong> {userData.id}</div>
          </div>
          
          <button 
            onClick={resetForm}
            className="submit-button"
            style={{ marginTop: '20px', backgroundColor: '#6c757d' }}
          >
            Register Another User
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="registration-container">
      <h1 className="registration-title">Create Your Account</h1>
      
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit} className="registration-form">
        <div className="form-group">
          <label htmlFor="email" className="form-label">
            Email Address *
          </label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            className="form-input"
            placeholder="Enter your email"
            required
            disabled={isLoading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="username" className="form-label">
            Username *
          </label>
          <input
            type="text"
            id="username"
            name="username"
            value={formData.username}
            onChange={handleChange}
            className="form-input"
            placeholder="Choose a username"
            required
            disabled={isLoading}
          />
        </div>

        <div className="form-group">
          <label htmlFor="password" className="form-label">
            Password *
          </label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            className="form-input"
            placeholder="Create a password"
            required
            disabled={isLoading}
            minLength="6"
          />
        </div>

        <div className="form-group">
          <label htmlFor="full_name" className="form-label">
            Full Name
          </label>
          <input
            type="text"
            id="full_name"
            name="full_name"
            value={formData.full_name}
            onChange={handleChange}
            className="form-input"
            placeholder="Enter your full name (optional)"
            disabled={isLoading}
          />
        </div>

        <button 
          type="submit" 
          className={`submit-button ${isLoading ? 'loading' : ''}`}
          disabled={isLoading}
        >
          {isLoading ? 'Creating Account...' : 'Create Account'}
        </button>
      </form>
    </div>
  );
};

export default RegistrationForm;
```

## 5. src/App.js
```javascript
import React from 'react';
import RegistrationForm from './components/RegistrationForm';
import './styles/RegistrationForm.css';

function App() {
  return (
    <div className="App">
      <RegistrationForm />
    </div>
  );
}

export default App;
```

## 6. src/index.js
```javascript
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

## 7. vite.config.js
```javascript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
  },
})
```

## 8. public/index.html
```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>User Registration</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/index.js"></script>
  </body>
</html>
```

## 🚀 **How to Run**

1. **Install dependencies:**
```bash
npm install
```

2. **Start the development server:**
```bash
npm run dev
```

3. **Make sure your FastAPI backend is running on http://localhost:8000**

## ✨ **Features**

- **Complete form validation**
- **Real-time error handling**
- **Loading states during API calls**
- **Success page with user details**
- **Option to register another user**
- **Responsive design**
- **Clean, modern UI**

## 📱 **User Experience Flow**

1. **Fill out registration form** with required information
2. **Submit form** - shows loading state
3. **On success**: Displays confirmation with user details
4. **On error**: Shows specific error messages
5. **Option to register another user** after success

The form will automatically communicate with your FastAPI backend and handle all the registration logic seamlessly!
