import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';
import Main from './pages/Main.jsx';
import Header from './header.js';

function App() {
  return (
    <div className="App">
      <Header />
      <Main/>
    </div>
  );
}

export default App;
