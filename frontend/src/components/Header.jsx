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
                className={`category-item ${location.pathname === (
                  item.label === '이슈' ? '/issues' :
                    item.label === '정치' ? '/politics' :
                      item.label === '경제' ? '/economy' :
                        item.label === '사회' ? '/society' :
                          item.label === '생활/문화' ? '/living-culture' :
                            item.label === 'IT/과학' ? '/science' :
                              item.label === '세계' ? '/world' :
                                item.label === '전체메뉴' ? '/total' : ''
                ) ? 'active' : ''
                  }`}
                onClick={() => {
                  if (item.label === '이슈') nav('/issues');
                  else if (item.label === '정치') nav('/politics');
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
