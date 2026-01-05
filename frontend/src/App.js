import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';
import Main from './pages/Main.jsx';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import ArticlePage from './pages/ArticlePage.jsx';

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
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
