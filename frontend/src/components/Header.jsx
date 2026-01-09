import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import './Header.css';
import { categories } from './categoryIcon/categoryData';
import sampleArticles from '../sample_/sampleArticle.json';

const Header = ({
  className = "",
  leftChild,
  midChild,
  rightChild,
  darkmode,
  headerTop = "on",
  headerMain = "on",
  headerBottom = "on"
}) => {
  const nav = useNavigate();
  const location = useLocation();
  const { name: activeCategory } = useParams();

  const [currentArticleIndex, setCurrentArticleIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentArticleIndex((prevIndex) => (prevIndex + 1) % sampleArticles.length);
    }, 2300);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className={"Header-Container " + className}>
      {headerTop === "on" && (
        <div className="Header-Top">
          <div className="header-top-content">
            <span 
              className="updated-articles" 
              onClick={() => nav('/article')} 
              style={{ cursor: 'pointer' }}
            >
              {sampleArticles[currentArticleIndex].title}
            </span>
            <span className="weather">서울 날씨</span>
          </div>
        </div>
      )}

      {headerMain === "on" && (
        <header className="Header-Main">
          <div className="header-main-content">
            <div className="left-child">
              {leftChild}
            </div>

            <div className="mid-child">
              {midChild}
            </div>

            <div className="right-child">
              {rightChild}
            </div>
          </div>
        </header>
      )}

      {headerBottom === "on" && (
        <div className="Header-Bottom">
          <div className="category-list">
            {categories.map((item) => (
              <div
                key={item.id}
                className={`category-item ${
                  activeCategory === item.label || (item.label === '이슈' && location.pathname === '/issues') 
                  ? 'active' : ''
                }`}
                onClick={() => {
                  if (item.label === '이슈') {
                    nav('/issues');
                  } else {
                    nav(`/category/${encodeURIComponent(item.label)}`);
                  }
                }}
              >
                <div className="icon-wrapper">
                  <img
                    src={item.icon}
                    alt={item.label}
                    className="category-icon"
                  />
                </div>
                <span>{item.label}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default Header;
