import * as React from 'react';
import { SVGProps } from 'react';

const BackIcon = (props: SVGProps<SVGSVGElement>) => (
  <svg
    width={42}
    height={42}
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    {...props}
  >
    <rect
      x={1.5}
      y={1.5}
      width={39}
      height={39}
      rx={10.5}
      stroke="#fff"
      strokeWidth={3}
    />
    <path
      d="M24.588 11.382a1.456 1.456 0 0 1 0 2.058l-7.207 7.207 7.207 7.207a1.456 1.456 0 0 1-2.059 2.058l-8.236-8.236a1.456 1.456 0 0 1 0-2.058l8.236-8.236a1.456 1.456 0 0 1 2.059 0Z"
      fill="#fff"
    />
  </svg>
);

export default BackIcon;
