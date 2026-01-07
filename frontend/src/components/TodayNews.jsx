import React from 'react';
import { useNavigate } from 'react-router-dom';
import Logo from '../components/Logo';
import loginIcon from '../login_icon/login.png';
import Header from '../components/Header';

const MyPage = () => {
  const scores = {
    politics: 80, economy: 65, society: 90, living: 70, itScience: 85, world: 50
  };

  const navigate = useNavigate();

  const getCoordinates = (scores) => {
    const labels = ['politics', 'economy', 'society', 'living', 'itScience', 'world'];
    const center = 100;
    const radius = 60;
    
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
      <Header
        headerTop="off"
        headerMain="on"
        headerBottom="off"
        leftChild={<Logo />}
        rightChild={<img src={loginIcon} width='35px' onClick={() => navigate('/login')} className="cursor-pointer" alt="login" />}
      />
      
      <main className="max-w-[1000px] mx-auto mt-6">
        {/* 상단 프로필 */}
        <section className="bg-black text-white p-8 mb-6 shadow-md">
          <h1 className="text-xl font-bold">행복한 춘식이</h1>
          <p className="text-gray-400 text-sm font-light">user_id@vaccine.com</p>
        </section>

        {/* [가로 스크롤 레이아웃 적용 구간] */}
        <div className="flex overflow-x-auto gap-6 pb-4 no-scrollbar">
          
          {/* 왼쪽 섹션: 최소 너비(min-w)를 지정해야 스크롤 시 안 찌그러짐 */}
          <section className="bg-white border p-6 shadow-sm min-w-[320px] md:flex-1 h-[320px] flex flex-col">
            <h3 className="font-bold mb-4 border-b pb-2 text-sm md:text-base">나의 관심 카테고리</h3>
            <div className="flex-1 flex items-center justify-center">
              <div className="relative w-36 h-36">
                {[0.2, 0.4, 0.6, 0.8, 1].map((r) => (
                  <polygon key={r} points={getCoordinates({ politics: 100*r, economy: 100*r, society: 100*r, living: 100*r, itScience: 100*r, world: 100*r })} fill="none" stroke="#f0f0f0" strokeWidth="1" />
                ))}
                <polygon points={points} fill="rgba(250, 204, 21, 0.6)" stroke="#facc15" strokeWidth="2" />
                <text x="100" y="25" textAnchor="middle" fontSize="14" className="fill-gray-600 font-bold">정치</text>
                <text x="180" y="75" textAnchor="start" fontSize="14" className="fill-gray-600 font-bold">경제</text>
                <text x="180" y="135" textAnchor="start" fontSize="14" className="fill-gray-600 font-bold">사회</text>
                <text x="100" y="185" textAnchor="middle" fontSize="14" className="fill-gray-600 font-bold">생활</text>
                <text x="20" y="135" textAnchor="end" fontSize="14" className="fill-gray-600 font-bold">IT</text>
                <text x="20" y="75" textAnchor="end" fontSize="14" className="fill-gray-600 font-bold">세계</text>
              </div>
            </div>
          </section>

          {/* 오른쪽 섹션 */}
          <section className="bg-white border p-6 shadow-sm min-w-[320px] md:flex-1 h-[320px] flex flex-col justify-between">
            <div>
              <h3 className="font-bold mb-6 border-b pb-2 text-sm md:text-base">나의 관심 키워드</h3>
              <div className="flex flex-wrap gap-2">
                {['#반도체', '#금리', '#오픈AI', '#미대선', '#건강'].map(tag => (
                  <span key={tag} className="bg-gray-900 text-yellow-400 px-3 py-1 text-[11px] border border-gray-700 font-mono italic">
                    {tag}
                  </span>
                ))}
              </div>
            </div>
            
            <div className="mt-4 pt-4 border-t border-gray-100">
               <p className="text-xs text-gray-400 mb-1">AI 분석 리포트</p>
               <p className="text-base font-black text-black leading-tight">주로 사회 이슈와 IT 기술에<br/>관심이 집중되어 있습니다.</p>
            </div>
          </section>

        </div>
      </main>
    </div>
  );
};

export default MyPage;