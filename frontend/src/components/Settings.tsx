import React, { useState } from 'react';

interface SettingsProps {
  temperature: number;
  setTemperature: (val: number) => void;
  maxTokens: number;
  setMaxTokens: (val: number) => void;
}

const Settings: React.FC<SettingsProps> = ({ temperature, setTemperature, maxTokens, setMaxTokens }) => {
  const [show, setShow] = useState(false);

  return (
    <div className="relative">
      <button onClick={() => setShow(!show)} className="px-3 py-1 bg-gray-800 border border-gray-700 rounded-md text-sm hover:bg-gray-700 transition-colors flex items-center gap-1">
        ⚙️ <span className="hidden sm:inline">Settings</span>
      </button>
      {show && (
        <div className="absolute right-0 mt-2 w-64 bg-gray-800 border border-gray-700 rounded-lg p-4 z-20 shadow-xl">
          <label className="block text-xs font-semibold text-gray-300">Temperature: {temperature}</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={temperature}
            onChange={(e) => setTemperature(parseFloat(e.target.value))}
            className="w-full mt-1"
          />
          <label className="block text-xs font-semibold text-gray-300 mt-3">Max Tokens: {maxTokens}</label>
          <input
            type="number"
            value={maxTokens}
            onChange={(e) => setMaxTokens(parseInt(e.target.value) || 512)}
            className="w-full bg-gray-700 border border-gray-600 rounded p-1.5 text-xs text-white mt-1"
          />
          <p className="text-[10px] text-gray-400 mt-2">Adjust inference parameters for Ollama DeepSeek-R1.</p>
        </div>
      )}
    </div>
  );
};

export default Settings;
