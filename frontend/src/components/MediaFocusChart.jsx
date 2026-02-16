import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine, Cell } from 'recharts';

const MediaFocusChart = ({ data }) => {
    // data 구조: { media_focus: [...], market_avg_pct: 3.5 }
    if (!data || !data.media_focus || data.media_focus.length === 0) {
        return (
            <div style={{ padding: '20px', textAlign: 'center', color: '#888', backgroundColor: '#f9f9f9', borderRadius: '12px', border: '1px solid #eee', fontSize: '13px' }}>
                <p style={{ marginBottom: '5px', fontWeight: 'bold' }}>분석된 언론사 데이터가 없습니다.</p>
                <p style={{ margin: 0 }}>전체 기사 수가 너무 적거나, 언론사를 식별할 수 없는 경우입니다.</p>
            </div>
        );
    }

    const { media_focus, market_avg_pct } = data;

    // 상위 5개만 표시 (모바일 고려)
    // 상위 5개만 표시 (모바일 고려)
    const chartData = media_focus.slice(0, 5);

    // 툴팁 커스텀 (마우스 따라다니기: Recharts 기본 동작 활용)
    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            const { focus_pct, total_count, issue_count } = payload[0].payload;
            return (
                <div style={{
                    backgroundColor: 'rgba(255, 255, 255, 0.95)',
                    border: '1px solid #ddd',
                    padding: '10px 14px',
                    borderRadius: '8px',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                    fontSize: '13px',
                    color: '#333',
                    pointerEvents: 'none', // 마우스 이벤트 간섭 방지
                    whiteSpace: 'nowrap'
                }}>
                    <p style={{ fontWeight: 'bold', marginBottom: '6px', fontSize: '14px', borderBottom: '1px solid #eee', paddingBottom: '4px' }}>
                        {label}
                    </p>
                    <p style={{ margin: '4px 0' }}>
                        <span style={{ color: '#666' }}>보도 비중: </span>
                        <strong style={{ color: '#3B82F6', fontSize: '1.1em' }}>{focus_pct}%</strong>
                    </p>
                    <p style={{ margin: '4px 0', fontSize: '12px', color: '#888' }}>
                        (전체 {total_count}건 중 {issue_count}건)
                    </p>
                </div>
            );
        }
        return null;
    };

    return (

        <div className="media-focus-chart-container" style={{ width: '100%', height: '100%', padding: '0' }}>
            <h3 className="section-title" style={{ textAlign: 'left', marginTop: '0' }}>
                언론사별 보도 비중 (관심도)
            </h3>
            {/* <p style={{ margin: '0 0 15px 0', fontSize: '0.85rem', color: '#666' }}>
                각 언론사가 전체 기사 중 이 이슈를 얼마나 많이 다뤘는지(%) 보여줍니다.
            </p> */}{/* 설명이 너무 길면 디자인을 해칠 수 있어 주석 처리하거나 제거 */}

            <ResponsiveContainer width="100%" height={250}>
                <BarChart
                    data={chartData}
                    layout="vertical"
                    margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
                >
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} opacity={0.3} />
                    <XAxis type="number" domain={[0, 'auto']} hide />
                    <YAxis
                        type="category"
                        dataKey="company"
                        width={60}
                        tick={{ fontSize: 13, fontWeight: 500 }}
                        axisLine={false}
                        tickLine={false}
                    />
                    <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(0,0,0,0.03)' }} />


                    <Bar dataKey="focus_pct" radius={[0, 4, 4, 0]} barSize={24} fill="#3B82F6" />
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
};

export default MediaFocusChart;
