# Project Structure Documentation

## Overview
This project consists of a Python backend API and a React frontend, structured as a monorepo. The application appears to be an AI-powered chat interface with creative matrix capabilities.

## Directory Structure 
├── app/ # Python Backend
│ ├── .venv/ # Python virtual environment
│ ├── tests/ # Backend tests
│ ├── resources/ # Static resources
│ │ └── static/
│ │ ├── out/ # Built frontend files
│ │ └── kp-static/ # Static knowledge pack files
│ └── main.py # Main FastAPI application
├── ui/ # Frontend React Application
│ ├── src/
│ │ ├── tests/ # Frontend tests
│ │ ├── app/ # React components
│ │ │ ├── chat.js
│ │ │ ├── sidebar.js
│ │ │ └── prompt_chat.js
│ │ └── pages/
│ │ └── creative-matrix.js
│ ├── public/ # Public assets
│ └── next.config.js # Next.js configuration
└── Dockerfile # Container configuration

## Backend (Python)

### Key Characteristics
- Located in the `app/` directory
- Built with FastAPI
- Uses constructor dependency injection pattern
- Requires virtual environment activation before running
- Must be started from the app directory

### Running the Backend
```bash
cd app
source .venv/bin/activate  # Activate virtual environment
python main.py            # Start the application
```

### Testing
```bash
cd app
source .venv/bin/activate
pytest tests/
```

## Frontend (React/Next.js)

### Key Characteristics
- Located in the `ui/` directory
- Built with React and Next.js
- Uses "client only" mode (no server-side features)
- Static build that calls Python API for data
- Uses yarn as package manager
- Uses vitest for testing
- Uses prettier for formatting
- Uses remix icons for icons

### Component Conventions
- Components are stored in `ui/app/`
- File naming convention: `_component_name.js`
- No JSDocs required

### Running the Frontend
```bash
cd ui
yarn install
yarn dev
```

### Testing
```bash
cd ui
yarn test
```

## Key Components

### Chat Components
- `_chat.js`: Main chat widget component
- `_prompt_chat.js`: Prompt-specific chat implementation
- `_sidebar.js`: Sidebar navigation component

### Creative Matrix
- `creative-matrix.js`: Matrix visualization component
- Handles dynamic rendering of ideas in a grid format
- Supports row and column-based organization

## Static File Serving

### Backend Configuration
- Static files are served through FastAPI's StaticFiles
- Knowledge pack files are served from `/kp-static/`
- Built frontend is served from `/resources/static/out/`

### Frontend Static Files
- Built as static assets
- Distributed through Python backend
- No server-side rendering

## Development Workflow

### Best Practices
1. Use TDD (Test-Driven Development)
   - Write tests first
   - Run tests (expect failure)
   - Implement feature
   - Run tests again (expect success)

2. Make regular commits at runnable states
3. Verify full application integration after backend changes

### Dependencies
- Frontend: managed with yarn
- Backend: managed with pip and virtual environment

## Docker Support
- Single Dockerfile for both frontend and backend
- Multi-stage build process
- Copies static files to appropriate locations
- Handles both development and production builds

## Guidelines for Adding New Components

### 🚨 Important Rules for Beginners
1. **NEVER modify existing components directly** - create new ones or extend existing ones
2. **ALWAYS create a new branch** before starting work
3. **ALWAYS run tests** before committing changes
4. **NEVER skip writing tests** - this is mandatory
5. **Ask for help** if you're unsure about architecture decisions

### Step-by-Step Development Workflow

#### 1. Initial Setup (Do this ONCE)
```bash
# Clone the repository
git clone [repository-url]

# Setup Backend
cd app
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Setup Frontend
cd ../ui
yarn install
```

#### 2. Starting New Feature (Do this EVERY time)
```bash
# Create new feature branch
git checkout -b feature/your-feature-name

# Activate virtual environment
cd app
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Start backend
python main.py

# In another terminal, start frontend
cd ui
yarn dev
```

### Backend Component Guidelines

#### 1. Planning Phase (REQUIRED)
- [ ] Define the purpose of your component
- [ ] List all dependencies needed
- [ ] Create component diagram showing interactions
- [ ] Get approval from team lead if major feature

#### 2. Create Component Files
```plaintext
app/
├── services/              # Business logic
├── models/               # Data models
├── api/                 # API endpoints
└── tests/              # Test files
```

Example structure for new feature:
```plaintext
app/
├── services/
│   ├── my_feature/
│   │   ├── __init__.py
│   │   ├── my_feature_service.py        # Implementation
│   │   └── my_feature_interface.py      # Interface
├── tests/
│   └── services/
│       └── my_feature/
│           └── test_my_feature.py
```

#### 3. Define Interface (REQUIRED)
```python
# app/services/my_feature/my_feature_interface.py
from abc import ABC, abstractmethod
from typing import Dict, Optional

class MyFeatureInterface(ABC):
    """
    Clear description of what this service does.
    """
    
    @abstractmethod
    async def process_data(self, input_data: Dict) -> Optional[Dict]:
        """
        Clear description of method purpose.
        
        Args:
            input_data: Description of input format
            
        Returns:
            Description of return format
            
        Raises:
            Specific exceptions that might be raised
        """
        pass
```

