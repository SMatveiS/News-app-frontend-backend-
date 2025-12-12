import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import NavBar from './components/NavBar';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import CreateNews from './pages/CreateNews';
import EditNews from './pages/EditNews';
import NewsDetail from './pages/NewsDetail';

function App() {
  return (
    <AuthProvider>
      <Router>
        <NavBar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/create" element={<CreateNews />} />
          <Route path="/edit-news/:id" element={<EditNews />} />
          <Route path="/news/:id" element={<NewsDetail />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
