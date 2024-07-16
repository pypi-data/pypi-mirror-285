import * as React from 'react';
import { SVGProps } from 'react';

const LinkIcon = (props: SVGProps<SVGSVGElement>) => (
  <svg
    width={14}
    height={14}
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    {...props}
  >
    <g clipPath="url(#a)" fill="#fff">
      <path d="M8.077 3.929 6.174 2.026a2.933 2.933 0 0 0-4.148 4.147L3.93 8.077a.583.583 0 1 1-.825.825L1.202 6.997A4.1 4.1 0 0 1 7 1.201l1.903 1.903a.583.583 0 0 1-.825.825h-.001ZM12.8 12.798A4.07 4.07 0 0 1 9.902 14a4.073 4.073 0 0 1-2.897-1.2l-1.906-1.903a.583.583 0 1 1 .825-.825l1.904 1.902a2.933 2.933 0 0 0 4.146-4.147L10.07 5.925a.584.584 0 0 1 .826-.826l1.902 1.902a4.104 4.104 0 0 1 .001 5.797Z" />
      <path d="m8.338 9.163-3.5-3.5a.583.583 0 1 1 .825-.824l3.5 3.5a.583.583 0 0 1-.825.824Z" />
    </g>
    <defs>
      <clipPath id="a">
        <path fill="#fff" transform="matrix(1 0 0 -1 0 14)" d="M0 0h14v14H0z" />
      </clipPath>
    </defs>
  </svg>
);

export default LinkIcon;
