import React from 'react';
import './header.css'; // We will create this next
import logo from './logo.png';
import Searchbar from './Searchbar';
import Button from './Button';

const Header = () => {
  return (
    <header className="header-container">
       <div className="left-child">
                {/* 2. Replace the placeholder with the img tag */}
                <img src={logo} alt="Vaccine 일보 Logo" style={{ height: '50px' }} />
            </div>
      
      <div className="mid-child">
        <Searchbar/>
      </div>
      
      <div className="right-child">
        <Button text={'로그인'} onClick={() => {

      }}/>
      </div>
    </header>
  );
};

export default Header;