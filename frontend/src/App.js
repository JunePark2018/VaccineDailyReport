import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';
import Main from './pages/Main.jsx';
import { BrowserRouter } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <div className="App">
        <Main />
      </div>
    </BrowserRouter>
  );
}

export default App;
