import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Logo from '../components/Logo';
import loginIcon from '../login_icon/login.png';
import Header from '../components/Header';
import './MyPage.css';

const MyPage = () => {
  const navigate = useNavigate();
  const [isActive, setIsActive] = useState(false);
  
  const targetScores = {
    politics: 80, economy: 65, society: 90, living: 70, itScience: 85, world: 50
  };

  const [currentScores, setCurrentScores] = useState({
    politics: 0, economy: 0, society: 0, living: 0, itScience: 0, world: 0
  });

  useEffect(() => {
    // 1. 값이 높은 순서대로 키(Key) 배열 정렬
    const sortedKeys = Object.keys(targetScores).sort((a, b) => targetScores[b] - targetScores[a]);
    
    let frame = 0;
    const totalFrames = 90; // 개별 애니메이션 지속 시간
    const staggerDelay = 4; // 각 카테고리 간의 시작 간격 (프레임 단위)

    const animate = () => {
      frame++;
      let updatedScores = { ...currentScores };
      let finished = true;

      sortedKeys.forEach((key, index) => {
        // 각 카테고리마다 시작 지점을 다르게 설정 (순서대로 0, 15, 30... 프레임 뒤에 시작)
        const startFrame = index * staggerDelay;
        if (frame > startFrame) {
          const relativeFrame = frame - startFrame;
          const progress = Math.min(relativeFrame / totalFrames, 1);
          const easeProgress = 1 - Math.pow(1 - progress, 3); // Ease-out

          updatedScores[key] = targetScores[key] * easeProgress;
          
          if (progress < 1) finished = false;
        } else {
          finished = false;
        }
      });

      setCurrentScores(updatedScores);

      if (!finished) {
        requestAnimationFrame(animate);
      }
    };

    const timer = setTimeout(() => {
      setIsActive(true);
      requestAnimationFrame(animate);
    }, 200);

    return () => {
      clearTimeout(timer);
      cancelAnimationFrame(animate);
    };
  }, []);

  const getCoordinates = (scores) => {
    const labels = ['politics', 'economy', 'society', 'living', 'itScience', 'world'];
    const center = 100;
    const radius = 60;
    return labels.map((label, i) => {
      const angle = (Math.PI / 3) * i - Math.PI / 2;
      const scoreRatio = (scores[label] || 0) / 100;
      const x = center + radius * scoreRatio * Math.cos(angle);
      const y = center + radius * scoreRatio * Math.sin(angle);
      return `${x},${y}`;
    }).join(' ');
  };

  return (
    <div className="mypage-container">
      <Header
        headerTop="off" headerMain="on" headerBottom="off"
        leftChild={<Logo />}
        rightChild={<img src={loginIcon} width='35px' onClick={() => navigate('/login')} className="cursor-pointer" alt="login" />}
      />
      
      <main className="mypage-main">
        <section className="profile-header">
          <h1 className="text-xl font-bold">나의 정보</h1>
          <p className="text-gray-400 text-sm mt-1">user_id@vaccine.com</p>
        </section>

        <div className="content-wrapper">
          <section className="info-section">
            <h3 className="section-title">나의 관심 카테고리</h3>
            <div className="chart-container">
              <div style={{ width: '450px', height: '350px' }}>
                <svg viewBox="-20 10 250 180" className="w-full h-full">
                  {[0.2, 0.4, 0.6, 0.8, 1].map((r) => (
                    <polygon key={r} points={getCoordinates({ politics: 100*r, economy: 100*r, society: 100*r, living: 100*r, itScience: 100*r, world: 100*r })} fill="none" stroke="#f0f0f0" strokeWidth="1" />
                  ))}
                  
                  <polygon 
                    className={`radar-polygon ${isActive ? 'active' : ''}`}
                    points={getCoordinates(currentScores)} 
                    fill="rgba(250, 204, 21, 0.6)" 
                    stroke="#ffffffff" // 경계선
                    strokeWidth="1" 
                    strokeLinejoin="round"
                  />

                  {/* 라벨 텍스트 생략... */}
                  <text x="100" y="25" textAnchor="middle" fontSize="14" fill="#4b5563" fontWeight="bold">정치</text>
                  <text x="180" y="75" textAnchor="start" fontSize="14" fill="#4b5563" fontWeight="bold">경제</text>
                  <text x="180" y="135" textAnchor="start" fontSize="14" fill="#4b5563" fontWeight="bold">사회</text>
                  <text x="100" y="185" textAnchor="middle" fontSize="14" fill="#4b5563" fontWeight="bold">생활</text>
                  <text x="20" y="135" textAnchor="end" fontSize="14" fill="#4b5563" fontWeight="bold">IT</text>
                  <text x="20" y="75" textAnchor="end" fontSize="14" fill="#4b5563" fontWeight="bold">세계</text>
                </svg>
              </div>
            </div>
          </section>

          <section className="info-section">
            <div style={{ flex: 1 }}>
              <h3 className="section-title">나의 관심 키워드</h3>
              <div className="keyword-list">
                {['#반도체', '#금리', '#오픈AI', '#미대선', '#건강'].map(tag => (
                  <span key={tag} className="keyword-tag">{tag}</span>
                ))}
              </div>
            </div>
            <div className="analysis-footer">
               <p className="text-xs text-gray-400 mb-1">AI 분석 결과</p>
               <p className="text-lg font-black leading-tight">주로 사회 이슈와 IT 기술에<br/>관심이 집중되어 있습니다.</p>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
};

export default MyPage;