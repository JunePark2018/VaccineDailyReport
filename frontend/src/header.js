import React from 'react';
import './header.css'; // We will create this next

const Header = ({className = "", leftChild, midChild, rightChild, darkmode}) => {
  return (
    <header className={"Header " + className}>
      <div className="left-child">
        {leftChild}
      </div>

      <div className="mid-child">
        {midChild}
      </div>

      <div className="right-child">
        {rightChild}
      </div>
    </header>
  );
};

export default Header;