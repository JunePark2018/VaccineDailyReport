import React from 'react';

const CATEGORIES = ['정치', '경제', '사회', '생활/문화', 'IT/과학', '세계'];

const CategoryRadarChart = ({ targetScores = {}, dynamicLimit, isActive }) => {
  const getCoordinates = (scores, limit, active) => {
    const center = 100, radius = 60;
    return CATEGORIES.map((label, i) => {
      const angle = (Math.PI / 3) * i - Math.PI / 2;
      const scoreRatio = active ? (scores[label] || 0) / limit : 0;
      return `${center + radius * scoreRatio * Math.cos(angle)},${center + radius * scoreRatio * Math.sin(angle)}`;
    }).join(' ');
  };

  return (
    <section className="info-section">
      <h3 className="section-title">나의 관심 카테고리</h3>
      <div className="chart-container" style={{ display: 'flex', justifyContent: 'center' }}>
        <div style={{ width: '500px', height: '350px' }}>
          <svg viewBox="-20 10 250 180" className="w-full h-full" style={{ overflow: 'visible' }}>
            {[0.2, 0.4, 0.6, 0.8, 1].map((r) => (
              <polygon 
                key={r} 
                points={getCoordinates(Object.fromEntries(CATEGORIES.map(c => [c, dynamicLimit * r])), dynamicLimit, true)} 
                fill="none" stroke="#f0f0f0" strokeWidth="1" 
              />
            ))}
            <polygon 
              points={getCoordinates(targetScores, dynamicLimit, isActive)} 
              fill="#0496f721" stroke="#000000ff" strokeWidth="0.1" strokeLinejoin="round"
              style={{ transition: 'points 1.2s cubic-bezier(0.34, 1.56, 0.64, 1)' }}
            />
            {CATEGORIES.map((label, i) => {
              const angle = (Math.PI / 3) * i - Math.PI / 2;
              const x = 100 + 85 * Math.cos(angle);
              const y = 100 + 85 * Math.sin(angle);
              return <text key={label} x={x} y={y} textAnchor="middle" fontSize="10" fill="#4b5563" fontWeight="bold" dominantBaseline="middle">{label}</text>
            })}
          </svg>
        </div>
      </div>
    </section>
  );
};

export default CategoryRadarChart; // 💡 Export 추가!