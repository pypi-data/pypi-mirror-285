import * as React from 'react';
import { SVGProps } from 'react';

const DescriptionIcon = (props: SVGProps<SVGSVGElement>) => (
  <svg
    width={14}
    height={18}
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    {...props}
  >
    <path
      d="M12.25 1.5V0h-1.5v1.5h-1.5V0h-1.5v1.5h-1.5V0h-1.5v1.5h-1.5V0h-1.5v1.5H.25v14.25A2.25 2.25 0 0 0 2.5 18h9a2.25 2.25 0 0 0 2.25-2.25V1.5h-1.5Zm0 14.25a.75.75 0 0 1-.75.75h-9a.75.75 0 0 1-.75-.75V3h10.5v12.75Zm-1.5-9h-7.5v-1.5h7.5v1.5Zm0 3h-7.5v-1.5h7.5v1.5Zm-3 3h-4.5v-1.5h4.5v1.5Z"
      fill="#fff"
    />
  </svg>
);

export default DescriptionIcon;
