import * as React from 'react';
import { SVGProps } from 'react';

const UserIcon = (props: SVGProps<SVGSVGElement>) => (
  <svg
    width={16}
    height={17}
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    {...props}
  >
    <path
      d="M8 .667A4.167 4.167 0 1 0 8 9 4.167 4.167 0 0 0 8 .667Zm0 6.666a2.5 2.5 0 1 1 0-5 2.5 2.5 0 0 1 0 5Zm7.5 9.167v-.833a5.833 5.833 0 0 0-5.833-5.834H6.333A5.833 5.833 0 0 0 .5 15.667v.833h1.667v-.833A4.167 4.167 0 0 1 6.333 11.5h3.334a4.167 4.167 0 0 1 4.166 4.167v.833H15.5Z"
      fill="#fff"
    />
  </svg>
);

export default UserIcon;
