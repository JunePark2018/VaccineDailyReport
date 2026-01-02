import React, { useState, useEffect } from 'react';
import './App.css';
import axios from 'axios';
import Main from './pages/Main.jsx';
import Header from './components/Header';
import Searchbar from './components/Searchbar';
import Button from './components/Button';
import Logo from './components/Logo.jsx';
import { BrowserRouter } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
    <div className="App">
      <Header
        leftChild={<Logo/>}
        midChild={<Searchbar maxWidth="400px" />}
        rightChild={<Button text={'로그인'} onClick={() => {

        }} />}
      />
      <Main />
    </div>
    </BrowserRouter>
  );
}

export default App;
