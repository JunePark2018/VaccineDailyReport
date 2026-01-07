import React from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import './Header.css';

// Import all category icons
import governmentIcon from './leftsidebaricon/government.png';
import economicsIcon from './leftsidebaricon/economics.png';
import societyIcon from './leftsidebaricon/society.png';
import entertainmentIcon from './leftsidebaricon/entertainment.png';
import healthIcon from './leftsidebaricon/health.png';
import sportsIcon from './leftsidebaricon/sports.png';
import weatherIcon from './leftsidebaricon/weather.png';
import scienceIcon from './leftsidebaricon/science.png';
import worldIcon from './leftsidebaricon/world.png';

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
  const { name: activeCategory } = useParams();

  // Data array for categories
  const categories = [
      { id: 'sub1', label: '정치', icon: governmentIcon },
      { id: 'sub2', label: '경제', icon: economicsIcon },
      { id: 'sub3', label: '사회', icon: societyIcon },
      { id: 'sub4', label: '엔터', icon: entertainmentIcon },
      { id: 'sub5', label: '건강', icon: healthIcon },
      { id: 'sub6', label: '스포츠', icon: sportsIcon },
      { id: 'sub7', label: '기후', icon: weatherIcon },
      { id: 'sub8', label: '과학', icon: scienceIcon },
      { id: 'sub9', label: '세계', icon: worldIcon },
  ];

  const today = new Date();
  const dateString = today.toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long'
  });

  return (
    <div className={"Header-Container " + className}>
      {headerTop === "on" && (
        <div className="Header-Top">
          <div className="header-top-content">
            <span className="today-date">{dateString}</span>
            <span className="trending-tag">#의대증원 #AI신약 #기후위기</span>
          </div>
        </div>
      )}

      {headerMain === "on" && (
        <header className="Header-Main">
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
      )}

      {headerBottom === "on" && (
        <div className="Header-Bottom">
          <div className="category-list">
            {categories.map((item) => (
              <div
                key={item.id}
                className={`category-item ${activeCategory === item.label ? 'active' : ''}`}
                onClick={() => nav(`/category/${item.label}`)}
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
