import React, { useState, useEffect } from 'react';
import '../../style/LogoLoader.css';

const logoData = [
  {
    url: 'https://qbraid-static.s3.amazonaws.com/logos/nvidia.png',
    name: 'nvidia',
    logo_class: ''
  },
  {
    url: 'https://qbraid-static.s3.amazonaws.com/logos/amd.png',
    name: 'amd',
    logo_class: 'invert'
  }
];

const LogoLoader = () => {
  const [currentLogo, setCurrentLogo] = useState();

  useEffect(() => {
    let i = 0;
    setCurrentLogo(logoData[i++ % logoData.length]);
    const timer = setInterval(() => {
      setCurrentLogo(logoData[i++ % logoData.length]);
    }, 1500);

    return () => clearInterval(timer);
  }, []);

  return (
    <div className={currentLogo?.name}>
      <img
        src={currentLogo?.url}
        width={200}
        height={40}
        className={currentLogo?.logo_class}
      />
    </div>
  );
};

export default LogoLoader;
