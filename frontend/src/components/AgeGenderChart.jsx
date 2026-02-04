import React, { useState } from 'react';
import './AgeGenderChart.css';

const AgeGenderChart = ({ ageData: propAgeData, genderData: propGenderData }) => {
    const [isActive, setIsActive] = useState(false);

    // 빈 데이터면 빈 배열 사용 (빈 차트 표시)
    const ageData = (propAgeData && propAgeData.length > 0) ? propAgeData : [];
    const genderData = (propGenderData && propGenderData.length > 0) ? propGenderData : [];

    const maxAgeCount = ageData.length > 0 ? Math.max(...ageData.map(d => d.count), 1) : 100;

    // 컴포넌트 마운트 시 애니메이션 시작
    React.useEffect(() => {
        setTimeout(() => setIsActive(true), 100);
    }, []);

    return (
        <div className="AgeGenderChart">
            {/* 연령대별 차트 */}
            <section className="chart-section">
                <h3 className="chart-title">연령대별 조회수</h3>
                <div className="chart-wrapper">
                    {ageData.length > 0 ? (
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
                                    <span className="bar-count">{item.count}명</span>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div style={{
                            height: '260px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            color: '#999',
                            fontSize: '12px'
                        }}>
                            데이터 없음
                        </div>
                    )}
                </div>
            </section>

            {/* 성별 차트 - 파이 차트 */}
            <section className="chart-section">
                <h3 className="chart-title">성별 조회수</h3>
                <div className="chart-wrapper">
                    <div className="pie-chart-container">
                        <div className="pie-chart-wrapper">
                            <div
                                className="pie-chart"
                                style={{
                                    background: (genderData.length > 0 && isActive)
                                        ? genderData.length === 1
                                            ? (genderData[0].gender === '남성' ? '#0891b2' : '#ec4899')
                                            : `conic-gradient(
                                                #0891b2 0deg ${(genderData[0].count / (genderData[0].count + genderData[1].count)) * 360}deg,
                                                #ec4899 ${(genderData[0].count / (genderData[0].count + genderData[1].count)) * 360}deg 360deg
                                              )`
                                        : '#f0f0f0',
                                    transition: 'background 1s ease-out'
                                }}
                            >
                                <div className="pie-chart-center">
                                    <div className="pie-chart-text">
                                        {genderData.length > 0 ? (
                                            genderData.map((item, index) => {
                                                const total = genderData.reduce((sum, g) => sum + g.count, 0);
                                                const percentage = total > 0 ? ((item.count / total) * 100).toFixed(1) : 0;
                                                return (
                                                    <div key={item.gender} className="pie-text-item">
                                                        <span className={`pie-text-label ${item.gender === '남성' ? 'male-text' : 'female-text'}`}>
                                                            {item.gender}
                                                        </span>
                                                        <span className="pie-text-value">
                                                            {item.count}명 ({percentage}%)
                                                        </span>
                                                    </div>
                                                );
                                            })
                                        ) : (
                                            <div style={{ color: '#999', fontSize: '12px' }}>
                                                데이터 없음
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    );
};

export default AgeGenderChart;
