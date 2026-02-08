import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine, Cell } from 'recharts';

const MediaFocusChart = ({ data }) => {
    if (!data || data.length === 0) {
        return (
            <div style={{ padding: '20px', textAlign: 'center', color: '#666', backgroundColor: '#f9f9f9', borderRadius: '8px' }}>
                데이터가 부족하여 분석할 수 없습니다.
            </div>
        );
    }

    // 상위 5개만 표시 (모바일 고려)
    const chartData = data.slice(0, 5);

    return (
        <div className="media-focus-chart-container" style={{ width: '100%', height: '300px', backgroundColor: '#fff', padding: '10px', borderRadius: '8px', border: '1px solid #eee' }}>
            <h4 style={{ margin: '0 0 10px 0', fontSize: '1rem', color: '#333', textAlign: 'left', borderBottom: '1px solid #eee', paddingBottom: '8px' }}>
                언론사별 집중도 분석
                <span style={{ fontSize: '0.8rem', color: '#888', fontWeight: 'normal', marginLeft: '8px' }}>
                    (1.0 = 평균, 높을수록 집중 보도)
                </span>
            </h4>
            <ResponsiveContainer width="100%" height="90%">
                <BarChart
                    data={chartData}
                    layout="vertical"
                    margin={{ top: 5, right: 30, left: 40, bottom: 5 }}
                >
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                    <XAxis type="number" domain={[0, 'dataMax + 0.5']} />
                    <YAxis type="category" dataKey="company" width={60} tick={{ fontSize: 12 }} />
                    <Tooltip
                        formatter={(value, name) => [value, "집중도 지수"]}
                        labelStyle={{ fontWeight: 'bold' }}
                        contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}
                    />
                    <ReferenceLine x={1} stroke="red" strokeDasharray="3 3" label={{ position: 'top', value: '평균(1.0)', fill: 'red', fontSize: 10 }} />
                    <Bar dataKey="focus_index" radius={[0, 4, 4, 0]} barSize={20}>
                        {chartData.map((entry, index) => (
                            <Cell key={`cell-${index}`} fill={entry.focus_index > 1.2 ? '#d32f2f' : '#1976d2'} />
                        ))}
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
};

export default MediaFocusChart;
