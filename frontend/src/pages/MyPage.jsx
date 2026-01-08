import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import Logo from '../components/Logo';
import Header from '../components/Header';
import UserMenu from '../components/UserMenu';
import './MyPage.css';

const MyPage = () => {
  const navigate = useNavigate();
  const [isActive, setIsActive] = useState(false);

  const targetScores = {
    politics: 80, economy: 65, society: 90, living: 70, itScience: 85, world: 50
  };

  // 1. 동적 최대값 계산 (최대값 + 10)
  const dynamicLimit = useMemo(() => {
    return Math.max(...Object.values(targetScores)) + 10;
  }, []);

  const [currentScores, setCurrentScores] = useState({
    politics: 0, economy: 0, society: 0, living: 0, itScience: 0, world: 0
  });

  // 2. 애니메이션 로직 (높은 값 순서대로 스프레드)
  useEffect(() => {
    const sortedKeys = Object.keys(targetScores).sort((a, b) => targetScores[b] - targetScores[a]);
    let frame = 0;
    const totalFrames = 90;
    const staggerDelay = 4;

    const animate = () => {
      frame++;
      let updatedScores = { ...currentScores };
      let finished = true;

      sortedKeys.forEach((key, index) => {
        const startFrame = index * staggerDelay;
        if (frame > startFrame) {
          const relativeFrame = frame - startFrame;
          const progress = Math.min(relativeFrame / totalFrames, 1);
          const easeProgress = 1 - Math.pow(1 - progress, 3);
          updatedScores[key] = targetScores[key] * easeProgress;
          if (progress < 1) finished = false;
        } else {
          finished = false;
        }
      });

      setCurrentScores(updatedScores);
      if (!finished) requestAnimationFrame(animate);
    };

    const timer = setTimeout(() => {
      setIsActive(true);
      requestAnimationFrame(animate);
    }, 200);

    return () => { clearTimeout(timer); cancelAnimationFrame(animate); };
  }, []);

  // 3. 좌표 계산 함수 (거미줄과 데이터 영역 공용)
  const getCoordinates = (scores, limit) => {
    const labels = ['politics', 'economy', 'society', 'living', 'itScience', 'world'];
    const center = 100;
    const radius = 60;
    return labels.map((label, i) => {
      const angle = (Math.PI / 3) * i - Math.PI / 2;
      const scoreRatio = (scores[label] || 0) / limit;
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
        rightChild={<UserMenu />}
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
              <div style={{ width: '500px', height: '350px' }}>
                <svg viewBox="-20 10 250 180" className="w-full h-full">
                  {/* --- 거미줄(가이드라인) 복구 구간 --- */}
                  {[0.2, 0.4, 0.6, 0.8, 1].map((r) => {
                    // 각 단계별로 모든 카테고리 점수가 동일한 가상의 객체 생성
                    const guideScores = {
                      politics: dynamicLimit * r, economy: dynamicLimit * r, 
                      society: dynamicLimit * r, living: dynamicLimit * r, 
                      itScience: dynamicLimit * r, world: dynamicLimit * r
                    };
                    return (
                      <polygon
                        key={r}
                        points={getCoordinates(guideScores, dynamicLimit)}
                        fill="none"
                        stroke="#f0f0f0"
                        strokeWidth="1"
                      />
                    );
                  })}
                  {/* ---------------------------------- */}

                  {/* 데이터 영역 */}
                  <polygon
                    className={`radar-polygon ${isActive ? 'active' : ''}`}
                    points={getCoordinates(currentScores, dynamicLimit)}
                    fill="#0496f721"
                    stroke="#000000ff"
                    strokeWidth="0.1"
                    strokeLinejoin="round"
                  />

                  {/* 라벨 텍스트 */}
                  <text x="100" y="33" textAnchor="middle" fontSize="10" fill="#4b5563" fontWeight="">정치</text>
                  <text x="160" y="75" textAnchor="start" fontSize="10" fill="#4b5563" fontWeight="">경제</text>
                  <text x="160" y="135" textAnchor="start" fontSize="10" fill="#4b5563" fontWeight="">사회</text>
                  <text x="100" y="177" textAnchor="middle" fontSize="10" fill="#4b5563" fontWeight="">생활</text>
                  <text x="40" y="135" textAnchor="end" fontSize="10" fill="#4b5563" fontWeight="">과학</text>
                  <text x="40" y="75" textAnchor="end" fontSize="10" fill="#4b5563" fontWeight="">세계</text>
                </svg>
              </div>
            </div>
          </section>

          {/* 오른쪽 키워드 섹션 (해시태그 스타일) */}
          <section className="info-section">
            <div style={{ flex: 1 }}>
              <h3 className="section-title">나의 관심 키워드</h3>
              <div className="keyword-list">
                {['반도체', '금리', '오픈AI', '미대선', '건강'].map(tag => (
                  <span key={tag} className="keyword-tag" style={{ color: '#0095f6', marginRight: '5px' }}>
                    #{tag}
                  </span>
                ))}
              </div>
            </div>
            <div className="analysis-footer">
              <p className="text-xs text-gray-400 mb-1">AI 분석 결과</p>
              <p className="text-lg font-black leading-tight italic">
                당신의 데이터 분석 결과,<br />사회 및 과학 분야의 관심도가 높습니다.
              </p>
            </div>
          </section>
        </div>
      </main>
    </div>
  );
};

export default MyPage;
