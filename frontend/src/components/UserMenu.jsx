import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import loginIcon from '../login_icon/login.png';
import './UserMenu.css';

const UserMenu = () => {
  const navigate = useNavigate();
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showMenu, setShowMenu] = useState(false);
  const menuRef = useRef(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    setIsLoggedIn(!!token);

    const handleClickOutside = (event) => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setShowMenu(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleIconClick = () => {
    if (isLoggedIn) {
      setShowMenu(!showMenu);
    } else {
      navigate('/login');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setIsLoggedIn(false);
    setShowMenu(false);
    navigate('/');
    window.location.reload(); // Refresh to update all components
  };

  const handleMyPage = () => {
    setShowMenu(false);
    navigate('/mypage');
  };

  return (
    <div className="user-menu-container" ref={menuRef}>
      <img
        src={loginIcon}
        alt={isLoggedIn ? "User Menu" : "Login"}
        className="user-icon"
        onClick={handleIconClick}
      />
      {isLoggedIn && showMenu && (
        <div className="dropdown-menu">
          <div className="menu-item" onClick={handleMyPage}>마이페이지</div>
          <div className="menu-item" onClick={handleLogout}>로그아웃</div>
        </div>
      )}
    </div>
  );
};

export default UserMenu;
