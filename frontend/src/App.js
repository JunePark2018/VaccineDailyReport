import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';
import Main from './pages/Main.jsx';
import Header from './header.js';
import logo from './logo.png';
import Searchbar from './Searchbar';
import Button from './Button';

function App() {
  return (
    <div className="App">
      <Header
        leftChild={<img src={logo} alt="Vaccine 일보 Logo" style={{ height: '50px' }} />}
        midChild={<Searchbar />}
        rightChild={<Button text={'로그인'} onClick={() => {

        }} />}
      />
      <Main />
    </div>
  );
}

export default App;
