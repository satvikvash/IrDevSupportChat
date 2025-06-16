# IrDevSupportChat

Nasdaq Internal Hackathon

## Technologies Used

### Frontend

- React 18
- TypeScript
- CSS3 (with responsive design)
- React Hooks

### Backend (Optional)

- FastAPI (Python)
- Pydantic for data validation

## Installation

### Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- Python 3.7+ (for backend only)

### Frontend Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/react-chatgpt-clone.git
   cd react-chatgpt-clone
   ```

2. Install dependencies:

   ```bash
   npm install
   # or
   yarn install
   ```

3. Start the development server:

   ```bash
   npm start
   # or
   yarn start
   ```

4. Open your browser and navigate to `http://localhost:3000`

### Backend Setup (Optional)

1. Navigate to the backend directory:

   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv

   # On Windows
   venv\Scripts\activate

   # On macOS/Linux
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install fastapi uvicorn pydantic
   ```

4. Start the FastAPI server:

   ```bash
   uvicorn main:app --reload
   ```

5. The API will be available at `http://localhost:8000`
