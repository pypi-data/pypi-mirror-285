import React from 'react';
import { SVGProps } from 'react';

const SearchIcon = ({ width, height, color }: SVGProps<SVGElement>) => {
  return (
    <svg
      width={width}
      height={height}
      viewBox="0 0 34 34"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <path
        d="M32.2501 32.25L25.1472 25.1345M29.0834 15.625C29.0834 19.1944 27.6655 22.6176 25.1416 25.1415C22.6176 27.6654 19.1945 29.0833 15.6251 29.0833C12.0557 29.0833 8.63253 27.6654 6.1086 25.1415C3.58468 22.6176 2.16675 19.1944 2.16675 15.625C2.16675 12.0556 3.58468 8.63245 6.1086 6.10852C8.63253 3.5846 12.0557 2.16667 15.6251 2.16667C19.1945 2.16667 22.6176 3.5846 25.1416 6.10852C27.6655 8.63245 29.0834 12.0556 29.0834 15.625V15.625Z"
        stroke={color}
        strokeWidth="3"
        strokeLinecap="round"
      />
    </svg>
  );
};

SearchIcon.defaultProps = {
  width: '16',
  height: '16',
  color: '#ABABAB'
};

export default SearchIcon;
