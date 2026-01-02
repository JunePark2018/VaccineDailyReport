import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';
import Main from './pages/Main.jsx';
import Header from './components/Header';
import logo from './logo.png';
import Searchbar from './components/Searchbar';
import Button from './components/Button';

function App() {
  return (
    <div className="App">
      <Header
        leftChild={<img src={logo} alt="Vaccine 일보 Logo" style={{ height: '50px' }} />}
        midChild={<Searchbar maxWidth="400px" />}
        rightChild={<Button text={'로그인'} onClick={() => {

        }} />}
      />
      <Main />
    </div>
  );
}

export default App;
