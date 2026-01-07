import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';
import Main from './pages/Main.jsx';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ArticlePage from './pages/ArticlePage.jsx';
import CategoryPage from './pages/CategoryPage.jsx';
import CreateAccount from './pages/CreateAccount.jsx';
import Issues from './pages/Issues.jsx';
import Login from './components/Login.jsx';
import MyPage from './pages/MyPage.jsx';

function App() {
  return (
    <BrowserRouter future={{
        v7_startTransition: true,
        v7_relativeSplatPath: true,
      }}>
      <div className="App">
        <Routes>
          <Route path="/" element={<Main />} />
          <Route path="/article" element={<ArticlePage />} />
          <Route path="/category/:name" element={<CategoryPage />} />
          <Route path="/issues" element={<Issues />} />
          <Route path='login' element={<Login />} />
          <Route path='/CreateAccount' element={<CreateAccount />} />
          <Route path='/MyPage' element={<MyPage />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
