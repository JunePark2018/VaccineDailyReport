import React, { useState, useEffect } from 'react';
import { useNavigate, useParams, useLocation } from 'react-router-dom';
import './Header.css';
import { categories } from './categoryIcon/categoryData';
import sampleArticles from '../sample_/sampleArticle.json';

import Weather from './Weather';

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
            <Weather />
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
                className={`category-item ${activeCategory === item.label
                  ? 'active' : ''
                  }`}
                onClick={() => {
                  if (item.label === '정치') nav('/politics');
                  else if (item.label === '경제') nav('/economy');
                  else if (item.label === '사회') nav('/society');
                  else if (item.label === '생활/문화') nav('/living-culture');
                  else if (item.label === 'IT/과학') nav('/science');
                  else if (item.label === '세계') nav('/world');
                  else if (item.label === '홈') nav('/');
                }}
              >
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
