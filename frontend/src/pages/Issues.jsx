import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import Logo from '../components/Logo';
import Searchbar from '../components/Searchbar';
import UserMenu from '../components/UserMenu';
import './Issues.css';

const Issues = () => {
  const navigate = useNavigate();

  return (
    <div className="Issues">
      <Header 
        leftChild={<Logo />}
        midChild={<Searchbar />}
        rightChild={<UserMenu />}
        headerTop="on" 
        headerMain="on" 
        headerBottom="on" 
      />
      <main className="Issues-Main">
        {/* Blank page content as requested */}
      </main>
    </div>
  );
};

export default Issues;