#### 4. Write Tests FIRST (REQUIRED)
```python
# app/tests/services/my_feature/test_my_feature.py
import pytest
from unittest.mock import Mock
from app.services.my_feature.my_feature_service import MyFeatureService

class TestMyFeature:
    @pytest.fixture
    def service(self):
        # Setup your service with mocked dependencies
        dependency = Mock()
        return MyFeatureService(dependency)

    def test_process_data_success(self, service):
        # Arrange
        test_input = {"key": "value"}
        
        # Act
        result = await service.process_data(test_input)
        
        # Assert
        assert result is not None
        assert "expected_key" in result

    def test_process_data_error(self, service):
        # Test error scenarios
        pass
```

#### 5. Implement Component
```python
# app/services/my_feature/my_feature_service.py
from .my_feature_interface import MyFeatureInterface
from typing import Dict, Optional

class MyFeatureService(MyFeatureInterface):
    def __init__(self, dependency: DependencyInterface):
        self._dependency = dependency
        
    async def process_data(self, input_data: Dict) -> Optional[Dict]:
        try:
            # Implementation
            result = await self._dependency.some_method(input_data)
            return {"processed": result}
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            return None
```

### Frontend Component Guidelines

#### 1. Planning Phase (REQUIRED)
- [ ] Create component mockup/design
- [ ] List all props and state needed
- [ ] Define component responsibilities
- [ ] Get design approval if user-facing

#### 2. Component Structure
```plaintext
ui/
├── src/
│   ├── app/
│   │   └── _my_feature/              # Feature folder
│   │       ├── _my_component.js      # Main component
│   │       ├── _my_component.css     # Styles
│   │       └── hooks/               # Custom hooks
│   └── __tests__/
│       └── my_feature/
│           └── MyComponent.test.js
```

#### 3. Write Tests FIRST (REQUIRED)
```javascript
// ui/src/__tests__/my_feature/MyComponent.test.js
import { render, screen, fireEvent } from '@testing-library/react'
import MyComponent from '../../app/_my_feature/_my_component'

describe('MyComponent', () => {
  // Setup - runs before each test
  beforeEach(() => {
    // Reset any mocks/state
  })

  // Basic rendering test
  it('renders without crashing', () => {
    render(<MyComponent />)
    expect(screen.getByTestId('my-component')).toBeInTheDocument()
  })

  // Interaction test
  it('handles user interaction correctly', () => {
    render(<MyComponent />)
    const button = screen.getByRole('button')
    fireEvent.click(button)
    expect(screen.getByText('Expected Result')).toBeInTheDocument()
  })

  // Error state test
  it('shows error state correctly', () => {
    render(<MyComponent hasError={true} />)
    expect(screen.getByText('Error Message')).toBeInTheDocument()
  })
})
```

#### 4. Implement Component
```javascript
// ui/src/app/_my_feature/_my_component.js
import { useState, useEffect } from 'react'
import styles from './_my_component.css'

const MyComponent = ({ prop1, prop2 }) => {
  // 1. State declarations
  const [data, setData] = useState(null)
  const [error, setError] = useState(null)
  
  // 2. Effects
  useEffect(() => {
    const loadData = async () => {
      try {
        // Load data
      } catch (err) {
        setError(err.message)
      }
    }
    loadData()
  }, [prop1]) // Clear dependency array
  
  // 3. Event handlers
  const handleClick = () => {
    // Handle events
  }
  
  // 4. Render helpers
  const renderContent = () => {
    if (error) return <ErrorMessage message={error} />
    if (!data) return <Loading />
    return <DataDisplay data={data} />
  }
  
  // 5. Main render
  return (
    <div className={styles.container} data-testid="my-component">
      {renderContent()}
    </div>
  )
}

export default MyComponent
```

### 🔍 Quality Checklist (Use BEFORE committing)

#### Backend
- [ ] All tests written and passing
- [ ] Interface properly defined
- [ ] Error handling implemented
- [ ] Logging added
- [ ] Type hints used
- [ ] Documentation updated

#### Frontend
- [ ] All tests written and passing
- [ ] PropTypes or TypeScript types defined
- [ ] Error boundaries implemented
- [ ] Loading states handled
- [ ] Responsive design tested
- [ ] Console free of warnings/errors

### 🚀 Deployment Checklist

1. **Local Testing**
```bash
# Backend
cd app
pytest
flake8 .

# Frontend
cd ui
yarn test
yarn build
```

2. **Integration Testing**
- [ ] API endpoints tested with Postman/curl
- [ ] Frontend-Backend integration verified
- [ ] Error scenarios tested

3. **Pre-Deployment**
- [ ] Documentation updated
- [ ] Change log updated
- [ ] Version numbers updated
- [ ] Docker build tested

### 🆘 Common Pitfalls to Avoid

1. **Backend**
- DON'T modify existing interfaces without discussion
- DON'T skip error handling
- DON'T use global state
- DON'T commit sensitive data

2. **Frontend**
- DON'T modify existing components directly
- DON'T skip loading/error states
- DON'T use inline styles
- DON'T ignore React warnings

### 📚 Resources

1. **Backend Resources**
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Python Testing Guide](https://docs.pytest.org/)
- [Type Hints Guide](https://mypy.readthedocs.io/)

2. **Frontend Resources**
- [React Documentation](https://reactjs.org/)
- [Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Next.js Documentation](https://nextjs.org/docs)

## Notes
- Frontend is distributed as static resources
- Backend serves both API and static content
- Constructor dependency injection is used for testability
- No server-side Next.js features are used
