import React from 'react';
import CallsList from './CallList'; 
import ChatPage from './ChatPage'
import { Routes, Route, BrowserRouter } from 'react-router-dom';

const App: React.FC = () => {
  return (
<BrowserRouter>
    <Routes>
      <Route path="/" element={<CallsList />} />
      <Route path="/calls" element={<CallsList />} />
      <Route path="/chat/:callId" element={<ChatPage/>} />
    </Routes>
    </BrowserRouter>
  );
}

export default App;
