import React, { useState } from 'react';

export const EditableTitle = ({ title, onChange }) => {
    const [isEditing, setIsEditing] = useState(false);
    const [currentTitle, setCurrentTitle] = useState(title);

    const handleBlur = () => {
        setIsEditing(false);
        onChange(currentTitle);
    };

    const handleKeyDown = (e) => {
        if (e.key === 'Enter') {
            setIsEditing(false);
            onChange(currentTitle);
        }
    };

    return (
        <div>
            {isEditing ? (
                <input
                    type="text"
                    value={currentTitle}
                    onChange={(e) => setCurrentTitle(e.target.value)}
                    onBlur={handleBlur}
                    onKeyDown={handleKeyDown}
                    autoFocus
                />
            ) : (
                <h2 onClick={() => setIsEditing(true)}>{currentTitle}</h2>
            )}
        </div>
    );
};