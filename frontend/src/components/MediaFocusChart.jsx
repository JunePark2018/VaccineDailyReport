import React from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, LabelList } from 'recharts';

const MOCK_MEDIA_FOCUS = {
    media_focus: [
        { company: '조선일보', focus_pct: 8.2, total_count: 120, issue_count: 10 },
        { company: '한겨레', focus_pct: 6.5, total_count: 95, issue_count: 6 },
        { company: '중앙일보', focus_pct: 5.1, total_count: 110, issue_count: 6 },
        { company: 'KBS', focus_pct: 4.3, total_count: 80, issue_count: 3 },
        { company: 'SBS', focus_pct: 3.7, total_count: 85, issue_count: 3 },
    ],
    market_avg_pct: 4.5,
};

const CustomBarLabel = (props) => {
    const { x, y, width, height, value, index } = props;
    const item = props.data[index];
    return (
        <text
            x={x + width + 6}
            y={y + height / 2}
            dominantBaseline="central"
            fontSize={14}
            fill="#333"
        >
            <tspan fontWeight="600" fill="#3B82F6" fontSize={15}>{value}%</tspan>
            <tspan fill="#888" dx="6" fontSize={13}>({item.issue_count}/{item.total_count}건)</tspan>
        </text>
    );
};

const MediaFocusChart = ({ data }) => {
    const effectiveData = (data && data.media_focus && data.media_focus.length > 0) ? data : MOCK_MEDIA_FOCUS;
    const { media_focus } = effectiveData;
    const chartData = media_focus.slice(0, 5);

    return (
        <div className="media-focus-chart-container" style={{ width: '100%', height: '100%', padding: '0' }}>
            <h3 className="section-title" style={{ textAlign: 'left', marginTop: '0' }}>
                이 이슈를 가장 많이 다룬 언론사
            </h3>

            <ResponsiveContainer width="100%" height={250}>
                <BarChart
                    data={chartData}
                    layout="vertical"
                    margin={{ top: 5, right: 120, left: 40, bottom: 5 }}
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
                    <Bar dataKey="focus_pct" radius={[0, 4, 4, 0]} barSize={24} fill="#3B82F6" isAnimationActive={false}>
                        <LabelList
                            dataKey="focus_pct"
                            content={<CustomBarLabel data={chartData} />}
                        />
                    </Bar>
                </BarChart>
            </ResponsiveContainer>
        </div>
    );
};

export default MediaFocusChart;
