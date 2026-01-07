import React from 'react';

const MyPage = () => {
  const scores = {
    politics: 80, economy: 65, society: 90, living: 70, itScience: 85, world: 50
  };

  const getCoordinates = (scores) => {
    const labels = ['politics', 'economy', 'society', 'living', 'itScience', 'world'];
    const center = 100;
    const radius = 70; // 라벨 공간 확보를 위해 반지름 살짝 축소
    
    return labels.map((label, i) => {
      const angle = (Math.PI / 3) * i - Math.PI / 2;
      const scoreRatio = scores[label] / 100;
      const x = center + radius * scoreRatio * Math.cos(angle);
      const y = center + radius * scoreRatio * Math.sin(angle);
      return `${x},${y}`;
    }).join(' ');
  };

  const points = getCoordinates(scores);

  return (
    <div className="min-h-screen bg-[#f3f4f6] p-4 md:p-10 font-sans">
      <main className="max-w-[1000px] mx-auto">
        
        <header className="bg-black text-white p-8 mb-6 flex items-center gap-6 shadow-md">
          <div className="w-11 h-11 bg-gray-700 rounded-full flex items-center justify-center text-2xl border-2 border-gray-500">👤</div>
          <div>
            <h1 className="text-xl font-bold">행복한 춘식이</h1>
            <p className="text-gray-400 text-sm">user_id@vaccine.com</p>
          </div>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          
          {/* 관심 카테고리 분석: 그래프 크기 축소 버전 */}
          <section className="bg-white border p-8 shadow-sm flex flex-col">
            <h3 className="font-bold mb-4 w-full border-b pb-2">관심 카테고리 분석</h3>
            
            <div className="flex-1 flex items-center justify-center">
              {/* w-64 -> w-40 으로 크기 대폭 축소 (약 1/3 ~ 1/2 수준) */}
              <div className="relative w-20 h-200">
                <svg viewBox="-350 0 900 200" className="w-full h-full">
                  {[0.2, 0.4, 0.6, 0.8, 1].map((r) => (
                    <polygon
                      key={r}
                      points={getCoordinates({ politics: 100*r, economy: 100*r, society: 100*r, living: 100*r, itScience: 100*r, world: 100*r })}
                      fill="none"
                      stroke="#f0f0f0"
                      strokeWidth="1"
                    />
                  ))}
                  
                  <polygon
                    points={points}
                    fill="rgba(250, 204, 21, 0.6)"
                    stroke="#facc15"
                    strokeWidth="2"
                  />

                  {/* 텍스트 위치 가독성 조정 */}
                  <text x="100" y="15" textAnchor="middle" fontSize="12" className="fill-gray-600 font-bold">정치</text>
                  <text x="180" y="65" textAnchor="start" fontSize="12" className="fill-gray-600 font-bold">경제</text>
                  <text x="180" y="145" textAnchor="start" fontSize="12" className="fill-gray-600 font-bold">사회</text>
                  <text x="100" y="195" textAnchor="middle" fontSize="12" className="fill-gray-600 font-bold">생활/문화</text>
                  <text x="20" y="145" textAnchor="end" fontSize="12" className="fill-gray-600 font-bold">IT/과학</text>
                  <text x="20" y="65" textAnchor="end" fontSize="12" className="fill-gray-600 font-bold">세계</text>
                </svg>
              </div>
            </div>
          </section>

          <section className="bg-white border p-8 shadow-sm flex flex-col justify-between">
            <div>
              <h3 className="font-bold mb-6 border-b pb-2">나의 관심 키워드</h3>
              <div className="flex flex-wrap gap-2">
                {['#반도체', '#금리', '#오픈AI', '#미대선'].map(tag => (
                  <span key={tag} className="bg-gray-900 text-yellow-400 px-3 py-1 text-xs border border-gray-700 font-mono">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
            
            <div className="mt-8 pt-6 border-t border-gray-100">
               <p className="text-sm text-gray-500 mb-1">가장 높은 관심사</p>
               <p className="text-xl font-black text-black tracking-tight">사회 / IT·과학</p>
            </div>
          </section>

        </div>
      </main>
    </div>
  );
};

export default MyPage;