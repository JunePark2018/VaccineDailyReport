import React, { useState } from 'react';
import './AgeGenderChart.css';

const AgeGenderChart = () => {
    const [isActive, setIsActive] = useState(false);

    // 더미 데이터 - 연령대별 조회 수
    const ageData = [
        { age: '10대', count: 15 },
        { age: '20대', count: 142 },
        { age: '30대', count: 98 },
        { age: '40대', count: 76 },
        { age: '50대', count: 45 },
        { age: '60대+', count: 23 }
    ];

    // 더미 데이터 - 성별 조회 수
    const genderData = [
        { gender: '남성', count: 245 },
        { gender: '여성', count: 154 }
    ];

    const maxAgeCount = Math.max(...ageData.map(d => d.count), 1);
    const totalGenderRaw = genderData[0].count + genderData[1].count;

    // 컴포넌트 마운트 시 애니메이션 시작
    React.useEffect(() => {
        setTimeout(() => setIsActive(true), 100);
    }, []);

    return (
        <div className="AgeGenderChart">
            {/* 성별 차트 - 도넛 차트 (New Design) */}
            <section className="chart-section gender-chart-section">
                <div className="gender-header">
                    <div className="chart-title" style={{ borderLeft: 'none', paddingLeft: 0 }}>통계</div>
                </div>

                <div className="gender-body">
                    {/* Left: Legend */}
                    <div className="gender-legend">
                        {genderData.map((item, index) => {
                            const percent = Math.round((item.count / totalGenderRaw) * 100);
                            const colorClass = item.gender === '남성' ? 'male-color' : 'female-color';
                            const labelEn = item.gender === '남성' ? '남성' : '여성';

                            return (
                                <div key={item.gender} className="legend-item">
                                    <div className={`legend-dot ${colorClass}`}></div>
                                    <div className="legend-text">
                                        <span className="legend-percent">{labelEn} {percent}% </span>
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    {/* Right: Donut Chart (SVG) */}
                    <div className="gender-chart-wrapper">
                        <div
                            className="donut-chart"
                            style={{
                                background: isActive
                                    ? `conic-gradient(
                                        #3b82f6 0deg ${(genderData[0].count / totalGenderRaw) * 360}deg,
                                        #ff7b98ff ${(genderData[0].count / totalGenderRaw) * 360}deg 360deg
                                      )`
                                    : '#f0f0f0'
                            }}
                        >
                            <div className="donut-hole"></div>
                        </div>
                    </div>
                </div>
            </section>

            {/* 연령대별 차트 */}
            <section className="chart-section">
                <div className="chart-wrapper">
                    <div className="bars-container age-bars">
                        {ageData.map((item, index) => (
                            <div key={item.age} className="bar-item">
                                <div className="bar-tooltip">
                                    {item.count}명
                                </div>
                                <div className="bar-track">
                                    <div
                                        className="bar-fill age-bar-fill"
                                        style={{
                                            height: isActive ? `${(item.count / maxAgeCount) * 100}%` : '0%',
                                            transitionDelay: `${index * 0.1}s`
                                        }}
                                    />
                                </div>
                                <span className="bar-label">{item.age}</span>
                            </div>
                        ))}
                    </div>
                </div>
            </section>
        </div>
    );
};

export default AgeGenderChart;
