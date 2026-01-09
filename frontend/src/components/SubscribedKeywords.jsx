import React, { useState } from 'react';
import Button from '../components/Button';

const SubscribedKeywords = ({ keywords = [], isEditMode, onToggleEdit, onDelete, onAdd }) => {
  const [newKeyword, setNewKeyword] = useState('');

  const handleAdd = () => {
    if (newKeyword.trim()) {
      onAdd(newKeyword.trim());
      setNewKeyword('');
    }
  };

  return (
    <section className='keyword-listname' style={{ marginTop: '20px', marginBottom:'50px', padding: '20px', backgroundColor: 'white', border: '1px solid #e5e7eb'  }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
        <span style={{ fontWeight: 'bold', fontSize: '18px' }}>구독 중인 키워드</span>
        <Button 
          text={isEditMode ? "저장" : "관리"} 
          color={isEditMode ? "#111" : "transparent"} 
          textColor={isEditMode ? "white" : "#6b7280"} 
          fontSize="11px" width="90px" height="32px" 
          onClick={onToggleEdit} 
        />
      </div>
      <div className="keyword-list" style={{ display: 'flex', flexWrap: 'wrap', gap: '10px', alignItems: 'center' }}>
        {keywords.map(tag => (
          <span key={tag} className="keyword-tag" style={{ color: '#0095f6', backgroundColor: isEditMode ? '#f0f9ff' : 'transparent', padding: isEditMode ? '4px 12px' : '0', borderRadius: '20px', border: isEditMode ? '1px solid #bae6fd' : 'none', display: 'flex', alignItems: 'center' }}>
            #{tag}
            {isEditMode && <span onClick={() => onDelete(tag)} style={{ marginLeft: '8px', color: '#ef4444', cursor: 'pointer', fontWeight: 'bold' }}>×</span>}
          </span>
        ))}
        {isEditMode && (
          <div style={{ display: 'flex', alignItems: 'center', borderBottom: '2px solid #0095f6', paddingBottom: '2px', marginLeft: '5px' }}>
            <input 
              type="text" value={newKeyword} 
              onChange={(e) => setNewKeyword(e.target.value)} 
              placeholder="추가..." 
              onKeyPress={(e) => e.key === 'Enter' && handleAdd()}
              style={{ border: 'none', outline: 'none', fontSize: '13px', width: '80px', backgroundColor: 'transparent' }} 
            />
            <span onClick={handleAdd} style={{ cursor: 'pointer', color: '#0095f6', fontSize: '18px', fontWeight: 'bold', marginLeft: '5px' }}>+</span>
          </div>
        )}
      </div>
      <br></br>  
    </section>
  );
};

export default SubscribedKeywords; // 💡 Export 추가!