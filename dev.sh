#!/bin/bash
# Start both backend and frontend dev servers

echo "🚀 Starting ChaiSaathi AI..."

# Start backend
cd backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
echo "✅ Backend running on http://localhost:8000 (PID: $BACKEND_PID)"

# Start frontend
cd ../frontend
npm run dev &
FRONTEND_PID=$!
echo "✅ Frontend running on http://localhost:5173 (PID: $FRONTEND_PID)"

echo ""
echo "🍵 ChaiSaathi AI is ready!"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo 'Servers stopped.'" INT
wait
