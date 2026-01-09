import React from 'react';

const KeywordBarChart = ({ readKeywords = {}, isActive }) => {
  const topKeywords = Object.entries(readKeywords)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 10);

  const maxCount = Math.max(...Object.values(readKeywords), 1);

  return (
    <section className="info-section">
      <h3 className="section-title">관심 키워드 Top 10</h3>
      <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-around', height: '180px', padding: '20px 0' }}>
        {topKeywords.map(([keyword, count], index) => (
          <div key={keyword} className="bar-wrapper" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: '9%', position: 'relative' }}>
            <div className="bar-tooltip" style={{ position: 'absolute', top: '-30px', backgroundColor: '#1e293b', color: 'white', padding: '4px 8px', fontSize: '10px', fontWeight: 'bold', opacity: 0, transition: 'opacity 0.2s ease', pointerEvents: 'none', whiteSpace: 'nowrap', zIndex: 10 }}>
              {count}회 읽음
            </div>
            <div style={{ width: '80%', backgroundColor: '#ffffff', height: '100px', position: 'relative', overflow: 'hidden', cursor: 'pointer', borderBottom: '1px solid #eee' }}>
              <div className="bar-fill-element" style={{ 
                  position: 'absolute', bottom: 0, left: 0, right: 0, backgroundColor: '#0095f6', 
                  height: isActive ? `${(count / (maxCount + 5)) * 100}%` : '0%',
                  transition: `height 1s cubic-bezier(0.17, 0.67, 0.83, 0.67) ${index * 0.05}s` 
              }} />
            </div>
            <span style={{ fontSize: '9px', marginTop: '8px', fontWeight: '600', color: '#475569', textAlign: 'center', wordBreak: 'keep-all' }}>{keyword}</span>
          </div>
        ))}
      </div>
    </section>
  );
};

export default KeywordBarChart; // 💡 Export 추가!